mapa_posiciones = {'Portero': r'\bGK\b', 'Central': r'\bCB\b|\bLCB\b|\bRCB\b|\bLCB3\b|\bRCB3\b|\bCB3\b', 'Lateral Derecho': r'\bRB\b|\bRWB\b|\bRB5\b', 'Lateral Izquierdo': r'\bLB\b|\bLWB\b|\bLB5\b',
                   'Pivote': r'\bDMF\b|\bLDMF\b|\bRDMF\b', 'Interior': r'\bCMF\b|\bLCMF\b|\bRCMF\b|\bLCMF3\b|\bRCMF3\b|\bCMF3\b', 'Mediapunta': r'\bAMF\b',  'Extremo Derecho': r'\bRW\b|\bRAMF\b|\bRWF\b', 'Extremo Izquierdo': r'\bLW\b|\bLAMF\b|\bLWF\b', 
                   'Delantero': r'\bCF\b|\bLCF\b|\bRCF\b', 'Medio': r'DMF|CMF|LDMF|RDMF|LCMF|RCMF',}

estilos_gk = {
    'Defensivo': {'Prevented goals per 90 Scale': 0.45, 'Save rate, % Scale': 0.15, 'Exits per 90 Scale': 0.15, 'Aerial duels won, % Scale': 0.15, 'xG against per 90 Scale': 0.10},
    'Distribuidor': {'Passes per 90 Scale': 0.25, 'Accurate passes, % Scale': 0.25, 'Long passes per 90 Scale': 0.20, 'Accurate long passes, % Scale': 0.15, 'Exits per 90 Scale': 0.15},
    'Hibrido': {'Save rate, % Scale': 0.15, 'Prevented goals per 90 Scale': 0.35, 'Accurate passes, % Scale': 0.30, 'Long passes per 90 Scale': 0.20}
}
 
estilos_lt = {
    'Defensivo': {'True PAdj Defensive Duels Scale': 0.35, 'True PAdj Interceptions Scale': 0.28, 'Shots blocked per 90 Scale': 0.10, 'PAdj Sliding Tackles Scale': 0.10, 'Aerial duels per 90 Scale': 0.17},
    'Ofensivo': {'True PAdj Touches in Box Scale': 0.25, 'Dribbles Master Scale': 0.20, 'Progressive runs per 90 Scale': 0.20, 'Shot assists per 90 Scale': 0.15, 'Cross Tendency Scale': 0.10, 'Accelerations per 90 Scale': 0.10},
    'Organizador': {'Passes Master Scale': 0.25, 'Progressive Tendency Scale': 0.30, 'Smart Tendency Scale': 0.20, 'Through Passes Master Scale': 0.15, 'Received passes per 90 Scale': 0.10},
    'Hibrido': {'True PAdj Defensive Duels Scale': 0.25, 'Aerial duels per 90 Scale': 0.10, 'Crosses Master Scale': 0.20, 'Progressive runs per 90 Scale': 0.20, 'Progressive Tendency Scale': 0.15, 'Smart Tendency Scale': 0.10}
}
 
estilos_cb = {
    'Defensivo': {'Aerial duels per 90 Scale': 0.25, 'True PAdj Defensive Duels Scale': 0.30, 'Shots blocked per 90 Scale': 0.10, 'True PAdj Interceptions Scale': 0.25, 'True PAdj Def Actions Scale': 0.10},
    'Organizador': {'Passes Master Scale': 0.25, 'Accurate passes, % Scale': 0.20, 'Progressive passes per 90 Scale': 0.25, 'Forward passes per 90 Scale': 0.15,'Passes to final third per 90 Scale': 0.15},
    'Hibrido': {'Aerial duels per 90 Scale': 0.20, 'True PAdj Defensive Duels Scale': 0.20, 'True PAdj Interceptions Scale': 0.15, 'Progressive passes per 90 Scale': 0.20, 'Accurate passes, % Scale': 0.15, 'Progressive runs per 90 Scale': 0.10}
}
 
