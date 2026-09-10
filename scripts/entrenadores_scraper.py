import requests
from bs4 import BeautifulSoup
import pandas as pd
import duckdb
import time
import re
import os
from datetime import datetime

# Headers avanzados para burlar el anti-bots de la Premier League
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}

# Diccionario con los IDs exactos corregidos (Croacia, Qatar, Sudáfrica, Hungría...)
MAPEO_TM = {
    "La Liga": "ES1",
    "Segunda Division": "ES2",
    "Premier League": "GB1",
    "Championship": "GB2",
    "League One": "GB3",
    "League Two": "GB4",
    "Serie A": "IT1",
    "Serie B": "IT2",
    "Serie C": "IT3A", 
    "Bundesliga": "L1",
    "2. Bundesliga": "L2",
    "3. Liga": "L3",
    "Ligue 1": "FR1",
    "Ligue 2": "FR2",
    "French National 1": "FR3",
    "Ligue 3": "FR3", 
    "Primeira Liga": "PO1",
    "Portuguese Segunda Liga": "PO2",
    "Eredivisie": "NL1",
    "Eerste Divisie": "NL2",
    "Brasileirao": "BRA1",
    "Brazil Serie B": "BRA2",
    "Liga Profesional Argentina": "AR1N",
    "Liga MX": "MEX1",
    "Liga de Expansion MX": "MEX2",
    "MLS": "MLS1",
    "MLS Next Pro": "MLNP",
    "USL Championship": "USL",
    "USL League One": "USL1",
    "Canadian Premier League": "CDN1",
    "Colombian Primera A": "COL1",
    "Chilean Primera Division": "CL1",
    "Ecuador Liga Pro": "EL1",
    "Paraguayan Division Profesional": "PAR1",
    "Peruvian Liga 1": "PER1",
    "Venezuelan Primera Division": "VEN1",
    "Bolivian Primera Division": "BOL1",
    "Belgian Pro League": "BE1",
    "Challenger Pro League": "BE2",
    "Austrian Bundesliga": "AT1",
    "Super Lig": "TR1",
    "Turkish 1. Lig": "TR2",
    "Russian Premier League": "RU1",
    "Scottish Premiership": "SC1",
    "Superliga": "DK1", 
    "Danish 1. Division": "DK2",
    "Allsvenskan": "SE1",
    "Eliteserien": "NO1",
    "Swiss Super League": "C1",
    "Swiss Challenge League": "C2",
    "Super League Greece": "GR1",
    "Ekstraklasa": "PL1",
    "1. HNL": "KR1",            # Corregido
    "Serbian Super Liga": "SER1",
    "Romanian Liga 1": "RO1",
    "NB I": "UNG1",              # Corregido
    "Slovak 1. Liga": "SLO1",
    "Czech First League": "TS1",
    "Besta-Deild Karla": "IS1",
    "Veikkausliiga": "FI1",
    "Ligat Ha'al": "ISR1",
    "Virsliga": "LET1",
    "J1": "JAP1",
    "J1 100 Year Vision League": "JAP1",
    "J2": "JAP2",
    "J3": "JAP3",
    "J2-J3 100 Year Vision League": "JAP3",
    "K League 1": "RSK1",
    "K League 2": "RSK2",
    "Chinese Super League": "CSL",
    "China League One": "CLO", # Corregido
    # "China League Two": "CSL3", # Corregido
    "A-League Men": "AUS1",
    "Saudi Pro League": "SA1",
    "Saudi Division 1": "SA2",
    "Qatari Stars League": "QSL",    # Corregido
    "Qatari Second Division": "QU2L", # Corregido
    "UAE Pro League": "UAE1",
    "Indian Super League": "IND1",
    "Thai League 1": "THA1",
    "Egyptian Premier League": "EGY1",
    "South Africa PSL": "SFA1",       # Corregido
}

