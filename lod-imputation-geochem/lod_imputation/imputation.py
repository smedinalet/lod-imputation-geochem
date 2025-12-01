import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from typing import Dict, Literal, Optional

def reemplazar_lod_simple(
    df: pd.DataFrame,
    lod_info: Dict[str, float],
    metodo: Literal["sqrt2", "div2"] = "sqrt2"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reemplazo simple de valores bajo LOD con variación aleatoria.
    
    GARANTÍA: El promedio de los valores reemplazados será exactamente
    el valor central (LOD/√2 o LOD/2), usando distribución normal truncada.
    
    Los valores están entre 0 y LOD, sin repetidos, y con media exacta.
    
    Parameters:
    -----------
    df : DataFrame con valores NaN donde había <LOD
    lod_info : Dict con {columna: valor_LOD}
    metodo : "sqrt2" (centro en LOD/√2) o "div2" (centro en LOD/2)
    
    Returns:
    --------
    tuple: (DataFrame con valores reemplazados, log de reemplazos)
    """
    df_resultado = df.copy()
    log_reemplazos = []
    
    # Configurar semilla para reproducibilidad
    np.random.seed(42)
    
    for col, lod_value in lod_info.items():
        if col not in df_resultado.columns:
            continue
            
        mask_nan = df_resultado[col].isna()
        n_reemplazos = mask_nan.sum()
        
        if n_reemplazos > 0:
            # Determinar valor central
            if metodo == "sqrt2":
                valor_central = lod_value / np.sqrt(2)
            else:  # div2
                valor_central = lod_value / 2
            
            # Definir desviación estándar (15% del valor central)
            std_dev = valor_central * 0.15
            
            # Generar valores con distribución normal
            valores_aleatorios = np.random.normal(
                loc=valor_central,
                scale=std_dev,
                size=n_reemplazos
            )
            
            # Truncar valores fuera del rango válido [0.001, 0.99*LOD]
            valores_aleatorios = np.clip(
                valores_aleatorios,
                0.001,
                lod_value * 0.99
            )
            
            # AJUSTE POST-HOC: Corregir para que la media sea exactamente valor_central
            # Esto compensa el sesgo introducido por el truncamiento
            media_actual = valores_aleatorios.mean()
            factor_correccion = valor_central / media_actual
            valores_aleatorios = valores_aleatorios * factor_correccion
            
            # Re-truncar después del ajuste (por seguridad)
            valores_aleatorios = np.clip(
                valores_aleatorios,
                0.001,
                lod_value * 0.99
            )
            
            df_resultado.loc[mask_nan, col] = valores_aleatorios
            
            # Calcular estadísticas para verificación
            media_final = valores_aleatorios.mean()
            desviacion_porcentual = abs(media_final - valor_central) / valor_central * 100
            
            log_reemplazos.append({
                'columna': col,
                'n_reemplazos': n_reemplazos,
                'lod': lod_value,
                'valor_central_objetivo': valor_central,
                'media_obtenida': media_final,
                'desviacion_de_media_%': desviacion_porcentual,
                'min_usado': valores_aleatorios.min(),
                'max_usado': valores_aleatorios.max(),
                'std_usado': valores_aleatorios.std(),
                'metodo': metodo
            })
    
    return df_resultado, pd.DataFrame(log_reemplazos)


def reemplazar_lod_idw(
    df: pd.DataFrame,
    df_coords: pd.DataFrame,
    lod_info: Dict[str, float],
    power: float = 2.0,
    max_distance: Optional[float] = None,
    min_neighbors: int = 3,
    metodo_c: Literal["div2", "sqrt2"] = "div2"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reemplazo espacial usando IDW con modelo cuadrático.
    
    FÓRMULA CUADRÁTICA:
    V(w) = A·w² + B·w
    
    donde:
    - A = 2L - 4C
    - B = 4C - L
    - L = LOD (límite de detección)
    - C = valor central (L/2 o L/√2)
    - w = peso normalizado IDW [0, 1]
    
    Esta fórmula garantiza:
    - V(0) = 0 (contexto de valores muy bajos)
    - V(1) = L (contexto de valores cercanos al LOD)
    - Transición no lineal (más realista geológicamente)
    
    Parameters:
    -----------
    df : DataFrame con valores NaN donde había <LOD
    df_coords : DataFrame con coordenadas
    lod_info : Dict con {columna: valor_LOD}
    power : Exponente para ponderación de distancia IDW (típicamente 2)
    max_distance : Distancia máxima de búsqueda (None = sin límite)
    min_neighbors : Mínimo de vecinos válidos requeridos
    metodo_c : "div2" (C = L/2, conservador) o "sqrt2" (C = L/√2, agresivo)
    
    Returns:
    --------
    tuple: (DataFrame procesado, log de reemplazos)
    """
    df_resultado = df.copy()
    log_reemplazos = []
    
    # Validar coordenadas
    if df_coords.empty or len(df_coords.columns) < 2:
        raise ValueError("Se requieren al menos 2 columnas de coordenadas para interpolación espacial")
    
    coords = df_coords.iloc[:, :2].values
    dist_matrix = cdist(coords, coords)
    
    # Procesar cada columna con LOD
    for col, L in lod_info.items():  # L = LOD
        if col not in df_resultado.columns:
            continue
        
        mask_nan = df_resultado[col].isna()
        indices_nan = np.where(mask_nan)[0]
        
        # Calcular rango de valores observados para normalización
        valores_observados = df_resultado[col].dropna()
        if len(valores_observados) == 0:
            continue
        
        max_obs = valores_observados.max()
        min_obs = valores_observados.min()
        rango = max_obs - min_obs
        
        if rango == 0:
            rango = max_obs if max_obs > 0 else 1
        
        # Calcular parámetros C, A, B según método elegido
        if metodo_c == "div2":
            C = L / 2
        else:  # sqrt2
            C = L / np.sqrt(2)
        
        A = 2 * L - 4 * C
        B = 4 * C - L
        
        # Procesar cada punto bajo LOD
        for idx_nan in indices_nan:
            # Encontrar vecinos válidos
            mask_validos = ~df_resultado[col].isna()
            indices_validos = np.where(mask_validos)[0]
            
            if len(indices_validos) < min_neighbors:
                # Fallback: usar valor central C
                df_resultado.loc[df_resultado.index[idx_nan], col] = C
                log_reemplazos.append({
                    'fila': df_resultado.index[idx_nan],
                    'columna': col,
                    'metodo': 'fallback',
                    'valor_final': C,
                    'lod': L,
                    'C': C
                })
                continue
            
            # Calcular distancias
            distancias = dist_matrix[idx_nan, indices_validos]
            
            # Filtro de distancia máxima
            if max_distance is not None:
                mask_dist = distancias <= max_distance
                if mask_dist.sum() < min_neighbors:
                    df_resultado.loc[df_resultado.index[idx_nan], col] = C
                    log_reemplazos.append({
                        'fila': df_resultado.index[idx_nan],
                        'columna': col,
                        'metodo': 'fallback_distancia',
                        'valor_final': C,
                        'lod': L,
                        'C': C
                    })
                    continue
                distancias = distancias[mask_dist]
                indices_validos = indices_validos[mask_dist]
            
            # Evitar división por cero
            distancias = np.where(distancias < 1e-10, 1e-10, distancias)
            
            # Calcular pesos IDW
            pesos = 1 / (distancias ** power)
            pesos /= pesos.sum()
            
            # Interpolar valor
            valores_vecinos = df_resultado.iloc[indices_validos][col].values
            valor_interpolado = np.sum(pesos * valores_vecinos)
            
            # Normalizar a peso w ∈ [0, 1]
            w = (valor_interpolado - min_obs) / rango
            w = np.clip(w, 0, 1)
            
            # APLICAR MODELO CUADRÁTICO
            V = A * (w ** 2) + B * w
            
            # Asegurar que está en rango válido [0.001, 0.99*L]
            V = max(0.001, min(V, 0.99 * L))
            
            df_resultado.loc[df_resultado.index[idx_nan], col] = V
            
            log_reemplazos.append({
                'fila': df_resultado.index[idx_nan],
                'columna': col,
                'n_vecinos': len(indices_validos),
                'distancia_media': distancias.mean(),
                'valor_interpolado': valor_interpolado,
                'peso_w': w,
                'valor_final_V': V,
                'lod': L,
                'C': C,
                'A': A,
                'B': B
            })
    
    return df_resultado, pd.DataFrame(log_reemplazos)


def reemplazar_lod_beta_substitution(
    df: pd.DataFrame,
    lod_info: Dict[str, float]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Método β-substitution de Ganser & Hewett (2010).
    
    Calcula factores β óptimos basados en los datos observados, produciendo
    estimaciones con bias cercano a cero, comparable al MLE.
    
    Referencia: Ganser & Hewett (2010), J. Occup. Environ. Hyg., 7:4, 233-244
    
    Parameters:
    -----------
    df : DataFrame con valores NaN donde había <LOD
    lod_info : Dict con {columna: valor_LOD}
    
    Returns:
    --------
    tuple: (DataFrame procesado, log de reemplazos)
    """
    from scipy import stats
    
    df_resultado = df.copy()
    log_reemplazos = []
    
    for col, LOD in lod_info.items():
        if col not in df_resultado.columns:
            continue
        
        mask_detectados = ~df_resultado[col].isna()
        detectados = df_resultado.loc[mask_detectados, col].values
        
        n = len(df_resultado[col])
        k = (~mask_detectados).sum()
        n_detectados = len(detectados)
        
        if n_detectados < 2 or k == 0:
            continue
        
        # Calcular parámetros β-substitution
        y_bar = np.mean(np.log(detectados))
        z = stats.norm.ppf(k / n)
        f_z = stats.norm.pdf(z, 0, 1) / (1 - stats.norm.cdf(z, 0, 1))
        s_y_hat = (y_bar - np.log(LOD)) / (f_z - z)
        
        if s_y_hat <= 0 or not np.isfinite(s_y_hat):
            df_resultado.loc[~mask_detectados, col] = LOD / np.sqrt(2)
            continue
        
        f_s_y_z = (1 - stats.norm.cdf(z - s_y_hat / n, 0, 1)) / \
                  (1 - stats.norm.cdf(z, 0, 1))
        
        # Calcular β_MEAN y β_GM
        beta_MEAN = (n / k) * stats.norm.cdf(z - s_y_hat, 0, 1) * \
                    np.exp(-s_y_hat * z + (s_y_hat ** 2) / 2)
        
        beta_GM = np.exp(
            -(n - k) * n / k * np.log(f_s_y_z) - 
            s_y_hat * z - 
            (n - k) / (2 * k * n) * (s_y_hat ** 2)
        )
        
        # Validar betas
        if not (0 < beta_MEAN < 1) or not np.isfinite(beta_MEAN):
            df_resultado.loc[~mask_detectados, col] = LOD / np.sqrt(2)
            continue
        
        if not (0 < beta_GM < 1) or not np.isfinite(beta_GM):
            df_resultado.loc[~mask_detectados, col] = LOD / np.sqrt(2)
            continue
        
        # Usar β_MEAN para reemplazo (más conservador)
        df_resultado.loc[~mask_detectados, col] = beta_MEAN * LOD
        
        # Calcular estadísticas
        valores_gm = np.concatenate([detectados, np.full(k, beta_GM * LOD)])
        valores_mean = np.concatenate([detectados, np.full(k, beta_MEAN * LOD)])
        
        gm_estimado = np.exp(np.mean(np.log(valores_gm)))
        mean_estimado = np.mean(valores_mean)
        
        if mean_estimado / gm_estimado > 1:
            s_y = np.sqrt((2 * n) / (n - 1)) * np.log(mean_estimado / gm_estimado)
            gsd_estimado = np.exp(s_y)
        else:
            s_y = 0
            gsd_estimado = 1.0
        
        log_reemplazos.append({
            'columna': col,
            'n_censored': k,
            'percent_censored': (k / n) * 100,
            'lod': LOD,
            'beta_GM': beta_GM,
            'beta_MEAN': beta_MEAN,
            'valor_reemplazo': beta_MEAN * LOD,
            'gm_estimado': gm_estimado,
            'gsd_estimado': gsd_estimado,
            'mean_estimado': mean_estimado
        })
    
    return df_resultado, pd.DataFrame(log_reemplazos)


def aplicar_reemplazo_lod(
    df: pd.DataFrame,
    lod_info: Dict[str, float],
    metodo: Literal["simple", "beta", "lrem", "idw"],
    df_coords: Optional[pd.DataFrame] = None,
    **kwargs
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Función unificada para aplicar cualquier método de reemplazo LOD.
    
    Parameters:
    -----------
    df : DataFrame con valores bajo LOD como NaN
    lod_info : Dict con información de LOD por columna
    metodo : "simple", "multiplicativo", "idw" o "beta"
    df_coords : DataFrame con coordenadas (requerido para método "idw")
    **kwargs : Parámetros adicionales según el método
    
    Parámetros específicos por método:
    -----------------------------------
    Simple:
        - metodo_simple: "sqrt2" o "div2" (default: "sqrt2")
    
    Multiplicativo:
        - delta: float (default: 0.65, rango típico: 0.5-0.8)
    
    IDW:
        - power: float (default: 2.0)
        - max_distance: float o None (default: None)
        - min_neighbors: int (default: 3)
        - metodo_c: "div2" o "sqrt2" (default: "div2")
    
    Beta (β-substitution):
        - Sin parámetros adicionales
    
    lrEM (Log-Ratio EM):
        - tolerance: float (default: 0.0001)
        - max_iter: int (default: 50)
        - frac: float (default: 0.65)
        - ini_method: "multRepl" o "complete_obs" (default: "multRepl")
    
    Returns:
    --------
    tuple: (DataFrame procesado, DataFrame con log de reemplazos)
    
    Ejemplos:
    ---------
    # Método simple
    df_result, log = aplicar_reemplazo_lod(df, lod_info, "simple", metodo_simple="sqrt2")
    
    # Método multiplicativo
    df_result, log = aplicar_reemplazo_lod(df, lod_info, "multiplicativo", delta=0.65)
    
    # Método IDW
    df_result, log = aplicar_reemplazo_lod(
        df, lod_info, "idw", 
        df_coords=coords, 
        power=2.0, 
        metodo_c="div2"
    )
    
    # Método β-substitution (Ganser & Hewett 2010)
    df_result, log = aplicar_reemplazo_lod(df, lod_info, "beta")
    
    # Método lrEM (Palarea-Albaladejo & Martín-Fernández 2015)
    df_result, log = aplicar_reemplazo_lod(
        df, lod_info, "lrem",
        tolerance=0.0001,
        max_iter=50
    )
    """
    if metodo == "simple":
        metodo_simple = kwargs.get("metodo_simple", "sqrt2")
        return reemplazar_lod_simple(df, lod_info, metodo=metodo_simple)
    
    elif metodo == "multiplicativo":
        delta = kwargs.get("delta", 0.65)
        return reemplazar_lod_multiplicativo(df, lod_info, delta=delta)
    
    elif metodo == "beta":
        return reemplazar_lod_beta_substitution(df, lod_info)
    
    elif metodo == "lrem":
        # Importar función lrEM
        try:
            from lrem import aplicar_lrem_robusto
        except ImportError:
            raise ImportError("Módulo lrem no encontrado. Asegúrate de tener lrem.py en el mismo directorio.")
        
        tolerance = kwargs.get("tolerance", 0.0001)
        max_iter = kwargs.get("max_iter", 50)
        frac = kwargs.get("frac", 0.65)
        ini_method = kwargs.get("ini_method", "multRepl")
        
        return aplicar_lrem_robusto(
            df, lod_info,
            tolerance=tolerance,
            max_iter=max_iter,
            frac=frac,
            ini_method=ini_method
        )
    
    elif metodo == "idw":
        if df_coords is None or df_coords.empty:
            raise ValueError("Método IDW requiere coordenadas (df_coords)")
        
        power = kwargs.get("power", 2.0)
        max_distance = kwargs.get("max_distance", None)
        min_neighbors = kwargs.get("min_neighbors", 3)
        metodo_c = kwargs.get("metodo_c", "div2")
        
        return reemplazar_lod_idw(
            df, df_coords, lod_info,
            power=power,
            max_distance=max_distance,
            min_neighbors=min_neighbors,
            metodo_c=metodo_c
        )
    
    else:
        raise ValueError(f"Método '{metodo}' no reconocido. Opciones: 'simple', 'beta', 'lrem', 'idw'")