estilos_mcd = {
    'Defensivo': {'True PAdj Defensive Duels Scale': 0.30, 'True PAdj Interceptions Scale': 0.30, 'True PAdj Def Actions Scale': 0.17, 'Aerial duels per 90 Scale': 0.13, 'Short Medium Passes Master Scale': 0.10},
    'Organizador': {'Passes Master Scale': 0.25, 'Accurate passes, % Scale': 0.20, 'Progressive Tendency Scale': 0.30, 'Final Third Tendency Scale': 0.25},
    'Conductor': {'Offensive Duels Master Scale': 0.25, 'Dribbles Master Scale': 0.20, 'Progressive runs per 90 Scale': 0.25, 'Passes Master Scale': 0.20, 'Fouls suffered per 90 Scale': 0.10},
    'Hibrido - B2B': {'True PAdj Interceptions Scale': 0.25, 'True PAdj Defensive Duels Scale': 0.25, 'Progressive Tendency Scale': 0.30, 'Smart Tendency Scale': 0.20}
}
 
estilos_int = {
    'Creativo': {'Smart Tendency Scale': 0.25, 'Through Passes Master Scale': 0.20, 'Passes Penalty Area Master Scale': 0.20, 'Shot assists per 90 Scale': 0.20, 'Final Third Tendency Scale': 0.15},
    'B2B': {
        'True PAdj Interceptions Scale': 0.25,          
        'Progressive runs per 90 Scale': 0.25,     
        'Final Third Tendency Scale': 0.20,   
        'True PAdj Touches in Box Scale': 0.15,       
        'Offensive Duels Master Scale': 0.15       
    },
    'Organizador': {'Passes Master Scale': 0.25, 'Accurate passes, % Scale': 0.20, 'Progressive Tendency Scale': 0.30, 'Long Passes Master Scale': 0.15, 'Fouls suffered per 90 Scale': 0.10}
}

estilos_med = {
    'Organizador Global': {
        'Passes Master Scale': 0.25, 
        'Accurate passes, % Scale': 0.20, 
        'Progressive Tendency Scale': 0.25, 
        'Smart Tendency Scale': 0.15, 
        'Long Passes Master Scale': 0.15
    },
    'Todocampista (B2B)': {
        'True PAdj Defensive Duels Scale': 0.20, 
        'Progressive runs per 90 Scale': 0.25, 
        'Passes Master Scale': 0.20, 
        'Touches in box per 90 Scale': 0.15, 
        'True PAdj Interceptions Scale': 0.20
    },
    'Destructor': {
        'True PAdj Defensive Duels Scale': 0.35, 
        'True PAdj Interceptions Scale': 0.30, 
        'Aerial duels per 90 Scale': 0.15, 
        'Short Medium Passes Master Scale': 0.20
    },
    'Pivote Posicional': {
        'True PAdj Interceptions Scale': 0.30, 
        'Received passes per 90 Scale': 0.25, 
        'Accurate passes, % Scale': 0.25, 
        'True PAdj Def Actions Scale': 0.20
    }
}
 
estilos_mp = {
    'Creador': {'Smart Tendency Scale': 0.25, 'Through Passes Master Scale': 0.15, 'Passes Penalty Area Master Scale': 0.15, 'Shot assists per 90 Scale': 0.20, 'Final Third Tendency Scale': 0.15, 'True PAdj Def Actions Scale': 0.10},
    'Llegador': {'True PAdj Touches in Box Scale': 0.35, 'xG per 90 Scale': 0.35, 'Finishing Efficiency p90 Scale': 0.15, 'Offensive Duels Master Scale': 0.15},
    'Movil': {'Dribbles Master Scale': 0.37, 'Progressive runs per 90 Scale': 0.32, 'Accelerations per 90 Scale': 0.21, 'Offensive Duels Master Scale': 0.10}
}
 
estilos_ext = {
    'Regateador': {'Dribbles Master Scale': 0.30, 'Progressive runs per 90 Scale': 0.25, 'Accelerations per 90 Scale': 0.20, 'True PAdj Touches in Box Scale': 0.15, 'Cross Tendency Scale': 0.10},
    'Finalizador': {'xG per 90 Scale': 0.45, 'True PAdj Touches in Box Scale': 0.40, 'Finishing Efficiency p90 Scale': 0.15},
    'Creativo': {'Shot assists per 90 Scale': 0.30, 'Passes Penalty Area Master Scale': 0.30, 'Smart Tendency Scale': 0.20, 'Final Third Tendency Scale': 0.20}
}
 
