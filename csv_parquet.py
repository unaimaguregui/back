import os
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. IMPORTAMOS TUS MATEMÁTICAS (Desde tu Backend)
# ==========================================
from core.pandas import _cols_nuevas_metricas, motor_escalado_unico, motor_calculo_ratings
from config.diccionarios import (
    estilos_gk, estilos_cb, estilos_lt, estilos_mcd, 
    estilos_int, estilos_mp, estilos_ext, estilos_del, estilos_med, PESOS_LIGAS
)

# ==========================================
# 2. CONFIGURACIÓN DE CARPETAS Y DICCIONARIO
# ==========================================
TEMPORADAS_ACTIVAS = ["26-27", "2026"] 

DIR_JUGADORES_CSV = Path("Data")
DIR_EQUIPOS_CSV = Path("Data_Teams")

DIR_JUGADORES_PARQUET = Path("Data_Parquet/Jugadores")
DIR_EQUIPOS_PARQUET = Path("Data_Parquet/Equipos")

MAPEO_ORIGINAL = {
    "Bundesliga": "Alemania", "2. Bundesliga": "Alemania", "3. Liga": "Alemania", "Regionalliga": "Alemania", "U17 Bundesliga": "Alemania", "U19 Bundesliga": "Alemania", "Regionalliga Nord": "Alemania", "1. HNL": "Croacia", "2. HNL": "Croacia", "HNL": "Croacia",
    "La Liga": "España", "La Liga 2": "España", "Primera RFEF": "España", "Segunda RFEF": "España","Premier League": "Inglaterra", "Championship": "Inglaterra", "League One": "Inglaterra", "League Two": "Inglaterra", "English National League": "Inglaterra", "English National League North South": "Inglaterra", "English Non-League Premier Division - Step 7": "Inglaterra", "Premier League 2": "Inglaterra",
    "Serie A": "Italia", "Serie B": "Italia", "Serie C": "Italia", "Serie D - Girone A": "Italia", "Serie D - Girone B": "Italia", "Serie D - Girone C": "Italia", "Serie D - Girone D": "Italia", "Serie D - Girone E": "Italia", "Serie D - Girone F": "Italia", "Serie D - Girone G": "Italia", "Serie D - Girone H": "Italia", "Primavera 1": "Italia",
    "Primeira Liga": "Portugal", "Portuguese Segunda Liga": "Portugal", "Portuguese Liga 3": "Portugal", "Campeonato de Portugal": "Portugal", "Portuguese Juniores U17": "Portugal", "Portuguese Juniores U19": "Portugal", "Portuguese Júniores U17": "Portugal", "Portuguese Júniores U19": "Portugal", "Portuguese Liga Revelacao Sub 23": "Portugal", "Portuguese Liga Revelação Sub 23": "Portugal",
    "MLS": "Estados Unidos", "MLS Next Pro": "Estados Unidos", "USL Championship": "Estados Unidos", "USL League 1": "Estados Unidos", "NCAA D1": "Estados Unidos", "NCAA D2": "Estados Unidos", "NCAA D3": "Estados Unidos", "Canadian Premier League": "Canadá",
    "Argentina Copa de la Liga": "Argentina", "Argentina LPF": "Argentina", "Argentina Primera Nacional": "Argentina", "Argentina Reserve League": "Argentina", "Brasileirao": "Brasil", "Brasileirão": "Brasil", "Brazil Serie B": "Brasil", "Brazil Serie C": "Brasil", "A-League Men": "Australia", "Australian NPLs": "Australia", "Capital Territory NPL": "Australia", "New South Wales NPL": "Australia", "Queensland NPL": "Australia", "Queensland Premier League": "Australia", "South Australia NPL": "Australia", "South Australia State League 1": "Australia", "Victoria NPL": "Australia", "Western Australia NPL": "Australia",
    "Liga MX": "México", "Liga de Expansion MX": "México", "Liga de Expansión MX": "México", "Mexican U17 League": "México", "Mexican U18 League": "México", "Mexican U19 League": "México", "Mexican U23 League": "México",
    "Colombian Primera A": "Colombia", "Colombian Torneo BetPlay": "Colombia", "Ligue 1": "Francia", "Ligue 2": "Francia", "French National 1": "Francia","Eredivisie": "Países Bajos", "Eerste Divisie": "Países Bajos", "Tweede Divisie": "Países Bajos", "Super Lig": "Turquía", "Süper Lig": "Turquía", "Turkish 1. Lig": "Turquía",
    "Allsvenskan": "Suecia", "Superettan": "Suecia", "Ettan": "Suecia", "Eliteserien": "Noruega", "OBOS Ligaen": "Noruega", "Norwegian 2. Division": "Noruega", "Veikkausliiga": "Finlandia", "Ykkonen": "Finlandia", "Ykkönen": "Finlandia", "Ykkosliiga": "Finlandia", "Ykkösliiga": "Finlandia",
    "Danish 1. Division": "Dinamarca", "Danish 2. Division": "Dinamarca", "Danish 3. Division": "Dinamarca", "Danish U17 Division": "Dinamarca", "Danish U17 Ligaen": "Dinamarca", "Danish U19 Division": "Dinamarca", "Danish U19 Ligaen": "Dinamarca",
    "Czech Fortuna Liga": "República Checa", "Czech FNL": "República Checa", "Czech 1. Liga U19": "República Checa", "Czech U17 League": "República Checa", "Slovak Super Liga": "Eslovaquia", "Slovak 2. Liga": "Eslovaquia", "Slovak U19 League": "Eslovaquia", "Ekstraklasa": "Polonia", "Polish I Liga": "Polonia", "Polish II Liga": "Polonia",
    "NB I": "Hungria", "NB II": "Hungria", "Russian Premier League": "Rusia", "Russian First League": "Rusia", "Ukrainian Premier League": "Ucrania", "Ukrainian Persha Liga": "Ucrania", "Ukrainian U19 League": "Ucrania", "Serbian Super Liga": "Serbia", "Serbian Prva Liga": "Serbia", "Serbian U17 League": "Serbia", "Serbian U19 League": "Serbia",
    "Romanian Superliga": "Rumanía", "Romanian Liga II": "Rumanía", "Romanian Liga Elitelor U17": "Rumanía", "Romanian Liga Tineret U18": "Rumanía", "Bulgarian First League": "Bulgaria", "Slovenian 1. SNL": "Eslovenia", "Slovenian 2. SNL": "Eslovenia", "Bosnian Premier League": "Bosnia", "North Macedonia First League": "Macedonia del Norte",
    "Montenegro First League": "Montenegro", "Montenegro Second League": "Montenegro", "Kosovo Superliga": "Kosovo", "Albanian Kategoria Superiore": "Albania", "Chinese Super League": "China", "China League One": "China", "China League Two": "China",
    "J1": "Japón", "J2": "Japón", "J3": "Japón", "K League 1": "Corea del Sur", "K League 2": "Corea del Sur", "K3 League": "Corea del Sur", "K4 League": "Corea del Sur", "Indian Super League": "India", "Thai League 1": "Tailandia", "Thai League 2": "Tailandia", "Malaysian Super League": "Malasia", "Singapore Premier League": "Singapur", "Hong Kong Premier League": "Hong Kong", "V.League 1": "Vietnam", "Cambodian Premier League": "Camboya", "BRI Liga 1": "Indonesia",
    "Saudi Pro League": "Arabia Saudita", "Saudi Division 1": "Arabia Saudita", "UAE Pro League": "Emiratos Árabes", "Qatari Stars League": "Catar", "Jordan Pro League": "Jordania", "Bahrain Premier League": "Baréin", "Ligat ha'Al": "Israel", "Liga Leumit": "Israel",
    "Austrian Bundesliga": "Austria", "Belgian Pro League": "Belgica", "Belgian First Division B": "Belgica", "Austrian 2. Liga": "Austria", "Swiss Super League": "Suiza", "Swiss Challenge League": "Suiza", "Swiss 1. Liga Promotion": "Suiza", "Swiss 1. Liga Classic": "Suiza", "Swiss U17 Elite": "Suiza", "Swiss U19 Elite": "Suiza",
    "Greek Super League": "Grecia", "Greek Super League 2": "Grecia", "Greek U19 Super League": "Grecia", "Cyprus 1. Division": "Chipre", "Cyprus 2. Division": "Chipre", "Irish Premier Division": "Irlanda", "Irish First Division": "Irlanda", "Northern Irish Premiership": "Irlanda del Norte", "Welsh Premier League": "Gales",
    "Scottish Premiership": "Escocia", "Scottish Championship": "Escocia", "Scottish League One": "Escocia", "Scottish League Two": "Escocia", "Luxembourg National Division": "Luxemburgo", "Malta Premier League": "Malta", "Malta Challenge League": "Malta", "Andorra Primera Divisió": "Andorra", "Andorra Primera Divisio": "Andorra",
    "Iceland 1. Deild": "Islandia", "Besta-deild karla": "Islandia", "Faroe Islands Meistaradeildin": "Islas Feroe", "Azeri Premyer Liqa": "Azerbaiyán", "Azeri Birinci Dasta": "Azerbaiyán", "Armenian Premier League": "Armenia", "Erovnuli Liga": "Georgia", "Erovnuli Liga 2": "Georgia", "Kazakh Premier League": "Kazajistán", "Kazakh 1. Division": "Kazajistán", "Kazakh 2. Division": "Kazajistán", "Kazakh U16 League": "Kazajistán", "Kazakh U17 League": "Kazajistán", "Kazakh U18 League": "Kazajistán",
    "Uzbek Super League": "Uzbekistán", "Kyrgyz Premier League": "Kirguistán", "Belarusian Premier League": "Bielorrusia", "Belarusian 1. Division": "Bielorrusia", "Belarusian Reserve League": "Bielorrusia", "Moldovan Super Liga": "Moldavia", "Estonia Meistriliiga": "Estonia", "Estonian Esiliiga A": "Estonia", "Latvian Virsliga": "Letonia", "Latvian 1. Liga": "Letonia", "Lithuanian A Lyga": "Lituania", "Lithuanian 1 Lyga": "Lituania",
    "Chilean Primera Division": "Chile", "Chilean Primera División": "Chile", "Chilean Primera B": "Chile", "Uruguay Primera Division": "Uruguay", "Uruguay Primera División": "Uruguay", "Paraguay Division Profesional": "Paraguay", "Peruvian Liga 1": "Perú", "Ecuador Liga Pro": "Ecuador", "Bolivian LFPB": "Bolivia",
    "Costa Rican Primera Division": "Costa Rica", "Costa Rican Primera División": "Costa Rica", "Guatemalan Liga Nacional": "Guatemala", "Honduran Liga Nacional": "Honduras", "El Salvador Primera Division": "El Salvador", "El Salvador Primera División": "El Salvador", "Panama LPF": "Panamá", "Nicaragua Primera Division": "Nicaragua",
    "New Zealand National League": "Nueva Zelanda", "South African PSL": "Sudáfrica", "Egyptian Premier League": "Egipto", "Botola Pro": "Marruecos", "Tunisia Ligue 1": "Túnez", "Nigerian Creative Championship": "Nigeria","Superliga": "Dinamarca_Serbia"
}

