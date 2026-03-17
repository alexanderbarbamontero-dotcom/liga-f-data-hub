import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# CONFIGURACIÓN DE ÉLITE
st.set_page_config(page_title="Liga F Elite Hub", page_icon="💎", layout="wide")

# URL de los datos generados por el Robot de GitHub
# SUSTITUYE 'TU_USUARIO' por tu nombre de usuario de GitHub
DATA_URL = "https://raw.githubusercontent.com/TU_USUARIO/liga-f-data-hub/main/liga_f_players.csv"
LEAGUE_URL = "https://raw.githubusercontent.com/TU_USUARIO/liga-f-data-hub/main/liga_f_league.csv"

@st.cache_data(ttl=3600)
def load_hub_data():
    try:
        df_p = pd.read_csv(DATA_URL)
        df_l = pd.read_csv(LEAGUE_URL)
        return df_p, df_l, "✅ Sincronización Élite: OK"
    except:
        return None, None, "❌ Error: Los datos aún se están generando o la URL es incorrecta."

df_main, df_league, status = load_hub_data()

# --- INTERFAZ PROFESIONAL ---
st.sidebar.title("Alexander Barba")
st.sidebar.info(status)

if df_main is not None:
    st.title("💎 Liga F: Ultimate Analytics Platform")
    
    tabs = st.tabs(["📈 Competición", "🔍 Scouting Pro", "🎯 Radar"])
    
    with tabs[0]:
        st.subheader("Clasificación en Tiempo Real")
        st.dataframe(df_league, use_container_width=True, hide_index=True)
        
    with tabs[1]:
        st.subheader("Buscador de Talento")
        # Aquí puedes añadir los filtros de scouting que creamos antes
        st.dataframe(df_main[['Jugadora', 'Escuadra', 'Gls.', 'Ast', 'xG']].head(20), use_container_width=True)
        
    with tabs[2]:
        st.subheader("Comparador de Jugadoras")
        j1 = st.selectbox("Jugadora A:", df_main['Jugadora'].unique(), index=0)
        j2 = st.selectbox("Jugadora B:", df_main['Jugadora'].unique(), index=1)
        
        # El código del Radar que ya tenemos...
        st.write("Radar listo para análisis.")
else:
    st.warning("Configura tu nombre de usuario de GitHub en el código para ver los datos.")