estilos_del = {
    'Rematador': {'xG per 90 Scale': 0.45, 'True PAdj Touches in Box Scale': 0.25, 'Finishing Efficiency p90 Scale': 0.15, 'Aerial Duels Master Scale': 0.15},
    'Movil': {'Progressive runs per 90 Scale': 0.30, 'Accelerations per 90 Scale': 0.25, 'xG per 90 Scale': 0.20, 'Offensive Duels Master Scale': 0.15, 'Finishing Efficiency p90 Scale': 0.10},
    'Falso 9': {'Smart Tendency Scale': 0.25, 'Shot assists per 90 Scale': 0.25, 'Short Medium Passes Master Scale': 0.20, 'Final Third Tendency Scale': 0.20, 'True PAdj Def Actions Scale': 0.10}
}

radar_ext = {
    'Ofensivo': ['Non-penalty goals per 90', 'xG per 90', 'Shots per 90', 'Touches in box per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Progressive runs per 90', 'Accelerations per 90', 'Finishing Efficiency p90'], 
    'Organizacion': ['Assists per 90', 'xA per 90', 'Key passes per 90', 'Shot assists per 90', 'Passes to penalty area per 90', 'Crosses per 90', 'Accurate crosses, %', 'Received passes per 90'], 
    'Defensivo': ['True PAdj Defensive Duels', 'Defensive duels won, %', 'True PAdj Interceptions', 'PAdj Sliding tackles', 'True PAdj Def Actions']
}

radar_del = {
    'Ofensivo': ['Non-penalty goals per 90', 'xG per 90', 'Shots per 90', 'Goal conversion, %', 'Touches in box per 90', 'Offensive duels per 90', 'Finishing Efficiency p90'], 
    'Organizacion': ['Assists per 90', 'xA per 90', 'Shot assists per 90', 'Key passes per 90', 'Passes to penalty area per 90', 'Received passes per 90', 'Smart passes per 90'], 
    'Defensivo': ['True PAdj Defensive Duels', 'Aerial duels per 90', 'Aerial duels won, %', 'True PAdj Interceptions', 'True PAdj Def Actions']
}

radar_mp = {
    'Ofensivo': ['Non-penalty goals per 90', 'xG per 90', 'Shots per 90', 'Touches in box per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Progressive runs per 90', 'Finishing Efficiency p90'], 
    'Organizacion': ['Assists per 90', 'xA per 90', 'Key passes per 90', 'Smart passes per 90', 'Through passes per 90', 'Shot assists per 90', 'Passes to penalty area per 90', 'Received passes per 90'], 
    'Defensivo': ['True PAdj Interceptions', 'True PAdj Defensive Duels', 'Defensive duels won, %', 'True PAdj Def Actions']
}

radar_int = {
    'Ofensivo': ['Non-penalty goals per 90', 'xG per 90', 'Shots per 90', 'Touches in box per 90', 'Dribbles per 90', 'Progressive runs per 90', 'Offensive duels per 90', 'Finishing Efficiency p90'], 
    'Organizacion': ['Assists per 90', 'xA per 90', 'Smart passes per 90', 'Key passes per 90', 'Progressive passes per 90', 'Passes to final third per 90', 'Passes to penalty area per 90', 'Received passes per 90'], 
    'Defensivo': ['True PAdj Defensive Duels', 'Defensive duels won, %', 'True PAdj Interceptions', 'PAdj Sliding tackles', 'True PAdj Def Actions']
}

radar_mcd = {
    'Ofensivo': ['Shots per 90', 'Touches in box per 90', 'Dribbles per 90', 'Progressive runs per 90', 'Offensive duels won, %', 'Fouls suffered per 90'], 
    'Organizacion': ['Passes per 90', 'Accurate passes, %', 'Forward passes per 90', 'Progressive passes per 90', 'Passes to final third per 90', 'Long passes per 90', 'Received passes per 90'], 
    'Defensivo': ['True PAdj Defensive Duels', 'Defensive duels won, %', 'True PAdj Interceptions', 'Aerial duels per 90', 'PAdj Sliding tackles', 'True PAdj Def Actions']
}

