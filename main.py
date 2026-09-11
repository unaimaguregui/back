from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import math
import os
from functools import lru_cache
import pandas as pd
import duckdb
from backend.core.pandas import motor_escalado_unico, motor_calculo_ratings
from backend.core.pandas import obtener_catalogo_datos
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import threading
import numpy as np
from fastapi.responses import StreamingResponse
import io
import json
import glob
from datetime import datetime
from backend.config.diccionarios import fases_juego
from backend.core.models import UserSettings
import pandas as pd
from backend.core.pandas import obtener_datos_sql
from backend.config.diccionarios import (
    mapa_posiciones, estilos_gk, estilos_cb, estilos_lt, estilos_mcd, 
    estilos_int, estilos_mp, estilos_ext, estilos_del, estilos_med,
    radar_gk, radar_cb, radar_lt, radar_mcd, radar_int, radar_mp, radar_ext, radar_del, PESOS_LIGAS
)

from backend.core.models import SquadPlannerPlayer, ShortlistPlayer
from backend.core.graficos import dibujar_posiciones, dibujar_radares, dibujar_scatter_multi
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity
import re

app = FastAPI(title="FScouting Backend", description="Motor asíncrono impulsado por DuckDB y FastAPI", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
os.makedirs("instance", exist_ok=True)

SQLITE_DATABASE_URL = "sqlite:///instance/scouting_app.db"

engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SquadPlannerPlayer.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_duckdb_conn():
    """ Abre la memoria RAM y enlaza los Parquets como si fueran tablas """
    conn = duckdb.connect(':memory:')
    # 1. Conectamos los jugadores
    conn.execute("""
        CREATE VIEW dim_jugadores_stats AS 
        SELECT * FROM 'Data_Parquet/Jugadores/*/*.parquet'
    """)
    
    try:
        conn.execute(""" CREATE VIEW dim_equipos_stats AS SELECT * FROM 'Data_Parquet/Equipos/*.parquet'""")
    except:
        pass
        
    return conn

def _to_clean_float(value) -> float:
    """Limpia cualquier basura (%, comas, NaNs) y devuelve un float puro."""
    if value is None: return 0.0
    try:
        if pd.isna(value): return 0.0
    except: pass
    if isinstance(value, (int, float)):
        f = float(value)
        return f if math.isfinite(f) else 0.0
    s = str(value).strip()
    if s.lower() in ("", "-", "--", "n/d", "nan", "none"): return 0.0
    s = s.replace("%", "").replace(" ", "").replace(",", ".")
    partes = s.split(".")
    if len(partes) > 2: s = partes[0] + "." + "".join(partes[1:])
    try:
        f = float(s)
        return f if math.isfinite(f) else 0.0
    except:
        return 0.0

def extraer_posiciones_jugador(fila_raw, posicion_evaluada="Principal"):
    """Extrae las posiciones y asegura que el porcentaje siempre sea válido."""
    pares = [
        ("Primary position", "Primary position, %"),
        ("Secondary position", "Secondary position, %"),
        ("Third position", "Third position, %"),
    ]
    resultado = []
    for col_nombre, col_pct in pares:
        nombre_pos = fila_raw.get(col_nombre)
        if nombre_pos is None or (isinstance(nombre_pos, float) and math.isnan(nombre_pos)): continue
        nombre_pos = str(nombre_pos).strip()
        if nombre_pos == "" or nombre_pos.lower() in ("nan", "none", "n/d"): continue

        pct = _to_clean_float(fila_raw.get(col_pct))
        pct = max(0.0, min(100.0, pct))
        resultado.append({"posicion": nombre_pos, "pct": round(pct, 1)})

    if not resultado:
        resultado = [{"posicion": posicion_evaluada, "pct": 100.0}]

    resultado.sort(key=lambda x: x["pct"], reverse=True)
    return resultado

class EquiposFiltroRequest(BaseModel):
    ligas: List[str] = []
    temporadas: List[str] = []

class ClonadorRequest(BaseModel):
    nombre: str
    ligas: List[str] = []
    edad_min: Optional[int] = 0
    edad_max: Optional[int] = 99
    posicion: Optional[str] = None

class JugadorRequest(BaseModel):
    nombre: str

class MoverJugadorRequest(BaseModel):
    nombre: str
    x: float
    y: float

class ProcesarRequest(BaseModel):
    paises: List[str] = []
    ligas: List[str] = []
    temporadas: List[str] = []
    posicion: str
    estilo: str
    mins: Optional[int] = 0
    edad_min: Optional[int] = 0
    edad_max: Optional[int] = 99
    custom_weights: Optional[Dict[str, float]] = None
    perfiles: List[str] = []
    equipos_filtro: List[str] = []

class CompararTemporadasRequest(BaseModel):
    ligas: List[str] = []
    temp_pasada: str = '24-25'
    temp_actual: str = '25-26'
    posicion: str
    estilo: str
    mins: Optional[int] = 500

class TeamFitRadarRequest(BaseModel):
    jugador: str
    wyscout_id: Optional[str] = None
    pesos: dict

class SimularTraspasoRequest(BaseModel):
    jugador: str
    liga_destino: str
    posicion: str = "Delantero"

class CompararRadaresRequest(BaseModel):
    jugadores: List[str]

class EquipoParamRequest(BaseModel):
    liga: str
    temporada: str

class SetEquipoRequest(BaseModel):
    equipo: str
    pais: Optional[str] = None
    liga: Optional[str] = None
    temporada: Optional[str] = None

class H2HRequest(BaseModel):
    jugador1: str
    jugador2: str

class SimilarTeamsRequest(BaseModel):
    equipo: str
    sort_by: Optional[str] = 'Sim_General'

class RadarEquiposRequest(BaseModel):
    equipos: List[str]

class TeamFitRequest(BaseModel):
    equipo_tactico: str
    posicion: str
    ligas: List[str] = []
    temporadas: List[str] = []
    mins: Optional[int] = 0
    edad_min: Optional[int] = 0
    edad_max: Optional[int] = 99
    calidad_min: Optional[int] = 0

# HELPER IA: Aislar cohortes desde DuckDB
def _obtener_cohorte_jugador_duckdb(nombre_jugador: str, posicion_req: Optional[str] = None, ligas_mercado: List[str] = None, edad_min: int = 0, edad_max: int = 99):
    # 🚀 PARSEAMOS EL NOMBRE Y EL EQUIPO
    nombre_real = nombre_jugador.split(" | ")[0].strip()
    equipo_real = nombre_jugador.split(" | ")[1].strip() if " | " in nombre_jugador else None

    with get_duckdb_conn() as conn:
        # Filtramos por nombre Y equipo (adiós homónimos)
        if equipo_real:
            df_jug = conn.execute('SELECT * FROM dim_jugadores_stats WHERE Player = ? AND Team = ? ORDER BY Season DESC, "Minutes played" DESC LIMIT 1', [nombre_real, equipo_real]).df()
        else:
            df_jug = conn.execute('SELECT * FROM dim_jugadores_stats WHERE Player = ? ORDER BY Season DESC, "Minutes played" DESC LIMIT 1', [nombre_real]).df()
            
        if df_jug.empty: return pd.DataFrame(), 'Delantero', nombre_real
        
        temp, comp = df_jug['Season'].iloc[0], df_jug['Competition'].iloc[0]
        gen_pos = next((k for k, v in mapa_posiciones.items() if pd.Series([str(df_jug['Position'].iloc[0])]).str.contains(v, regex=True).iloc[0]), 'Delantero')
        
        if ligas_mercado and len(ligas_mercado) > 0:
            ligas_str = ", ".join([f"'{l.replace(chr(39), '')}'" for l in ligas_mercado])
            df_cohorte = conn.execute(f"SELECT * FROM dim_jugadores_stats WHERE Season = ? AND Competition IN ({ligas_str})", [temp]).df()
            if nombre_real not in df_cohorte['Player'].values:
                df_cohorte = pd.concat([df_cohorte, df_jug]).drop_duplicates(subset=['Player'])
        else:
            df_cohorte = conn.execute('SELECT * FROM dim_jugadores_stats WHERE Season = ? AND Competition = ?', [temp, comp]).df()
    
    if 'Age' in df_cohorte.columns:
        df_cohorte['Age'] = pd.to_numeric(df_cohorte['Age'], errors='coerce').fillna(25)
        df_cohorte = df_cohorte[
            ((df_cohorte['Age'] >= edad_min) & (df_cohorte['Age'] <= edad_max)) | 
            (df_cohorte['Player'] == nombre_real)
        ]

    pos_final = posicion_req if posicion_req else gen_pos
    from backend.core.pandas import filtrar_por_posicion_real, preparar_dataframe
    df_filtrado = filtrar_por_posicion_real(df_cohorte, mapa_posiciones.get(pos_final, ''))
    
    if nombre_real not in df_filtrado['Player'].values:
        df_filtrado = pd.concat([df_filtrado, df_cohorte[df_cohorte['Player'] == nombre_real]])

    df_filtrado = df_filtrado[~df_filtrado['Player'].str.contains(r'\[REF\]', na=False)].copy()
    
    # 🚀 Devolvemos nombre_real para que los modelos no se confundan con el " | Equipo"
    return preparar_dataframe(df_filtrado), pos_final, nombre_real

def cargar_pool_temporada_duckdb(ligas, temporadas, posicion, estilo):
    """ Extrae el pool de jugadores directamente de DuckDB con los ratings calculados """
    df = obtener_datos_sql(ligas, temporadas)
    if df.empty: return pd.DataFrame()
    
    from backend.core.pandas import filtrar_por_posicion_real
    df_filtrado = filtrar_por_posicion_real(df, mapa_posiciones.get(posicion, ''))
    if df_filtrado.empty: return pd.DataFrame()
    
    col_rating = f"Rating_{estilo}"
    df_filtrado['Rating'] = df_filtrado[col_rating] if col_rating in df_filtrado.columns else 50
    col_comp = 'Competition' if 'Competition' in df_filtrado.columns else 'League'
    
    # 🚀 AÑADIDO: Incluimos League_Weight para el cruce de datos
    cols_extraer = ['Wyscout id', 'Player', 'Team', col_comp, 'Minutes played', 'Rating']
    if 'League_Weight' in df_filtrado.columns: cols_extraer.append('League_Weight')
        
    return df_filtrado[cols_extraer].sort_values('Minutes played', ascending=False).drop_duplicates(subset=['Wyscout id'])


def _comparar_temporadas_ia(payload: CompararTemporadasRequest, columna_diff: str, umbral: float, ascending: bool):
    if not payload.ligas: return None, "Faltan ligas."
    
    df_p = cargar_pool_temporada_duckdb(payload.ligas, [payload.temp_pasada], payload.posicion, payload.estilo)
    df_a = cargar_pool_temporada_duckdb(payload.ligas, [payload.temp_actual], payload.posicion, payload.estilo)
    
    if df_p.empty or df_a.empty: return None, "No hay suficientes jugadores para comparar."

    df_merge = pd.merge(df_p, df_a, on=['Wyscout id', 'Player'], suffixes=('_pasado', '_actual'))
    
    # 🚀 LA FÓRMULA PROFESIONAL: Ajuste por coeficiente de Liga
    if 'League_Weight_actual' in df_merge.columns and 'League_Weight_pasado' in df_merge.columns:
        df_merge['Rating_Ponderado_actual'] = df_merge['Rating_actual'] * df_merge['League_Weight_actual'].fillna(1.0)
        df_merge['Rating_Ponderado_pasado'] = df_merge['Rating_pasado'] * df_merge['League_Weight_pasado'].fillna(1.0)
    else:
        df_merge['Rating_Ponderado_actual'] = df_merge['Rating_actual']
        df_merge['Rating_Ponderado_pasado'] = df_merge['Rating_pasado']

    # Calculamos la diferencia basándonos en la dificultad real
    df_merge[columna_diff] = (df_merge['Rating_Ponderado_actual'] - df_merge['Rating_Ponderado_pasado']) * (1 if ascending else -1)
    
    filtro_base = df_merge['Minutes played_actual'] >= payload.mins
    filtro_umbral = df_merge[columna_diff] >= umbral
    return df_merge[filtro_base & filtro_umbral].sort_values(columna_diff, ascending=False).head(30), None

def escanear_mercado_background():
    """
    Tarea en segundo plano: Detección REAL estadística de anomalías (Z-Score).
    """
    nuevas_alertas = []
    try:
        with get_duckdb_conn() as conn:
            df = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Season IN ('25-26', '2026') AND League_Weight >= 0.9").df()
            
        if df.empty or len(df) < 10: return
        
        rating_cols = [c for c in df.columns if c.startswith('Rating_') and c != 'Rating_Personalizado']
        if not rating_cols: return
        
        df['Rating'] = df[rating_cols].max(axis=1).fillna(50)
        mean_r = df['Rating'].mean()
        std_r = df['Rating'].std()
        if std_r == 0: return
        
        df['Z_Score'] = (df['Rating'] - mean_r) / std_r
        
        if 'Age' in df.columns:
            jovenes_top = df[(pd.to_numeric(df['Age'], errors='coerce') <= 21) & (df['Z_Score'] > 1.5)]
            if not jovenes_top.empty:
                sample = jovenes_top.sort_values('Z_Score', ascending=False).head(2)
                for _, row in sample.iterrows():
                    nuevas_alertas.append({
                        "tipo": "breakout", "jugador": row['Player'],
                        "mensaje": f"🚀 ALERTA Z-SCORE: Rendimiento anómalo (+{row['Z_Score']:.1f} σ). A sus {row.get('Age', '?')} años rinde matemáticamente por encima del 90% de sus pares."
                    })
                    
            veteranos_bajos = df[(pd.to_numeric(df['Age'], errors='coerce') >= 30) & (df['Z_Score'] < -1.0)]
            if not veteranos_bajos.empty:
                sample = veteranos_bajos.sort_values('Z_Score').head(1)
                for _, row in sample.iterrows():
                    nuevas_alertas.append({
                        "tipo": "dropoff", "jugador": row['Player'],
                        "mensaje": f"📉 ALERTA DECLIVE: Z-Score negativo ({row['Z_Score']:.1f} σ). Sus métricas han caído por debajo de la desviación estándar aceptable de la liga."
                    })
                    
        with _lock_alertas:
            global MOTOR_ALERTAS
            for na in nuevas_alertas:
                if not any(a['jugador'] == na['jugador'] for a in MOTOR_ALERTAS):
                    MOTOR_ALERTAS.insert(0, na)
            MOTOR_ALERTAS = MOTOR_ALERTAS[:15]
            
    except duckdb.IOException:
        # Silencio: La base de datos está ocupada (seguramente ejecutando el ETL).
        pass
    except duckdb.ConnectionException:
        # Silencio: Choque de configuración temporal.
        pass
    except Exception as e:
        pass # Silenciamos los errores de background para no ensuciar la consola
    

# Nuestro primer Endpoint Asíncrono (async def)
@app.get("/")
async def root():
    return {"status": "ok", "mensaje": "¡FastAPI está vivo y respirando!"}

@app.get("/api/ping")
async def health_check():
    return {"status": "ok", "database": "DuckDB ready"}

# Variable global ultrarrápida en memoria para el catálogo
_CACHE_CATALOGO = []
_CACHE_RADAR_ACTUAL = {}
_CACHE_PLANTILLA = pd.DataFrame()
_CACHE_TEAM_FIT_PESOS = {}
MOTOR_ALERTAS = []
_lock_alertas = threading.Lock()

@app.get("/api/catalogo")
@lru_cache(maxsize=1)
def obtener_catalogo():
    try:
        with get_duckdb_conn() as conn:
            # Consulta SQL corregida: solo usamos 'Competition' que es la columna real de Wyscout
            query = """
                SELECT DISTINCT 
                    Competition as liga, 
                    CAST(Season AS VARCHAR) as temporada 
                FROM dim_jugadores_stats 
                WHERE Competition IS NOT NULL 
                  AND Season IS NOT NULL
            """
            df = conn.execute(query).df()
            return df.to_dict(orient="records")
    except Exception as e:
        print(f"🔴 Error en obtener_catalogo: {e}")
        return {"error": str(e)}


@app.get("/api/jugadores_totales")
async def jugs_tot(db: Session = Depends(get_db)):
    """ Extrae nombres y equipos ultrarrápido sin bloquear el servidor """
    try:
        with get_duckdb_conn() as conn:
            query = "SELECT DISTINCT Player || ' | ' || Team AS Combo FROM dim_jugadores_stats WHERE Player IS NOT NULL"
            df = conn.execute(query).df()
            
            # Pasamos la columna directamente a una lista de Python de golpe
            jugadores_db = df['Combo'].dropna().tolist()
            
        jugadores_pizarra = db.query(SquadPlannerPlayer.player_name).filter_by(user_id='default_user').all()
        jugadores_db.extend([j[0] for j in jugadores_pizarra])
            
        return list(set(jugadores_db))
    except Exception as e:
        print(f"Error cargando jugadores_totales: {e}")
        return []
    

@app.get("/api/metricas_disponibles/{posicion}")
async def api_metricas_disponibles(posicion: str):
    """ Extrae las métricas únicas de una posición para que el UI dibuje el Radar Personalizado """
    try:
        d_pos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo': estilos_ext, 'Medio': estilos_med 
        }.get(posicion.split(' ')[0], estilos_del)
        
        metricas = set()
        for estilo, pesos in d_pos.items():
            if estilo != 'Personalizado': metricas.update(pesos.keys())
            
        return sorted(list(metricas))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preseleccion/add")
