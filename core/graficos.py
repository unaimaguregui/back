import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from config.diccionarios import scatter_configs_multi

def dibujar_radares(df, jugadores_lista, dict_radar):
    colores_linea = ['rgba(14, 165, 233, 1)', 'rgba(244, 63, 94, 1)', 'rgba(16, 185, 129, 1)']
    colores_relleno = ['rgba(14, 165, 233, 0.2)', 'rgba(244, 63, 94, 0.2)', 'rgba(16, 185, 129, 0.2)']
    
    fig = make_subplots(
        rows=1, cols=3, 
        specs=[[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}]], 
        subplot_titles=('Ofensiva', 'Organización', 'Defensiva'), 
        horizontal_spacing=0.15
    )
    
    for i, (categoria, variables) in enumerate(dict_radar.items()):
        for p_idx, nombre_jugador in enumerate(jugadores_lista):
            if nombre_jugador not in df['Player'].values: continue
            
            valores_percentiles, textos_hover, etiquetas = [], [], []
            for var in variables:
                if var in df.columns:
                    # Valor real para mostrar al usuario
                    val_real = df[df['Player'] == nombre_jugador][var].values[0]
                    
                    # ⚡ SOLUCIÓN AL "MICRO-UNIVERSO": Usar el percentil GLOBAL ya calculado
                    scale_col = f"{var} Scale"
                    if scale_col in df.columns:
                        percentil = df[df['Player'] == nombre_jugador][scale_col].values[0]
                    else:
                        # Fallback por si la columna no fue escalada
                        percentil = 50.0 
                        
                    valores_percentiles.append(percentil)
                    v_str = f"{val_real:.2f}" if isinstance(val_real, (int, float)) else str(val_real)
                    
                    nombre_metrica = var.replace(' per 90', ' p90').replace(', %', '%')
                    textos_hover.append(f"<b>{nombre_jugador}</b><br>{nombre_metrica}<br>Valor: {v_str}<br>Percentil: {int(percentil)}")
                    etiquetas.append(nombre_metrica)
                else:
                    valores_percentiles.append(0)
                    textos_hover.append("N/D")
                    etiquetas.append(var)
                    
            # Cerrar el polígono para Plotly
            if valores_percentiles:
                valores_percentiles.append(valores_percentiles[0])
                textos_hover.append(textos_hover[0])
                etiquetas.append(etiquetas[0])
                
            fig.add_trace(go.Scatterpolar(
                r=valores_percentiles, theta=etiquetas, mode='lines+markers', 
                marker=dict(size=6, color=colores_linea[p_idx]), 
                fill='toself', fillcolor=colores_relleno[p_idx], 
                name=nombre_jugador, legendgroup=nombre_jugador, 
                showlegend=(i == 0), line=dict(color=colores_linea[p_idx], width=2.5), 
                hoverinfo="text", text=textos_hover
            ), row=1, col=i+1)
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(150,150,150,0.2)'), angularaxis=dict(gridcolor='rgba(150,150,150,0.2)', tickfont=dict(size=10))),
        polar2=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(150,150,150,0.2)'), angularaxis=dict(gridcolor='rgba(150,150,150,0.2)', tickfont=dict(size=10))),
        polar3=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(150,150,150,0.2)'), angularaxis=dict(gridcolor='rgba(150,150,150,0.2)', tickfont=dict(size=10))),
        paper_bgcolor="rgba(0,0,0,0)", 
        height=450, 
        margin=dict(l=60, r=60, t=50, b=30),
        font=dict(color='white'),
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
    )
    return pio.to_json(fig)