radar_lt = {
    'Ofensivo': ['Touches in box per 90', 'Dribbles per 90', 'Successful dribbles, %', 'Progressive runs per 90', 'Accelerations per 90', 'Offensive duels per 90'], 
    'Organizacion': ['Crosses per 90', 'Accurate crosses, %', 'Passes to penalty area per 90', 'Progressive passes per 90', 'Smart passes per 90', 'Key passes per 90', 'Received passes per 90'], 
    'Defensivo': ['True PAdj Defensive Duels', 'Defensive duels won, %', 'True PAdj Interceptions', 'PAdj Sliding tackles', 'Aerial duels per 90', 'True PAdj Def Actions']
}

radar_cb = {
    'Ofensivo': ['Goals per 90', 'xG per 90', 'Touches in box per 90', 'Offensive duels won, %', 'Progressive runs per 90'], 
    'Organizacion': ['Passes per 90', 'Accurate passes, %', 'Forward passes per 90', 'Progressive passes per 90', 'Long passes per 90', 'Passes to final third per 90'], 
    'Defensivo': ['True PAdj Defensive Duels', 'Defensive duels won, %', 'Aerial duels per 90', 'Aerial duels won, %', 'True PAdj Interceptions', 'Shots blocked per 90', 'PAdj Sliding tackles', 'True PAdj Def Actions']
}

radar_gk = {
    'Ofensivo': ['Exits per 90', 'Aerial duels per 90', 'Aerial duels won, %', 'PAdj Interceptions'], 
    'Organizacion': ['Passes per 90', 'Accurate passes, %', 'Long passes per 90', 'Accurate long passes, %', 'Forward passes per 90', 'Back passes received as GK per 90'], 
    'Defensivo': ['Save rate, %', 'Prevented goals per 90', 'Successful defensive actions per 90']
}

