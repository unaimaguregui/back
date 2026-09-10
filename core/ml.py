import os
import warnings

os.environ['OMP_NUM_THREADS'] = '2'
os.environ['KMP_DUPLICATE_OK'] = 'True'
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import norm
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import plotly.graph_objects as go
import plotly.io as pio

STYLE_AXES = {
    'Portero': {
        'Long Pass Tendency':    {'team_metric': 'Avg Pass Height', 'invertido': False, 'base_pct': 40, 'team_influence': 0.55, 'floor': 10, 'ceiling': 80},
        'Pass Risk Index':       {'team_metric': 'Possession',      'invertido': False, 'base_pct': 40, 'team_influence': 0.45, 'floor': 15, 'ceiling': 75},
        'Forward Tendency':      {'team_metric': 'Possession',      'invertido': True,  'base_pct': 30, 'team_influence': 0.50, 'floor': 10, 'ceiling': 60},
        'Interception Tendency': {'team_metric': 'PPDA',            'invertido': True,  'base_pct': 55, 'team_influence': 0.40, 'floor': 30, 'ceiling': 85},
    },
    'Central Defensivo': {
        'Defensive Duel Tendency':  {'team_metric': 'On-Ball Pressure Share',  'invertido': False, 'base_pct': 55, 'team_influence': 0.35, 'floor': 35, 'ceiling': 80},
        'Interception Tendency':    {'team_metric': 'Off-Ball Pressure Share', 'invertido': False, 'base_pct': 55, 'team_influence': 0.35, 'floor': 35, 'ceiling': 80},
        'Aerial Duel Tendency':     {'team_metric': 'Set Piece xGA',          'invertido': False, 'base_pct': 60, 'team_influence': 0.40, 'floor': 40, 'ceiling': 90},
        'Long Pass Tendency':       {'team_metric': 'Avg Pass Height',        'invertido': False, 'base_pct': 45, 'team_influence': 0.50, 'floor': 15, 'ceiling': 80},
        'Pass Risk Index':          {'team_metric': 'xT Against',             'invertido': True,  'base_pct': 45, 'team_influence': 0.40, 'floor': 15, 'ceiling': 70},
        'Progressive Tendency':     {'team_metric': 'Game Control Share',     'invertido': False, 'base_pct': 50, 'team_influence': 0.45, 'floor': 20, 'ceiling': 85},
        'True PAdj Interceptions':  {'team_metric': 'PPDA',                   'invertido': True,  'base_pct': 45, 'team_influence': 0.30, 'floor': 20, 'ceiling': 75},
    },
    'Lateral': {
        'Cross Tendency':           {'team_metric': 'Crosses',                'invertido': False, 'base_pct': 60, 'team_influence': 0.45, 'floor': 30, 'ceiling': 90},
        'Final Third Tendency':     {'team_metric': 'Field Tilt',             'invertido': False, 'base_pct': 65, 'team_influence': 0.35, 'floor': 40, 'ceiling': 90},
        'True PAdj Progressive Passes': {'team_metric': 'xT',                 'invertido': False, 'base_pct': 55, 'team_influence': 0.50, 'floor': 20, 'ceiling': 90},
        'Defensive Duel Tendency':  {'team_metric': 'On-Ball Pressure Share',  'invertido': False, 'base_pct': 55, 'team_influence': 0.30, 'floor': 30, 'ceiling': 80},
        'Interception Tendency':    {'team_metric': 'High Recoveries Against', 'invertido': True,  'base_pct': 50, 'team_influence': 0.35, 'floor': 25, 'ceiling': 75},
        'Box Threat Index':         {'team_metric': 'Passes into Box',        'invertido': False, 'base_pct': 45, 'team_influence': 0.40, 'floor': 15, 'ceiling': 80},
        'Long Pass Tendency':       {'team_metric': 'Avg Pass Height',        'invertido': False, 'base_pct': 40, 'team_influence': 0.40, 'floor': 10, 'ceiling': 70},
    },
    'Pivote Mediocentro': {  
        'Interception Tendency':    {'team_metric': 'Off-Ball Pressure Share', 'invertido': False, 'base_pct': 55, 'team_influence': 0.35, 'floor': 35, 'ceiling': 85},
        'Defensive Duel Tendency':  {'team_metric': 'On-Ball Pressure Share',  'invertido': False, 'base_pct': 50, 'team_influence': 0.30, 'floor': 30, 'ceiling': 80},
        'Forward Tendency':         {'team_metric': 'Possession',             'invertido': True,  'base_pct': 45, 'team_influence': 0.30, 'floor': 25, 'ceiling': 70},
        'Long Pass Tendency':       {'team_metric': 'Avg Pass Height',        'invertido': False, 'base_pct': 50, 'team_influence': 0.55, 'floor': 15, 'ceiling': 90},
        'Pass Risk Index':          {'team_metric': 'Game Control Share',     'invertido': False, 'base_pct': 45, 'team_influence': 0.40, 'floor': 15, 'ceiling': 75},
        'True PAdj Progressive Passes': {'team_metric': 'xT',                 'invertido': False, 'base_pct': 50, 'team_influence': 0.50, 'floor': 15, 'ceiling': 85},
        'True PAdj Interceptions':  {'team_metric': 'High Recoveries',        'invertido': False, 'base_pct': 50, 'team_influence': 0.30, 'floor': 25, 'ceiling': 80},
    },
    'Interior': {  
        'Smart Tendency':           {'team_metric': 'xT',                     'invertido': False, 'base_pct': 55, 'team_influence': 0.50, 'floor': 20, 'ceiling': 90},
        'Box Threat Index':         {'team_metric': 'Passes into Box',        'invertido': False, 'base_pct': 50, 'team_influence': 0.45, 'floor': 15, 'ceiling': 85},
        'Pass Risk Index':          {'team_metric': 'Shots per 1.0 xT',       'invertido': False, 'base_pct': 45, 'team_influence': 0.35, 'floor': 15, 'ceiling': 75},
        'Progressive Tendency':     {'team_metric': 'Field Tilt',             'invertido': False, 'base_pct': 55, 'team_influence': 0.35, 'floor': 25, 'ceiling': 85},
        'Forward Tendency':         {'team_metric': 'Possession',             'invertido': True,  'base_pct': 45, 'team_influence': 0.40, 'floor': 15, 'ceiling': 75},
        'Interception Tendency':    {'team_metric': 'PPDA',                   'invertido': True,  'base_pct': 35, 'team_influence': 0.30, 'floor': 10, 'ceiling': 60},
    },
    'Mediapunta': {
        'Box Threat Index':         {'team_metric': 'Passes into Box',        'invertido': False, 'base_pct': 65, 'team_influence': 0.40, 'floor': 30, 'ceiling': 95},
        'Forward Tendency':         {'team_metric': 'Possession',             'invertido': True,  'base_pct': 65, 'team_influence': 0.30, 'floor': 30, 'ceiling': 90},
        'Interception Tendency':    {'team_metric': 'PPDA',                   'invertido': True,  'base_pct': 45, 'team_influence': 0.35, 'floor': 15, 'ceiling': 80},
        'Progressive Tendency':     {'team_metric': 'Field Tilt',             'invertido': False, 'base_pct': 60, 'team_influence': 0.35, 'floor': 30, 'ceiling': 90},
        'Smart Tendency':           {'team_metric': 'Open Play xG',           'invertido': False, 'base_pct': 50, 'team_influence': 0.35, 'floor': 20, 'ceiling': 85},
        'Pass Risk Index':          {'team_metric': 'xT',                     'invertido': False, 'base_pct': 55, 'team_influence': 0.35, 'floor': 20, 'ceiling': 85},
    },
    'Extremo': {
        'Final Third Tendency':     {'team_metric': 'Field Tilt',             'invertido': False, 'base_pct': 75, 'team_influence': 0.30, 'floor': 55, 'ceiling': 95},
        'Forward Tendency':         {'team_metric': 'Possession',             'invertido': True,  'base_pct': 75, 'team_influence': 0.30, 'floor': 50, 'ceiling': 90},
        'Interception Tendency':    {'team_metric': 'PPDA',                   'invertido': True,  'base_pct': 20, 'team_influence': 0.25, 'floor': 5,  'ceiling': 45},
        'Dribbles Master':          {'team_metric': 'xT',                     'invertido': False, 'base_pct': 65, 'team_influence': 0.40, 'floor': 35, 'ceiling': 95},
        'Box Threat Index':         {'team_metric': 'Passes into Box',        'invertido': False, 'base_pct': 45, 'team_influence': 0.30, 'floor': 15, 'ceiling': 80},
        'Smart Tendency':           {'team_metric': 'Open Play xG',           'invertido': False, 'base_pct': 60, 'team_influence': 0.40, 'floor': 25, 'ceiling': 85},
    },
    'Delantero': {
        'Box Threat Index':         {'team_metric': 'Passes into Box',        'invertido': False, 'base_pct': 60, 'team_influence': 0.40, 'floor': 30, 'ceiling': 90},
        'xG per Shot':              {'team_metric': 'Shots per 1.0 xT',       'invertido': True,  'base_pct': 50, 'team_influence': 0.35, 'floor': 20, 'ceiling': 80},
        'Aerial Duel Tendency':     {'team_metric': 'Set Piece xG',           'invertido': False, 'base_pct': 55, 'team_influence': 0.40, 'floor': 25, 'ceiling': 85},
        'Pass Risk Index':          {'team_metric': 'Game Control Share',     'invertido': False, 'base_pct': 40, 'team_influence': 0.30, 'floor': 10, 'ceiling': 70},
        'Interception Tendency':    {'team_metric': 'High Recoveries',        'invertido': False, 'base_pct': 40, 'team_influence': 0.40, 'floor': 15, 'ceiling': 75},
        'Smart Tendency':           {'team_metric': 'Open Play xG',           'invertido': False, 'base_pct': 40, 'team_influence': 0.30, 'floor': 10, 'ceiling': 65},
    },
}

