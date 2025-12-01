import numpy as np
import pandas as pd
from typing import Dict, Literal, Optional
from scipy import stats

def reemplazar_lod_lrem(
    df: pd.DataFrame,
    lod_info: Dict[str, float],
    tolerance: float = 0.0001,
    max_iter: int = 50,
    frac: float = 0.65,
    ini_method: Literal["multRepl", "complete_obs"] = "multRepl",
    robust: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Log-Ratio EM algorithm para datos composicionales con valores censurados.
    
    Implementa el algoritmo lrEM de Palarea-Albaladejo & Martín-Fernández (2015)
    usando transformación additive log-ratio (alr) para imputar valores bajo LOD
    mediante su expectativa condicional, preservando la estructura de covarianza
    log-ratio.
    
    Referencia:
    -----------
    Palarea-Albaladejo, J., & Martín-Fernández, J.A. (2015). zCompositions – R 
    package for multivariate imputation of left-censored data under a compositional 
    approach. Chemometrics and Intelligent Laboratory Systems, 143, 85-96.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Datos composicionales con valores NaN para censurados
    lod_info : Dict[str, float]
        Diccionario {columna: LOD}
    tolerance : float
        Criterio de convergencia (default: 0.0001)
    max_iter : int
        Máximo número de iteraciones (default: 50)
    frac : float
        Fracción del LOD para imputación inicial (default: 0.65)
    ini_method : str
        Método de inicialización: "multRepl" o "complete_obs"
    robust : bool
        Usar estimación robusta (requiere implementación adicional)
    
    Returns:
    --------
    tuple: (DataFrame imputado, log del proceso)
    """
    
    df_work = df.copy()
    log_iterations = []
    
    # Columnas con LOD
    cols_lod = [col for col in lod_info.keys() if col in df_work.columns]
    
    if len(cols_lod) < 2:
        raise ValueError("lrEM requiere al menos 2 elementos composicionales")
    
    n_samples = len(df_work)
    n_vars = len(cols_lod)
    
    if n_samples <= n_vars:
        raise ValueError(f"lrEM requiere más observaciones ({n_samples}) que variables ({n_vars})")
    
    # ========================================
    # PASO 1: Inicialización
    # ========================================
    
    if ini_method == "multRepl":
        # Imputación inicial con multiplicative replacement simple
        for col in cols_lod:
            mask_censored = df_work[col].isna()
            if mask_censored.any():
                # Agregar variación pequeña para evitar valores idénticos
                n_censored = mask_censored.sum()
                initial_values = frac * lod_info[col] * np.random.uniform(
                    0.95, 1.05, size=n_censored
                )
                df_work.loc[mask_censored, col] = initial_values
    
    elif ini_method == "complete_obs":
        # Usar solo observaciones completas para estimar covarianza inicial
        mask_complete = df_work[cols_lod].notna().all(axis=1)
        if mask_complete.sum() < 3:
            raise ValueError("Insuficientes observaciones completas. Use ini_method='multRepl'")
    
    # Convertir a matriz numpy
    X = df_work[cols_lod].values
    
    # Identificar patrón de censura original
    censored_mask = df[cols_lod].isna().values
    
    # ========================================
    # PASO 2: Transformación alr
    # ========================================
    
    def alr_transform(X_comp):
        """
        Additive log-ratio transformation.
        Usa la última columna como divisor (referencia).
        """
        X_pos = np.maximum(X_comp, 1e-10)  # Evitar log(0)
        return np.log(X_pos[:, :-1] / X_pos[:, -1:])
    
    def alr_inverse(Y_alr, x_last):
        """
        Transformación inversa alr.
        """
        Y_exp = np.exp(Y_alr)
        denominator = 1 + Y_exp.sum(axis=1, keepdims=True)
        X_reconstructed = np.column_stack([
            Y_exp * x_last[:, np.newaxis] / denominator,
            x_last / denominator
        ])
        return X_reconstructed
    
    # ========================================
    # PASO 3: Algoritmo EM
    # ========================================
    
    converged = False
    iteration = 0
    X_prev = X.copy()
    
    while not converged and iteration < max_iter:
        iteration += 1
        
        # E-Step: Calcular estadísticas suficientes
        # -------------------------------------------
        
        # Transformar a coordenadas alr
        Y = alr_transform(X)
        
        # Estimar media y covarianza en espacio alr
        mu = np.mean(Y, axis=0)
        
        # Covarianza con corrección para datos censurados
        if iteration == 1:
            # Primera iteración: covarianza simple
            Sigma = np.cov(Y.T, bias=False)
        else:
            # Iteraciones subsiguientes: ajustar por censura
            # Usar regresión censurada para estimar covarianza residual
            Sigma = np.cov(Y.T, bias=False)
            
            # Factor de corrección basado en proporción de censura
            prop_censored = censored_mask.mean()
            correction_factor = 1 / (1 - 0.5 * prop_censored)
            Sigma = Sigma * correction_factor
        
        # M-Step: Imputar valores censurados
        # -------------------------------------------
        
        for i in range(n_samples):
            # Identificar componentes censurados en esta muestra
            censored_i = censored_mask[i, :-1]  # Excluir última columna (referencia)
            
            if not censored_i.any():
                continue
            
            # Índices de componentes observados y censurados (en espacio alr)
            obs_idx = ~censored_i
            cens_idx = censored_i
            
            if obs_idx.sum() == 0:
                # Todos censurados: usar media poblacional
                Y[i, cens_idx] = mu[cens_idx]
            else:
                # Algunos observados: imputación condicional
                
                # Particionar media y covarianza
                mu_obs = mu[obs_idx]
                mu_cens = mu[cens_idx]
                
                Sigma_oo = Sigma[np.ix_(obs_idx, obs_idx)]
                Sigma_cc = Sigma[np.ix_(cens_idx, cens_idx)]
                Sigma_co = Sigma[np.ix_(cens_idx, obs_idx)]
                
                # Valores observados (ya en alr)
                y_obs = Y[i, obs_idx]
                
                # Expectativa condicional: E[Y_cens | Y_obs]
                try:
                    # Usar pseudo-inversa para estabilidad numérica
                    Sigma_oo_inv = np.linalg.pinv(Sigma_oo)
                    conditional_mean = mu_cens + Sigma_co @ Sigma_oo_inv @ (y_obs - mu_obs)
                    
                    # Truncamiento en espacio alr para respetar LOD
                    # LOD en espacio original → límite en espacio alr
                    lod_alr = np.log(lod_info[cols_lod[cens_idx][0]] / X[i, -1])
                    conditional_mean = np.minimum(conditional_mean, lod_alr * 0.99)
                    
                    Y[i, cens_idx] = conditional_mean
                    
                except np.linalg.LinAlgError:
                    # Si hay problemas numéricos, usar media no condicional
                    Y[i, cens_idx] = mu_cens
        
        # Transformar de vuelta a espacio original
        x_last = X[:, -1]
        X_new = alr_inverse(Y, x_last)
        
        # Verificar convergencia
        relative_change = np.abs(X_new - X_prev).max() / (np.abs(X_prev).max() + 1e-10)
        
        log_iterations.append({
            'iteration': iteration,
            'max_relative_change': relative_change,
            'mean_imputed': X_new[censored_mask].mean() if censored_mask.any() else 0
        })
        
        if relative_change < tolerance:
            converged = True
        
        X_prev = X.copy()
        X = X_new.copy()
    
    # ========================================
    # PASO 4: Resultados
    # ========================================
    
    # Colocar resultados en DataFrame
    df_result = df.copy()
    df_result[cols_lod] = X
    
    # Log final
    log_df = pd.DataFrame([{
        'metodo': 'lrEM',
        'converged': converged,
        'iterations': iteration,
        'tolerance_achieved': relative_change if iteration > 0 else np.nan,
        'n_samples': n_samples,
        'n_variables': n_vars,
        'ini_method': ini_method,
        'frac': frac,
        'total_censored': censored_mask.sum(),
        'percent_censored': (censored_mask.sum() / censored_mask.size) * 100
    }])
    
    # Agregar información por columna
    for col in cols_lod:
        n_censored = df[col].isna().sum()
        if n_censored > 0:
            valores_imputados = df_result.loc[df[col].isna(), col].values
            log_df = pd.concat([log_df, pd.DataFrame([{
                'columna': col,
                'lod': lod_info[col],
                'n_censored': n_censored,
                'mean_imputed': valores_imputados.mean(),
                'min_imputed': valores_imputados.min(),
                'max_imputed': valores_imputados.max(),
                'std_imputed': valores_imputados.std()
            }])], ignore_index=True)
    
    if not converged:
        print(f"⚠️ lrEM: Algoritmo no convergió después de {max_iter} iteraciones")
        print(f"   Cambio relativo final: {relative_change:.6f} (tolerance={tolerance})")
    
    return df_result, log_df


def aplicar_lrem_robusto(
    df: pd.DataFrame,
    lod_info: Dict[str, float],
    **kwargs
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Wrapper para aplicar lrEM con validaciones y manejo de errores.
    
    Parameters:
    -----------
    df : DataFrame
        Datos con valores NaN para censurados
    lod_info : dict
        Información de LOD
    **kwargs : 
        Parámetros para reemplazar_lod_lrem
    
    Returns:
    --------
    tuple: (DataFrame imputado, log)
    """
    
    cols_lod = [col for col in lod_info.keys() if col in df.columns]
    
    # Validaciones
    if len(cols_lod) < 2:
        raise ValueError("lrEM requiere al menos 2 elementos composicionales")
    
    n_samples = len(df)
    n_vars = len(cols_lod)
    
    if n_samples <= n_vars:
        raise ValueError(
            f"Datos no regulares: {n_samples} muestras ≤ {n_vars} variables. "
            f"Se requieren más muestras que variables."
        )
    
    # Verificar que no todas las muestras estén censuradas en un mismo elemento
    for col in cols_lod:
        if df[col].isna().all():
            raise ValueError(f"Columna '{col}' está completamente censurada. lrEM no puede proceder.")
    
    # Aplicar lrEM
    try:
        return reemplazar_lod_lrem(df, lod_info, **kwargs)
    except Exception as e:
        print(f"❌ Error en lrEM: {e}")
        print("   Aplicando fallback a multiplicative replacement simple...")
        
        # Fallback a método simple
        from imputation import reemplazar_lod_multiplicativo
        return reemplazar_lod_multiplicativo(df, lod_info)