scatter_configs_multi = {'Central': [{'title': 'Pases vs Duelos Aéreos', 'x_name': 'Pases Progresivos %', 'x_vars': ['Accurate progressive passes, % Scale', 'Progressive Passes Master'], 'y_name': 'Duelos Aéreos %', 'y_vars': ['Aerial duels won, % Scale']},
        {'title': 'Construcción vs Destrucción', 'x_name': 'Pases 3/4 + Progresivos', 'x_vars': ['Passes to final third per 90 Scale', 'Progressive passes per 90 Scale'], 'y_name': 'Intercepciones + Aéreos', 'y_vars': ['True PAdj Interceptions Scale', 'Aerial duels won, % Scale']},
        {'title': 'Volumen Pases vs Efectividad Def.', 'x_name': 'Pases Completados p90', 'x_vars': ['Passes Master', 'Accurate passes, % Scale'], 'y_name': 'Duelos Def. Ganados %', 'y_vars': ['Defensive duels won, % Scale']}],
    'Pivote': [{'title': 'Progresión vs Destrucción', 'x_name': 'Pases Progresivos Comp.', 'x_vars': ['Progressive Passes Master', 'Accurate progressive passes, % Scale'], 'y_name': 'Int + Def.Duels + Aerial', 'y_vars': ['True PAdj Interceptions Scale', 'True PAdj Defensive Duels Scale', 'Aerial duels per 90 Scale']},
        {'title': 'Pases 3/4 vs Pases al Área', 'x_name': 'Pases al último tercio p90', 'x_vars': ['Passes to final third per 90 Scale'], 'y_name': 'Pases al área p90', 'y_vars': ['Passes to penalty area per 90 Scale']},
        {'title': 'Pases Prog. vs Conducciones Prog.', 'x_name': 'Pases Progresivos p90', 'x_vars': ['Progressive passes per 90 Scale'], 'y_name': 'Conducciones Progresivas', 'y_vars': ['Progressive runs per 90 Scale']},
        {'title': 'Volumen Def. vs Eficacia Def.', 'x_name': 'Duelos Def. + Aéreos (Vol.)', 'x_vars': ['True PAdj Defensive Duels Scale', 'Aerial duels per 90 Scale'], 'y_name': 'Duelos Def. + Aéreos %', 'y_vars': ['Defensive duels won, % Scale', 'Aerial duels won, % Scale']},
        {'title': 'Pases Adelante % vs Duelos Def. %', 'x_name': 'Pases hacia adelante %', 'x_vars': ['Accurate forward passes, % Scale', 'Forward Passes Master'], 'y_name': 'Duelos Defensivos %', 'y_vars': ['Defensive duels won, % Scale']},
        {'title': 'Duelos Ofensivos vs Aéreos', 'x_name': 'Duelos Ofensivos Ganados', 'x_vars': ['Offensive duels won, % Scale', 'Offensive Duels Master'], 'y_name': 'Duelos Aéreos Ganados', 'y_vars': ['Aerial duels won, % Scale']}],
    'Interior': [ {'title': 'Progresión vs Destrucción', 'x_name': 'Pases Progresivos Comp.', 'x_vars': ['Progressive Passes Master', 'Accurate progressive passes, % Scale'], 'y_name': 'Int + Def.Duels + Aerial', 'y_vars': ['True PAdj Interceptions Scale', 'True PAdj Defensive Duels Scale', 'Aerial duels per 90 Scale']},
        {'title': 'Pases 3/4 vs Pases al Área', 'x_name': 'Pases al último tercio p90', 'x_vars': ['Passes to final third per 90 Scale'], 'y_name': 'Pases al área p90', 'y_vars': ['Passes to penalty area per 90 Scale']},
        {'title': 'Pases Prog. vs Conducciones Prog.', 'x_name': 'Pases Progresivos p90', 'x_vars': ['Progressive passes per 90 Scale'], 'y_name': 'Conducciones Progresivas', 'y_vars': ['Progressive runs per 90 Scale']},
        {'title': 'Volumen Def. vs Eficacia Def.', 'x_name': 'Duelos Def. + Aéreos (Vol.)', 'x_vars': ['True PAdj Defensive Duels Scale', 'Aerial duels per 90 Scale'], 'y_name': 'Duelos Def. + Aéreos %', 'y_vars': ['Defensive duels won, % Scale', 'Aerial duels won, % Scale']},
        {'title': 'Pases Adelante % vs Duelos Def. %', 'x_name': 'Pases hacia adelante %', 'x_vars': ['Accurate forward passes, % Scale', 'Forward Passes Master'], 'y_name': 'Duelos Defensivos %', 'y_vars': ['Defensive duels won, % Scale']},
        {'title': 'Duelos Ofensivos vs Aéreos', 'x_name': 'Duelos Ofensivos Ganados', 'x_vars': ['Offensive duels won, % Scale', 'Offensive Duels Master'], 'y_name': 'Duelos Aéreos Ganados', 'y_vars': ['Aerial duels won, % Scale']}],
    'Extremo Derecho': [{'title': 'Regates vs Conducciones', 'x_name': 'Regates p90', 'x_vars': ['Dribbles per 90 Scale'], 'y_name': 'Conducciones Progresivas', 'y_vars': ['Progressive runs per 90 Scale']},
        {'title': 'Volumen vs Eficacia Regate', 'x_name': 'Regates p90', 'x_vars': ['Dribbles per 90 Scale'], 'y_name': 'Regates con Éxito %', 'y_vars': ['Successful dribbles, % Scale']},
        {'title': 'Regates Exitosos vs Creación', 'x_name': 'Regates Exitosos p90', 'x_vars': ['Dribbles Master', 'Successful dribbles, % Scale'], 'y_name': 'Pases Clave p90', 'y_vars': ['Key passes per 90 Scale']},
        {'title': 'Centros Comp. vs xA p90', 'x_name': 'Centros Completados p90', 'x_vars': ['Crosses Master', 'Accurate crosses, % Scale'], 'y_name': 'xA p90', 'y_vars': ['xA per 90 Scale']}],
    'Extremo Izquierdo': [{'title': 'Regates vs Conducciones', 'x_name': 'Regates p90', 'x_vars': ['Dribbles per 90 Scale'], 'y_name': 'Conducciones Progresivas', 'y_vars': ['Progressive runs per 90 Scale']},
        {'title': 'Volumen vs Eficacia Regate', 'x_name': 'Regates p90', 'x_vars': ['Dribbles per 90 Scale'], 'y_name': 'Regates con Éxito %', 'y_vars': ['Successful dribbles, % Scale']},
        {'title': 'Regates Exitosos vs Creación', 'x_name': 'Regates Exitosos p90', 'x_vars': ['Dribbles Master', 'Successful dribbles, % Scale'], 'y_name': 'Pases Clave p90', 'y_vars': ['Key passes per 90 Scale']},
        {'title': 'Centros Comp. vs xA p90', 'x_name': 'Centros Completados p90', 'x_vars': ['Crosses Master', 'Accurate crosses, % Scale'], 'y_name': 'xA p90', 'y_vars': ['xA per 90 Scale']}],
    'Lateral Derecho': [{'title': 'Centros Comp. vs xA p90', 'x_name': 'Centros Completados p90', 'x_vars': ['Crosses Master', 'Accurate crosses, % Scale'], 'y_name': 'xA p90', 'y_vars': ['xA per 90 Scale']},
        {'title': 'Defensa vs Ataque', 'x_name': 'Solidez Defensiva', 'x_vars': ['True PAdj Defensive Duels Scale', 'True PAdj Interceptions Scale'], 'y_name': 'Aportación Ofensiva', 'y_vars': ['Crosses Master', 'Progressive runs per 90 Scale']}],
    'Lateral Izquierdo': [{'title': 'Centros Comp. vs xA p90', 'x_name': 'Centros Completados p90', 'x_vars': ['Crosses Master', 'Accurate crosses, % Scale'], 'y_name': 'xA p90', 'y_vars': ['xA per 90 Scale']},
        {'title': 'Defensa vs Ataque', 'x_name': 'Solidez Defensiva', 'x_vars': ['True PAdj Defensive Duels Scale', 'True PAdj Interceptions Scale'], 'y_name': 'Aportación Ofensiva', 'y_vars': ['Crosses Master', 'Progressive runs per 90 Scale']}],
    'Delantero': [{'title': 'Asociación vs Generación', 'x_name': 'Pases Recibidos p90', 'x_vars': ['Received passes per 90 Scale'], 'y_name': 'xA p90', 'y_vars': ['xA per 90 Scale']},
        {'title': 'Duelos Aéreos vs Ofensivos', 'x_name': 'Duelos Aéreos Ganados', 'x_vars': ['Aerial duels won, % Scale', 'Aerial Duels Master'], 'y_name': 'Duelos Ofensivos Ganados', 'y_vars': ['Offensive duels won, % Scale', 'Offensive Duels Master']},
        {'title': 'Olfato Goleador', 'x_name': 'xG p90', 'x_vars': ['xG per 90 Scale'], 'y_name': 'Eficiencia de Finalización', 'y_vars': ['Finishing Efficiency p90 Scale']}],
    'Mediapunta': [{'title': 'Presencia Área vs Generación', 'x_name': 'Toques en Área p90', 'x_vars': ['True PAdj Touches in Box Scale'], 'y_name': 'npxG + xA p90', 'y_vars': ['xG per 90 Scale', 'xA per 90 Scale']},
        {'title': 'Peligro vs Efectividad', 'x_name': 'Toques en Área', 'x_vars': ['True PAdj Touches in Box Scale'], 'y_name': 'Eficiencia Finalización', 'y_vars': ['Finishing Efficiency p90 Scale']}],
    'Portero': [{'title': 'Seguridad vs Juego de Pies', 'x_name': 'Seguridad Bajo Palos', 'x_vars': ['Save rate, % Scale', 'Prevented goals per 90 Scale'], 'y_name': 'Juego con los Pies', 'y_vars': ['Passes Master', 'Long Passes Master', 'Forward passes per 90 Scale']}]}