async def ps_add(payload: JugadorRequest, db: Session = Depends(get_db)):
    j = payload.nombre
    if not db.query(ShortlistPlayer).filter_by(user_id='default_user', player_name=j).first():
        equipo, edad, mins = "N/D", 0, 0
        try:
            with get_duckdb_conn() as conn:
                df_jug = conn.execute('SELECT "Team within selected timeframe", Team, Age, "Minutes played" FROM dim_jugadores_stats WHERE Player = ? LIMIT 1', [j]).df()
            if not df_jug.empty:
                f = df_jug.iloc[0]
                equipo = str(f.get('Team within selected timeframe') if pd.notna(f.get('Team within selected timeframe')) else f.get('Team', 'N/D'))
                edad = int(f.get('Age', 0)) if pd.notna(f.get('Age')) else 0
                mins = int(f.get('Minutes played', 0)) if pd.notna(f.get('Minutes played')) else 0
        except: 
            pass

        nuevo = ShortlistPlayer(user_id='default_user', player_name=j, team=equipo, age=edad, minutes=mins)
        db.add(nuevo)
        db.commit()
    return {"status": "ok"}

@app.get("/api/preseleccion/get")
async def ps_get(db: Session = Depends(get_db)):
    jugadores = db.query(ShortlistPlayer).filter_by(user_id='default_user').all()
    return [{"nombre": p.player_name, "equipo": p.team, "edad": p.age, "minutos": p.minutes} for p in jugadores]

@app.post("/api/preseleccion/remove")
async def ps_remove(payload: JugadorRequest, db: Session = Depends(get_db)):
    db.query(ShortlistPlayer).filter_by(user_id='default_user', player_name=payload.nombre).delete()
    db.commit()
    return {"status": "ok"}

@app.post("/api/squad/add")
async def sq_add(payload: JugadorRequest, db: Session = Depends(get_db)):
    nombre = payload.nombre
    jugador = db.query(SquadPlannerPlayer).filter_by(user_id='default_user', player_name=nombre).first()
    if not jugador:
        nuevo = SquadPlannerPlayer(user_id='default_user', player_name=nombre, is_fichaje=True)
        db.add(nuevo)
    elif jugador.is_deleted:
        jugador.is_deleted = False # Lo sacamos de la papelera
    db.commit()
    return {"status": "ok"}

@app.post("/api/squad/move")
async def sq_move(payload: MoverJugadorRequest, db: Session = Depends(get_db)):
    jugador = db.query(SquadPlannerPlayer).filter_by(user_id='default_user', player_name=payload.nombre).first()
    if jugador:
        jugador.x_pos = payload.x
        jugador.y_pos = payload.y
        db.commit()
    return {"status": "ok"}

@app.post("/api/squad/toggle_filial")
async def sq_toggle_filial(payload: JugadorRequest, db: Session = Depends(get_db)):
    jugador = db.query(SquadPlannerPlayer).filter_by(user_id='default_user', player_name=payload.nombre).first()
    is_filial = False
    if jugador:
        jugador.is_filial = not jugador.is_filial
        is_filial = jugador.is_filial
        db.commit()
    return {"status": "ok", "is_filial": is_filial}

@app.post("/api/squad/remove")
async def sq_remove(payload: JugadorRequest, db: Session = Depends(get_db)):
    jugador = db.query(SquadPlannerPlayer).filter_by(user_id='default_user', player_name=payload.nombre).first()
    if jugador:
        jugador.is_deleted = True
        db.commit()
    return {"status": "ok"}

@app.post("/api/squad/restore")
async def sq_restore(payload: JugadorRequest, db: Session = Depends(get_db)):
    jugador = db.query(SquadPlannerPlayer).filter_by(user_id='default_user', player_name=payload.nombre).first()
    if jugador:
        jugador.is_deleted = False
        db.commit()
    return {"status": "ok"}

@app.get("/api/squad/get")
async def sq_get(db: Session = Depends(get_db)):
    jugadores = db.query(SquadPlannerPlayer).filter_by(user_id='default_user').all()
    plantilla, fichajes, eliminados = [], [], []
    
    for j in jugadores:
        if j.is_deleted:
            eliminados.append(j.player_name)
        else:
            data = {"nombre": j.player_name, "x": j.x_pos, "y": j.y_pos, "is_filial": j.is_filial}
            if j.is_fichaje:
                fichajes.append(data)
            else:
                plantilla.append(data)
                
    return {"fichajes": fichajes, "plantilla": plantilla, "eliminados": eliminados}

