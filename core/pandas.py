import pandas as pd
import numpy as np
import os
import duckdb
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text
from config.diccionarios import PESOS_LIGAS

# ============================================================
# CATÁLOGO
# ============================================================
DB_URI = 'sqlite:///instance/scouting_app.db'
db_engine = create_engine(DB_URI)

def obtener_catalogo_datos():
    """Consulta a SQLite instantánea para construir los menús de País, Liga y Temporada"""
    query = text("SELECT DISTINCT Pais_Liga as pais, Competition as liga, Season as temporada FROM dim_jugadores_stats")
    with db_engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_dict(orient='records')

def obtener_datos_sql(ligas=None, temporadas=None):
    """
    Extrae datos ultrarrápidos usando DuckDB (OLAP).
    Usa read_only=True para soportar múltiples usuarios concurrentes sin colas.
    """
    db_path = 'instance/scouting_analitica.duckdb'
    if not os.path.exists(db_path):
        db_path = 'scouting_analitica.duckdb' # Fallback
        if not os.path.exists(db_path):
            return pd.DataFrame()

    query = "SELECT * FROM dim_jugadores_stats WHERE 1=1"
    
    if ligas and len(ligas) > 0:
        ligas_str = ", ".join([f"'{str(l).replace(chr(39), '')}'" for l in ligas])
        # ⚡ FIX: Solo usamos Competition, ya que el ETL unificó todo bajo este nombre.
        query += f" AND Competition IN ({ligas_str})"
        
    if temporadas and len(temporadas) > 0:
        temps_str = ", ".join([f"'{str(t).replace(chr(39), '')}'" for t in temporadas])
        query += f" AND Season IN ({temps_str})"
        
    try:
        with duckdb.connect(db_path, read_only=True) as conn:
            df = conn.execute(query).df()
        return df
    except Exception as e:
        print(f"Error en DuckDB: {e}")
        return pd.DataFrame()

# ============================================================
# UTILIDADES
# ============================================================

def limpiar_numeros(serie):
    return pd.to_numeric(
        serie.astype(str).str.replace(',', '', regex=False).replace('-', '0'),
        errors='coerce'
    ).fillna(0)


# ============================================================
# CALCULAR OVERPERFORMERS
# Devuelve un dict de columnas nuevas — sin tocar df todavía
# ============================================================

def _cols_overperformers(df):
    """Devuelve {nombre_col: serie} sin modificar df."""
    cols = {}
    if 'Non-penalty goals per 90' in df.columns and 'xG per 90' in df.columns:
        cols['Finishing Efficiency p90'] = (
            df['Non-penalty goals per 90'].astype(float) - df['xG per 90'].astype(float)
        )
    elif 'Goals per 90' in df.columns and 'xG per 90' in df.columns:
        cols['Finishing Efficiency p90'] = (
            df['Goals per 90'].astype(float) - df['xG per 90'].astype(float)
        )
    else:
        cols['Finishing Efficiency p90'] = pd.Series(0.0, index=df.index)
    return cols

