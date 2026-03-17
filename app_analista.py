import streamlit as st
import pandas as pd
import requests
import io
import plotly.graph_objects as go
import plotly.express as px
from bs4 import BeautifulSoup
import urllib.parse

# 1. CONFIGURACIÓN UI ELITE (Colores de las capturas)
st.set_page_config(page_title="LIGA F | SCOUTING PRO", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid #00f2ff; }
    .profile-card { background-color: #1e2130; padding: 20px; border-radius: 15px; border: 1px solid #3d425b; }
    .stat-bar { height: 10px; background-color: #00f2ff; border-radius: 5px; }
    .tab-content { background-color: #161b22; padding: 20px; border-radius: 0 0 15px 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DATOS REALES (Sin datos de emergencia)
@st.cache_data(ttl=3600)
def get_elite_data():
    target = "https://fbref.com/es/comps/31/Estadisticas-de-Liga-F"
    proxy = f"https://api.allorigins.win/get?url={urllib.parse.quote(target)}"
    try:
        r = requests.get(proxy, timeout=30)
        html = r.json()['contents']
        df_l = pd.read_html(io.StringIO(html), attrs={'id': 'results2024-2025311_overall'})[0]
        soup = BeautifulSoup(html, 'html.parser')
        placeholder = soup.find('div', id='all_stats_standard')
        comment = placeholder.find(string=lambda text: isinstance(text, str) and 'table' in text)
        df_p = pd.read_html(io.StringIO(str(comment)))[0]
        if isinstance(df_p.columns, pd.MultiIndex): df_p.columns = df_p.columns.droplevel(0)
        df_p = df_p[df_p['Jugador'] != 'Jugador'].copy()
        df_p['Jugadora'] = df_p['Jugador'].str.split('\\').str[0]
        for c in ['Gls.', 'Ast', 'xG', 'PrgP', 'Min', 'Tkl', 'Int', 'PasKP', 'PPA']:
            if c in df_p.columns:
                df_p[c] = pd.to_numeric(df_p[c], errors='coerce').fillna(0)
                df_p[f'Perc_{c}'] = df_p[c].rank(pct=True) * 100
        return df_p, df_l, "✅ SISTEMA SINCRONIZADO"
    except: return None, None, "❌ ERROR DE CONEXIÓN"

df_p, df_l, status = get_elite_data()

# 3. INTERFAZ TÁCTICA (Clon de las capturas)
if df_p is not None:
    st.title("💎 LIGA F | Professional Scouting Intelligence")
    
    # Barra Superior de Filtros
    c_f1, c_f2, c_f3 = st.columns([1, 1, 2])
    with c_f1: club_sel = st.selectbox("Seleccionar Equipo:", sorted(df_l['Equipo'].unique()))
    with c_f2: 
        jug_list = sorted(df_p[df_p['Escuadra'] == club_sel]['Jugadora'].unique())
        jug_sel = st.selectbox("Seleccionar Jugadora:", jug_list)
    
    # DATOS DE LA JUGADORA SELECCIONADA
    player = df_p[df_p['Jugadora'] == jug_sel].iloc[0]
    
    # BLOQUE 1: FICHA DE PERFIL (Header Rojo/Azul de la captura)
    st.markdown(f"""
        <div class="profile-card" style="background: linear-gradient(90deg, #8e0e2f 0%, #1e2130 100%);">
            <h1 style='margin:0;'>{player['Jugadora']}</h1>
            <p style='margin:0;'>{player['Escuadra']} | {player['Pos']} | Minutos: {int(player['Min'])}</p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # BLOQUE 2: DASHBOARD DE RENDIMIENTO
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("📊 Valoración por Fases")
        def draw_metric(label, perc):
            color = "#00f2ff" if perc > 70 else "#ffa500" if perc > 40 else "#ff4b4b"
            st.markdown(f"**{label}**")
            st.markdown(f"""<div style="background-color: #3d425b; border-radius: 5px;">
                <div style="width: {perc}%; background-color: {color}; height: 10px; border-radius: 5px;"></div>
            </div>""", unsafe_allow_html=True)
            st.caption(f"Percentil: {int(perc)}")

        draw_metric("Trabajo Defensivo", player.get('Perc_Tkl', 50))
        draw_metric("Capacidad de Creación", player.get('Perc_Ast', 50))
        draw_metric("Progresión / Avance", player.get('Perc_PrgP', 50))
        draw_metric("Finalización", player.get('Perc_Gls.', 50))

    with col_right:
        st.subheader("🎯 Contexto de Posición")
        # Radar de 5 ejes como en la imagen 2
        categories = ['Defensa', 'Creación', 'Progresión', 'Ataque', 'xG']
        values = [player.get('Perc_Tkl', 50), player.get('Perc_Ast', 50), player.get('Perc_PrgP', 50), player.get('Perc_Gls.', 50), player.get('Perc_xG', 50)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#00f2ff'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # BLOQUE 3: ANÁLISIS COLECTIVO (Imagen 3 y 4)
    st.divider()
    tab_team, tab_comp = st.tabs(["🏟️ Aportación al Equipo", "⚖️ Comparativa Directa"])
    
    with tab_team:
        st.markdown("### Reparto de Goles y xG en el Club")
        df_club = df_p[df_p['Escuadra'] == club_sel]
        fig_team = px.scatter(df_club, x='Min', y='xG', text='Jugadora', size='Gls.', color='Pos', template="plotly_dark")
        st.plotly_chart(fig_team, use_container_width=True)

    with tab_comp:
        st.markdown("### Duelo de Perfiles")
        j2_sel = st.selectbox("Comparar con:", sorted(df_p['Jugadora'].unique()), index=1)
        player2 = df_p[df_p['Jugadora'] == j2_sel].iloc[0]
        
        # Gráfico de barras comparativo
        metrics_comp = ['Gls.', 'Ast', 'xG', 'PrgP', 'Tkl']
        fig_comp = go.Figure(data=[
            go.Bar(name=jug_sel, x=metrics_comp, y=[player[m] for m in metrics_comp], marker_color='#00f2ff'),
            go.Bar(name=j2_sel, x=metrics_comp, y=[player2[m] for m in metrics_comp], marker_color='#ff4b4b')
        ])
        fig_comp.update_layout(barmode='group', template="plotly_dark")
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.error("🚨 Sincronizando con los servidores de la Liga F... por favor, espera 10 segundos.")
    if st.button("🔄 Forzar Sincronización"): st.rerun()
