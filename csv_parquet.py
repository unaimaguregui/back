import os
import duckdb
from pathlib import Path

TEMPORADAS_ACTIVAS = ["2026", "26-27"] 

DIR_JUGADORES_CSV = Path("Data")
DIR_EQUIPOS_CSV = Path("Data_Teams")
DIR_JUGADORES_PARQUET = Path("Data_Parquet/Jugadores")
DIR_EQUIPOS_PARQUET = Path("Data_Parquet/Equipos")

# ==========================================
# 🌍 EL GRAN DICCIONARIO MUNDIAL DE LIGAS (ACTUALIZADO)
# ==========================================
MAPEO_PAISES = {
    # --- NUEVAS LIGAS AÑADIDAS ---
    "2. Bundesliga": "Alemania",
    "Besta-Deild Karla": "Islandia",
    "Besta-deild karla": "Islandia",
    "Bolivian Primera Division": "Bolivia",
    "Bolivian LFPB": "Bolivia",
    "Brasileirao": "Brasil",
    "Brasileirão": "Brasil",
    "Challenger Pro League": "Bélgica",
    "Czech First League": "República Checa",
    "Frauen-Bundesliga": "Alemania",
    "Liga F": "España",
    "Liga Profesional Argentina": "Argentina",
    "Ligue 3": "Francia",
    "Mexican U21 League": "México",
    "Northern Super League": "Canadá",
    "NWSL": "Estados Unidos",
    "Paraguayan Division Profesional": "Paraguay",
    "Premiere Ligue": "Francia",
    "Qatari Second Division": "Catar",
    "Romanian Liga 1": "Rumania",
    "Segunda Division": "España",
    "Slovak 1. Liga": "Eslovaquia",
    "South Africa PSL": "Sudáfrica",
    "Super League Greece": "Grecia",
    "USL League One": "Estados Unidos",
    "USL Super League": "Estados Unidos",
    "Venezuelan Primera Division": "Venezuela",
    "Virsliga": "Letonia",
    "Vrouwen Eredivisie": "Países Bajos",
    "World Cup": "Internacional", # Lo mandamos a Internacional a propósito

    # --- LIGAS ANTERIORES ---
    "1. HNL": "Croacia",
    "Bundesliga": "Alemania", 
    "2. HNL": "Croacia",
    "3. Liga": "Alemania",
    "A-League Men": "Australia",
    "Albanian Kategoria Superiore": "Albania",
    "Allsvenskan": "Suecia",
    "Andorra Primera Divisió": "Andorra",
    "Argentina Copa de la Liga": "Argentina",
    "Argentina LPF": "Argentina",
    "Argentina Primera Nacional": "Argentina",
    "Argentina Reserve League": "Argentina",
    "Armenian Premier League": "Armenia",
    "Australian NPLs": "Australia",
    "Austrian 2. Liga": "Austria",
    "Austrian Bundesliga": "Austria",
    "Azeri Birinci Dasta": "Azerbaiyán",
    "Azeri Premyer Liqa": "Azerbaiyán",
    "BRI Liga 1": "Indonesia",
    "Bahrain Premier League": "Baréin",
    "Belarusian 1. Division": "Bielorrusia",
    "Belarusian Premier League": "Bielorrusia",
    "Belarusian Reserve League": "Bielorrusia",
    "Belgian First Division B": "Bélgica",
    "Belgian Pro League": "Bélgica",
    "Bosnian Premier League": "Bosnia y Herzegovina",
    "Botola Pro": "Marruecos",
    "Brazil Serie B": "Brasil",
    "Brazil Serie C": "Brasil",
    "Bulgarian First League": "Bulgaria",
    "Cambodian Premier League": "Camboya",
    "Campeonato de Portugal": "Portugal",
    "Canadian Premier League": "Canadá",
    "Capital Territory NPL": "Australia",
    "Championship": "Inglaterra",
    "Chilean Primera B": "Chile",
    "Chilean Primera Division": "Chile",
    "Chilean Primera División": "Chile",
    "China League One": "China",
    "China League Two": "China",
    "Chinese Super League": "China",
    "Colombian Primera A": "Colombia",
    "Colombian Torneo BetPlay": "Colombia",
    "Costa Rican Primera Division": "Costa Rica",
    "Costa Rican Primera División": "Costa Rica",
    "Cyprus 1. Division": "Chipre",
    "Cyprus 2. Division": "Chipre",
    "Czech 1. Liga U19": "República Checa",
    "Czech FNL": "República Checa",
    "Czech Fortuna Liga": "República Checa",
    "Czech U17 League": "República Checa",
    "Danish 1. Division": "Dinamarca",
    "Danish 2. Division": "Dinamarca",
    "Danish 3. Division": "Dinamarca",
    "Danish U17 Division": "Dinamarca",
    "Danish U17 Ligaen": "Dinamarca",
    "Danish U19 Division": "Dinamarca",
    "Danish U19 Ligaen": "Dinamarca",
    "Ecuador Liga Pro": "Ecuador",
    "Eerste Divisie": "Países Bajos",
    "Egyptian Premier League": "Egipto",
    "Ekstraklasa": "Polonia",
    "El Salvador Primera Division": "El Salvador",
    "El Salvador Primera División": "El Salvador",
    "Eliteserien": "Noruega",
    "English National League North South": "Inglaterra", 
    "English National League": "Inglaterra",
    "English Non-League Premier Division - Step 7": "Inglaterra",
    "Eredivisie": "Países Bajos",
    "Erovnuli Liga 2": "Georgia",
    "Erovnuli Liga": "Georgia",
    "Estonia Meistriliiga": "Estonia",
    "Estonian Esiliiga A": "Estonia",
    "Ettan": "Suecia",
    "Faroe Islands Meistaradeildin": "Islas Feroe",
    "French National 1": "Francia",
    "Greek Super League 2": "Grecia",
    "Greek Super League": "Grecia",
    "Greek U19 Super League": "Grecia",
    "Guatemalan Liga Nacional": "Guatemala",
    "Honduran Liga Nacional": "Honduras",
    "Hong Kong Premier League": "Hong Kong",
    "Iceland 1. Deild": "Islandia",
    "Indian Super League": "India",
    "Irish First Division": "Irlanda",
    "Irish Premier Division": "Irlanda",
    "J1": "Japón",
    "J2": "Japón",
    "J3": "Japón",
    "Jordan Pro League": "Jordania",
    "K League 1": "Corea del Sur",
    "K League 2": "Corea del Sur",
    "K3 League": "Corea del Sur",
    "K4 League": "Corea del Sur",
    "Kazakh 1. Division": "Kazajistán",
    "Kazakh 2. Division": "Kazajistán",
    "Kazakh Premier League": "Kazajistán",
    "Kazakh U16 League": "Kazajistán",
    "Kazakh U17 League": "Kazajistán",
    "Kazakh U18 League": "Kazajistán",
    "Kosovo Superliga": "Kosovo",
    "Kyrgyz Premier League": "Kirguistán",
    "La Liga 2": "España",
    "La Liga": "España",
    "Latvian 1. Liga": "Letonia",
    "Latvian Virsliga": "Letonia",
    "League One": "Inglaterra",
    "League Two": "Inglaterra",
    "Liga Leumit": "Israel",
    "Liga MX": "México",
    "Liga de Expansion MX": "México",
    "Liga de Expansión MX": "México",
    "Ligat ha'Al": "Israel",
    "Ligue 1": "Francia",
    "Ligue 2": "Francia",
    "Lithuanian 1 Lyga": "Lituania",
    "Lithuanian A Lyga": "Lituania",
    "Luxembourg National Division": "Luxemburgo",
    "MLS Next Pro": "Estados Unidos",
    "MLS": "Estados Unidos",
    "Malaysian Super League": "Malasia",
    "Malta Challenge League": "Malta",
    "Malta Premier League": "Malta",
    "Mexican U17 League": "México",
    "Mexican U18 League": "México",
    "Mexican U19 League": "México",
    "Mexican U23 League": "México",
    "Moldovan Super Liga": "Moldavia",
    "Montenegro First League": "Montenegro",
    "Montenegro Second League": "Montenegro",
    "NB I": "Hungría",
    "NB II": "Hungría",
    "NCAA D2": "Estados Unidos",
    "NCAA D3": "Estados Unidos",
    "New South Wales NPL": "Australia",
    "New Zealand National League": "Nueva Zelanda",
    "Nicaragua Primera Division": "Nicaragua",
    "Nigerian Creative Championship": "Nigeria",
    "North Macedonia First League": "Macedonia del Norte",
    "Northern Irish Premiership": "Irlanda del Norte",
    "Norwegian 2. Division": "Noruega",
    "OBOS Ligaen": "Noruega",
    "Panama LPF": "Panamá",
    "Paraguay Division Profesional": "Paraguay",
    "Peruvian Liga 1": "Perú",
    "Polish I Liga": "Polonia",
    "Polish II Liga": "Polonia",
    "Portuguese Juniores U17": "Portugal",
    "Portuguese Juniores U19": "Portugal",
    "Portuguese Júniores U17": "Portugal",
    "Portuguese Júniores U19": "Portugal",
    "Portuguese Liga 3": "Portugal",
    "Portuguese Liga Revelacao Sub 23": "Portugal",
    "Portuguese Liga Revelação Sub 23": "Portugal",
    "Portuguese Segunda Liga": "Portugal",
    "Premier League 2": "Inglaterra",
    "Premier League": "Inglaterra",
    "Primavera 1": "Italia",
    "Primeira Liga": "Portugal",
    "Primera RFEF": "España",
    "Qatari Stars League": "Catar",
    "Queensland NPL": "Australia",
    "Queensland Premier League": "Australia",
    "Regionalliga": "Alemania",
    "Romanian Liga Elitelor U17": "Rumania",
    "Romanian Liga II": "Rumania",
    "Romanian Liga Tineret U18": "Rumania",
    "Romanian Superliga": "Rumania",
    "Russian First League": "Rusia",
    "Russian Premier League": "Rusia",
    "Saudi Division 1": "Arabia Saudita",
    "Saudi Pro League": "Arabia Saudita",
    "Scottish Championship": "Escocia",
    "Scottish League One": "Escocia",
    "Scottish League Two": "Escocia",
    "Scottish Premiership": "Escocia",
    "Segunda RFEF": "España",
    "Serbian Prva Liga": "Serbia",
    "Serbian Super Liga": "Serbia",
    "Serbian U17 League": "Serbia",
    "Serbian U19 League": "Serbia",
    "Serie A": "Italia",
    "Serie B": "Italia",
    "Serie C": "Italia",
    "Serie D - Girone A": "Italia",
    "Serie D - Girone B": "Italia",
    "Serie D - Girone C": "Italia",
    "Serie D - Girone D": "Italia",
    "Serie D - Girone E": "Italia",
    "Serie D - Girone F": "Italia",
    "Serie D - Girone G": "Italia",
    "Serie D - Girone H": "Italia",
    "Singapore Premier League": "Singapur",
    "Slovak 2. Liga": "Eslovaquia",
    "Slovak Super Liga": "Eslovaquia",
    "Slovak U19 League": "Eslovaquia",
    "Slovenian 1. SNL": "Eslovenia",
    "Slovenian 2. SNL": "Eslovenia",
    "South African PSL": "Sudáfrica",
    "South Australia NPL": "Australia",
    "South Australia State League 1": "Australia",
    "Super Lig": "Turquía",
    "Süper Lig": "Turquía",
    "Superettan": "Suecia",
    "Superliga": "Europa", 
    "Swiss 1. Liga Classic": "Suiza",
    "Swiss 1. Liga Promotion": "Suiza",
    "Swiss Challenge League": "Suiza",
    "Swiss Super League": "Suiza",
    "Swiss U17 Elite": "Suiza",
    "Swiss U19 Elite": "Suiza",
    "Thai League 1": "Tailandia",
    "Thai League 2": "Tailandia",
    "Tunisia Ligue 1": "Túnez",
    "Turkish 1. Lig": "Turquía",
    "Tweede Divisie": "Países Bajos",
    "U17 Bundesliga": "Alemania",
    "U19 Bundesliga": "Alemania",
    "UAE Pro League": "Emiratos Árabes Unidos",
    "USL Championship": "Estados Unidos",
    "Ukrainian Persha Liga": "Ucrania",
    "Ukrainian Premier League": "Ucrania",
    "Ukrainian U19 League": "Ucrania",
    "Uruguay Primera Division": "Uruguay",
    "Uruguay Primera División": "Uruguay",
    "Uzbek Super League": "Uzbekistán",
    "V.League 1": "Vietnam",
    "Veikkausliiga": "Finlandia",
    "Victoria NPL": "Australia",
    "Welsh Premier League": "Gales",
    "Western Australia NPL": "Australia",
    "Ykkonen": "Finlandia",
    "Ykkosliiga": "Finlandia",
    "Ykkönen": "Finlandia",
    "Ykkösliiga": "Finlandia"
}