def _cols_nuevas_metricas(df):
    """Calcula todas las métricas compuestas y aplica Shrinkage Bayesiano para proteger la pureza estadística."""
    cols = {}    
    def bayesian_shrinkage(input_data, volumen_serie, k=20):
        porcentaje_serie = df[input_data] if isinstance(input_data, str) else input_data
        if 'Primary position' in df.columns:
            pos_col = df['Primary position'].fillna('Unknown')
            mean_val = porcentaje_serie.groupby(pos_col).transform('mean')
            mean_val = mean_val.fillna(porcentaje_serie.mean())
        else:
            mean_val = porcentaje_serie.mean()
        weight = volumen_serie / (volumen_serie + k)
        return (weight * porcentaje_serie) + ((1.0 - weight) * mean_val)
        
    partidos_90s = (df['Minutes played'].replace(0, np.nan) / 90.0).fillna(0)

    # 1. TUPLA MAGISTRAL (Original intacta)
    pares = [
        ('Aerial duels per 90',                  'Aerial duels won, %',                  'Aerial Duels Master', 20),
        ('Defensive duels per 90',               'Defensive duels won, %',               'Defensive Duels Master', 25),
        ('Passes per 90',                        'Accurate passes, %',                   'Passes Master', 150),
        ('Short / medium passes per 90',         'Accurate short / medium passes, %',    'Short Medium Passes Master', 100),
        ('Long passes per 90',                   'Accurate long passes, %',              'Long Passes Master', 30),
        ('Forward passes per 90',                'Accurate forward passes, %',           'Forward Passes Master', 40),
        ('Back passes per 90',                   'Accurate back passes, %',              'Back Passes Master', 30),
        ('Vertical passes per 90',               'Accurate vertical passes, %',          'Vertical Passes Master', 30),
        ('Progressive passes per 90',            'Accurate progressive passes, %',       'Progressive Passes Master', 30),
        ('Passes to final third per 90',         'Accurate passes to final third, %',    'Passes Final Third Master', 25),
        ('Passes to penalty area per 90',        'Accurate passes to penalty area, %',   'Passes Penalty Area Master', 15),
        ('Smart passes per 90',                  'Accurate smart passes, %',             'Smart Passes Master', 10),
        ('Through passes per 90',                'Accurate through passes, %',           'Through Passes Master', 10),
        ('Dribbles per 90',                      'Successful dribbles, %',               'Dribbles Master', 20),
        ('Offensive duels per 90',               'Offensive duels won, %',               'Offensive Duels Master', 30),
        ('Crosses per 90',                       'Accurate crosses, %',                  'Crosses Master', 15),
        ('Crosses from left flank per 90',       'Accurate crosses from left flank, %',  'Crosses Left Flank Master', 10),
        ('Crosses from right flank per 90',      'Accurate crosses from right flank, %', 'Crosses Right Flank Master', 10),
    ]
    
    for c_vol, c_efi, c_out, k_val in pares:
        if c_vol in df.columns and c_efi in df.columns:
            intentos_totales = df[c_vol] * partidos_90s
            eficacia_shrunk = bayesian_shrinkage(c_efi, intentos_totales, k=k_val)
            cols[c_efi] = eficacia_shrunk 
            cols[c_out] = df[c_vol] * (eficacia_shrunk / 100.0)

    # 2. MÉTRICAS DE TENDENCIA (Aíslan al jugador del volumen con los 'K' corregidos por la IA)
    pases_totales = df['Passes per 90'].replace(0, np.nan)
    vol_pases = (df['Passes per 90'] * partidos_90s).fillna(0)
    
    if 'Progressive passes per 90' in df.columns: cols['Progressive Tendency'] = bayesian_shrinkage((df['Progressive passes per 90'] / pases_totales) * 100, vol_pases, k=30)
    if 'Forward passes per 90' in df.columns: cols['Forward Tendency'] = bayesian_shrinkage((df['Forward passes per 90'] / pases_totales) * 100, vol_pases, k=30)
    if 'Passes to final third per 90' in df.columns: cols['Final Third Tendency'] = bayesian_shrinkage((df['Passes to final third per 90'] / pases_totales) * 100, vol_pases, k=30)
    if 'Smart passes per 90' in df.columns: cols['Smart Tendency'] = bayesian_shrinkage((df['Smart passes per 90'] / pases_totales) * 100, vol_pases, k=40)
    if 'Crosses per 90' in df.columns: cols['Cross Tendency'] = bayesian_shrinkage((df['Crosses per 90'] / pases_totales) * 100, vol_pases, k=35)
    if 'Long passes per 90' in df.columns: cols['Long Pass Tendency'] = bayesian_shrinkage((df['Long passes per 90'] / pases_totales) * 100, vol_pases, k=30)
        
    acciones_defensivas = df['Successful defensive actions per 90'].replace(0, np.nan)
    vol_def = (df['Successful defensive actions per 90'] * partidos_90s).fillna(0)
    
    if 'Defensive duels per 90' in df.columns: cols['Defensive Duel Tendency'] = bayesian_shrinkage((df['Defensive duels per 90'] / acciones_defensivas) * 100, vol_def, k=25)
    if 'Interceptions per 90' in df.columns: cols['Interception Tendency'] = bayesian_shrinkage((df['Interceptions per 90'] / acciones_defensivas) * 100, vol_def, k=25)

    # 🚀 NUEVO IA: Aerial Duel Tendency 
    if 'Aerial duels per 90' in df.columns and 'Aerial duels won, %' in df.columns:
        vol_aereo = (df['Aerial duels per 90'] * partidos_90s).fillna(0)
        cols['Aerial Duel Tendency'] = bayesian_shrinkage('Aerial duels won, %', vol_aereo, k=20)

    # 3. 🚀 FIX IA: True PAdj con Shrinkage
    if 'Team_Possession' in df.columns:
        poss = df['Team_Possession'].clip(35.0, 65.0)
        factor_def = 50.0 / (100.0 - poss)
        factor_of = 50.0 / poss

        if 'Defensive duels per 90' in df.columns:
            raw = df['Defensive duels per 90'] * factor_def
            cols['True PAdj Defensive Duels'] = bayesian_shrinkage(raw, vol_def, k=20)
        if 'Interceptions per 90' in df.columns:
            raw = df['Interceptions per 90'] * factor_def
            cols['True PAdj Interceptions'] = bayesian_shrinkage(raw, vol_def, k=20)
        if 'Progressive passes per 90' in df.columns:
            raw = df['Progressive passes per 90'] * factor_of
            cols['True PAdj Progressive Passes'] = bayesian_shrinkage(raw, vol_pases, k=25)
        if 'Successful defensive actions per 90' in df.columns:
            cols['True PAdj Def Actions'] = df['Successful defensive actions per 90'] * factor_def
        if 'Touches in box per 90' in df.columns:
            cols['True PAdj Touches in Box'] = df['Touches in box per 90'] * factor_of

    # 4. EXCEPCIONES AISLADAS
    if 'Goals per 90' in df.columns: cols['Goals per 90'] = bayesian_shrinkage('Goals per 90', partidos_90s, k=5)
    if 'Exits per 90' in df.columns: cols['Exits per 90'] = bayesian_shrinkage('Exits per 90', partidos_90s, k=10)
    if 'Save rate, %' in df.columns: cols['Save rate, %'] = bayesian_shrinkage('Save rate, %', partidos_90s * 4, k=25)

    if 'Goals per 90' in df.columns and 'xG per 90' in df.columns:
        raw_efficiency = df['Goals per 90'] - df['xG per 90']
        tiros_totales = df['Shots per 90'] * partidos_90s if 'Shots per 90' in df.columns else partidos_90s * 2 
        factor_shrinkage = tiros_totales.fillna(0) / (tiros_totales.fillna(0) + 30.0)
        cols['Finishing Efficiency p90'] = raw_efficiency * factor_shrinkage

    # 5. FIX AUDITORÍA: MÉTRICAS AVANZADAS "PRO"
    if 'xG per 90' in df.columns and 'Shots per 90' in df.columns:
        cols['xG per Shot'] = (df['xG per 90'] / df['Shots per 90'].replace(0, np.nan)).fillna(0)

    if 'Touches in box per 90' in df.columns and 'xG per 90' in df.columns:
        cols['Box Threat Index'] = df['Touches in box per 90'] * df['xG per 90']

    if 'Through passes per 90' in df.columns and 'Smart passes per 90' in df.columns and 'Accurate passes, %' in df.columns:
        intentos_arriesgados = df['Through passes per 90'] + df['Smart passes per 90']
        cols['Pass Risk Index'] = intentos_arriesgados / (df['Accurate passes, %'].replace(0, np.nan) / 100.0)

    if 'Fouls per 90' in df.columns and 'Defensive duels per 90' in df.columns:
        cols['Discipline Rate'] = (df['Fouls per 90'] / df['Defensive duels per 90'].replace(0, np.nan)).fillna(0)
        
    return cols