POSITION_TO_AXIS_KEY = {
    "Portero": "Portero",
    "Central": "Central Defensivo",
    "Lateral Izquierdo": "Lateral",
    "Lateral Derecho": "Lateral",
    "Pivote": "Pivote Mediocentro",
    "Medio": "Pivote Mediocentro",
    "Interior": "Interior",
    "Mediapunta": "Mediapunta",
    "Extremo Izquierdo": "Extremo",
    "Extremo Derecho": "Extremo",
    "Delantero": "Delantero",
}

def _match_position(pos: str) -> str:
    return POSITION_TO_AXIS_KEY.get(pos, "Delantero")

def generar_target_estilo_equipo(team_row, pos, df_tactico_completo, df_jugadores_posicion=None, team_name=None):
    def _percentil_equipo(col, valor_equipo, invertido=False):
        if col not in df_tactico_completo.columns: return 50.0
        serie = pd.to_numeric(df_tactico_completo[col], errors='coerce').dropna()
        if serie.empty or pd.isna(valor_equipo): return 50.0
        pct = (serie < valor_equipo).mean() * 100
        return (100 - pct) if invertido else pct
        
    pos_gen = _match_position(pos)
    axes = STYLE_AXES.get(pos_gen, STYLE_AXES['Delantero'])
    
    target_z, saliencia = {}, {}

    # 🚀 MODO HÍBRIDO: Identificamos a los jugadores actuales del equipo en esta posición
    df_plantilla = None
    if df_jugadores_posicion is not None and team_name is not None:
        # Filtramos a los que tienen > 400 min para no coger reservas que falseen los datos
        df_plantilla = df_jugadores_posicion[(df_jugadores_posicion['Team'] == team_name) & (df_jugadores_posicion['Minutes played'] >= 400)]

    for player_metric, cfg in axes.items():
        valor_equipo = team_row.get(cfg['team_metric'], np.nan)
        pct_team = _percentil_equipo(cfg['team_metric'], valor_equipo, invertido=cfg['invertido'])
        
        # 1. Target del Sistema (Táctica pura)
        pct_system = cfg.get('base_pct', 50.0) + cfg.get('team_influence', 0.5) * (pct_team - 50.0)
        pct_system = float(np.clip(pct_system, cfg.get('floor', 5.0), cfg.get('ceiling', 95.0)))
        
        pct_final = pct_system

        # 2. Target de Plantilla (Lo que hacen los jugadores reales)
        if df_plantilla is not None and not df_plantilla.empty and player_metric in df_jugadores_posicion.columns:
            media_plantilla = df_plantilla[player_metric].mean()
            if not pd.isna(media_plantilla):
                # Calculamos en qué percentil global de esa posición cae la media del equipo
                serie_global = pd.to_numeric(df_jugadores_posicion[player_metric], errors='coerce').dropna()
                if not serie_global.empty:
                    pct_roster = (serie_global <= media_plantilla).mean() * 100
                    # 🔥 LA FUSIÓN: 60% Sistema Teórico + 40% Jugadores Reales
                    pct_final = (pct_system * 0.60) + (pct_roster * 0.40)
        
        pct_clip = min(max(pct_final, 0.5), 99.5) / 100.0
        target_z[player_metric] = float(norm.ppf(pct_clip))
        # La saliencia (peso) se calcula ahora sobre el target híbrido
        saliencia[player_metric] = abs(pct_final - 50.0) / 50.0

    perfil = []
    pct_poss = _percentil_equipo('Possession', team_row.get('Possession', 50))
    if pct_poss > 75: perfil.append("Dominio de Posesión")
    elif pct_poss < 30: perfil.append("Bloque Bajo / Reactivo")
    if _percentil_equipo('PPDA', team_row.get('PPDA', 12), invertido=True) > 75:
        perfil.append("Presión Asfixiante")
    if _percentil_equipo('Avg Pass Height', team_row.get('Avg Pass Height', 30)) > 75:
        perfil.append("Juego Directo")
        
    # Añadimos un chivato visual para saber que el modo híbrido está funcionando
    if df_plantilla is not None and not df_plantilla.empty:
        perfil.append("Fusión Híbrida (Plantilla + Táctica)")
    else:
        if not perfil: perfil.append("Sistema Táctico")

    return target_z, saliencia, " | ".join(perfil)

