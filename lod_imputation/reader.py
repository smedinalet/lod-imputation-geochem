import pandas as pd
import numpy as np
import re

def cargar_csv(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df.replace(["null", "NULL", "NaN", ""], np.nan, inplace=True)
    return df

def detectar_lod(df):
    lod_info = {}
    for col in df.columns:
        mask = df[col].astype(str).str.match(r"^<\s*\d+(\.\d+)?$")
        if mask.any():
            lod_value = (
                df.loc[mask, col]
                .astype(str)
                .str.replace("<", "", regex=False)
                .astype(float)
                .max()
            )
            lod_info[col] = lod_value
            df.loc[mask, col] = np.nan

        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df, lod_info

def extraer_coordenadas(df):
    columnas = df.columns
    utm_cols = [c for c in columnas if c.upper() in ("UTM_E", "UTM_N", "EASTING", "NORTHING")]
    geo_cols = [c for c in columnas if c not in utm_cols]

    df_coords = df[utm_cols].copy() if utm_cols else pd.DataFrame()
    df_geo = df[geo_cols].copy()

    return df_geo, df_coords