@app.post("/api/procesar")
async def procesar_datos(payload: ProcesarRequest):
    try:
        # FastAPI ya ha validado que 'posicion' y 'estilo' vengan en el payload
        if not payload.posicion or not payload.estilo:
            raise HTTPException(status_code=400, detail="Falta seleccionar posición o estilo.")

        # 1. Extracción DuckDB
        with get_duckdb_conn() as conn:
            query = "SELECT * FROM dim_jugadores_stats WHERE 1=1"
            if payload.ligas:
                ligas_str = ", ".join([f"'{l.replace(chr(39), '')}'" for l in payload.ligas])
                query += f" AND Competition IN ({ligas_str})"
            if payload.temporadas:
                temps_str = ", ".join([f"'{t.replace(chr(39), '')}'" for t in payload.temporadas])
                query += f" AND Season IN ({temps_str})"
            df_crudo = conn.execute(query).df()
        if df_crudo.empty:
            raise HTTPException(status_code=404, detail="No hay datos en las ligas seleccionadas.")
                
        # Limpiamos notas antiguas para calcular las nuevas en tiempo real
        cols_to_drop = [c for c in df_crudo.columns if c.startswith('Rating_') or c == 'Rating']
        cols_to_drop += [c for c in df_crudo.columns if c.startswith('Score_') or c.endswith('Scale')]
        df_crudo.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        
        # 2. Filtro Posicional
        regex_pos = mapa_posiciones.get(payload.posicion, '')
        from backend.core.pandas import filtrar_por_posicion_real, preparar_dataframe
        
        df_filtrado = filtrar_por_posicion_real(df_crudo, regex_pos)
        df_filtrado = df_filtrado[~df_filtrado['Player'].str.contains(r'\[REF\]', na=False)].copy()
        if df_filtrado.empty: 
            return {"jugadores": [], "conteo": ""} 

        COLS_STR = {'Player', 'Team', 'Team within selected timeframe', 'Position', 'Primary position', 
                    'Secondary position', 'Third position', 'Competition', 'League', 'Birth country', 
                    'Foot', 'Contract expires', 'Season', 'Pais_Liga'}
        
        for col in df_filtrado.columns:
            if col not in COLS_STR and df_filtrado[col].dtype == 'object':
                df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)
        
        df_filtrado = preparar_dataframe(df_filtrado)
        df_base = df_filtrado[(df_filtrado['Minutes played'] >= payload.mins) & 
                              (df_filtrado['Age'] >= payload.edad_min) & 
                              (df_filtrado['Age'] <= payload.edad_max)].copy()
        
        # 🚀 FIX: AQUÍ HEMOS BORRADO EL FILTRO PREMATURO DE EQUIPOS. 
        # Ahora dejamos pasar a toda la liga a la calculadora matemática.

        if df_base.empty: return {"jugadores": [], "conteo": ""}

        # 3. Filtro de Ligas (Cohorte del usuario)
        col_comp = 'Competition' if 'Competition' in df_base.columns else 'League'
        if payload.ligas: 
            df_base = df_base[df_base[col_comp].isin(payload.ligas)].copy()
            
        if df_base.empty: return {"jugadores": [], "conteo": ""} 

        # 4. Escalado y Ratings (Contexto Global contra toda la liga)
        COLS_META = {'Age', 'Matches played', 'Minutes played', 'Height', 'Weight', 'League_Weight', 'Wyscout id'}
        col_num = [c for c in df_base.select_dtypes(include=[np.number]).columns if c not in COLS_META and not c.startswith('Rating_')]
        METRICAS_INVERSAS = ['conceded', 'against', 'losses', 'turnovers', 'fouls', 'yellow', 'red', 'pérdidas', 'faltas', 'encajados']
        
        from backend.core.pandas import motor_escalado_unico, motor_calculo_ratings
        
        df_base = motor_escalado_unico(
            df=df_base, col_num=col_num, metricas_inversas=METRICAS_INVERSAS,
            agrupar_por=None, usar_pesos_liga=True, min_minutos=payload.mins
        )

        d_pos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo': estilos_ext, 'Medio': estilos_med 
        }.get(payload.posicion.split(' ')[0], estilos_del)
        
        df_base = motor_calculo_ratings(df_base, diccionarios=d_pos, mascara_posicion=None, aplicar_peso_liga=True)

        # 5. Asignación de la Nota Visual (Rating)
        aplicar_penalizacion = len(payload.ligas) > 1 

        if payload.estilo == 'Personalizado' and payload.custom_weights:
            variables = payload.custom_weights
            suma_main = pd.Series(0.0, index=df_base.index)
            peso_aplicado = 0
            
            for var, peso in variables.items():
                clean_v = str(var).replace(' Scale', '').replace(' Master', '').strip()
                col_target = f"{clean_v} Scale"
                if col_target in df_base.columns:
                    suma_main += df_base[col_target] * peso
                    peso_aplicado += peso
                    
            if peso_aplicado > 0:
                nota_base = suma_main / peso_aplicado
                if aplicar_penalizacion and 'League_Weight' in df_base.columns:
                    league_w = df_base['League_Weight'].fillna(1.0)
                    penalizacion = (1.0 - league_w) * 30
                else:
                    penalizacion = 0.0
                    
                df_base['Rating'] = (nota_base - penalizacion).clip(1, 99).round().astype('Int64')
            else:
                df_base['Rating'] = 50
        else:
            col_estilo = f"Rating_{payload.estilo}"
            if col_estilo in df_base.columns:
                nota_base = df_base[col_estilo].fillna(50)
                if aplicar_penalizacion and 'League_Weight' in df_base.columns:
                    league_w = df_base['League_Weight'].fillna(1.0)
                    penalizacion = (1.0 - league_w) * 25 
                    df_base['Rating'] = (nota_base - penalizacion).clip(1, 99).round().astype(int)
                else:
                    df_base['Rating'] = nota_base.clip(1, 99).round().astype(int)
            else:
                df_base['Rating'] = 50

        # Tiers ajustados
        df_base['Tier'] = df_base['Rating'].apply(
            lambda r: 'S' if r >= 85 else ('A' if r >= 75 else ('B' if r >= 65 else ('C' if r >= 50 else 'D')))
        )

        # 6. Etiquetado Scouting Pro
        try:
            from backend.core.pandas import generar_matriz_ortogonalidad
            matriz_ort = generar_matriz_ortogonalidad(d_pos)
        except Exception:
            matriz_ort = None

        if not df_base.empty and len(df_base) > 10:
            cohort_stats = {'valido': True, 'p95': df_base['Rating'].quantile(0.95), 'p85': df_base['Rating'].quantile(0.85)}
        else:
            cohort_stats = {'valido': False}

        from backend.core.pandas import calcular_etiqueta_pro

        def aplicar_etiqueta_real(row):
            rat_est = {est: int(row.get(f'Rating_{est}', 50)) for est in d_pos.keys() if est != 'Personalizado'}
            rat_est['Rating'] = int(row.get('Rating', 50)) 
            edad = int(row.get('Age', 25)) if pd.notna(row.get('Age')) else 25
            liga = str(row.get(col_comp, 'N/D'))
            try: return calcular_etiqueta_pro(rat_est, arg2=edad, arg3=liga, matriz_ort=matriz_ort, cohort_stats=cohort_stats)
            except Exception: return calcular_etiqueta_pro(rat_est, arg2=edad, arg3=liga, cohort_stats=cohort_stats)

        def obtener_mejor_estilo_exacto(row):
            estilos = [e for e in d_pos.keys() if e != 'Personalizado']
            return max(estilos, key=lambda e: row.get(f'ScoreFloat_{e}', 0)) if estilos else "N/D"

        df_base['Mejor Estilo'] = df_base.apply(obtener_mejor_estilo_exacto, axis=1)
        df_base['Perfil_Scouting'] = df_base.apply(aplicar_etiqueta_real, axis=1)

        # 🚀 FIX: APLICAMOS EL FILTRO DE EQUIPO AQUÍ AL FINAL (Filtro Puramente Visual)
        if payload.perfiles: 
            df_base = df_base[df_base['Perfil_Scouting'].isin(payload.perfiles)]
            
        if payload.equipos_filtro and len(payload.equipos_filtro) > 0:
            equipos_limpios = [eq.strip() for eq in payload.equipos_filtro if eq.strip()]
            if equipos_limpios:
                patron_equipos = '|'.join(equipos_limpios)
                col_t = 'Team within selected timeframe' if 'Team within selected timeframe' in df_base.columns else 'Team'
                df_base = df_base[df_base[col_t].str.contains(patron_equipos, case=False, na=False)]

        df_final = df_base.sort_values(by='Rating', ascending=False)
        conteo_dict = df_final['Perfil_Scouting'].value_counts().to_dict()
        conteo_str = " | ".join([f"{v} {k}" for k, v in conteo_dict.items()])

        return {
            "jugadores": df_final[['Wyscout id', 'Player', 'Team', 'Age', 'Minutes played', 'Mejor Estilo', 'Rating', 'Tier', 'Perfil_Scouting']].to_dict('records'),
            "conteo": conteo_str
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error interno al procesar la búsqueda.")

@app.get("/api/ficha/{nombre_jugador:path}")
async def obtener_ficha(nombre_jugador: str, id: Optional[str] = None, posicion: Optional[str] = None, ligas_mercado: Optional[str] = None):
    global _CACHE_RADAR_ACTUAL
    req_pos = posicion
    try:
        with get_duckdb_conn() as conn:
            if id and id != "undefined" and id != "null" and id != "":
                df_jugador = conn.execute(
                    """SELECT * FROM dim_jugadores_stats 
                       WHERE CAST("Wyscout id" AS VARCHAR) = ? 
                          OR CAST("Wyscout id" AS VARCHAR) = ?
                       ORDER BY Season DESC, "Minutes played" DESC LIMIT 1""", 
                    [str(id), f"{id}.0"]
                ).df()                
                if df_jugador.empty:
                    df_jugador = conn.execute(
                        """SELECT * FROM dim_jugadores_stats 
                           WHERE Player = ? 
                           ORDER BY Season DESC, "Minutes played" DESC LIMIT 1""", 
                        [nombre_jugador]
                    ).df()
            else:
                df_jugador = conn.execute(
                    """SELECT * FROM dim_jugadores_stats 
                       WHERE Player = ? 
                       ORDER BY Season DESC, "Minutes played" DESC LIMIT 1""", 
                    [nombre_jugador]
                ).df()
            
            if df_jugador.empty:
                raise HTTPException(status_code=404, detail="Jugador no encontrado en la BD analítica.")
                
            fila_raw = df_jugador.iloc[0]
            
            t_jug = str(fila_raw.get('Season', ''))
            c_jug = str(fila_raw.get('Competition', fila_raw.get('League', '')))
            nombre_real_jugador = str(fila_raw.get('Player'))
            
            # 🚀 NUEVO: Cargamos a sus rivales dependiendo de las ligas elegidas en el Buscador PRO
            if ligas_mercado:
                lista_ligas = [l.strip() for l in ligas_mercado.split(',')]
                ligas_str = ", ".join([f"'{l.replace(chr(39), '')}'" for l in lista_ligas])
                df_peers = conn.execute(
                    f"SELECT * FROM dim_jugadores_stats WHERE Season = ? AND Competition IN ({ligas_str})",
                    [t_jug]
                ).df()
                # Blindaje: asegurar que él mismo esté en la cohorte para poder compararlo
                if nombre_real_jugador not in df_peers['Player'].values:
                    df_peers = pd.concat([df_peers, df_jugador]).drop_duplicates(subset=['Player'])
            else:
                df_peers = conn.execute(
                    """SELECT * FROM dim_jugadores_stats 
                       WHERE Season = ? AND Competition = ?""",
                    [t_jug, c_jug]
                ).df()
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    df_peers = df_peers[~df_peers['Player'].str.contains(r'\[REF\]', na=False)].copy()
    
    posiciones_validas = []
    for pos_name, regex in mapa_posiciones.items():
        total_pct = 0.0
        m_prim = pd.notna(fila_raw.get('Primary position')) and bool(re.search(regex, str(fila_raw.get('Primary position'))))
        
        for k in ['Primary position, %', 'Secondary position, %', 'Third position, %']:
            pct = fila_raw.get(k, 0)
            total_pct += float(pct) if pd.notna(pct) and str(pct).strip() != '' else 0.0
            
        m_fall = pd.isna(fila_raw.get('Primary position')) and pd.notna(fila_raw.get('Position')) and bool(re.search(regex, str(fila_raw.get('Position'))))
        
        if m_prim or total_pct >= 25.0 or m_fall:
            posiciones_validas.append(pos_name)
            
    if not req_pos:
        req_pos = posiciones_validas[0] if posiciones_validas else 'Delantero'
            
    if req_pos not in posiciones_validas: posiciones_validas.append(req_pos)
    
    from backend.core.pandas import filtrar_por_posicion_real, preparar_dataframe
    regex_pos = mapa_posiciones.get(req_pos, '')
    df_peers = preparar_dataframe(filtrar_por_posicion_real(df_peers, regex_pos))

    posiciones_dict = {}
    for col_nombre, col_pct in [("Primary position", "Primary position, %"), ("Secondary position", "Secondary position, %"), ("Third position", "Third position, %")]:
        if col_nombre in fila_raw.index and col_pct in fila_raw.index:
            p = str(fila_raw[col_nombre]).strip()
            v = fila_raw[col_pct]
            if p.lower() not in ["", "nan", "none", "n/d"]:
                try:
                    posiciones_dict[p] = float(str(v).replace('%', '').replace(',', '.').strip())
                except:
                    posiciones_dict[p] = 0.0
    if not posiciones_dict or sum(posiciones_dict.values()) == 0:
        posiciones_dict[req_pos] = 100.0

    info = {
        "wyscout_id": str(fila_raw.get('Wyscout id', '')).replace('.0', ''),
        "nombre": fila_raw.get('Player'), 
        "edad": int(fila_raw.get('Age', 0)) if pd.notna(fila_raw.get('Age')) else 0,
        "equipo": str(fila_raw.get('Team within selected timeframe' if 'Team within selected timeframe' in fila_raw else 'Team', '')), 
        "pais": str(fila_raw.get('Birth country', '')),
        "pie": str(fila_raw.get('Foot', '')), 
        "contrato": str(fila_raw.get('Contract expires', '')), 
        "partidos": int(fila_raw.get('Matches played', 0)) if pd.notna(fila_raw.get('Matches played')) else 0,
        "minutos": int(fila_raw.get('Minutes played', 0)) if pd.notna(fila_raw.get('Minutes played')) else 0, 
        "goles": int(fila_raw.get('Goals', 0)) if pd.notna(fila_raw.get('Goals')) else 0,
        "asistencias": int(fila_raw.get('Assists', 0)) if pd.notna(fila_raw.get('Assists')) else 0, 
        "amarillas": int(fila_raw.get('Yellow cards', 0)) if pd.notna(fila_raw.get('Yellow cards')) else 0, 
        "rojas": int(fila_raw.get('Red cards', 0)) if pd.notna(fila_raw.get('Red cards')) else 0,            
        "posiciones_validas": list(set(posiciones_validas)),
        "posicion_evaluada": req_pos,
        "posiciones": posiciones_dict  
    }

    d_estilos = {
        'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
        'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
        'Extremo': estilos_ext, 'Medio': estilos_med
    }.get(req_pos.split(' ')[0], estilos_del)
    
    d_radar = {
        'Portero': radar_gk, 'Central': radar_cb, 'Lateral': radar_lt, 
        'Pivote': radar_mcd, 'Interior': radar_int, 'Mediapunta': radar_mp, 
        'Extremo': radar_ext, 'Medio': radar_int
    }.get(req_pos.split(' ')[0], radar_del)

    _CACHE_RADAR_ACTUAL = d_radar

    ratings_dict = {est: int(float(val)) if pd.notna(val) and val != '' else 50 for est in d_estilos.keys() if est != 'Personalizado' and (val := fila_raw.get(f'Rating_{est}')) is not None}
    
    ratings_dict['Rating'] = max(ratings_dict.values()) if ratings_dict else 50
    best_style = max({k:v for k,v in ratings_dict.items() if k != 'Rating'}, key={k:v for k,v in ratings_dict.items() if k != 'Rating'}.get) if ratings_dict else None

    rating_cols = [f"Rating_{e}" for e in d_estilos if e != 'Personalizado' and f"Rating_{e}" in df_peers.columns]
    if rating_cols and not df_peers.empty and len(df_peers) > 10:
        best_ratings = df_peers[rating_cols].max(axis=1)
        cohort_stats = {'valido': True, 'p95': best_ratings.quantile(0.95), 'p85': best_ratings.quantile(0.85)}
    else:
        cohort_stats = {'valido': False}

    try:
        from backend.core.pandas import calcular_etiqueta_pro, generar_matriz_ortogonalidad
        matriz_ort = generar_matriz_ortogonalidad(d_estilos)
        perfil_scouting = calcular_etiqueta_pro(ratings_dict, arg2=info['edad'], arg3=c_jug, matriz_ort=matriz_ort, cohort_stats=cohort_stats)
    except Exception:
        from backend.core.pandas import calcular_etiqueta_pro
        perfil_scouting = calcular_etiqueta_pro(ratings_dict, arg2=info['edad'], arg3=c_jug, cohort_stats=cohort_stats)
        
    info['perfil_scouting'] = f"{perfil_scouting} (en {c_jug})"
    info['ratings_roles'] = ratings_dict

    pos_fig = dibujar_posiciones(fila_raw)
    radar_fig = dibujar_radares(df_peers, [nombre_real_jugador], d_radar) 
    scatters_figs = dibujar_scatter_multi(df_peers, nombre_real_jugador, req_pos)
    
    # =========================================================
    # 🚀 NUEVO MOTOR DE CLONACIÓN PCA PARA LA FICHA DEL JUGADOR
    # =========================================================
    clones = []
    try:
        from backend.core.ml import generar_modelo_similitud
        
        # Invocamos al motor PCA de manera "invisible"
        fig_json, pca_clones = generar_modelo_similitud(df_peers, nombre_real_jugador, d_estilos)
        
        if pca_clones:
            for c in pca_clones:
                c['Tipo'] = 'Liga' # Compatibilidad con el frontend antiguo
            clones = pca_clones[:10] # Top 10 clones para la ficha
            
    except Exception as e:
        print(f"Error generando clones PCA en ficha: {e}")

    # No mandamos 'grafico_pca' para mantener la interfaz limpia
    return {
        "info": info, 
        "pos_fig": pos_fig, 
        "radar": radar_fig, 
        "scatters": scatters_figs, 
        "clones": clones
    }

@app.post("/api/buscar_similares")
async def buscar_similares(payload: ClonadorRequest):
    try:
        nombre_jugador = payload.nombre.strip()
        if not nombre_jugador: 
            raise HTTPException(status_code=400, detail="Selecciona un jugador.")
            
        # Recibimos las 3 variables
        df_filtrado, gen_pos, nombre_real = _obtener_cohorte_jugador_duckdb(
            nombre_jugador, payload.posicion, payload.ligas, payload.edad_min, payload.edad_max
        )
        
        # 🚀 ESCUDO FINAL: Si ahogas al mercado y hay menos de 5, avisa en lugar de romper
        if len(df_filtrado) < 5:
            raise HTTPException(status_code=400, detail=f"Filtros muy estrictos. Solo hay {len(df_filtrado)} jugador(es) disponibles. La IA necesita al menos 5 para comparar. ¡Amplía la edad o añade más ligas!")
            
        d_estilos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo': estilos_ext, 'Medio': estilos_med
        }.get(gen_pos.split(' ')[0], estilos_del)
        
        from backend.core.ml import generar_modelo_similitud
        # Usamos nombre_real aquí
        fig_json, clones_dict = generar_modelo_similitud(df_filtrado, nombre_real, d_estilos)
        
        if not fig_json: 
            raise HTTPException(status_code=400, detail="No hay datos suficientes para clonar.")

        return {
            "objetivo": nombre_real, # Así el Frontend solo lee "A. Gordon"
            "mejor_rol": gen_pos, 
            "grafico_pca": fig_json,
            "similares": clones_dict
        }
    except HTTPException: raise
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
@app.post("/api/comparar_radares")
async def comp_rad(payload: CompararRadaresRequest):
    global _CACHE_RADAR_ACTUAL
    try:
        if not payload.jugadores:
            raise HTTPException(status_code=400, detail="No se han enviado jugadores.")
            
        jugs_str = ", ".join([f"'{j.replace(chr(39), '')}'" for j in payload.jugadores])
        with get_duckdb_conn() as conn:
            df_u = conn.execute(f"SELECT * FROM dim_jugadores_stats WHERE Player IN ({jugs_str})").df()
            
        radar_activo = _CACHE_RADAR_ACTUAL if _CACHE_RADAR_ACTUAL else radar_del
        h2h_data = []
        
        for cat, vars_ in radar_activo.items():
            for var in vars_:
                row = {"metrica": var, "categoria": cat}
                v_puros = [round(float(df_u[df_u['Player'] == jug][var].values[0]), 2) if jug in df_u['Player'].values and var in df_u.columns and pd.notna(df_u[df_u['Player'] == jug][var].values[0]) else 0 for jug in payload.jugadores]
                for i, jug in enumerate(payload.jugadores): row[jug] = v_puros[i]
                row.update({'max': max(v_puros) if v_puros else 0, 'min': min(v_puros) if v_puros else 0})
                h2h_data.append(row)
                
        return {"radar": dibujar_radares(df_u, payload.jugadores, radar_activo), "h2h": h2h_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gangas")
async def buscar_gangas(payload: CompararTemporadasRequest):
    try:
        resultado, error = _comparar_temporadas_ia(payload, 'Caida', umbral=10, ascending=False)
        if error: raise HTTPException(status_code=400, detail=error)
        return resultado.fillna('N/D').to_dict('records')
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error calculando gangas: {e}")


@app.post("/api/explosiones")
async def buscar_explosiones(payload: CompararTemporadasRequest):
    try:
        resultado, error = _comparar_temporadas_ia(payload, 'Mejora', umbral=10, ascending=True)
        if error: raise HTTPException(status_code=400, detail=error)
        return resultado.fillna('N/D').to_dict('records')
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error calculando explosiones: {e}")


@app.get("/api/evolucion/{wyscout_id}")
async def obtener_evolucion(wyscout_id: str, posicion: str = 'Delantero'):
    try:
        with get_duckdb_conn() as conn:
            df_hist = conn.execute('''
                SELECT * FROM dim_jugadores_stats 
                WHERE CAST("Wyscout id" AS VARCHAR) = ? 
                   OR CAST("Wyscout id" AS VARCHAR) = ?
                ORDER BY Season DESC, "Minutes played" DESC
            ''', [str(wyscout_id), f"{wyscout_id}.0"]).df()
            
        if df_hist.empty: raise HTTPException(status_code=404, detail="No se encontraron datos históricos en DuckDB.")

        # Eliminamos duplicados por si jugó en 2 equipos el mismo año
        df_hist = df_hist.drop_duplicates(subset=['Season'])

        res = []
        d_estilos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo': estilos_ext, 'Medio': estilos_med
        }.get(posicion.split(' ')[0], estilos_del)

        # 🚀 AÑADIDO: Mapeo de Radares Tácticos para las fases
        d_radar = {
            'Portero': radar_gk, 'Central': radar_cb, 'Lateral': radar_lt, 
            'Pivote': radar_mcd, 'Interior': radar_int, 'Mediapunta': radar_mp, 
            'Extremo': radar_ext, 'Medio': radar_int
        }.get(posicion.split(' ')[0], radar_del)

        try:
            from backend.core.pandas import generar_matriz_ortogonalidad
            matriz_ort = generar_matriz_ortogonalidad(d_estilos)
        except Exception: matriz_ort = None
        from backend.core.pandas import calcular_etiqueta_pro

        for _, row in df_hist.iterrows():
            minutos_jugados = int(row.get('Minutes played', 0)) if pd.notna(row.get('Minutes played')) else 0
            if minutos_jugados < 300: continue
                
            rat_est = {}
            for col in df_hist.columns:
                if col.startswith('Rating_') and col not in ['Rating_Personalizado', 'Rating']:
                    valor = row.get(col)
                    if pd.notna(valor) and valor != '':
                        try:
                            v_int = int(float(valor))
                            if v_int > 0: rat_est[col.replace('Rating_', '')] = v_int
                        except: pass
                        
            if not rat_est: rat_est = {"Base": 50}
            rat_est['Rating'] = max(rat_est.values())
            
            # 🚀 AÑADIDO: Extracción de métricas para los 3 radares de fases
            fases_radar = {}
            for fase, metricas in d_radar.items():
                fases_radar[fase] = {}
                for m in metricas:
                    # Buscamos la métrica escalada (Scale) y si no, cogemos la cruda
                    val = row.get(f"{m} Scale")
                    if pd.isna(val): val = row.get(m, 50)
                    
                    try:
                        # Aseguramos que encaje en el radar de 0 a 100
                        fases_radar[fase][m] = min(max(int(float(val)), 0), 100)
                    except:
                        fases_radar[fase][m] = 50

            edad_hist = int(row.get('Age', 25)) if pd.notna(row.get('Age')) else 25
            liga_hist = str(row.get('Competition', 'N/D'))
            col_equipo = 'Team within selected timeframe' if 'Team within selected timeframe' in row and pd.notna(row['Team within selected timeframe']) else 'Team'
            equipo_hist = str(row.get(col_equipo, 'N/D'))
            temp = str(row.get('Season', 'N/D'))
            
            perfil_yoy = calcular_etiqueta_pro(rat_est, arg2=edad_hist, arg3=liga_hist, matriz_ort=matriz_ort, cohort_stats={'valido': False})
            detalle = "Filial" if any(x in equipo_hist.upper() for x in [" B", "U21", "U19", "RESERVE", "FILIAL", " II", "U23", " C"]) else "Primer Equipo"

            res.append({
                "Temporada": temp, "Equipo": equipo_hist, "Competicion": liga_hist, "Caracteristica": detalle,
                "Minutos": minutos_jugados, "Goles": int(row.get('Goals', 0)) if pd.notna(row.get('Goals')) else 0,
                "Asistencias": int(row.get('Assists', 0)) if pd.notna(row.get('Assists')) else 0,
                "Ratings": rat_est, 
                "Fases": fases_radar, # 🚀 LO MANDAMOS AL FRONTEND
                "Perfil": perfil_yoy
            })
            
        return sorted(res, key=lambda x: (x['Temporada'], x['Minutos']))
    except HTTPException: raise
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Error calculando evolución: {str(e)}")
    