def calcular_style_fit(df_pool, target_z, saliencia, min_saliencia=0.15, usar_mahalanobis=True):
    """
    🚀 FIX IA: Distancia de Mahalanobis Real usando Matriz Inversa de Covarianza
    🚀 NUEVO: Calcula el 'Breakdown' (nota individual de encaje de 0 a 100 para cada eje)
    🚀 NUEVO: Aplicado Coeficiente de Liga a los datos RAW para corregir distorsión
    """
    df_calc = df_pool.copy()
    metrics = [m for m in target_z.keys() if m in df_calc.columns and df_calc[m].notna().sum() > 5]

    if not metrics:
        df_calc['Style_Fit_Score'] = 50.0
        df_calc['Breakdown'] = "{}"
        return df_calc

    sub = df_calc[metrics].apply(pd.to_numeric, errors='coerce').fillna(df_calc[metrics].mean())
    
    # 🚀 LA MAGIA: Multiplicamos los datos crudos por el Coeficiente de Liga.
    # Así, 5 regates en Eredivisie (peso 0.8) cuentan como 4 regates reales. 
    # 5 regates en Premier League (peso 1.0) cuentan como 5. 
    # Esto hunde el Z-Score de los jugadores de ligas menores y corrige el sesgo!
    if 'League_Weight' in df_calc.columns:
        league_weights = pd.to_numeric(df_calc['League_Weight'], errors='coerce').fillna(1.0)
        sub = sub.multiply(league_weights, axis=0)

    means = sub.mean()
    stds = sub.std(ddof=0).replace(0, 1.0)

    Z_players = (sub - means) / stds
    Z_target = np.array([target_z[m] for m in metrics])
    
    # Aplicar pesos
    W = np.array([max(saliencia.get(m, 0.0), min_saliencia) for m in metrics])
    W = W / W.sum() * len(W)
    
    # Diferencia ponderada para Mahalanobis (Nota Global)
    diff = (Z_players.values - Z_target) * np.sqrt(W)

    n_validos = Z_players.dropna().shape[0]
    # 1. CÁLCULO DE LA NOTA GLOBAL (MAHALANOBIS)
    if usar_mahalanobis and n_validos >= 50:
        cov = Z_players.dropna().cov().values
        cov_reg = cov + np.eye(cov.shape[0]) * 1e-6
        try:
            inv_cov = np.linalg.pinv(cov_reg)
            diff_filled = np.nan_to_num(diff, nan=0.0)
            dist_sq = np.einsum('ij,jk,ik->i', diff_filled, inv_cov, diff_filled)
            dist = np.sqrt(np.maximum(dist_sq, 0))
        except:
            dist = np.linalg.norm(np.nan_to_num(diff, nan=0.0), axis=1)
    else:
        dist = np.linalg.norm(np.nan_to_num(diff, nan=0.0), axis=1)

    escala_esperada = np.sqrt(len(metrics)) * 1.4

    df_calc['Style_Distance'] = dist
    df_calc['Style_Fit_Score'] = (100 * np.exp(-0.5 * (dist / escala_esperada) ** 2)).clip(1, 100).round(1)
    
    # 2. CÁLCULO DEL BREAKDOWN INDIVIDUAL (XAI)
    import json
    breakdown_list = []
    
    for idx, row in Z_players.iterrows():
        jugador_breakdown = {}
        for i, m in enumerate(metrics):
            if pd.isna(row[m]):
                jugador_breakdown[m] = 50  # Si falta dato, neutro
            else:
                # Convertimos el Z-Score del jugador en su Percentil Real (de 0 a 100)
                # Como ya hemos multiplicado por el League Weight, este percentil ya refleja su "Calidad Real Ponderada".
                pct_jugador = float(norm.cdf(row[m]) * 100)
                jugador_breakdown[m] = int(np.clip(round(pct_jugador), 1, 99))
        
        breakdown_list.append(json.dumps(jugador_breakdown))
    df_calc['Breakdown'] = breakdown_list
    return df_calc