def nuevas_metricas(df, *args, **kwargs):
    extra = _cols_nuevas_metricas(df)
    if extra:
        df_extra = pd.DataFrame(extra, index=df.index).fillna(0)
        df_final = pd.concat([df, df_extra], axis=1)
        # Eliminamos columnas duplicadas quedándonos con la versión más reciente
        return df_final.loc[:, ~df_final.columns.duplicated(keep='last')].copy()
    return df

# ============================================================
# PREPARAR DATAFRAME  ← aquí estaban todos los warnings
# ============================================================

def preparar_dataframe(df):
    """
    ⚡ OPTIMIZACIÓN ETL: 
    El motor de Base de Datos ya ha pre-calculado las Acciones Exitosas y los Percentiles.
    Esta función ahora solo se asegura de que no haya nulos.
    """
    if df.empty: 
        return df
    return df.fillna(0).copy()


# FILTRAR POR POSICIÓN
def filtrar_por_posicion_real(df, regex_pos):
    """
    Filtra el DataFrame por la posición solicitada.
    Suma los porcentajes de todas las posiciones (Primaria, Secundaria, Terciaria) 
    que encajen en el Regex. Si el sumatorio total >= 25%, el jugador entra.
    """
    if regex_pos == '': 
        return df
        
    if 'Primary position' in df.columns and 'Secondary position, %' in df.columns:
        
        # 1. Comprobamos qué columnas encajan con la posición que buscamos
        m_prim_match = df['Primary position'].str.contains(regex_pos, regex=True, na=False)
        m_sec_match = df['Secondary position'].str.contains(regex_pos, regex=True, na=False)
        
        # 2. Extraemos los porcentajes numéricos
        pct_prim = pd.to_numeric(df.get('Primary position, %', 0), errors='coerce').fillna(0)
        pct_sec = pd.to_numeric(df.get('Secondary position, %', 0), errors='coerce').fillna(0)
        
        # 3. Sumamos los porcentajes SOLO de las columnas que han hecho "Match"
        total_pct = (m_prim_match.astype(float) * pct_prim) + (m_sec_match.astype(float) * pct_sec)
        
        # 4. Sumamos también la tercera posición si existe
        if 'Third position, %' in df.columns:
            m_third_match = df['Third position'].str.contains(regex_pos, regex=True, na=False)
            pct_third = pd.to_numeric(df['Third position, %'], errors='coerce').fillna(0)
            total_pct += (m_third_match.astype(float) * pct_third)
            
        # Fallback de seguridad
        m_fallback = df['Position'].str.contains(regex_pos, regex=True, na=False) & df['Primary position'].isna()

        # 5. Entra si es su posición primaria, o si la SUMA TOTAL de sus roles similares es >= 25%
        m_final = m_prim_match | (total_pct >= 25) | m_fallback
        
        return df[m_final].copy()
    
    elif 'Position' in df.columns:
        return df[df['Position'].str.contains(regex_pos, regex=True, na=False)].copy()
        
    return df