@app.get("/api/predecir_potencial/{nombre_jugador:path}")
async def predecir_potencial(nombre_jugador: str, posicion: str = 'Delantero'):
    try:
        df_filtrado, gen_pos, nombre_real = _obtener_cohorte_jugador_duckdb(nombre_jugador, posicion)
        
        if df_filtrado.empty or nombre_real not in df_filtrado['Player'].values:
            raise HTTPException(status_code=404, detail="Jugador no encontrado para predicción en BD.")
            
        d_estilos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo': estilos_ext, 'Medio': estilos_med
        }.get(posicion.split(' ')[0], estilos_del)
        
        from backend.core.ml import predecir_potencial_jugador
        resultado = predecir_potencial_jugador(df_filtrado, nombre_real, d_estilos)
        if not resultado: raise HTTPException(status_code=400, detail="No se pudo generar el modelo.")
        return resultado
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del motor XGBoost: {str(e)}")

@app.post("/api/simular_traspaso")
async def api_simular_traspaso(payload: SimularTraspasoRequest):
    try:
        nombre_jugador, liga_destino, posicion = payload.jugador, payload.liga_destino, payload.posicion
        
        # Parseamos el equipo
        nombre_real = nombre_jugador.split(" | ")[0].strip()
        equipo_real = nombre_jugador.split(" | ")[1].strip() if " | " in nombre_jugador else None
        
        with get_duckdb_conn() as conn:
            if equipo_real:
                df_jug = conn.execute('SELECT * FROM dim_jugadores_stats WHERE Player = ? AND Team = ? ORDER BY Season DESC, "Minutes played" DESC LIMIT 1', [nombre_real, equipo_real]).df()
            else:
                df_jug = conn.execute('SELECT * FROM dim_jugadores_stats WHERE Player = ? ORDER BY Season DESC, "Minutes played" DESC LIMIT 1', [nombre_real]).df()
                
            if df_jug.empty: raise HTTPException(status_code=404, detail="Jugador no encontrado en BD.")
            
            jugador_row = df_jug.iloc[0]
            temp = jugador_row['Season']
            df_liga_destino = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Season = ? AND Competition = ?", [temp, liga_destino]).df()
            
        df_base = pd.concat([df_jug, df_liga_destino]).drop_duplicates(subset=['Player'])
        d_estilos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt, 
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo': estilos_ext, 'Medio': estilos_med
        }.get(posicion.split(' ')[0], estilos_del)
        
        from backend.core.ml import simular_traspaso
        resultado = simular_traspaso(jugador_row, df_base, d_estilos, liga_destino)
        return resultado
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del simulador: {str(e)}")
    
# ==========================================
# RUTAS DE ANÁLISIS DE EQUIPOS Y TÁCTICA
# ==========================================

def obtener_datos_equipos_tacticos_duckdb():
    try:
        with get_duckdb_conn() as conn:
            return conn.execute("SELECT * FROM dim_equipos_stats").df()
    except Exception:
        return pd.DataFrame()

@app.get("/api/equipos_tacticos")
async def api_equipos_tacticos():
    try:
        with get_duckdb_conn() as conn:
            # 🚀 IA: Leemos la liga y país nativos de la tabla de equipos. Cero contaminación.
            query = """
                SELECT 
                    Team,
                    Pais_Eq as Pais,
                    Competition_Eq as Liga
                FROM dim_equipos_stats
                ORDER BY Pais, Liga, Team
            """
            df = conn.execute(query).df()
            
            if df.empty:
                return {"equipos_detallados": [], "equipos": []}

            return {
                "equipos_detallados": df.to_dict(orient="records"),
                "equipos": sorted(df['Team'].tolist())
            }
    except Exception as e:
        print(f"Error en api_equipos_tacticos: {e}")
        return {"equipos_detallados": [], "equipos": []}

@app.post("/api/equipos")
async def api_equipos(payload: EquipoParamRequest):
    df = obtener_datos_sql([payload.liga], [payload.temporada])
    if not df.empty:
        col_t = 'Team within selected timeframe' if 'Team within selected timeframe' in df.columns else 'Team'
        return {"equipos": sorted(df[col_t].dropna().unique().tolist()), "ruta": ""}
    return {"equipos": []}

@app.post("/api/set_equipo")
async def set_equipo(payload: SetEquipoRequest, db: Session = Depends(get_db)):
    global _CACHE_PLANTILLA
    equipo = payload.equipo
    
    user = db.query(UserSettings).filter_by(user_id='default_user').first()
    if user: user.equipo_actual = equipo    
    db.query(SquadPlannerPlayer).filter_by(user_id='default_user').delete()
    db.commit()

    if equipo != "Freelance" and payload.liga and payload.temporada:
        from backend.core.pandas import preparar_dataframe
        try:
            with get_duckdb_conn() as conn:
                df = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Competition = ? AND Season = ?", [payload.liga, payload.temporada]).df()
                
            if df.empty: raise HTTPException(status_code=400, detail="No se encontraron datos para ese equipo y temporada.")
            col_t = 'Team within selected timeframe' if 'Team within selected timeframe' in df.columns else 'Team'
            _CACHE_PLANTILLA = preparar_dataframe(df[df[col_t] == equipo].copy()).copy()            
            for _, row in _CACHE_PLANTILLA.iterrows():
                jugador_db = SquadPlannerPlayer(user_id='default_user', player_name=row['Player'], is_fichaje=False)
                db.add(jugador_db)
            db.commit()
        except Exception: raise HTTPException(status_code=500, detail="No se pudo leer el fichero de datos.")
    else: 
        _CACHE_PLANTILLA = pd.DataFrame()

    return {"status": "ok", "equipo": equipo}

@app.post("/api/similar_teams")
async def similar_teams(payload: SimilarTeamsRequest):
    try:
        target_team = payload.equipo
        sort_by = payload.sort_by 
        
        df_tactico = obtener_datos_equipos_tacticos_duckdb()
        if df_tactico.empty or target_team not in df_tactico['Team'].values:
            raise HTTPException(status_code=404, detail="No hay datos tácticos para este equipo.")
        
        todas_las_cols = list(set([col for lista in fases_juego.values() for col in lista]))
        cols_ok = [c for c in todas_las_cols if c in df_tactico.columns]
        if not cols_ok: raise HTTPException(status_code=400, detail="Faltan columnas tácticas en el CSV.")
        
        df_calc = df_tactico.copy()
        df_calc[cols_ok] = df_calc[cols_ok].apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan).fillna(0)
        target_idx = df_calc.index[df_calc['Team'] == target_team][0]
        df_res = df_calc[['Team']].copy()
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        
        fases_calculadas = []
        for nombre_fase, columnas in fases_juego.items():
            cols_fase = [c for c in columnas if c in df_calc.columns]
            if not cols_fase:
                df_res[f'Sim_{nombre_fase}'] = 0.0
                continue
            matriz = scaler.fit_transform(df_calc[cols_fase])
            dist = euclidean_distances(matriz)
            max_dist = dist[target_idx].max() or 1
            df_res[f'Sim_{nombre_fase}'] = (100 - (dist[target_idx] / max_dist) * 60).round(2)
            fases_calculadas.append(f'Sim_{nombre_fase}')
        
        df_res['Sim_General'] = df_res[fases_calculadas].mean(axis=1).round(2) if fases_calculadas else 0.0
        sort_by = sort_by if sort_by in df_res.columns else 'Sim_General'
        
        similares = df_res[df_res['Team'] != target_team].sort_values(by=sort_by, ascending=False).head(15)
        target_row = df_res[df_res['Team'] == target_team].copy()
        for f in list(fases_juego.keys()) + ['General']: target_row[f'Sim_{f}'] = 100.0
            
        final_df = pd.concat([target_row, similares])
        for c in [c for c in ['Possession', 'PPDA', 'Avg Pass Height'] if c in df_calc.columns]:
            final_df[c] = df_calc.loc[final_df.index, c].round(2).values
            
        return {"similares": final_df.to_dict('records')}
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail="Error interno al buscar clubes similares.")