MAPEO_LIGAS_PAISES = {"Bundesliga": "Alemania", "2. Bundesliga": "Alemania", "3. Liga": "Alemania", "Regionalliga": "Alemania", "U17 Bundesliga": "Alemania", "U19 Bundesliga": "Alemania", "Regionalliga Nord": "Alemania", "1. HNL": "Croacia", "2. HNL": "Croacia", "HNL": "Croacia",
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
                "New Zealand National League": "Nueva Zelanda", "South African PSL": "Sudáfrica", "Egyptian Premier League": "Egipto", "Botola Pro": "Marruecos", "Tunisia Ligue 1": "Túnez", "Nigerian Creative Championship": "Nigeria","Superliga": "Dinamarca_Serbia"}

# =========================================================
# FASES DEL JUEGO (AUDITADAS PARA ANÁLISIS DE EQUIPOS)
# =========================================================
fases_juego = {
    'Ofensiva': ['Open Play xG', 'Passes into Box', 'Shots', 'xT'],
    'Defensiva': ['Open Play xGA', 'Shots Faced', 'xT Against', 'Shots Faced per 1.0 xT Against'],
    'Verticalidad': ['Shots per 1.0 xT', 'Avg Pass Height', 'Field Tilt'],
    'Presión': ['PPDA', 'High Recoveries', 'On-Ball Pressure Share', 'Off-Ball Pressure Share'],
    'Pizarra (ABP)': ['Set Piece xG', 'Set Piece xGA', 'Corners', 'Throw-Ins into the Box']
}