# PESOS DE LIGA
def obtener_peso_liga(nombre_liga):
    liga_str = str(nombre_liga)
    if liga_str in PESOS_LIGAS:
        return PESOS_LIGAS[liga_str]
    liga_lower = liga_str.lower()
    for key, weight in PESOS_LIGAS.items():
        if key.lower() in liga_lower:
            return weight
    return 0.50


# ETIQUETA PRO (perfil de scouting)
# ============================================================
# ============================================================

def calcular_etiqueta_pro(datos, arg2=25, arg3='N/D', matriz_ort=None, cohort_stats=None):
    """
    Motor de Etiquetado - Nivel Élite (Universalizado para cualquier división)
    """
    edad = int(arg2)
    if hasattr(datos, 'get') and pd.notna(datos.get('Age')):
        try: edad = int(float(datos.get('Age')))
        except: pass

    rating_visual = None
    if isinstance(datos, dict) and datos.get('Rating') is not None:
        try: rating_visual = int(float(datos.get('Rating')))
        except: pass

    ratings_dict = {}
    if isinstance(datos, dict):
        for k, v in datos.items():
            if k in ['Age', 'Rating', 'Competition', 'League']: continue
            try: ratings_dict[k.replace('Rating_', '')] = int(float(v))
            except: pass

    if not ratings_dict and rating_visual is None:
        return "Rendimiento Insuficiente"
    if not ratings_dict:
        ratings_dict = {'Global': rating_visual}

    es_portero = "Defensivo" in ratings_dict and "Distribuidor" in ratings_dict and len(ratings_dict) <= 3

    max_sub = max(ratings_dict.values())
    min_sub = min(ratings_dict.values())
    avg_sub = sum(ratings_dict.values()) / len(ratings_dict)
    diff = max_sub - min_sub

    rating_absoluto = rating_visual if rating_visual is not None else max_sub

    if cohort_stats and cohort_stats.get('valido', False):
        p95 = cohort_stats.get('p95', 94)
        p85 = cohort_stats.get('p85', 90)
        u_gen_19, u_gen_21 = max(94, min(96, p95)), max(95, min(97, p95 + 1))
        u_won_21 = max(90, min(93, p85))
        u_gen_23 = max(96, min(98, p95 + 2))
        u_elite_min, u_elite_max = max(90, min(92, p85)), max(94, min(96, p95))
        u_especialista = max(92, min(94, p95 - 1))
    else:
        u_gen_19, u_gen_21, u_won_21, u_gen_23 = 94, 95, 90, 96
        u_elite_min, u_elite_max, u_especialista = 90, 94, 92

    # 1. JÓVENES
    if edad <= 19 and rating_absoluto >= u_gen_19: return "Talento Generacional"
    elif edad <= 21 and rating_absoluto >= u_gen_21: return "Talento Generacional"
    elif edad <= 21 and rating_absoluto >= u_won_21: return "Wonderkid"
    elif edad <= 23 and rating_absoluto >= u_gen_23: return "Talento Generacional"
    elif edad <= 23 and rating_absoluto >= 85: return "Gran Prospecto"
    elif edad <= 23 and rating_absoluto >= 80: return "Talento Emergente"

    # 2. PORTEROS
    if es_portero:
        if min_sub >= (u_elite_min - 8) and max_sub >= (u_elite_max - 2): return "Élite de la Categoría"
        if max_sub >= 88 and min_sub < 55 and diff >= 25: return "Perfil Polarizado"
        if max_sub >= u_especialista - 2 and diff >= 15: return "Especialista Táctico"
        if diff <= 12 and avg_sub >= 78: return "Perfil Armónico"
        if rating_absoluto >= 72: return "Titular de Garantías"
        if rating_absoluto >= 65: return "Jugador de Sistema"
        return "Perfil de Rotación"

    # 3. PERFILES TÁCTICOS SENIOR
    if min_sub >= u_elite_min and max_sub >= u_elite_max:
        return "Élite de la Categoría"
    if max_sub >= 90 and min_sub < 60 and diff >= 25:
        return "Perfil Polarizado"
    if max_sub >= u_especialista and diff >= 12:
        return "Especialista Táctico"
    if diff <= 7 and avg_sub >= 80:
        return "Perfil Armónico"

    # 4. SOLUCIÓN UNIVERSAL (Cualquier división)
    if rating_absoluto >= 82:
        return "Rendimiento Dominante"
    if rating_absoluto >= 75:
        return "Titular de Garantías"
    if rating_absoluto >= 65:
        return "Jugador de Sistema"
    if rating_absoluto >= 55:
        return "Perfil de Rotación"
    return "Rendimiento Insuficiente"

