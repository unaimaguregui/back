import os
import requests
from pathlib import Path
import urllib.parse

GITHUB_TOKEN = "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" 

DESCARGAS = [
    {
        "tipo": "JUGADORES",
        "owner": "btgriff",
        "repo": "Wyscout_Data",
        "folder": "Main App",
        "destino": Path("Data")
    },
    {
        "tipo": "EQUIPOS",
        "owner": "griffisben",
        "repo": "Post_Match_App",
        "folder": "Stat_Files",
        "destino": Path("Data_Teams")
    }
]

def descargar_carpeta_github(config):
    tipo = config["tipo"]
    owner = config["owner"]
    repo = config["repo"]
    folder = config["folder"]
    destino = config["destino"]
    
    destino.mkdir(parents=True, exist_ok=True)

    # Codificamos el nombre de la carpeta por si tiene espacios (como "Main App")
    folder_encoded = urllib.parse.quote(folder)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_encoded}"
    
    print(f"\n📡 [{tipo}] Conectando a GitHub ({owner}/{repo}/{folder})...")
    
    # Añadimos el Token si lo has puesto
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error al conectar: HTTP {response.status_code}")
        print(response.json())
        return

    archivos = response.json()
    archivos_csv = [a for a in archivos if a['name'].endswith('.csv') and a['type'] == 'file']
    
    if not archivos_csv:
        print("⚠️ No se encontraron archivos .csv en esta carpeta.")
        return
        
    print(f"🎯 Encontrados {len(archivos_csv)} archivos CSV. Iniciando descarga...")
    
    descargados = 0
    for archivo in archivos_csv:
        nombre = archivo['name']
        url_raw = archivo['download_url']
        ruta_guardado = destino / nombre
        
        # Opcional: imprimir qué está descargando (puedes comentarlo si es mucho texto)
        print(f"   ⬇️ Descargando: {nombre}...")
        
        try:
            csv_response = requests.get(url_raw, timeout=15)
            csv_response.raise_for_status()
            
            with open(ruta_guardado, 'wb') as f:
                f.write(csv_response.content)
                
            descargados += 1
        except Exception as e:
            print(f"   ❌ Error descargando {nombre}: {e}")
            
    print(f"✅ [{tipo}] Completado: {descargados} CSVs guardados en '{destino}'.")

if __name__ == "__main__":
    print("🚀 INICIANDO DESCARGA AUTOMÁTICA DESDE GITHUB...")
    for cfg in DESCARGAS:
        descargar_carpeta_github(cfg)
    print("\n🎉 ¡Misión cumplida! Todo el Data Lake local está actualizado.")