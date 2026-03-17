import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# Configuración de Alexander Barba
st.set_page_config(page_title="Alexander Barba | Datos Reales Liga F", layout="wide")

@st.cache_data(ttl=300)
def scraping_puro():
    url = "https://fbref.com/es/comps/230/stats/Estadisticas-de-Liga-F"
    # Cabecera para simular navegador real
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # Extraer datos de los comentarios (donde FBRef oculta el censo de 350+)
            html = response.text.replace('', '')
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'stats_standard'})
            
            df = pd.read_html(io.StringIO(str(table)))[0]
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)
            
            # Limpieza profesional de columnas
            df = df[df['Jugador'] != 'Jugador'].copy()
            df = df[['Jugador', 'Escuadra', 'PJ', 'Min', 'Gls.', 'Ast']].copy()
            df.columns = ['Jugadora', 'Equipo', 'PJ', 'Minutos', 'Goles', 'Asistencias']
            
            # Limpieza de nombres (quita códigos raros de FBRef)
            df['Jugadora'] = df['Jugadora'].str.split('\\').str[0]
            
            return df, "Conexión Exitosa: Datos 100% Reales"
        else:
            return None, f"Error {response.status_code}: IP bloqueada localmente."
    except Exception as e:
        return None, f"Error de red: {e}"

# Ejecución
df, mensaje = scraping_puro()

st.title("🎯 Panel de Big Data: Liga F")
if df is not None:
    st.success(f"{mensaje} - {len(df)} jugadoras en base de datos.")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.error(mensaje)
    st.info("💡 Alexander, para saltar este bloqueo local, el siguiente paso es conectar esta carpeta a Streamlit Cloud.")