from config.diccionarios import estilos_gk, estilos_cb, estilos_lt, estilos_mcd, estilos_int, estilos_mp, estilos_ext, estilos_del
import pandas as pd

def calcular_mejor_rol_vectorizado(row, posicion):
    """
    Calcula dinámicamente cuál es el mejor rol táctico de un jugador.
    Utiliza los Ratings precalculados (percentiles) para que la comparación sea justa y precisa.
    """
    # 1. Intentar usar los percentiles exactos ya calculados por el algoritmo
    ratings = {col.replace('Rating_', ''): float(row[col]) for col in row.index if isinstance(col, str) and col.startswith('Rating_') and col != 'Rating_Fit'}
    
    if ratings:
        # Devuelve la clave (el estilo) con la puntuación más alta
        return max(ratings, key=ratings.get)
        
    # 2. Fallback: Cálculo en bruto si se llama desde otra función antigua
    mapa_estilos = {
        'Portero': estilos_gk, 'Central': estilos_cb, 'Lateral': estilos_lt,
        'Pivote': estilos_mcd, 'Interior': estilos_int, 'Mediapunta': estilos_mp,
        'Extremo': estilos_ext
    }
    estilos = mapa_estilos.get(posicion.split(' ')[0], estilos_del)
    
    mejor_rol = "N/D"
    mejor_score = -1
    
    for nombre_estilo, pesos in estilos.items():
        if nombre_estilo == 'Personalizado': continue
        
        score = sum(float(row.get(var, 0)) * peso for var, peso in pesos.items() if pd.notna(row.get(var, 0)))
        if score > mejor_score:
            mejor_score = score
            mejor_rol = nombre_estilo
            
    return mejor_rol

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

def generar_matriz_ortogonalidad(d_estilos):
    """
    Calcula la matriz de solapamiento (ortogonalidad) entre estilos tácticos
    usando la similitud del coseno sobre los pesos de sus métricas.
    """
    estilos_validos = {k: v for k, v in d_estilos.items() if k != 'Personalizado'}
    if not estilos_validos:
        return pd.DataFrame()
        
    metricas = set()
    for pesos in estilos_validos.values():
        metricas.update(pesos.keys())
    metricas = list(metricas)
    
    nombres = list(estilos_validos.keys())
    vectores = []
    for nombre in nombres:
        vectores.append([estilos_validos[nombre].get(m, 0.0) for m in metricas])
        
    sim = cosine_similarity(vectores)
    return pd.DataFrame(sim, index=nombres, columns=nombres)

# =====================================================================
# 🧠 MOTOR MATEMÁTICO ÚNICO (SINGLE SOURCE OF TRUTH)
# =====================================================================