@app.post("/api/radar_equipos")
async def radar_equipos(payload: RadarEquiposRequest):
    equipos = payload.equipos
    df = obtener_datos_equipos_tacticos_duckdb()
    if df.empty or not equipos: raise HTTPException(status_code=400, detail="No hay datos para comparar.")
    
    cols_ok = [c for c in list(set([c for lista in fases_juego.values() for c in lista])) if c in df.columns]
    df_pct = df[['Team']].copy()
    
    for c in cols_ok:
        df[c] = pd.to_numeric(df[c], errors='coerce').replace([np.inf, -np.inf], np.nan).fillna(0)
        if c in ['Open Play xGA', 'Shots Faced', 'xT Against', 'Shots Faced per 1.0 xT Against', 'PPDA', 'High Recoveries Against', 'Set Piece xGA']:
            df_pct[c] = df[c].rank(pct=True, ascending=False) * 100
        else:
            df_pct[c] = df[c].rank(pct=True) * 100
            
    colores_linea = ['rgba(14, 165, 233, 1)', 'rgba(244, 63, 94, 1)', 'rgba(16, 185, 129, 1)']
    colores_relleno = ['rgba(14, 165, 233, 0.2)', 'rgba(244, 63, 94, 0.2)', 'rgba(16, 185, 129, 0.2)']
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    fig = make_subplots(rows=2, cols=3, specs=[[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}], [{'type': 'polar'}, {'type': 'polar'}, None]], subplot_titles=list(fases_juego.keys()), horizontal_spacing=0.15, vertical_spacing=0.15)
    
    for p_idx, eq in enumerate(equipos[:3]):
        if eq not in df_pct['Team'].values: continue
        for i, (fase, variables) in enumerate(fases_juego.items()):
            vars_ok = [v for v in variables if v in cols_ok]
            if not vars_ok: continue
            valores, etiquetas, textos = [], [], []
            for v in vars_ok:
                pct = df_pct[df_pct['Team'] == eq][v].values[0]
                valores.append(pct)
                etiquetas.append(v.replace(' per 1.0', '').replace(' into the Box', '').replace('Pressure', 'Press'))
                textos.append(f"{eq}<br>{v}: {df[df['Team'] == eq][v].values[0]:.2f}<br>Pcl: {int(pct)}")
            valores.append(valores[0]); etiquetas.append(etiquetas[0]); textos.append(textos[0])
            r, c = (1, i+1) if i < 3 else (2, i-2)
            fig.add_trace(go.Scatterpolar(r=valores, theta=etiquetas, mode='lines+markers', marker=dict(size=6, color=colores_linea[p_idx]), fill='toself', fillcolor=colores_relleno[p_idx], name=eq, legendgroup=eq, showlegend=(i == 0), line=dict(color=colores_linea[p_idx], width=2.5), hoverinfo="text", text=textos), row=r, col=c)
            
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=650, margin=dict(l=50, r=50, t=80, b=30), font=dict(color='white', size=10), legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5))    
    for annotation in fig['layout']['annotations']: annotation['yshift'] = 20; annotation['font'] = dict(size=14, weight='bold')
    for i in range(1, 6):
        fig['layout'][f'polar{i if i > 1 else ""}'].update(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(150,150,150,0.3)'), angularaxis=dict(gridcolor='rgba(150,150,150,0.3)'))
    return {"radar": pio.to_json(fig)}

@app.post("/api/team_fit")
async def calcular_team_fit(payload: TeamFitRequest):
    global _CACHE_TEAM_FIT_PESOS
    try:
        df_tactico = obtener_datos_equipos_tacticos_duckdb()
        if df_tactico.empty or payload.equipo_tactico not in df_tactico['Team'].values: 
            raise HTTPException(status_code=404, detail="No hay datos tácticos para este equipo.")
            
        # =========================================================
        # 🚀 FIX SUPREMO: EL CERROJO SQL DE DUCKDB
        # =========================================================
        with get_duckdb_conn() as conn:
            query = "SELECT * FROM dim_jugadores_stats WHERE 1=1"
            
            # 🚀 ALERTA DE SEGURIDAD: Si no hay ligas, bloqueamos la búsqueda
            if not payload.ligas or len(payload.ligas) == 0:
                raise HTTPException(status_code=400, detail="Debes seleccionar al menos una Liga de Mercado válida.")
            
            # Cerrojo 1: Ligas
            if payload.ligas and len(payload.ligas) > 0:
                ligas_str = ", ".join([f"'{str(l).replace(chr(39), '')}'" for l in payload.ligas])
                query += f" AND Competition IN ({ligas_str})"
                
            # Cerrojo 2: Temporada
            if payload.temporadas and len(payload.temporadas) > 0:
                temps_str = ", ".join([f"'{str(t).replace(chr(39), '')}'" for t in payload.temporadas])
                query += f" AND Season IN ({temps_str})"
                
            # Cerrojo 3: Anti-Femeninas y Anti-Juveniles directos en BBDD
            query += """
                AND UPPER(Team) NOT LIKE '% WOMEN%'
                AND UPPER(Team) NOT LIKE '% FEMENINO%'
                AND Team NOT LIKE '% U17%'
                AND Team NOT LIKE '% U18%'
                AND Team NOT LIKE '% U19%'
                AND Team NOT LIKE '% U20%'
                AND Team NOT LIKE '% U21%'
                AND Team NOT LIKE '% U23%'
                AND Team NOT LIKE '% B'
                AND Team NOT LIKE '% II'
            """
                
            df_crudo = conn.execute(query).df()

        if df_crudo.empty: 
            raise HTTPException(status_code=404, detail="No hay jugadores en las ligas seleccionadas.")
        # =========================================================
        
        from backend.core.pandas import filtrar_por_posicion_real, preparar_dataframe
        df_filtrado = filtrar_por_posicion_real(df_crudo, mapa_posiciones.get(payload.posicion))
        df_filtrado = df_filtrado[~df_filtrado['Player'].str.contains(r'\[REF\]', na=False)].copy()
        
        if df_filtrado.empty: raise HTTPException(status_code=404, detail="No hay jugadores válidos en esa posición.")
        
        df_filtrado = preparar_dataframe(df_filtrado)

        from backend.core.ml import generar_target_estilo_equipo, calcular_style_fit, calcular_quality_score
        
        # 2. GENERAMOS EL TARGET HÍBRIDO TÁCTICO
        target_z, saliencia, perfil_texto = generar_target_estilo_equipo(
            team_row=df_tactico[df_tactico['Team'] == payload.equipo_tactico].iloc[0],
            pos=payload.posicion,
            df_tactico_completo=df_tactico,
            df_jugadores_posicion=df_filtrado,  
            team_name=payload.equipo_tactico    
        )

        # 3. Calculamos la Distancia Matemática de Encaje
        df_filtrado = calcular_style_fit(df_filtrado, target_z, saliencia, usar_mahalanobis=True)

        # 4. Calculamos la Calidad Absoluta
        d_pos = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral Izquierdo': estilos_lt, 'Lateral Derecho': estilos_lt,
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp, 
            'Extremo Izquierdo': estilos_ext, 'Extremo Derecho': estilos_ext, 'Medio': estilos_med 
        }.get(payload.posicion, estilos_del)
        
        rating_cols_pos = [f"Rating_{e}" for e in d_pos.keys() if e != 'Personalizado' and f"Rating_{e}" in df_filtrado.columns]
        df_filtrado = calcular_quality_score(df_filtrado, columnas_rating=rating_cols_pos)

        if rating_cols_pos:
            df_filtrado['Perfil_Scouting'] = df_filtrado[rating_cols_pos].fillna(0).idxmax(axis=1).astype(str).str.replace('Rating_', '')
        else:
            df_filtrado['Perfil_Scouting'] = "Analizado"

        df_filtrado['Rating_Fit'] = df_filtrado['Style_Fit_Score'].fillna(50).round().astype(int)
        
        # 5. FILTROS FINALES DE LA INTERFAZ
        df_final = df_filtrado[(df_filtrado['Minutes played'] >= payload.mins) & 
                               (df_filtrado['Age'] >= payload.edad_min) & 
                               (df_filtrado['Age'] <= payload.edad_max) &
                               (df_filtrado['Quality_Score'] >= payload.calidad_min)]
        
        from scipy.stats import norm
        _CACHE_TEAM_FIT_PESOS = {k: float(norm.cdf(v) * 100) for k, v in target_z.items()}
        
        columnas_salida = ['Wyscout id', 'Player', 'Team', 'Age', 'Minutes played', 'Rating_Fit', 'Quality_Score', 'Perfil_Scouting', 'Breakdown']
        columnas_seguras = [c for c in columnas_salida if c in df_final.columns]
        
        jugadores_raw = df_final.sort_values(by='Rating_Fit', ascending=False).head(50)[columnas_seguras].fillna('N/D').to_dict('records')
        
        import json
        for jug in jugadores_raw:
            if 'Breakdown' in jug and isinstance(jug['Breakdown'], str):
                try:
                    jug['Breakdown'] = json.loads(jug['Breakdown'])
                except:
                    jug['Breakdown'] = {}
        
        return {
            "perfil_tactico": perfil_texto, 
            "pesos_usados": _CACHE_TEAM_FIT_PESOS, 
            "jugadores": jugadores_raw
        }
    except HTTPException: raise
    except Exception as e: 
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
         
@app.post("/api/team_fit_radar")
async def team_fit_radar(payload: TeamFitRadarRequest):
    pesos = payload.pesos # 🚀 AHORA ESTOS SON LOS TARGET PERCENTILES (0-100)
    if not pesos: raise HTTPException(status_code=400, detail="Sin pesos tácticos configurados.")
    try:
        with get_duckdb_conn() as conn:
            if payload.wyscout_id and payload.wyscout_id not in ["undefined", "", "null"]:
                df = conn.execute(
                    """SELECT * FROM dim_jugadores_stats 
                       WHERE CAST("Wyscout id" AS VARCHAR) = ? 
                          OR CAST("Wyscout id" AS VARCHAR) = ?
                       ORDER BY Season DESC, "Minutes played" DESC LIMIT 1""",
                    [str(payload.wyscout_id), f"{payload.wyscout_id}.0"]
                ).df()
            else:
                df = pd.DataFrame()

            if df.empty:
                df = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Player = ? ORDER BY Season DESC LIMIT 1", [payload.jugador]).df()
        
            if df.empty: raise HTTPException(status_code=404, detail="Jugador no encontrado.")
            
            # Extraemos la cohorte del jugador para comparar manzanas con manzanas
            temp = df['Season'].iloc[0]
            comp = df['Competition'].iloc[0]
            df_cohort = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Season = ? AND Competition = ?", [temp, comp]).df()
            
        top_metrics = pesos.items()
        
        etiquetas, valores_jugador, valores_demanda = [], [], []
        
        for m, target_pct in top_metrics:
            if m in df.columns and m in df_cohort.columns:
                val_bruto = df[m].iloc[0]
                
                # 🚀 LA MAGIA: Convertimos su valor bruto en Percentil comparándolo con su liga
                serie = pd.to_numeric(df_cohort[m], errors='coerce').dropna()
                if len(serie) > 0:
                    player_pct = (serie < val_bruto).mean() * 100
                else:
                    player_pct = 50.0
                    
                etiquetas.append(m.replace(' Tendency', ''))
                valores_jugador.append(player_pct)
                valores_demanda.append(target_pct)
                
        if not etiquetas:
            raise HTTPException(status_code=400, detail="No hay métricas válidas para dibujar el radar.")

        # Cerramos el polígono para que el radar se dibuje bien
        valores_jugador.append(valores_jugador[0])
        valores_demanda.append(valores_demanda[0])
        etiquetas.append(etiquetas[0])
        
        import plotly.graph_objects as go
        import plotly.io as pio
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=valores_demanda, theta=etiquetas, fill='toself', name='Exigencia', line=dict(color='rgba(244, 63, 94, 1)', width=2.5, dash='dash'), fillcolor='rgba(244, 63, 94, 0.15)'))
        fig.add_trace(go.Scatterpolar(r=valores_jugador, theta=etiquetas, fill='toself', name=payload.jugador, line=dict(color='rgba(14, 165, 233, 1)', width=2.5), fillcolor='rgba(14, 165, 233, 0.4)'))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(150,150,150,0.3)'), 
                angularaxis=dict(gridcolor='rgba(150,150,150,0.3)')
            ), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            margin=dict(l=40, r=40, t=40, b=40), 
            showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5)
        )
        
        return {"radar": pio.to_json(fig)}
    except HTTPException: raise
    except Exception as e: 
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
# ==========================================
# RUTAS DE SISTEMA (SYNC, ALERTAS Y GUARDAR)

@app.get("/api/alertas")
async def obtener_alertas():
    if not MOTOR_ALERTAS:
        # Si está vacío, forzamos un escaneo rápido
        escanear_mercado_background()
    return MOTOR_ALERTAS