# Añadimos los faltantes por si acaso (Para evitar errores de clasificación)
FALTANTES = {
    "CHALLENGER PRO LEAGUE": "Bélgica", "CZECH FIRST LEAGUE": "República Checa", 
    "FRAUEN-BUNDESLIGA": "Alemania", "LIGA F": "España", "LIGA PROFESIONAL ARGENTINA": "Argentina",
    "LIGUE 3": "Francia", "MEXICAN U21 LEAGUE": "México", "NORTHERN SUPER LEAGUE": "Canadá", 
    "NWSL": "Estados Unidos", "PARAGUAYAN DIVISION PROFESIONAL": "Paraguay", "PREMIERE LIGUE": "Francia",
    "QATARI SECOND DIVISION": "Catar", "ROMANIAN LIGA 1": "Rumania", "SEGUNDA DIVISION": "España", 
    "SLOVAK 1. LIGA": "Eslovaquia", "SOUTH AFRICA PSL": "Sudáfrica", "SUPER LEAGUE GREECE": "Grecia",
    "USL LEAGUE ONE": "Estados Unidos", "USL SUPER LEAGUE": "Estados Unidos",
    "VENEZUELAN PRIMERA DIVISION": "Venezuela", "VIRSLIGA": "Letonia", "VROUWEN EREDIVISIE": "Países Bajos", 
    "WORLD CUP": "Internacional", "BESTA-DEILD KARLA": "Islandia"
}