def dibujar_posiciones(fila_jug):
    pos, pcts = [], []
    for p_c, pct_c in [('Primary position', 'Primary position, %'), ('Secondary position', 'Secondary position, %'), ('Third position', 'Third position, %')]:
        if p_c in fila_jug.index and pct_c in fila_jug.index and pd.notna(fila_jug[p_c]):
            val = fila_jug[pct_c]
            if pd.notna(val) and str(val).strip() != '':
                try:
                    pos.append(str(fila_jug[p_c]))
                    pcts.append(float(str(val).replace(',', '.').replace('-', '0')))
                except ValueError: 
                    pass
                    
    fig = go.Figure(go.Bar(
        x=pcts, y=pos, orientation='h', 
        marker_color=['#0ea5e9', '#10b981', '#f59e0b'][:len(pos)], 
        text=[f"{p}%" for p in pcts], textposition='auto'
    ))
    fig.update_layout(
        height=120, margin=dict(l=0, r=0, t=0, b=0), 
        xaxis=dict(visible=False, range=[0, 100]), 
        yaxis=dict(autorange="reversed", tickfont=dict(weight='bold')), 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color='white')
    )
    return pio.to_json(fig)

def dibujar_scatter_multi(df, nombre_jugador, posicion):
    import plotly.graph_objects as go
    import plotly.io as pio
    import traceback
    
    try:
        pos_gen = posicion.split(' ')[0]
        configs = scatter_configs_multi.get(posicion, scatter_configs_multi.get(pos_gen, []))
        
        if not configs: return []
        
        plots_generados = []
        for config in configs:
            # 1. Quitamos los "Scale" para buscar la columna real de Wyscout
            x_raw = [v.replace(' Scale', '').replace(' Master', '').strip() for v in config['x_vars']]
            y_raw = [v.replace(' Scale', '').replace(' Master', '').strip() for v in config['y_vars']]
            
            df_plot = df.copy()
            
            # 2. Calculamos los percentiles al vuelo solo para las columnas que de verdad existen
            x_pct_cols = []
            for col in x_raw:
                if col in df_plot.columns:
                    df_plot[f"{col}_pct"] = df_plot[col].rank(pct=True) * 100
                    x_pct_cols.append(f"{col}_pct")
                    
            y_pct_cols = []
            for col in y_raw:
                if col in df_plot.columns:
                    df_plot[f"{col}_pct"] = df_plot[col].rank(pct=True) * 100
                    y_pct_cols.append(f"{col}_pct")
            
            # 3. Hacemos la media. Si no hay datos, ponemos 50 (mitad de la tabla) para que no crashee
            df_plot['Indice_X'] = df_plot[x_pct_cols].mean(axis=1).fillna(50) if x_pct_cols else 50
            df_plot['Indice_Y'] = df_plot[y_pct_cols].mean(axis=1).fillna(50) if y_pct_cols else 50
            
            fig = go.Figure()
            df_others = df_plot[df_plot['Player'] != nombre_jugador]
            df_player = df_plot[df_plot['Player'] == nombre_jugador]
            
            # Puntos grises (Resto de la liga)
            if not df_others.empty:
                fig.add_trace(go.Scatter(
                    x=df_others['Indice_X'], y=df_others['Indice_Y'],
                    mode='markers', marker=dict(color='rgba(150, 150, 150, 0.3)', size=7),
                    text=df_others['Player'], hoverinfo='text', name='Liga'
                ))
            
            # Punto azul brillante (El jugador buscado)
            if not df_player.empty:
                fig.add_trace(go.Scatter(
                    x=df_player['Indice_X'], y=df_player['Indice_Y'],
                    mode='markers', marker=dict(color='#0ea5e9', size=14, line=dict(color='white', width=2)),
                    text=df_player['Player'] + " ⭐", hoverinfo='text', name=nombre_jugador
                ))
                
            fig.update_layout(
                title=dict(text=config['title'], font=dict(color='white', size=14)),
                xaxis_title=f"{config['x_name']} (Pcl)", yaxis_title=f"{config['y_name']} (Pcl)",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.1)', range=[0, 100]), 
                yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.1)', range=[0, 100]),
                showlegend=False, margin=dict(l=40, r=40, t=40, b=40), font=dict(color='white')
            )
            fig.add_hline(y=50, line_dash="dash", line_color="rgba(150,150,150,0.3)")
            fig.add_vline(x=50, line_dash="dash", line_color="rgba(150,150,150,0.3)")
            plots_generados.append({"title": config['title'], "json": pio.to_json(fig)})
            
        return plots_generados
    except Exception as e:
        print(f"🔴 ERROR EN SCATTERS: {e}")
        traceback.print_exc()
        return []