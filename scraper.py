import pandas as pd
import requests
import io
from bs4 import BeautifulSoup
import numpy as np
import time

def fetch_and_save_data():
    print("Iniciando el proceso de scraping de FBRef...")
    base_url = "https://fbref.com/es/comps/31/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    try:
        print("Obteniendo tabla de clasificación...")
        res_league = requests.get(base_url + "Estadisticas-de-Liga-F", headers=headers, timeout=30)
        if res_league.status_code != 200:
            print(f"Error al obtener la clasificación: Status {res_league.status_code}")
            return

        df_league = pd.read_html(io.StringIO(res_league.text), attrs={'id': 'results2024-2025311_overall'})[0]
        print("Tabla de clasificación obtenida.")

        def get_fbref_table(url_suffix, table_id):
            print(f"Obteniendo tabla: {table_id}...")
            time.sleep(5)
            res = requests.get(base_url + url_suffix, headers=headers, timeout=30)
            if res.status_code != 200:
                print(f"Error en tabla {table_id}: Status {res.status_code}")
                return pd.DataFrame()

            soup = BeautifulSoup(res.text, 'html.parser')
            placeholder = soup.find('div', id=f'all_{table_id}')
            if placeholder:
                comment = placeholder.find(string=lambda text: isinstance(text, str) and 'table' in text)
                if comment:
                    print(f"Tabla {table_id} extraída de comentarios.")
                    return pd.read_html(io.StringIO(str(comment)))[0]
            print(f"Tabla {table_id} extraída directamente.")
            return pd.read_html(io.StringIO(res.text), attrs={'id': table_id})[0]

        df_std = get_fbref_table("stats/Estadisticas-de-Liga-F", "stats_standard")
        df_shoot = get_fbref_table("shooting/Estadisticas-de-Liga-F", "stats_shooting")
        df_pass = get_fbref_table("passing/Estadisticas-de-Liga-F", "stats_passing")
        df_def = get_fbref_table("defense/Estadisticas-de-Liga-F", "stats_defense")
        df_poss = get_fbref_table("possession/Estadisticas-de-Liga-F", "stats_possession")

        print("Procesando y uniendo tablas...")
        for df in [df_std, df_shoot, df_pass, df_def, df_poss]:
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(0)
            df.drop_duplicates(subset=['Jugador'], keep='first', inplace=True)

        df_final = df_std.copy()
        for df_to_merge in [df_shoot, df_pass, df_def, df_poss]:
             if not df_to_merge.empty:
                df_final = df_final.merge(df_to_merge, on='Jugador', how='left', suffixes=('', '_dup'))
                df_final.drop([col for col in df_final.columns if '_dup' in col], axis=1, inplace=True)

        df_final['Jugadora'] = df_final['Jugador'].str.split('\\\\').str[0]
        df_final.to_csv("liga_f_players.csv", index=False)
        df_league.to_csv("liga_f_league.csv", index=False)
        print("Archivos CSV generados.")

    except Exception as e:
        print(f"Error en el proceso de scraping: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