import hashlib
import time
_cache_similitud = {}
CACHE_ML_TTL = 900 # 15 minutos

def generar_modelo_similitud(df, nombre_jugador, d_estilos):
    firma = hashlib.md5(",".join(sorted(df['Player'].astype(str).tolist())).encode()).hexdigest()
    clave_cache = f"{firma}:{nombre_jugador}"
    
    entrada = _cache_similitud.get(clave_cache)
    if entrada and (time.time() - entrada['ts']) < CACHE_ML_TTL:
        return entrada['resultado'] 

    metricas = set()
    for estilo, pesos in d_estilos.items():
        if estilo != 'Personalizado':
            metricas.update(pesos.keys())
    metricas = [m for m in metricas if m in df.columns]
    
    if not metricas or nombre_jugador not in df['Player'].values:
        return None, None

    df_calc = df.dropna(subset=['Player']).copy()
    df_calc[metricas] = df_calc[metricas].fillna(0)
    df_calc = df_calc.reset_index(drop=True)
    
    X = df_calc[metricas].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_clusters = min(5, max(2, len(df_calc) // 10))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_calc['Cluster'] = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_calc['PCA_X'] = X_pca[:, 0]
    df_calc['PCA_Y'] = X_pca[:, 1]

    idx_target = np.where(df_calc['Player'] == nombre_jugador)[0][0]
    
    cos_sim = cosine_similarity(X_scaled)
    eucl_dist = euclidean_distances(X_scaled)
    max_dist = eucl_dist[idx_target].max() or 1
    
    sim_hibrida = ((cos_sim[idx_target] * 100 * 0.60) + ((100 - (eucl_dist[idx_target] / max_dist) * 100) * 0.40))
    df_calc['Similitud'] = np.clip(sim_hibrida, 1, 99).round(2)

    top_clones = df_calc[df_calc['Player'] != nombre_jugador].nlargest(5, 'Similitud')['Player'].tolist()
    
    fig = go.Figure()
    colores = ['#0ea5e9', '#10b981', '#f59e0b', '#f43f5e', '#8b5cf6']
    
    for c in range(n_clusters):
        df_cluster = df_calc[df_calc['Cluster'] == c]
        textos = [f"<b>{row['Player']}</b><br>{row.get('Team within selected timeframe', row.get('Team', ''))}<br>Similitud: {row['Similitud']}%" for _, row in df_cluster.iterrows()]
        
        fig.add_trace(go.Scatter(
            x=df_cluster['PCA_X'], y=df_cluster['PCA_Y'], mode='markers',
            marker=dict(size=8, color=colores[c % len(colores)], opacity=0.4, line=dict(width=1, color='rgba(255,255,255,0.2)')),
            name=f'Perfil Táctico {c+1}', text=textos, hoverinfo='text'
        ))

    target_row = df_calc.iloc[idx_target]
    
    clones_x = []
    clones_y = []
    clones_text = []

    for clon_name in top_clones:
        clon_row = df_calc[df_calc['Player'] == clon_name].iloc[0]
        
        fig.add_trace(go.Scatter(
            x=[target_row['PCA_X'], clon_row['PCA_X']], y=[target_row['PCA_Y'], clon_row['PCA_Y']],
            mode='lines', line=dict(color='rgba(255, 255, 255, 0.4)', width=1.5, dash='dot'),
            showlegend=False, hoverinfo='skip'
        ))
        
        clones_x.append(clon_row['PCA_X'])
        clones_y.append(clon_row['PCA_Y'])
        clones_text.append(f"{clon_name}")

    fig.add_trace(go.Scatter(x=clones_x, y=clones_y, mode='markers+text', marker=dict(size=10, color='#10b981', line=dict(width=2, color='white')), 
                            text=clones_text, textposition='bottom center', textfont=dict(size=11, color='rgba(255,255,255,0.9)', weight='bold'), showlegend=False, hoverinfo='text', name='Clones'
    ))

    fig.add_trace(go.Scatter(
        x=[target_row['PCA_X']], y=[target_row['PCA_Y']], mode='markers+text',
        marker=dict(size=18, color='#f59e0b', symbol='star', line=dict(width=2, color='white')),
        name='Objetivo', text=['⭐ ' + nombre_jugador], textposition='top center',
        textfont=dict(size=14, color='#f59e0b', weight='bold'), hoverinfo='text'
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color='white'))
    )

    fig_json = pio.to_json(fig)    
    similares = df_calc[df_calc['Player'] != nombre_jugador].sort_values(by='Similitud', ascending=False).head(15)
    col_t = 'Team within selected timeframe' if 'Team within selected timeframe' in similares.columns else 'Team'
    
    datos_tabla = similares[['Player', col_t, 'Age', 'Similitud']].rename(columns={col_t: 'Team'}).fillna('N/D').to_dict('records')

    resultado_final = (fig_json, datos_tabla)    
    _cache_similitud[clave_cache] = {'resultado': resultado_final, 'ts': time.time()}
    
    return resultado_final

import xgboost as xgb
import shap

def predecir_potencial_jugador(df, nombre_jugador, d_estilos):
    """
    Entrena un modelo XGBoost libre de Data Leakage (evitando circularidad).
    Predice si el jugador pertenece al tercio superior de minutos y consistencia.
    """
    metricas = set()
    for estilo, pesos in d_estilos.items():
        if estilo != 'Personalizado': metricas.update(pesos.keys())
    metricas = [m for m in metricas if m in df.columns]
    
    if not metricas or nombre_jugador not in df['Player'].values:
        return {"error": "Faltan métricas o el jugador no existe."}
        
    df_calc = df.dropna(subset=['Player']).copy()
    df_calc[metricas] = df_calc[metricas].fillna(0)
    df_calc = df_calc.reset_index(drop=True)
    
    if 'Minutes played' in df_calc.columns and 'League_Weight' in df_calc.columns:
        y = ((df_calc['Minutes played'] >= 1500) & (df_calc['League_Weight'] >= 0.85)).astype(int)
    else:
        y = (df_calc['Minutes played'] >= 1200).astype(int)

    if sum(y) < 2:
        return {"error": "⚠️ No hay suficientes registros con alta carga de minutos para entrenar la validación."}
        
    features = [m for m in metricas if 'League_Weight' not in m and 'Rating' not in m and 'Age' not in m]
    X = df_calc[features]
    
    modelo = xgb.XGBClassifier(
        n_estimators=100, 
        max_depth=2, # ⚡ Bajamos la profundidad para evitar que memorice a los jugadores
        learning_rate=0.05, 
        reg_lambda=5.0, # ⚡ Regularización L2 fuerte
        random_state=42, 
        eval_metric='logloss'
    )
    
    from sklearn.model_selection import cross_val_predict, StratifiedKFold
    cv = StratifiedKFold(n_splits=min(5, sum(y)), shuffle=True, random_state=42)
    
    try:
        y_probs_cv = cross_val_predict(modelo, X, y, cv=cv, method='predict_proba')
        idx_target = df_calc.index[df_calc['Player'] == nombre_jugador].tolist()[0]
        prob_final = float(y_probs_cv[idx_target][1])
    except Exception:
        # Fallback de seguridad por si la muestra es exageradamente pequeña
        modelo.fit(X, y)
        idx_target = df_calc.index[df_calc['Player'] == nombre_jugador].tolist()[0]
        prob_final = float(modelo.predict_proba(X.iloc[[idx_target]])[0][1])
        
    modelo.fit(X, y) # Entrenamos el final solo para extraer las explicaciones SHAP
    X_target = X.iloc[[idx_target]]
    
    explainer = shap.TreeExplainer(modelo)
    shap_values = explainer.shap_values(X)
    jugador_shap = shap_values[idx_target]
    
    explicacion = []
    for i, feature in enumerate(features):
        impacto = float(jugador_shap[i])
        if abs(impacto) > 0.01:
            nombre_limpio = str(feature.replace(' Scale', '').replace(' Master', '').replace(' per 90', ' p90'))
            valor_real = float(X_target.iloc[0][feature])
            
            explicacion.append({
                "metrica": nombre_limpio,
                "valor_real": valor_real,
                "impacto_shap": impacto
            })
            
    explicacion = sorted(explicacion, key=lambda x: abs(x['impacto_shap']), reverse=True)[:8]
    
    return {"probabilidad": round(prob_final * 100, 1), "factores": explicacion}

from backend.config.diccionarios import PESOS_LIGAS
METRICAS_FISICAS = {'Duels', 'Accelerations', 'runs'}
METRICAS_TECNICAS = {'Passes', 'Smart', 'Crosses'}

def _clasificar_metrica(nombre_metrica):
    if any(clave in nombre_metrica for clave in METRICAS_FISICAS):
        return 'fisica'
    if any(clave in nombre_metrica for clave in METRICAS_TECNICAS):
        return 'tecnica'
    return 'neutra'


def simular_traspaso(jugador_row, df_base, d_estilos, liga_destino):
    liga_origen = jugador_row.get('Competition within selected timeframe', jugador_row.get('Competition', ''))
    peso_origen = PESOS_LIGAS.get(liga_origen, 0.5)
    peso_destino = PESOS_LIGAS.get(liga_destino, 0.5)
    
    if peso_destino <= 0: peso_destino = 0.5 
    ratio_general = peso_origen / peso_destino
    
    pos_col = 'Pos' if 'Pos' in df_base.columns else ('Position' if 'Position' in df_base.columns else '')
    pos_jugador = jugador_row.get(pos_col, '') if pos_col else ''
    
    if pd.notna(pos_jugador) and pos_jugador != '':
        df_pos = df_base[df_base[pos_col] == pos_jugador]
    else:
        df_pos = df_base
        
    if df_pos.empty: df_pos = df_base 

    metricas = set()
    for est, pesos in d_estilos.items(): 
        if est != 'Personalizado':
            metricas.update(pesos.keys())
    
    datos_proyectados = {}
    datos_reales = {}
    
    for m in metricas:
        if m in jugador_row.index and m in df_pos.columns:
            valor_real_bruto = float(jugador_row[m]) if pd.notna(jugador_row[m]) else 0
            
            ratio_especifico = ratio_general
            
            tipo = _clasificar_metrica(m)
            if ratio_general < 1.0: 
                if tipo == 'fisica':
                    ratio_especifico = ratio_general * 0.9
                elif tipo == 'tecnica':
                    ratio_especifico = min(1.0, ratio_general * 1.1)
                
            valor_proyectado_bruto = valor_real_bruto * ratio_especifico
            
            serie = pd.to_numeric(df_pos[m], errors='coerce').dropna()
            if len(serie) > 0:
                pct_real = (serie <= valor_real_bruto).mean() * 100
                pct_proy = (serie <= valor_proyectado_bruto).mean() * 100
            else:
                pct_real, pct_proy = 0, 0
                
            datos_reales[m] = round(pct_real, 1)
            datos_proyectados[m] = round(pct_proy, 1)

    return {
        "origen": liga_origen,
        "destino": liga_destino,
        "peso_origen": peso_origen,
        "peso_destino": peso_destino,
        "datos_reales": datos_reales,
        "datos_proyectados": datos_proyectados
    }

def calcular_quality_score(df_pool, columnas_rating=None):
    df_calc = df_pool.copy()
    cols_ok = [c for c in (columnas_rating or []) if c in df_calc.columns]
    
    if cols_ok:
        # Añadido fillna(50) por seguridad
        df_calc['Quality_Score'] = df_calc[cols_ok].max(axis=1).fillna(50).clip(1, 99).round().astype(int)
    else:
        num_cols = df_calc.select_dtypes(include=[np.number]).columns
        df_calc['Quality_Score'] = (df_calc[num_cols].rank(pct=True).mean(axis=1) * 100).fillna(50).round().astype(int)
        
    return df_calc