MAPEO_PAISES = {k.upper(): v for k, v in MAPEO_ORIGINAL.items()}
MAPEO_PAISES.update(FALTANTES)

def obtener_pais_inteligente(csv_path: Path, carpeta_raiz: Path) -> str:
    carpeta_padre = csv_path.parent.name
    if csv_path.parent != carpeta_raiz:
        return carpeta_padre
        
    nombre_archivo = csv_path.name.upper()
    claves_ordenadas = sorted(MAPEO_PAISES.keys(), key=len, reverse=True)
    for liga in claves_ordenadas:
        if nombre_archivo.startswith(liga):
            return MAPEO_PAISES[liga]
            
    return "Internacional"

def procesar_jugadores():
    print("\n🏃‍♂️ PROCESANDO JUGADORES (Con Matemáticas)...")
    if not DIR_JUGADORES_CSV.exists():
        print(f"⚠️ No existe la carpeta {DIR_JUGADORES_CSV}")
        return

    archivos = list(DIR_JUGADORES_CSV.rglob("*.csv"))
    if not archivos:
        print("⚠️ No hay CSVs de jugadores.")
        return

    for csv_path in archivos:
        nombre = csv_path.stem
        pais = obtener_pais_inteligente(csv_path, DIR_JUGADORES_CSV)
        
        partes = nombre.rsplit(' ', 1)
        liga_sucia, temp = (partes[0], partes[1]) if len(partes) == 2 else (nombre, "Unknown")
        
        carpeta_destino = DIR_JUGADORES_PARQUET / pais
        parquet_path = carpeta_destino / f"{nombre}.parquet"
        
        es_activa = any(t in temp for t in TEMPORADAS_ACTIVAS)
        if parquet_path.exists() and not es_activa:
            continue

        print(f"⚙️  Calculando y Organizando: [{pais}] {nombre}...")
        try:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False)
            
            df = df.loc[:, ~df.columns.duplicated()].copy()
            df = df.reset_index(drop=True)
            
            df = df.assign(
                Pais_Liga=pais, Competition=liga_sucia, 
                Season=temp, League_Weight=PESOS_LIGAS.get(liga_sucia, 0.30)
            )
            df = df[~df['Player'].astype(str).str.contains(r'\[REF\]', na=False)].copy()

            COLS_STR = {'Player', 'Team', 'Team within selected timeframe', 'Position', 
                        'Primary position', 'Secondary position', 'Third position', 
                        'Competition', 'League', 'Birth country', 'Foot', 'Contract expires', 'Season', 'Pais_Liga', 'Wyscout id'}
            
            for col in df.columns:
                if col in COLS_STR:
                    df[col] = df[col].fillna("N/D").astype(str)
                else:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.', regex=False).str.replace('-', '0', regex=False), errors='coerce').fillna(0.0)

            extra_masters = _cols_nuevas_metricas(df)
            if extra_masters:
                df = pd.concat([df, pd.DataFrame(extra_masters, index=df.index).fillna(0.0)], axis=1)
                df = df.loc[:, ~df.columns.duplicated(keep='last')].copy()

            COLS_META = {'Player', 'Team', 'Competition', 'League', 'Season', 'Position', 'Primary position', 
                         'Secondary position', 'Third position', 'Birth country', 'Foot', 'Contract expires', 
                         'Age', 'Matches played', 'Minutes played', 'Height', 'Weight', 'League_Weight', 'Wyscout id', 'Pais_Liga'}
            col_num = [c for c in df.select_dtypes(include=[np.number]).columns if c not in COLS_META]
            METRICAS_INVERSAS = ['conceded', 'against', 'losses', 'turnovers', 'fouls', 'yellow', 'red', 'pérdidas', 'faltas', 'encajados']
            
            df = motor_escalado_unico(df, col_num, METRICAS_INVERSAS, None, True, 0)

            todos_los_estilos = {**estilos_gk, **estilos_cb, **estilos_lt, **estilos_mcd, **estilos_int, **estilos_mp, **estilos_ext, **estilos_del, **estilos_med}
            df = motor_calculo_ratings(df, diccionarios=todos_los_estilos, mascara_posicion=None, aplicar_peso_liga=True)

            carpeta_destino.mkdir(parents=True, exist_ok=True)
            df.to_parquet(parquet_path, engine='pyarrow', index=False, compression='zstd')

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