def motor_escalado_unico(df, col_num, metricas_inversas, agrupar_por=None, usar_pesos_liga=True, min_minutos=0):
    """
    Calcula todos los percentiles de golpe (Vectorizado) para evitar la fragmentación de Pandas.
    """
    df_calc = df.copy()
    league_w = df_calc['League_Weight'].fillna(1.0) if usar_pesos_liga and 'League_Weight' in df_calc.columns else 1.0
    mask_validos = df_calc['Minutes played'] >= min_minutos
    nuevas_columnas = {}
    
    for c in col_num:
        clean_c_lower = str(c).lower()
        es_inversa = any(kw in clean_c_lower for kw in metricas_inversas)
        
        if es_inversa:
            val_calc = df_calc[c] / league_w
        else:
            val_calc = df_calc[c] * league_w
            
        # Creamos una serie vacía para llenarla solo donde los minutos son válidos
        serie_rank = pd.Series(np.nan, index=df_calc.index)
        
        if agrupar_por:
            # Agrupamos pasando la lista de columnas reales del dataframe
            grupos = [df_calc[g] for g in agrupar_por]
            serie_rank.loc[mask_validos] = val_calc.loc[mask_validos].groupby(grupos).rank(pct=True, ascending=not es_inversa) * 100
        else:
            serie_rank.loc[mask_validos] = val_calc.loc[mask_validos].rank(pct=True, ascending=not es_inversa) * 100
            
        # Guardamos la serie en el diccionario
        nuevas_columnas[f"{c} Scale"] = serie_rank        
    df_new = pd.DataFrame(nuevas_columnas, index=df_calc.index)
    df_calc = pd.concat([df_calc, df_new], axis=1)
    
    return df_calc


def motor_calculo_ratings(df, diccionarios, mascara_posicion=None, aplicar_peso_liga=False):
    """
    ÚNICA función de la plataforma para aplicar los pesos tácticos y calcular el Rating (1-99).
    🌟 MODIFICADO: Ahora genera Notas PURAS. El jugador se compara al 100% solo con su liga.
    La penalización por nivel de liga solo se aplica "en vivo" en el buscador.
    """
    df_calc = df.copy()
    
    if mascara_posicion is None:
        mascara_posicion = pd.Series(True, index=df_calc.index)

    # 🌟 PARCHE DE COHERENCIA GK: Si faltan las Master de Pases, usamos las métricas crudas
    # Esto evita el falso "99" en distribución de porteros como José Sá
    for col_master, col_cruda_vol, col_cruda_pct in [
        ('Passes Master Scale', 'Passes per 90 Scale', 'Accurate passes, % Scale'),
        ('Long Passes Master Scale', 'Long passes per 90 Scale', 'Accurate long passes, % Scale'),
        ('Short Medium Passes Master Scale', 'Passes per 90 Scale', 'Accurate passes, % Scale') 
    ]:
        if col_master not in df_calc.columns:
            if col_cruda_vol in df_calc.columns and col_cruda_pct in df_calc.columns:
                df_calc[col_master] = df_calc[[col_cruda_vol, col_cruda_pct]].mean(axis=1).fillna(50)
            else:
                df_calc[col_master] = 50.0

    # 🧮 CÁLCULO DE RATINGS
    for est, vars_est in diccionarios.items():
        if est == 'Personalizado': continue
        
        suma_est = pd.Series(0.0, index=df_calc[mascara_posicion].index)
        peso_aplicado = 0
        
        for v, p in vars_est.items():
            clean_v = str(v).replace(' Scale', '').replace(' Master', '').strip()
            col_target = f"{clean_v} Scale"
            
            if col_target in df_calc.columns:
                suma_est += df_calc.loc[mascara_posicion, col_target] * p
                peso_aplicado += p
            elif clean_v in df_calc.columns:
                suma_est += df_calc.loc[mascara_posicion, clean_v] * p
                peso_aplicado += p
                
        if peso_aplicado > 0:
            nota_base = suma_est / peso_aplicado
            
            # 🚀 LÓGICA PURA: Guardamos el rendimiento real (1-99). 
            # ¡Se acabó el castigo permanente a los jugadores de categorías inferiores!
            df_calc.loc[mascara_posicion, f'ScoreFloat_{est}'] = nota_base
            df_calc.loc[mascara_posicion, f'Rating_{est}'] = nota_base.clip(1, 99).round().astype('Int64')
        else:
            df_calc.loc[mascara_posicion, f'ScoreFloat_{est}'] = np.nan
            df_calc.loc[mascara_posicion, f'Rating_{est}'] = np.nan
            
    return df_calc