@app.get("/api/guardar")
async def guardar():
    try:
        # En FastAPI, las descargas de archivos generados en memoria se hacen así:
        datos_guardar = {
            "pesos_teamfit": _CACHE_TEAM_FIT_PESOS,
            "radar_actual": _CACHE_RADAR_ACTUAL,
            "plantilla_activa": True if not _CACHE_PLANTILLA.empty else False
        }
        mem = io.BytesIO()
        mem.write(json.dumps(datos_guardar).encode('utf-8'))
        mem.seek(0)
        
        # Devolvemos un StreamingResponse con las cabeceras de descarga
        return StreamingResponse(
            iter([mem.getvalue()]), 
            media_type="application/json", 
            headers={"Content-Disposition": f"attachment; filename=Proyecto_Scouting_{datetime.now().strftime('%Y%m%d_%H%M')}.json"}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error guardando.")

@app.get("/api/sync_data")
@app.post("/api/sync_data")
async def sync_data():
    """ Escanea la carpeta Data y convierte a Parquet (Con Server-Sent Events) """
    async def generate():
        import re
        import os
        from backend.core.pandas import obtener_catalogo_datos
        from backend.config.diccionarios import MAPEO_LIGAS_PAISES
        try:
            yield f"data: {json.dumps({'progress': 5, 'msg': 'Iniciando escaneo...'})}\n\n"
            ruta_origen = "Data"
            ruta_destino = "Data_Parquet"
            temporadas_activas = ['25-26', '2026']
            if not os.path.exists(ruta_destino): os.makedirs(ruta_destino)

            csvs_a_procesar = [(r, a) for r, _, archs in os.walk(ruta_origen) for a in archs if a.endswith(".csv")]
            procesados, saltados = 0, 0
            for idx, (raiz, archivo) in enumerate(csvs_a_procesar):
                ruta_nueva_carpeta = os.path.join(ruta_destino, os.path.relpath(raiz, ruta_origen))
                if not os.path.exists(ruta_nueva_carpeta): os.makedirs(ruta_nueva_carpeta)
                match = re.search(r'\s(\d{2}-\d{2}|\d{4})$', archivo.replace('.csv', ''))
                temporada = match.group(1) if match else "Unknown"
                ruta_csv = os.path.join(raiz, archivo)
                ruta_parquet = os.path.join(ruta_nueva_carpeta, archivo.replace(".csv", ".parquet"))
                
                if temporada not in temporadas_activas and os.path.exists(ruta_parquet): 
                    saltados += 1
                else:
                    try:
                        pd.read_csv(ruta_csv, low_memory=False).to_parquet(ruta_parquet, engine='pyarrow', index=False)
                        procesados += 1
                    except: pass
                yield f"data: {json.dumps({'progress': 20 + int((idx / max(1, len(csvs_a_procesar))) * 70), 'msg': f'Comprimiendo {archivo}...'})}\n\n"

            global _CACHE_CATALOGO
            _CACHE_CATALOGO = obtener_catalogo_datos()
            yield f"data: {json.dumps({'progress': 100, 'msg': '¡Completado!', 'done': True, 'procesados': procesados, 'saltados': saltados})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
            
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/jugadores")
@lru_cache(maxsize=1)
def obtener_nombres_jugadores():
    try:
        with get_duckdb_conn() as conn:
            # Saca todos los nombres únicos ordenados alfabéticamente
            df = conn.execute("SELECT DISTINCT Player FROM dim_jugadores_stats WHERE Player IS NOT NULL ORDER BY Player").df()
            return df['Player'].tolist()
    except:
        return []


class ETLResponse(BaseModel):
    status: str
    mensaje: str
    registros_insertados: int = 0
    tiempo_segundos: float = 0.0

def unificar_liga_y_pais(liga_raw, pais_raw):
    """ Asignación 100% Manual, a prueba de fallos mediante Diccionario Exacto """
    import re
    l_original = str(liga_raw).upper().strip()

    # 1. LIMPIEZA DEL AÑO (Ej: "Premier League 24-25" -> "PREMIER LEAGUE")
    l = re.sub(r'\s(\d{2}-\d{2}|\d{4})$', '', l_original).strip()
    
    # 2. BARRERAS EXCLUYENTES: Ligas Femeninas y Mundial (¡FUERA!)
    if l in [
        "FRAUEN-BUNDESLIGA", "LIGA F", "NWSL", "PREMIERE LIGUE", 
        "SERIE A FEMMINILE", "USL SUPER LEAGUE", "VROUWEN EREDIVISIE", 
        "WOMEN'S SUPER LEAGUE", "WORLD CUP", "NORTHERN SUPER LEAGUE"
    ] or "WOMEN" in l or "FEMMINILE" in l or "WORLD CUP" in l or "FRAUEN" in l or "VROUWEN" in l:
        return "DESCARTAR", "DESCARTAR"

    # 3. EL DICCIONARIO MAESTRO (1 a 1 extraído de tus datos)
    MAPEO = {
        "1. HNL": ("Primera División Croacia", "Croacia"),
        "2. BUNDESLIGA": ("Segunda División Alemania", "Alemania"),
        "2. HNL": ("Segunda División Croacia", "Croacia"),
        "3. LIGA": ("Tercera División Alemania", "Alemania"),
        "A-LEAGUE MEN": ("Primera División Australia", "Australia"),
        "ALBANIAN KATEGORIA SUPERIORE": ("Primera División Albania", "Albania"),
        "ALLSVENSKAN": ("Primera División Suecia", "Suecia"),
        "ANDORRA PRIMERA DIVISIÓ": ("Primera División Andorra", "Andorra"),
        "ARGENTINA COPA DE LA LIGA": ("Copa de la Liga Profesional Argentina", "Argentina"),
        "ARGENTINA LPF": ("Primera División Argentina (Liga Profesional)", "Argentina"),
        "ARGENTINA PRIMERA NACIONAL": ("Segunda División Argentina", "Argentina"),
        "ARGENTINA RESERVE LEAGUE": ("Liga de Reservas Argentina", "Argentina"),
        "ARMENIAN PREMIER LEAGUE": ("Primera División Armenia", "Armenia"),
        "AUSTRALIAN NPLS": ("Ligas Nacionales Premier Australia (Nivel Regional)", "Australia"),
        "AUSTRIAN 2. LIGA": ("Segunda División Austria", "Austria"),
        "AUSTRIAN BUNDESLIGA": ("Primera División Austria", "Austria"),
        "AZERI BIRINCI DASTA": ("Segunda División Azerbaiyán", "Azerbaiyán"),
        "AZERI PREMYER LIQA": ("Primera División Azerbaiyán", "Azerbaiyán"),
        "BRI LIGA 1": ("Primera División Indonesia", "Indonesia"),
        "BAHRAIN PREMIER LEAGUE": ("Primera División Baréin", "Baréin"),
        "BELARUSIAN 1. DIVISION": ("Segunda División Bielorrusia", "Bielorrusia"),
        "BELARUSIAN PREMIER LEAGUE": ("Primera División Bielorrusia", "Bielorrusia"),
        "BELARUSIAN RESERVE LEAGUE": ("Liga de Reservas Bielorrusia", "Bielorrusia"),
        "BELGIAN FIRST DIVISION B": ("Segunda División Bélgica", "Bélgica"),
        "BELGIAN PRO LEAGUE": ("Primera División Bélgica", "Bélgica"),
        "BESTA-DEILD KARLA": ("Primera División Islandia", "Islandia"),
        "BOLIVIAN LFPB": ("Primera División Bolivia", "Bolivia"),
        "BOSNIAN PREMIER LEAGUE": ("Primera División Bosnia y Herzegovina", "Bosnia y Herzegovina"),
        "BOTOLA PRO": ("Primera División Marruecos", "Marruecos"),
        "BRASILEIRÃO": ("Primera División Brasil", "Brasil"),
        "BRASILEIRAO": ("Primera División Brasil", "Brasil"),
        "BRAZIL SERIE B": ("Segunda División Brasil", "Brasil"),
        "BRAZIL SERIE C": ("Tercera División Brasil", "Brasil"),
        "BULGARIAN FIRST LEAGUE": ("Primera División Bulgaria", "Bulgaria"),
        "BUNDESLIGA": ("Primera División Alemania", "Alemania"),
        "CAMBODIAN PREMIER LEAGUE": ("Primera División Camboya", "Camboya"),
        "CAMPEONATO DE PORTUGAL": ("Cuarta División Portugal", "Portugal"),
        "CANADIAN PREMIER LEAGUE": ("Primera División Canadá", "Canadá"),
        "CAPITAL TERRITORY NPL": ("Liga Regional Australia (Territorio de la Capital)", "Australia"),
        "CHAMPIONSHIP": ("Segunda División Inglaterra", "Inglaterra"),
        "CHILEAN PRIMERA B": ("Segunda División Chile", "Chile"),
        "CHILEAN PRIMERA DIVISION": ("Primera División Chile", "Chile"),
        "CHILEAN PRIMERA DIVISIÓN": ("Primera División Chile", "Chile"),
        "CHINA LEAGUE ONE": ("Segunda División China", "China"),
        "CHINA LEAGUE TWO": ("Tercera División China", "China"),
        "CHINESE SUPER LEAGUE": ("Primera División China", "China"),
        "COLOMBIAN PRIMERA A": ("Primera División Colombia", "Colombia"),
        "COLOMBIAN TORNEO BETPLAY": ("Segunda División Colombia", "Colombia"),
        "COSTA RICAN PRIMERA DIVISION": ("Primera División Costa Rica", "Costa Rica"),
        "COSTA RICAN PRIMERA DIVISIÓN": ("Primera División Costa Rica", "Costa Rica"),
        "CYPRUS 1. DIVISION": ("Primera División Chipre", "Chipre"),
        "CYPRUS 2. DIVISION": ("Segunda División Chipre", "Chipre"),
        "CZECH 1. LIGA U19": ("Liga Juvenil Sub-19 República Checa", "República Checa"),
        "CZECH FNL": ("Segunda División República Checa", "República Checa"),
        "CZECH FORTUNA LIGA": ("Primera División República Checa", "República Checa"),
        "CZECH U17 LEAGUE": ("Liga Juvenil Sub-17 República Checa", "República Checa"),
        "DANISH 1. DIVISION": ("Segunda División Dinamarca", "Dinamarca"),
        "DANISH 2. DIVISION": ("Tercera División Dinamarca", "Dinamarca"),
        "DANISH 3. DIVISION": ("Cuarta División Dinamarca", "Dinamarca"),
        "DANISH U17 DIVISION": ("Liga Juvenil Sub-17 Dinamarca (División)", "Dinamarca"),
        "DANISH U17 LIGAEN": ("Liga Juvenil Sub-17 Dinamarca (Liga)", "Dinamarca"),
        "DANISH U19 DIVISION": ("Liga Juvenil Sub-19 Dinamarca (División)", "Dinamarca"),
        "DANISH U19 LIGAEN": ("Liga Juvenil Sub-19 Dinamarca (Liga)", "Dinamarca"),
        "ECUADOR LIGA PRO": ("Primera División Ecuador", "Ecuador"),
        "EERSTE DIVISIE": ("Segunda División Países Bajos", "Países Bajos"),
        "EGYPTIAN PREMIER LEAGUE": ("Primera División Egipto", "Egipto"),
        "EKSTRAKLASA": ("Primera División Polonia", "Polonia"),
        "EL SALVADOR PRIMERA DIVISION": ("Primera División El Salvador", "El Salvador"),
        "EL SALVADOR PRIMERA DIVISIÓN": ("Primera División El Salvador", "El Salvador"),
        "ELITESERIEN": ("Primera División Noruega", "Noruega"),
        "ENGLISH NATIONAL LEAGUE": ("Quinta División Inglaterra", "Inglaterra"),
        "ENGLISH NATIONAL LEAGUE NORTH SOUTH": ("Sexta División Inglaterra", "Inglaterra"),
        "ENGLISH NON-LEAGUE PREMIER DIVISION - STEP 7": ("Séptima División Inglaterra", "Inglaterra"),
        "EREDIVISIE": ("Primera División Países Bajos", "Países Bajos"),
        "EROVNULI LIGA": ("Primera División Georgia", "Georgia"),
        "EROVNULI LIGA 2": ("Segunda División Georgia", "Georgia"),
        "ESTONIA MEISTRILIIGA": ("Primera División Estonia", "Estonia"),
        "ESTONIAN ESILIIGA A": ("Segunda División Estonia", "Estonia"),
        "ETTAN": ("Tercera División Suecia", "Suecia"),
        "FAROE ISLANDS MEISTARADEILDIN": ("Primera División Islas Feroe", "Islas Feroe"),
        "FRENCH NATIONAL 1": ("Tercera División Francia", "Francia"),
        "GREEK SUPER LEAGUE": ("Primera División Grecia", "Grecia"),
        "GREEK SUPER LEAGUE 2": ("Segunda División Grecia", "Grecia"),
        "GREEK U19 SUPER LEAGUE": ("Liga Juvenil Sub-19 Grecia", "Grecia"),
        "GUATEMALAN LIGA NACIONAL": ("Primera División Guatemala", "Guatemala"),
        "HONDURAN LIGA NACIONAL": ("Primera División Honduras", "Honduras"),
        "HONG KONG PREMIER LEAGUE": ("Primera División Hong Kong", "Hong Kong"),
        "ICELAND 1. DEILD": ("Segunda División Islandia", "Islandia"),
        "INDIAN SUPER LEAGUE": ("Primera División India", "India"),
        "IRISH FIRST DIVISION": ("Segunda División Irlanda", "Irlanda"),
        "IRISH PREMIER DIVISION": ("Primera División Irlanda", "Irlanda"),
        "J1": ("Primera División Japón", "Japón"),
        "J2": ("Segunda División Japón", "Japón"),
        "J3": ("Tercera División Japón", "Japón"),
        "JORDAN PRO LEAGUE": ("Primera División Jordania", "Jordania"),
        "K LEAGUE 1": ("Primera División Corea del Sur", "Corea del Sur"),
        "K LEAGUE 2": ("Segunda División Corea del Sur", "Corea del Sur"),
        "K3 LEAGUE": ("Tercera División Corea del Sur", "Corea del Sur"),
        "K4 LEAGUE": ("Cuarta División Corea del Sur", "Corea del Sur"),
        "KAZAKH 1. DIVISION": ("Segunda División Kazajistán", "Kazajistán"),
        "KAZAKH 2. DIVISION": ("Tercera División Kazajistán", "Kazajistán"),
        "KAZAKH PREMIER LEAGUE": ("Primera División Kazajistán", "Kazajistán"),
        "KAZAKH U16 LEAGUE": ("Liga Juvenil Sub-16 Kazajistán", "Kazajistán"),
        "KAZAKH U17 LEAGUE": ("Liga Juvenil Sub-17 Kazajistán", "Kazajistán"),
        "KAZAKH U18 LEAGUE": ("Liga Juvenil Sub-18 Kazajistán", "Kazajistán"),
        "KOSOVO SUPERLIGA": ("Primera División Kosovo", "Kosovo"),
        "KYRGYZ PREMIER LEAGUE": ("Primera División Kirguistán", "Kirguistán"),
        "LA LIGA": ("Primera División España", "España"),
        "LA LIGA 2": ("Segunda División España", "España"),
        "LATVIAN 1. LIGA": ("Segunda División Letonia", "Letonia"),
        "LATVIAN VIRSLIGA": ("Primera División Letonia", "Letonia"),
        "LEAGUE ONE": ("Tercera División Inglaterra", "Inglaterra"),
        "LEAGUE TWO": ("Cuarta División Inglaterra", "Inglaterra"),
        "LIGA LEUMIT": ("Segunda División Israel", "Israel"),
        "LIGA MX": ("Primera División México", "México"),
        "LIGA DE EXPANSION MX": ("Segunda División México", "México"),
        "LIGA DE EXPANSIÓN MX": ("Segunda División México", "México"),
        "LIGAT HA'AL": ("Primera División Israel", "Israel"),
        "LIGUE 1": ("Primera División Francia", "Francia"),
        "LIGUE 2": ("Segunda División Francia", "Francia"),
        "LITHUANIAN 1 LYGA": ("Segunda División Lituania", "Lituania"),
        "LITHUANIAN A LYGA": ("Primera División Lituania", "Lituania"),
        "LUXEMBOURG NATIONAL DIVISION": ("Primera División Luxemburgo", "Luxemburgo"),
        "MLS": ("Primera División Estados Unidos", "Estados Unidos"),
        "MLS NEXT PRO": ("Tercera División Estados Unidos (Liga de Reservas)", "Estados Unidos"),
        "MALAYSIAN SUPER LEAGUE": ("Primera División Malasia", "Malasia"),
        "MALTA CHALLENGE LEAGUE": ("Segunda División Malta", "Malta"),
        "MALTA PREMIER LEAGUE": ("Primera División Malta", "Malta"),
        "MEXICAN U17 LEAGUE": ("Liga Juvenil Sub-17 México", "México"),
        "MEXICAN U18 LEAGUE": ("Liga Juvenil Sub-18 México", "México"),
        "MEXICAN U19 LEAGUE": ("Liga Juvenil Sub-19 México", "México"),
        "MEXICAN U23 LEAGUE": ("Liga Juvenil Sub-23 México", "México"),
        "MOLDOVAN SUPER LIGA": ("Primera División Moldavia", "Moldavia"),
        "MONTENEGRO FIRST LEAGUE": ("Primera División Montenegro", "Montenegro"),
        "MONTENEGRO SECOND LEAGUE": ("Segunda División Montenegro", "Montenegro"),
        "NB I": ("Primera División Hungría", "Hungría"),
        "NB II": ("Segunda División Hungría", "Hungría"),
        "NCAA D2": ("Fútbol Universitario Estados Unidos División 2", "Estados Unidos"),
        "NCAA D3": ("Fútbol Universitario Estados Unidos División 3", "Estados Unidos"),
        "NEW SOUTH WALES NPL": ("Liga Regional Australia (Nueva Gales del Sur)", "Australia"),
        "NEW ZEALAND NATIONAL LEAGUE": ("Primera División Nueva Zelanda", "Nueva Zelanda"),
        "NICARAGUA PRIMERA DIVISION": ("Primera División Nicaragua", "Nicaragua"),
        "NIGERIAN CREATIVE CHAMPIONSHIP": ("Liga de Desarrollo Nigeria", "Nigeria"),
        "NORTH MACEDONIA FIRST LEAGUE": ("Primera División Macedonia del Norte", "Macedonia del Norte"),
        "NORTHERN IRISH PREMIERSHIP": ("Primera División Irlanda del Norte", "Irlanda del Norte"),
        "NORWEGIAN 2. DIVISION": ("Tercera División Noruega", "Noruega"),
        "OBOS LIGAEN": ("Segunda División Noruega", "Noruega"),
        "PANAMA LPF": ("Primera División Panamá", "Panamá"),
        "PARAGUAY DIVISION PROFESIONAL": ("Primera División Paraguay", "Paraguay"),
        "PERUVIAN LIGA 1": ("Primera División Perú", "Perú"),
        "POLISH I LIGA": ("Segunda División Polonia", "Polonia"),
        "POLISH II LIGA": ("Tercera División Polonia", "Polonia"),
        "PORTUGUESE JUNIORES U17": ("Liga Juvenil Sub-17 Portugal", "Portugal"),
        "PORTUGUESE JUNIORES U19": ("Liga Juvenil Sub-19 Portugal", "Portugal"),
        "PORTUGUESE JÚNIORES U17": ("Liga Juvenil Sub-17 Portugal", "Portugal"),
        "PORTUGUESE JÚNIORES U19": ("Liga Juvenil Sub-19 Portugal", "Portugal"),
        "PORTUGUESE LIGA 3": ("Tercera División Portugal", "Portugal"),
        "PORTUGUESE LIGA REVELACAO SUB 23": ("Liga Sub-23 Portugal (Revelación)", "Portugal"),
        "PORTUGUESE LIGA REVELAÇÃO SUB 23": ("Liga Sub-23 Portugal (Revelación)", "Portugal"),
        "PORTUGUESE SEGUNDA LIGA": ("Segunda División Portugal", "Portugal"),
        "PREMIER LEAGUE": ("Primera División Inglaterra", "Inglaterra"),
        "PREMIER LEAGUE 2": ("Liga de Reservas Inglaterra Sub-21", "Inglaterra"),
        "PRIMAVERA 1": ("Liga Juvenil Sub-19 Italia", "Italia"),
        "PRIMEIRA LIGA": ("Primera División Portugal", "Portugal"),
        "PRIMERA RFEF": ("Tercera División España", "España"),
        "QATARI STARS LEAGUE": ("Primera División Catar", "Catar"),
        "QUEENSLAND NPL": ("Liga Regional Australia (Queensland)", "Australia"),
        "QUEENSLAND PREMIER LEAGUE": ("Segunda Liga Regional Australia (Queensland)", "Australia"),
        "REGIONALLIGA": ("Cuarta División Alemania", "Alemania"),
        "ROMANIAN LIGA ELITELOR U17": ("Liga Juvenil Sub-17 Rumania", "Rumania"),
        "ROMANIAN LIGA II": ("Segunda División Rumania", "Rumania"),
        "ROMANIAN LIGA TINERET U18": ("Liga Juvenil Sub-18 Rumania", "Rumania"),
        "ROMANIAN SUPERLIGA": ("Primera División Rumania", "Rumania"),
        "RUSSIAN FIRST LEAGUE": ("Segunda División Rusia", "Rusia"),
        "RUSSIAN PREMIER LEAGUE": ("Primera División Rusia", "Rusia"),
        "SAUDI DIVISION 1": ("Segunda División Arabia Saudita", "Arabia Saudita"),
        "SAUDI PRO LEAGUE": ("Primera División Arabia Saudita", "Arabia Saudita"),
        "SCOTTISH CHAMPIONSHIP": ("Segunda División Escocia", "Escocia"),
        "SCOTTISH LEAGUE ONE": ("Tercera División Escocia", "Escocia"),
        "SCOTTISH LEAGUE TWO": ("Cuarta División Escocia", "Escocia"),
        "SCOTTISH PREMIERSHIP": ("Primera División Escocia", "Escocia"),
        "SEGUNDA RFEF": ("Cuarta División España", "España"),
        "SERBIAN PRVA LIGA": ("Segunda División Serbia", "Serbia"),
        "SERBIAN SUPER LIGA": ("Primera División Serbia", "Serbia"),
        "SERBIAN U17 LEAGUE": ("Liga Juvenil Sub-17 Serbia", "Serbia"),
        "SERBIAN U19 LEAGUE": ("Liga Juvenil Sub-19 Serbia", "Serbia"),
        "SERIE A": ("Primera División Italia", "Italia"),
        "SERIE B": ("Segunda División Italia", "Italia"),
        "SERIE C": ("Tercera División Italia", "Italia"),
        "SERIE D - GIRONE A": ("Cuarta División Italia (Grupo A)", "Italia"),
        "SERIE D - GIRONE B": ("Cuarta División Italia (Grupo B)", "Italia"),
        "SERIE D - GIRONE C": ("Cuarta División Italia (Grupo C)", "Italia"),
        "SERIE D - GIRONE D": ("Cuarta División Italia (Grupo D)", "Italia"),
        "SERIE D - GIRONE E": ("Cuarta División Italia (Grupo E)", "Italia"),
        "SERIE D - GIRONE F": ("Cuarta División Italia (Grupo F)", "Italia"),
        "SERIE D - GIRONE G": ("Cuarta División Italia (Grupo G)", "Italia"),
        "SERIE D - GIRONE H": ("Cuarta División Italia (Grupo H)", "Italia"),
        "SINGAPORE PREMIER LEAGUE": ("Primera División Singapur", "Singapur"),
        "SLOVAK 2. LIGA": ("Segunda División Eslovaquia", "Eslovaquia"),
        "SLOVAK SUPER LIGA": ("Primera División Eslovaquia", "Eslovaquia"),
        "SLOVAK U19 LEAGUE": ("Liga Juvenil Sub-19 Eslovaquia", "Eslovaquia"),
        "SLOVENIAN 1. SNL": ("Primera División Eslovenia", "Eslovenia"),
        "SLOVENIAN 2. SNL": ("Segunda División Eslovenia", "Eslovenia"),
        "SOUTH AFRICAN PSL": ("Primera División Sudáfrica", "Sudáfrica"),
        "SOUTH AUSTRALIA NPL": ("Liga Regional Australia (Australia del Sur)", "Australia"),
        "SOUTH AUSTRALIA STATE LEAGUE 1": ("Segunda Liga Regional Australia (Australia del Sur)", "Australia"),
        "SUPER LIG": ("Primera División Turquía", "Turquía"),
        "SUPERETTAN": ("Segunda División Suecia", "Suecia"),
        "SUPERLIGA": ("Primera División Dinamarca", "Dinamarca"), 
        "SWISS 1. LIGA CLASSIC": ("Cuarta División Suiza", "Suiza"),
        "SWISS 1. LIGA PROMOTION": ("Tercera División Suiza", "Suiza"),
        "SWISS CHALLENGE LEAGUE": ("Segunda División Suiza", "Suiza"),
        "SWISS SUPER LEAGUE": ("Primera División Suiza", "Suiza"),
        "SWISS U17 ELITE": ("Liga Juvenil Sub-17 Suiza", "Suiza"),
        "SWISS U19 ELITE": ("Liga Juvenil Sub-19 Suiza", "Suiza"),
        "SÜPER LIG": ("Primera División Turquía", "Turquía"),
        "THAI LEAGUE 1": ("Primera División Tailandia", "Tailandia"),
        "THAI LEAGUE 2": ("Segunda División Tailandia", "Tailandia"),
        "TUNISIA LIGUE 1": ("Primera División Túnez", "Túnez"),
        "TURKISH 1. LIG": ("Segunda División Turquía", "Turquía"),
        "TWEEDE DIVISIE": ("Tercera División Países Bajos", "Países Bajos"),
        "U17 BUNDESLIGA": ("Liga Juvenil Sub-17 Alemania", "Alemania"),
        "U19 BUNDESLIGA": ("Liga Juvenil Sub-19 Alemania", "Alemania"),
        "UAE PRO LEAGUE": ("Primera División Emiratos Árabes Unidos", "Emiratos Árabes Unidos"),
        "USL CHAMPIONSHIP": ("Segunda División Estados Unidos", "Estados Unidos"),
        "USL LEAGUE 1": ("Tercera División Estados Unidos", "Estados Unidos"),
        "USL LEAGUE ONE": ("Tercera División Estados Unidos", "Estados Unidos"),
        "UKRAINIAN PERSHA LIGA": ("Segunda División Ucrania", "Ucrania"),
        "UKRAINIAN PREMIER LEAGUE": ("Primera División Ucrania", "Ucrania"),
        "UKRAINIAN U19 LEAGUE": ("Liga Juvenil Sub-19 Ucrania", "Ucrania"),
        "URUGUAY PRIMERA DIVISION": ("Primera División Uruguay", "Uruguay"),
        "URUGUAY PRIMERA DIVISIÓN": ("Primera División Uruguay", "Uruguay"),
        "UZBEK SUPER LEAGUE": ("Primera División Uzbekistán", "Uzbekistán"),
        "V.LEAGUE 1": ("Primera División Vietnam", "Vietnam"),
        "VEIKKAUSLIIGA": ("Primera División Finlandia", "Finlandia"),
        "VICTORIA NPL": ("Liga Regional Australia (Victoria)", "Australia"),
        "WELSH PREMIER LEAGUE": ("Primera División Gales", "Gales"),
        "WESTERN AUSTRALIA NPL": ("Liga Regional Australia (Australia Occidental)", "Australia"),
        "YKKONEN": ("Tercera División Finlandia", "Finlandia"),
        "YKKOSLIIGA": ("Segunda División Finlandia", "Finlandia"),
        "YKKÖNEN": ("Tercera División Finlandia", "Finlandia"),
        "YKKÖSLIIGA": ("Segunda División Finlandia", "Finlandia")
    }

    if l in MAPEO:
        return MAPEO[l][0], MAPEO[l][1]

    # Si por algún casual la liga llega sin estar en tu lista, le ponemos "Otros"
    pais_final = pais_raw.title() if isinstance(pais_raw, str) and str(pais_raw).upper() not in ["DESCONOCIDO", "STAT_FILES", "POST_MATCH_APP", "NONE", "NAN", ""] else "Otros"
    return l_original, pais_final

@app.post("/api/admin/run_etl", response_model=ETLResponse)
async def ejecutar_etl_completo():
    """ 
    Ruta para ejecutar el script ETL (Zero-Downtime Swap y subcarpetas).
    """
    import time
    import os
    import glob
    t0 = time.time()
    
    try:
        # 1. Extracción Jugadores
        ruta_origen = "Data"
        patron = os.path.join(ruta_origen, "**", "*.csv")
        archivos = glob.glob(patron, recursive=True)
        lista_dfs = []
        
        for ruta in archivos:
            try:
                nombre = os.path.basename(ruta).replace('.csv', '')            
                carpeta_pais = os.path.basename(os.path.dirname(ruta))            
                if carpeta_pais == os.path.basename(ruta_origen) or not carpeta_pais:
                    carpeta_pais = "Desconocido"
                
                partes = nombre.rsplit(' ', 1)
                liga_sucia, temp = (partes[0], partes[1]) if len(partes) == 2 else (nombre, "Unknown")
                
                # 🚀 IA: Pasamos la liga sucia por el normalizador
                liga_limpia, pais_limpio = unificar_liga_y_pais(liga_sucia, carpeta_pais)
                
                # 🚀 FIX: Si es una liga femenina o juvenil, ignoramos el archivo por completo
                if liga_limpia == "DESCARTAR":
                    continue
                    
                df = pd.read_csv(ruta, low_memory=False)            
                df = df.loc[:, ~df.columns.duplicated()].copy()            
                df = df.assign(
                    Pais_Liga=pais_limpio, Competition=liga_limpia, 
                    Season=temp, League_Weight=PESOS_LIGAS.get(liga_limpia, PESOS_LIGAS.get(liga_sucia, 0.30))
                )
                lista_dfs.append(df)
            except Exception as e:
                print(f"  ❌ Error leyendo {ruta}: {e}")
                
        if not lista_dfs:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV en Data/")
            
        df_crudo = pd.concat(lista_dfs, ignore_index=True)
        df_crudo = df_crudo[~df_crudo['Player'].str.contains(r'\[REF\]', na=False)].copy()

        # 2. Transformación Equipos
        archivos_eq = list(set(
            glob.glob(os.path.join("Post_Match_App", "Stat_Files", "**", "*25-26*.csv"), recursive=True) +
            glob.glob(os.path.join("Post_Match_App", "Stat_Files", "**", "*2026*.csv"), recursive=True)
        ))
        
        df_equipos = pd.DataFrame()
        if archivos_eq:
            lista_eq_dfs = []
            for f in archivos_eq:
                try:
                    df_tmp = pd.read_csv(f, low_memory=False)
                    if df_tmp.empty or 'Team' not in df_tmp.columns: continue
                    
                    nombre_f = os.path.basename(f).replace('.csv', '')
                    carpeta_f = os.path.basename(os.path.dirname(f))
                    if carpeta_f in ["Stat_Files", "Post_Match_App"] or not carpeta_f: 
                        carpeta_f = "Desconocido"
                        
                    partes_f = nombre_f.rsplit(' ', 1)
                    liga_sucia_eq = partes_f[0] if len(partes_f) == 2 else nombre_f
                    
                    liga_eq_limpia, pais_eq_limpio = unificar_liga_y_pais(liga_sucia_eq, carpeta_f)
                    
                    # 🚀 FIX: Si el equipo es de liga femenina o juvenil, lo ignoramos
                    if liga_eq_limpia == "DESCARTAR":
                        continue
                    
                    df_tmp['Competition_Eq'] = liga_eq_limpia
                    df_tmp['Pais_Eq'] = pais_eq_limpio
                    lista_eq_dfs.append(df_tmp)
                except: pass
                
            if lista_eq_dfs:
                df_equipos_crudos = pd.concat(lista_eq_dfs, ignore_index=True)
                num_cols = [c for c in df_equipos_crudos.select_dtypes(include=[np.number]).columns if c not in ['Team', 'Competition_Eq', 'Pais_Eq']]
                df_equipos = df_equipos_crudos.groupby(['Team', 'Competition_Eq', 'Pais_Eq'])[num_cols].mean().reset_index()

        # 3. Limpieza Jugadores
        if not df_equipos.empty and 'Possession' in df_equipos.columns:
            possession_dict = df_equipos.set_index('Team')['Possession'].to_dict()
            df_crudo['Team_Possession'] = df_crudo['Team'].map(possession_dict).fillna(50.0)
        else:
            df_crudo['Team_Possession'] = 50.0

        COLS_STR = {'Player', 'Team', 'Team within selected timeframe', 'Position', 
                    'Primary position', 'Secondary position', 'Third position', 
                    'Competition', 'League', 'Birth country', 'Foot', 'Contract expires', 'Season'}
        
        for col in df_crudo.columns:
            if col not in COLS_STR and df_crudo[col].dtype == 'object':
                df_crudo[col] = pd.to_numeric(df_crudo[col].astype(str).str.replace(',', '.', regex=False).str.replace('-', '0', regex=False), errors='coerce')

        df_crudo = df_crudo.fillna(0)

        # 4. Matemáticas (Acciones exitosas)
        from backend.core.pandas import _cols_nuevas_metricas
        extra_masters = _cols_nuevas_metricas(df_crudo)
        if extra_masters:
            df_crudo = pd.concat([df_crudo, pd.DataFrame(extra_masters, index=df_crudo.index).fillna(0)], axis=1)
            df_crudo = df_crudo.loc[:, ~df_crudo.columns.duplicated(keep='last')].copy()

        # 5. Escalar a Percentiles
        COLS_META = {'Player', 'Team', 'Competition', 'League', 'Season', 'Position', 'Primary position', 
                     'Secondary position', 'Third position', 'Birth country', 'Foot', 'Contract expires', 
                     'Age', 'Matches played', 'Minutes played', 'Height', 'Weight', 'League_Weight', 'Wyscout id'}
        
        col_num = [c for c in df_crudo.select_dtypes(include=[np.number]).columns if c not in COLS_META]
        METRICAS_INVERSAS = ['conceded', 'against', 'losses', 'turnovers', 'fouls', 'yellow', 'red', 'pérdidas', 'faltas', 'encajados']
        
        from backend.core.pandas import motor_escalado_unico, motor_calculo_ratings
        df_limpio = motor_escalado_unico(df_crudo, col_num, METRICAS_INVERSAS, None, True, 0)

        # 6. Ratings
        todos_los_estilos = {**estilos_gk, **estilos_cb, **estilos_lt, **estilos_mcd, **estilos_int, **estilos_mp, **estilos_ext, **estilos_del, **estilos_med}
        df_limpio = motor_calculo_ratings(df_limpio, diccionarios=todos_los_estilos, mascara_posicion=None, aplicar_peso_liga=True)

        # 7. 🚀 EL CAMBIAZO SEGURO (Zero-Downtime Swap)
        db_path = 'instance/scouting_analitica.duckdb'
        db_temp = 'instance/scouting_analitica_temp.duckdb'
        os.makedirs('instance', exist_ok=True)
        
        if os.path.exists(db_temp):
            try: os.remove(db_temp)
            except: pass
            
        conn_write = duckdb.connect(db_temp)    
        conn_write.execute("CREATE OR REPLACE TABLE dim_jugadores_stats AS SELECT * FROM df_limpio")
        if not df_equipos.empty:
            conn_write.execute("CREATE OR REPLACE TABLE dim_equipos_stats AS SELECT * FROM df_equipos")
        conn_write.close()
        
        # Sustituimos el archivo "en caliente"
        swap_exitoso = False
        for _ in range(5):
            try:
                os.replace(db_temp, db_path)
                swap_exitoso = True
                break
            except PermissionError:
                time.sleep(1)
                
        if not swap_exitoso:
            raise HTTPException(status_code=500, detail="ERROR CRÍTICO: Windows tiene bloqueada la base de datos. APAGA LA TERMINAL (Ctrl+C), BORRA EL ARCHIVO 'instance/scouting_analitica.duckdb' MANUALMENTE, INICIA LA TERMINAL Y VUELVE A EJECUTAR EL ETL.")
        
        t1 = time.time()
        return ETLResponse(status="ok", mensaje="Pipeline OLAP completado con éxito.", registros_insertados=len(df_limpio), tiempo_segundos=round(t1-t0, 2))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en ETL: {str(e)}")
    
@app.post("/api/admin/curar_bd", response_model=ETLResponse)
async def curar_base_de_datos():
    """ 
    Ruta para Curación (Matemáticas Avanzadas con Zero-Downtime Swap).
    """
    import time
    import gc
    import os
    t0 = time.time()
    
    db_path = 'instance/scouting_analitica.duckdb'
    db_temp = 'instance/scouting_analitica_temp.duckdb'
    
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Base de datos no encontrada. Ejecuta run_etl primero.")

    try:
        # 1. 🚀 Leemos TODO en modo READ_ONLY para evitar bloqueos con la web
        conn_read = duckdb.connect(db_path, read_only=True)
        
        todas_columnas = [c[0] for c in conn_read.execute("DESCRIBE dim_jugadores_stats").fetchall()]
        cols_a_mantener = [
            f'"{c}"' for c in todas_columnas 
            if not (c.startswith("Rating") or c.startswith("Score") or c.endswith("Scale"))
        ]
        
        query_optimizada = f"SELECT {', '.join(cols_a_mantener)} FROM dim_jugadores_stats"
        df = conn_read.execute(query_optimizada).df() 
        
        # Extraemos también la tabla de equipos para no perderla
        try:
            df_equipos = conn_read.execute("SELECT * FROM dim_equipos_stats").df()
        except:
            df_equipos = pd.DataFrame()
            
        # 🚀 ¡Soltamos la base de datos para que la web siga funcionando!
        conn_read.close() 
        gc.collect()

        def asignar_mejor_posicion(row):
            pos_str = str(row.get('Primary position', ''))
            for pos_name, regex in mapa_posiciones.items():
                if __import__('re').search(regex, pos_str): return pos_name
            pos_str2 = str(row.get('Position', ''))
            for pos_name, regex in mapa_posiciones.items():
                if __import__('re').search(regex, pos_str2): return pos_name
            return 'Delantero'
            
        def atrapar_posiciones_secundarias(row):
            pos_str = str(row.get('Primary position', '')) + " " + str(row.get('Position', ''))
            pos_encontradas = [pos for pos, regex in mapa_posiciones.items() if __import__('re').search(regex, pos_str)]
            return pos_encontradas if pos_encontradas else ['Delantero']

        df['Pos_Estricta'] = df.apply(asignar_mejor_posicion, axis=1)
        df['Pos_Multiples'] = df.apply(atrapar_posiciones_secundarias, axis=1)

        COLS_META = {'Player', 'Team', 'Competition', 'League', 'Season', 'Position', 'Primary position', 
                     'Secondary position', 'Third position', 'Birth country', 'Foot', 'Contract expires', 
                     'Age', 'Matches played', 'Minutes played', 'Height', 'Weight', 'League_Weight', 'Wyscout id', 'Pos_Estricta', 'Pos_Multiples'}
        
        for col in df.columns:
            if col not in COLS_META and df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        col_num = [c for c in df.select_dtypes(include=[np.number]).columns if c not in COLS_META]
        METRICAS_INVERSAS = ['conceded', 'against', 'losses', 'turnovers', 'fouls', 'yellow', 'red', 'pérdidas', 'faltas', 'encajados']
        col_comp = 'Competition' if 'Competition' in df.columns else 'League'

        from backend.core.pandas import motor_escalado_unico, motor_calculo_ratings
        df = motor_escalado_unico(df, col_num, METRICAS_INVERSAS, ['Season', col_comp, 'Pos_Estricta'], False, 300)

        gc.collect()

        diccionarios_por_posicion = {
            'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral Derecho': estilos_lt, 'Lateral Izquierdo': estilos_lt,
            'Pivote': estilos_mcd, 'Interior': estilos_int, 'Medio': estilos_med, 'Mediapunta': estilos_mp,
            'Extremo Derecho': estilos_ext, 'Extremo Izquierdo': estilos_ext, 'Delantero': estilos_del
        }

        for pos_estricta, d_pos in diccionarios_por_posicion.items():
            mask = df['Pos_Multiples'].apply(lambda x: pos_estricta in x)
            if mask.any():
                df = motor_calculo_ratings(df, diccionarios=d_pos, mascara_posicion=mask)

        df.drop(columns=['Pos_Estricta', 'Pos_Multiples'], inplace=True, errors='ignore')

        # 3. 🚀 Escribimos en el archivo temporal libre de bloqueos
        if os.path.exists(db_temp):
            try: os.remove(db_temp)
            except: pass
            
        conn_write = duckdb.connect(db_temp)
        conn_write.execute("CREATE OR REPLACE TABLE dim_jugadores_stats AS SELECT * FROM df LIMIT 0")    
        chunk_size = 25000
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            conn_write.execute("INSERT INTO dim_jugadores_stats SELECT * FROM chunk")
            
        if not df_equipos.empty:
            conn_write.execute("CREATE OR REPLACE TABLE dim_equipos_stats AS SELECT * FROM df_equipos")
            
        conn_write.close()
        
        # 4. 🚀 Swap Atómico
        swap_exitoso = False
        for _ in range(5):
            try:
                os.replace(db_temp, db_path)
                swap_exitoso = True
                break
            except PermissionError:
                time.sleep(1)
                
        if not swap_exitoso:
            raise HTTPException(status_code=500, detail="ERROR CRÍTICO: Windows tiene bloqueada la base de datos. APAGA LA TERMINAL (Ctrl+C), BORRA EL ARCHIVO 'instance/scouting_analitica.duckdb' MANUALMENTE, INICIA LA TERMINAL Y VUELVE A EJECUTAR EL ETL.")
        
        t1 = time.time()
        return ETLResponse(status="ok", mensaje="Base de Datos curada exitosamente.", registros_insertados=len(df), tiempo_segundos=round(t1-t0, 2))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en curación: {str(e)}")

@app.get("/api/equipos")
def obtener_lista_equipos():
    """Devuelve la lista de todos los equipos únicos para el autocompletado del buscador"""
    try:
        with get_duckdb_conn() as conn:
            # Saca todos los nombres únicos de equipos ordenados alfabéticamente
            df = conn.execute("SELECT DISTINCT Team FROM dim_jugadores_stats WHERE Team IS NOT NULL ORDER BY Team").df()
            return df['Team'].tolist()
    except Exception as e:
        print(f"Error cargando equipos: {e}")
        return []

@app.post("/api/comparar_h2h")
async def comparar_h2h(payload: H2HRequest):
    try:
        with get_duckdb_conn() as conn:
            df_1 = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Player ILIKE ? ORDER BY Season DESC, \"Minutes played\" DESC LIMIT 1", [f"%{payload.jugador1}%"]).df()
            df_2 = conn.execute("SELECT * FROM dim_jugadores_stats WHERE Player ILIKE ? ORDER BY Season DESC, \"Minutes played\" DESC LIMIT 1", [f"%{payload.jugador2}%"]).df()
            
            if df_1.empty or df_2.empty: raise HTTPException(status_code=404, detail="Jugador no encontrado.")

            j1, j2 = df_1.iloc[0], df_2.iloc[0]
            
            metricas_candidatas = {
                "Acciones ofensivas p90": {"cols": ["Successful attacking actions per 90", "Attacking actions per 90"], "max": 10, "unit": ""},
                "Carreras progresivas p90": {"cols": ["Progressive runs per 90"], "max": 6, "unit": ""},
                "Pases precisos (%)": {"cols": ["Accurate passes, %"], "max": 100, "unit": "%"},
                "Duelos defensivos ganados": {"cols": ["Defensive duels won, %"], "max": 100, "unit": "%"},
                "Goles esperados (xG)": {"cols": ["xG per 90", "xG"], "max": 0.8, "unit": ""},
                "Intercepciones p90": {"cols": ["PAdj Interceptions", "Interceptions per 90"], "max": 8, "unit": ""}
            }
            
            cols_available = set(df_1.columns).intersection(set(df_2.columns))
            metricas_comparadas = []
            
            import pandas as pd
            for label, cfg in metricas_candidatas.items():
                col_found = next((c for c in cfg["cols"] if c in cols_available), None)
                if col_found:
                    val1 = float(j1[col_found]) if pd.notna(j1[col_found]) else 0.0
                    val2 = float(j2[col_found]) if pd.notna(j2[col_found]) else 0.0
                    metricas_comparadas.append({
                        "label": label, "valA": round(val1, 2), "valB": round(val2, 2),
                        "max": max(cfg["max"], val1 * 1.1, val2 * 1.1), "unit": cfg["unit"]
                    })
            
            ventajas_A = [m for m in metricas_comparadas if m['valA'] > (m['valB'] * 1.05)]
            ventajas_B = [m for m in metricas_comparadas if m['valB'] > (m['valA'] * 1.05)]
            
            if ventajas_A and ventajas_B:
                mejor_A = max(ventajas_A, key=lambda x: (x['valA'] - x['valB']) / max(x['valB'], 0.01))
                mejor_B = max(ventajas_B, key=lambda x: (x['valB'] - x['valA']) / max(x['valA'], 0.01))
                txt = f"Analizando el cara a cara, {j1['Player']} domina el registro de {mejor_A['label'].lower()}. Por contra, {j2['Player']} compensa la balanza imponiéndose claramente en {mejor_B['label'].lower()}, mostrando un perfil distinto."
            elif ventajas_A: txt = f"{j1['Player']} domina estadísticamente la comparativa de forma casi total."
            elif ventajas_B: txt = f"{j2['Player']} se impone con muchísima autoridad en este Cara a Cara."
            else: txt = f"Enfrentamiento tremendamente igualado. Ambos perfiles calcan prácticamente sus datos."

            return {
                "jugadorA": {"name": j1['Player'], "team": j1.get('Team', 'N/D'), "age": int(j1.get('Age', 0))},
                "jugadorB": {"name": j2['Player'], "team": j2.get('Team', 'N/D'), "age": int(j2.get('Age', 0))},
                "metricas": metricas_comparadas, "veredicto": txt
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

scheduler = BackgroundScheduler()
scheduler.add_job(func=escanear_mercado_background, trigger="interval", minutes=2)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())