def extraer_entrenadores_equipo(club_url, club_name, max_retries=3):
    historial_url = club_url.replace("startseite", "mitarbeiterhistorie")
    
    for intento in range(max_retries):
        try:
            response = requests.get(historial_url, headers=HEADERS, timeout=25)
            
            if response.status_code != 200:
                print(f"    ❌ Bloqueo HTTP {response.status_code} en {club_name}")
                return []

            soup = BeautifulSoup(response.content, "html.parser")
            entrenadores = []
            
            tablas = soup.find_all("table", class_="items")
            if not tablas: return []
                
            filas = tablas[0].find("tbody").find_all("tr", recursive=False)
            
            for fila in filas:
                cols = fila.find_all("td", recursive=False)
                
                # En el HTML real, la fila tiene 7 columnas principales
                if len(cols) >= 7:
                    # 1. Nombre exacto (Buscamos la clase 'hauptlink' que TM usa para el nombre principal)
                    celda_nombre = cols[0].find("td", class_="hauptlink")
                    if celda_nombre:
                        nombre = celda_nombre.text.strip()
                    else:
                        # Fallback por si la estructura cambia levemente
                        nombre = cols[0].find("a").text.strip() if cols[0].find("a") else "Desconocido"
                    
                    # 2. Fechas (Índices exactos del HTML: 2 es Appointed, 3 es End)
                    fecha_inicio_raw = cols[2].text.strip()
                    fecha_fin_raw = cols[3].text.strip()
                    
                    # Parseo de Fecha de Fin
                    if fecha_fin_raw in ["expected", "-", "expected ...", ""] or "expected" in fecha_fin_raw.lower():
                        fecha_fin_str = "2099-12-31" 
                    else:
                        parsed_end = pd.to_datetime(fecha_fin_raw, errors='coerce', dayfirst=True)
                        fecha_fin_str = parsed_end.strftime('%Y-%m-%d') if pd.notna(parsed_end) else "2099-12-31"
                        
                    # Parseo de Fecha de Inicio
                    parsed_start = pd.to_datetime(fecha_inicio_raw, errors='coerce', dayfirst=True)
                    fecha_inicio_str = parsed_start.strftime('%Y-%m-%d') if pd.notna(parsed_start) else None
                    
                    if fecha_inicio_str:
                        entrenadores.append({
                            "Team": club_name,
                            "Entrenador": nombre,
                            "Fecha_Inicio": fecha_inicio_str,
                            "Fecha_Fin": fecha_fin_str
                        })
                            
            if entrenadores:
                print(f"    ✅ {len(entrenadores)} entrenadores extraídos (Historial completo):")
                if len(entrenadores) > 5:
                    for e in entrenadores[:3]:
                        print(f"       👉 {e['Entrenador']}: {e['Fecha_Inicio']} hasta {e['Fecha_Fin']}")
                    print(f"       ... y {len(entrenadores)-5} históricos más ...")
                    for e in entrenadores[-2:]:
                        print(f"       👉 {e['Entrenador']}: {e['Fecha_Inicio']} hasta {e['Fecha_Fin']}")
                else:
                    for e in entrenadores:
                        print(f"       👉 {e['Entrenador']}: {e['Fecha_Inicio']} hasta {e['Fecha_Fin']}")
            else:
                print(f"    ⚠️ No se extrajeron entrenadores.")
                
            return entrenadores
            
        except requests.exceptions.Timeout:
            print(f"    ⏳ Timeout en {club_name}. Reintentando ({intento+1}/{max_retries})...")
            time.sleep(3)
        except Exception as e:
            print(f"    ❌ Error procesando {club_name}: {e}")
            return []
            
    print(f"    ❌ Transfermarkt no responde para {club_name}.")
    return []

def ejecutar_scraper():
    print("🚀 Iniciando Scraper de Entrenadores (Versión Acorazada a Parquet)...")
    todos_los_entrenadores = []
    
    for liga_nombre, tm_id in MAPEO_TM.items():
        print(f"\n==================================================")
        print(f"🏆 LIGA: {liga_nombre} (ID: {tm_id})")
        print(f"==================================================")
        liga_url = f"https://www.transfermarkt.com/wettbewerb/startseite/wettbewerb/{tm_id}"
        
        try:
            response = requests.get(liga_url, headers=HEADERS, timeout=20)
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code} en liga {liga_nombre}")
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            tabla_equipos = soup.find("table", class_="items")
            
            if not tabla_equipos: 
                print(f"⚠️ No se encontraron equipos. Puede que el ID {tm_id} haya cambiado.")
                continue
            
            filas_equipos = tabla_equipos.find("tbody").find_all("tr")
            
            for fila in filas_equipos:
                celda_nombre = fila.find("td", class_="hauptlink")
                if celda_nombre and celda_nombre.find("a"):
                    club_name = celda_nombre.find("a").text.strip()
                    club_href = celda_nombre.find("a")["href"]
                    club_url = f"https://www.transfermarkt.com{club_href}"
                    
                    print(f"  -> {club_name}")
                    historial = extraer_entrenadores_equipo(club_url, club_name)
                    
                    # Añadimos la Liga a los datos para mayor control
                    for h in historial:
                        h['Liga'] = liga_nombre
                        
                    todos_los_entrenadores.extend(historial)
                    time.sleep(2) # Pausa vital anti-baneo
                    
        except Exception as e:
            print(f"❌ Fallo al procesar la liga {liga_nombre}: {e}")
                
    if todos_los_entrenadores:
        df = pd.DataFrame(todos_los_entrenadores)
        
        # Movemos la columna 'Liga' al principio
        cols = ['Liga', 'Team', 'Entrenador', 'Fecha_Inicio', 'Fecha_Fin']
        df = df[[c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]]
        
        print("\n==================================================")
        print("💾 GUARDANDO DATOS DIRECTAMENTE EN PARQUET...")        
        out_dir = 'Data_Parquet'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        out_file = f"{out_dir}/dim_entrenadores.parquet"
            
        try:
            with duckdb.connect(':memory:') as conn:
                conn.execute(f"COPY (SELECT * FROM df) TO '{out_file}' (FORMAT PARQUET, COMPRESSION ZSTD)")
                
            print(f"✅ ¡ÉXITO! {len(df)} entrenadores guardados en '{out_file}'.")            
            df.to_csv("Entrenadores.csv", index=False, encoding='utf-8-sig')
            
        except Exception as e:
            print(f"❌ Error al guardar el archivo Parquet: {e}")
            
    else:
        print("\n❌ Finalizado. No se cazaron entrenadores (Revisa tu conexión a internet).")

if __name__ == "__main__":
    ejecutar_scraper()