# PONDERACIONES LIGAS
LEAGUE_COEFFICIENTS = {
    'Tier 1': {'weight': 1.00, 'keywords': ['Premier League']},
    'Tier 2': {'weight': 0.97, 'keywords': ['La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']},
    'Tier 3': {'weight': 0.92, 'keywords': ['Eredivisie', 'Primeira Liga', 'Championship', 'Russian Premier League', 'Belgian Pro League', 'Scottish Premiership', 'Swiss Super League', 'Austrian Bundesliga', 'Süper Lig', 'Super Lig', 'Danish Superliga', 'Greek Super League', 'Czech Fortuna Liga', 'Ekstraklasa', 'Eliteserien', 'Allsvenskan', 'Ukrainian Premier League']},
    'Tier 4': {'weight': 0.87, 'keywords': ['Croatian 1. HNL', '1. HNL', 'Superliga', 'Cyprus 1. Division', 'Bulgarian First League', 'Serbian Super Liga', 'Romanian Superliga', 'NB I', 'Slovak Super Liga', 'Slovenian 1. SNL']},
    'Tier 5': {'weight': 0.82, 'keywords': ['Brasileirão', 'Argentina LPF', 'Liga MX', 'MLS', 'Argentina Copa de la Liga']},
    'Tier 6': {'weight': 0.77, 'keywords': ['Colombian Primera A', 'Chilean Primera Division', 'Chilean Primera División', 'Uruguay Primera Division', 'Uruguay Primera División', 'Paraguay Division Profesional', 'Bolivian LFPB', 'Ecuador Liga Pro', 'Peruvian Liga 1']},
    'Tier 7': {'weight': 0.72, 'keywords': ['2. Bundesliga', 'La Liga 2', 'Serie B', 'Ligue 2', 'Eerste Divisie', 'Portuguese Segunda Liga']},
    'Tier 8': {'weight': 0.67, 'keywords': ['2. HNL', 'Belgian First Division B', 'Scottish Championship', 'Swiss Challenge League', 'Austrian 2. Liga', 'Czech FNL', 'Polish I Liga', 'Turkish 1. Lig', 'Danish 1. Division', 'Greek Super League 2', 'Russian First League', 'Ukrainian Persha Liga', 'Superettan', 'OBOS Ligaen']},
    'Tier 9': {'weight': 0.62, 'keywords': ['Saudi Pro League', 'Qatari Stars League', 'UAE Pro League', 'J1 League', 'J1', 'K League 1', 'Chinese Super League', 'A-League Men']},
    'Tier 10': {'weight': 0.57, 'keywords': ['Brazil Serie B', 'Argentina Primera Nacional', 'Liga de Expansion MX', 'Liga de Expansión MX', 'USL Championship', 'Chilean Primera B', 'Colombian Torneo BetPlay']},
    'Tier 11': {'weight': 0.52, 'keywords': ['J2 League', 'J2', 'K League 2', 'China League One', 'Saudi Division 1']},
    'Tier 12': {'weight': 0.47, 'keywords': ['Irish Premier Division', 'Welsh Premier League', 'Northern Irish Premiership', 'Besta-deild karla', 'Veikkausliiga', 'Erovnuli Liga', 'Latvian Virsliga', 'Lithuanian A Lyga', 'Estonia Meistriliiga', 'Luxembourg National Division', 'Albanian Kategoria Superiore', 'Bosnian Premier League', 'North Macedonia First League', 'Kosovo Superliga', 'Montenegro First League', 'Faroe Islands Meistaradeildin', 'Maltese Premier League', 'Andorra Primera Divisió']},
    'Tier 13': {'weight': 0.42, 'keywords': ['3. Liga', 'Primera RFEF', 'Serie C', 'National League', 'League One', 'Portuguese Liga 3', 'Tweede Divisie', 'J3 League', 'J3', 'K3 League', 'China League Two', 'Brazil Serie C', 'Norwegian 2. Division', 'Danish 2. Division', 'Polish II Liga', 'Ettan', 'Ykkonen', 'Ykkönen', 'French National 1', 'Scottish League One', 'Swiss 1. Liga Promotion', 'MLS Next Pro', 'USL League 1']},
    'Tier 14': {'weight': 0.37, 'keywords': ['Egyptian Premier League', 'Botola Pro', 'Tunisia Ligue 1', 'South African PSL', 'Indian Super League', 'Thai League 1', 'V.League 1', 'Malaysian Super League', 'Singapore Premier League', 'Hong Kong Premier League', 'Uzbek Super League', 'Kazakh Premier League', 'Azeri Premyer Liqa', 'BRI Liga 1', 'Bahrain Premier League', 'Jordan Pro League', 'Kyrgyz Premier League', 'Cambodian Premier League']},
    'Tier 15': {'weight': 0.32, 'keywords': ['Irish First Division', 'Iceland 1. Deild', 'Ykkosliiga', 'Ykkösliiga', 'Erovnuli Liga 2', 'Latvian 1. Liga', 'Lithuanian 1 Lyga', 'Estonian Esiliiga A', 'Montenegro Second League', 'Slovenian 2. SNL', 'Slovak 2. Liga', 'Cyprus 2. Division', 'Romanian Liga II', 'Serbian Prva Liga', 'NB II', 'Liga Leumit', 'Scottish League Two', 'Belarusian 1. Division', 'Azeri Birinci Dasta', 'Kazakh 1. Division', 'Thai League 2', 'Malta Challenge League']},
    'Tier 16': {'weight': 0.27, 'keywords': ['Regionalliga', 'Segunda RFEF', 'Serie D - Girone A', 'Serie D - Girone B', 'Serie D - Girone C', 'Serie D - Girone D', 'Serie D - Girone E', 'Serie D - Girone F', 'Serie D - Girone G', 'Serie D - Girone H', 'League Two', 'English National League', 'English National League North South', 'Swiss 1. Liga Classic', 'Danish 3. Division', 'Campeonato de Portugal', 'K4 League']},
    'Tier 17': {'weight': 0.22, 'keywords': ['U19 Bundesliga', 'U17 Bundesliga', 'Primavera 1', 'Greek U19 Super League', 'Czech 1. Liga U19', 'Danish U19 Ligaen', 'Danish U19 Division', 'Swiss U19 Elite', 'Swiss U17 Elite', 'Serbian U19 League', 'Serbian U17 League', 'Slovak U19 League', 'Ukrainian U19 League', 'Portuguese Juniores U19', 'Portuguese Júniores U19', 'Portuguese Juniores U17', 'Portuguese Júniores U17', 'Mexican U23 League', 'Mexican U19 League', 'Mexican U18 League', 'Mexican U17 League', 'Kazakh U18 League', 'Kazakh U17 League', 'Kazakh U16 League', 'Czech U17 League', 'Danish U17 Ligaen', 'Danish U17 Division', 'Romanian Liga Elitelor U17', 'Romanian Liga Tineret U18']},
    'Tier 18': {'weight': 0.17, 'keywords': ['New South Wales NPL', 'Victoria NPL', 'Queensland NPL', 'South Australia NPL', 'Western Australia NPL', 'Capital Territory NPL', 'Australian NPLs', 'Queensland Premier League', 'South Australia State League 1']},
    'Tier 19': {'weight': 0.10, 'keywords': ['Argentina Reserve League', 'Belarusian Reserve League', 'Premier League 2', 'Portuguese Liga Revelacao Sub 23', 'Portuguese Liga Revelação Sub 23', 'Nigerian Creative Championship']},
    'Tier 20': {'weight': 0.05, 'keywords': ['English Non-League Premier Division - Step 7', 'NCAA D2', 'NCAA D3', 'Belarusian Premier League', 'Armenian Premier League', 'Moldovan Super Liga', 'Kazakh 2. Division', 'Guatemalan Liga Nacional', 'Honduran Liga Nacional', 'Costa Rican Primera Division', 'Costa Rican Primera División', 'Panama LPF', 'El Salvador Primera Division', 'El Salvador Primera División', 'Nicaragua Primera Division', 'New Zealand National League']}
}
PESOS_LIGAS = {}
for tier, info in LEAGUE_COEFFICIENTS.items():
    for liga in info['keywords']:
        PESOS_LIGAS[liga] = info['weight']

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
