import pandas as pd
import requests
import io
from bs4 import BeautifulSoup
import numpy as np
import time

def fetch_and_save_data():
    print("🚀 Iniciando el proceso de scraping de FBRef...")
    base_url = "https://fbref.com/es/comps/31/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    try:
        # 1. CLASIFICACIÓN COLECTIVA
        print("📊 Obteniendo tabla de clasificación...")
        res_league = requests.get(base_url + "Estadisticas-de-Liga-F", headers=headers, timeout=30)
        if res_league.status_code != 200:
            print(f"❌ Error al obtener la clasificación: Status {res_league.status_code}")
            return

        df_league = pd.read_html(io.StringIO(res_league.text), attrs={'id': 'results2024-2025311_overall'})[0]
        print("✅ Tabla de clasificación obtenida.")

        # 2. FUNCIÓN PARA EXTRAER TABLAS INDIVIDUALES
        def get_fbref_table(url_suffix, table_id):
            print(f"🔍 Buscando tabla: {table_id}...")
            time.sleep(5)  # Espera para no saturar el servidor
            res = requests.get(base_url + url_suffix, headers=headers, timeout=30)
            if res.status_code != 200:
                print(f"⚠️ Error en tabla {table_id}: Status {res.status_code}")
                return pd.DataFrame()

            soup = BeautifulSoup(res.text, 'html.parser')
            placeholder = soup.find('div', id=f'all_{table_id}')
            if placeholder:
                comment = placeholder.find(string=lambda text: isinstance(text, str) and 'table' in text)
                if comment:
                    return pd.read_html(io.StringIO(str(comment)))[0]
            
            try:
                return pd.read_html(io.StringIO(res.text), attrs={'id': table_id})[0]
            except:
                return pd.DataFrame()

        # Extraemos las tablas clave
        df_std = get_fbref_table("stats/Estadisticas-de-Liga-F", "stats_standard")
        df_shoot = get_fbref_table("shooting/Estadisticas-de-Liga-F", "stats_shooting")
        df_pass = get_fbref_table("passing/Estadisticas-de-Liga-F", "stats_passing")
        df_def = get_fbref_table("defense/Estadisticas-de-Liga-F", "stats_defense")

        # 3. PROCESAMIENTO Y UNIÓN DE DATOS
        print("🔄 Procesando y uniendo tablas...")
        
        # Limpiamos MultiIndex
        for df in [df_std, df_shoot, df_pass, df_def]:
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(0)
                df.drop_duplicates(subset=['Jugador'], keep='first', inplace=True)

        # Merge de todas las métricas en un solo archivo de jugadoras
        df_final = df_std[['Jugador', 'Escuadra', 'Pos', 'Min', 'Gls.', 'Ast', 'xG', 'PrgP']].copy()
        
        # Unimos el resto de métricas si existen
        if not df_shoot.empty:
            df_final = df_final.merge(df_shoot[['Jugador', 'Rem', 'RaPu']], on='Jugador', how='left')
        if not df_pass.empty:
            df_final = df_final.merge(df_pass[['Jugador', 'PasKP', 'PPA']], on='Jugador', how='left')
        if not df_def.empty:
            df_final = df_final.merge(df_def[['Jugador', 'Tkl', 'Int']], on='Jugador', how='left')

        # Limpieza final de nombres
        df_final['Jugadora'] = df_final['Jugador'].str.split('\\').str[0]
        
        # 4. GUARDADO DE ARCHIVOS
        print("💾 Guardando archivos CSV...")
        df_final.to_csv("liga_f_players.csv", index=False)
        df_league.to_csv("liga_f_league.csv", index=False)
        print("✅ ARCHIVOS GENERADOS CON ÉXITO")

    except Exception as e:
        print(f"❌ Error crítico en el proceso: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