def procesar_equipos():
    print("\n🛡️ PROCESANDO EQUIPOS...")
    if not DIR_EQUIPOS_CSV.exists():
        print(f"⚠️ No existe la carpeta {DIR_EQUIPOS_CSV}")
        return

    archivos = list(DIR_EQUIPOS_CSV.rglob("*.csv"))
    for csv_path in archivos:
        nombre = csv_path.stem
        pais = obtener_pais_inteligente(csv_path, DIR_EQUIPOS_CSV)
        
        carpeta_destino = DIR_EQUIPOS_PARQUET / pais
        parquet_path = carpeta_destino / f"{nombre}.parquet"
        
        es_activa = any(t in nombre for t in TEMPORADAS_ACTIVAS)
        if parquet_path.exists() and not es_activa:
            continue

        print(f"⚙️  Organizando Equipo: [{pais}] {nombre}...")
        try:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False)
            df['Pais_Eq'] = pais
            
            COLS_STR_EQ = {'Team', 'Competition_Eq', 'Pais_Eq', 'Season', 'Match'}
            for col in df.columns:
                if col in COLS_STR_EQ:
                    df[col] = df[col].fillna("N/D").astype(str)
                else:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.', regex=False).str.replace('-', '0', regex=False), errors='coerce').fillna(0.0)

            carpeta_destino.mkdir(parents=True, exist_ok=True)
            df.to_parquet(parquet_path, engine='pyarrow', index=False, compression='zstd')
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO SUPER ETL: Clasificación Inteligente + Matemáticas + Parquet")
    procesar_jugadores()
    procesar_equipos()
    print("\n🎉 ¡ETL FINALIZADO! Tienes un Data Lake profesional listo para subir a GitHub.")