def clasificar_pais(nombre_archivo: str) -> str:
    """Busca en el diccionario a qué país pertenece la liga.
    Ordena las llaves por longitud para que 'La Liga 2' se detecte antes que 'La Liga'."""
    # Ordenamos de mayor a menor longitud para evitar pisar nombres cortos
    claves_ordenadas = sorted(MAPEO_PAISES.keys(), key=len, reverse=True)
    
    for liga in claves_ordenadas:
        if nombre_archivo.startswith(liga):
            return MAPEO_PAISES[liga]
            
    return "Internacional" # Por si se cuela algún archivo desconocido

def convertir_csv_a_parquet(csv_path: Path, parquet_path: Path):
    """Convierte un CSV a Parquet hipercomprimido usando DuckDB."""
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    
    csv_str = str(csv_path).replace("\\", "/")
    parq_str = str(parquet_path).replace("\\", "/")
    
    query = f"""
        COPY (SELECT * FROM read_csv_auto('{csv_str}', header=True)) 
        TO '{parq_str}' 
        (FORMAT PARQUET, COMPRESSION ZSTD);
    """
    
    with duckdb.connect(':memory:') as conn:
        conn.execute(query)

def procesar_carpeta(dir_origen: Path, dir_destino: Path, tipo_dato: str):
    print(f"\n🔍 Analizando carpeta de {tipo_dato} ({dir_origen})...")
    
    if not dir_origen.exists():
        print(f"⚠️ La carpeta {dir_origen} no existe. Saltando...")
        return

    archivos_procesados = 0
    archivos_saltados = 0

    for csv_path in dir_origen.rglob("*.csv"):
        nombre_archivo = csv_path.name
        
        # Obtenemos el país cruzándolo con el gran diccionario
        pais = clasificar_pais(nombre_archivo)
        
        # 1. ¿Es una temporada activa?
        es_activa = any(temp in nombre_archivo for temp in TEMPORADAS_ACTIVAS)
        
        # Construimos la ruta: Data_Parquet / Jugadores / España / La Liga 25-26.parquet
        parquet_path = dir_destino / pais / csv_path.with_suffix('.parquet').name
        
        # 2. ¿Ya existe el Parquet histórico?
        existe_parquet = parquet_path.exists()
        
        if existe_parquet and not es_activa:
            # Es histórico y ya está procesado -> LO SALTAMOS
            archivos_saltados += 1
        else:
            # Es temporada actual o archivo nuevo
            print(f"   ⚙️ Procesando: [{pais}] {nombre_archivo} ...")
            try:
                convertir_csv_a_parquet(csv_path, parquet_path)
                archivos_procesados += 1
            except Exception as e:
                print(f"   ❌ Error con {nombre_archivo}: {e}")

    print(f"✅ {tipo_dato}: {archivos_procesados} actualizados | ⏭️ {archivos_saltados} históricos saltados.")

if __name__ == "__main__":
    print("🚀 INICIANDO ETL: CSV a PARQUET (Clasificación Automática por Países)")    
    procesar_carpeta(DIR_JUGADORES_CSV, DIR_JUGADORES_PARQUET, "JUGADORES")
    procesar_carpeta(DIR_EQUIPOS_CSV, DIR_EQUIPOS_PARQUET, "EQUIPOS")
    print("\n🎉 ¡Todos los datos están clasificados y listos en formato Parquet!")