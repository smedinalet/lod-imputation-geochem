"""
Script de prueba para el método β-substitution (Ganser & Hewett 2010)
Compara todos los métodos disponibles
"""

print("="*70)
print("COMPARACIÓN DE MÉTODOS DE REEMPLAZO LOD")
print("Incluyendo β-substitution (Ganser & Hewett 2010)")
print("="*70)

# ========================================
# Importaciones
# ========================================
print("\n[1] Importando módulos...")

try:
    from reader import cargar_csv, detectar_lod, extraer_coordenadas
    from imputation import aplicar_reemplazo_lod
    import pandas as pd
    import numpy as np
    print("✅ Importaciones exitosas")
except ImportError as e:
    print(f"❌ Error: {e}")
    exit(1)

# Intentar usar gestor de archivos
try:
    from utils_output import GestorArchivos
    gestor = GestorArchivos()
    usar_gestor = True
except ImportError:
    gestor = None
    usar_gestor = False

# ========================================
# Cargar datos
# ========================================
print("\n[2] Cargando datos de prueba...")

try:
    if usar_gestor:
        archivo = gestor.obtener_ruta_cache('test_data') / 'datos_prueba_geoquimicos.csv'
    else:
        archivo = 'datos_prueba_geoquimicos.csv'
    
    df_original = cargar_csv(str(archivo))
    print(f"✅ Datos cargados: {len(df_original)} muestras")
except FileNotFoundError:
    print(f"❌ Archivo no encontrado. Ejecuta primero: python 01_crear_datos_prueba.py")
    exit(1)

# ========================================
# Detectar LOD y separar coordenadas
# ========================================
print("\n[3] Procesando datos...")

df_procesado, lod_info = detectar_lod(df_original)
df_geo, df_coords = extraer_coordenadas(df_procesado)

print(f"✅ LOD detectados: {len(lod_info)} elementos")
for elemento, lod_value in lod_info.items():
    n_lod = df_procesado[elemento].isna().sum()
    print(f"   • {elemento}: LOD={lod_value}, N_censored={n_lod} ({n_lod/len(df_geo)*100:.1f}%)")

# ========================================
# Aplicar TODOS los métodos
# ========================================
print("\n" + "="*70)
print("[4] APLICANDO MÉTODOS DE REEMPLAZO")
print("="*70)

resultados = {}
logs = {}
metodos_info = {
    'simple': {'nombre': 'Simple (LOD/√2)', 'kwargs': {'metodo_simple': 'sqrt2'}},
    'beta': {'nombre': 'β-substitution (Ganser & Hewett 2010)', 'kwargs': {}},
    'lrem': {'nombre': 'Log-Ratio EM (Palarea-Albaladejo 2015)', 'kwargs': {'tolerance': 0.0001, 'max_iter': 50}},
    'idw': {'nombre': 'IDW Cuadrático', 'kwargs': {'power': 2.0, 'metodo_c': 'div2'}}
}

for metodo_id, info in metodos_info.items():
    print(f"\n--- {info['nombre']} ---")
    
    try:
        if metodo_id == 'idw':
            if df_coords.empty:
                print("⚠️  Sin coordenadas. Saltando IDW.")
                continue
            df_result, log = aplicar_reemplazo_lod(
                df_geo, lod_info, metodo_id,
                df_coords=df_coords,
                **info['kwargs']
            )
        else:
            df_result, log = aplicar_reemplazo_lod(
                df_geo, lod_info, metodo_id,
                **info['kwargs']
            )
        
        resultados[metodo_id] = df_result
        logs[metodo_id] = log
        
        print(f"✅ Aplicado exitosamente")
        if not log.empty:
            print("\nLog (primeras 3 columnas):")
            print(log.head(3).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ========================================
# COMPARACIÓN DETALLADA
# ========================================
print("\n" + "="*70)
print("[5] COMPARACIÓN DETALLADA DE RESULTADOS")
print("="*70)

if lod_info and len(resultados) > 0:
    for elemento in lod_info.keys():
        print(f"\n{'='*70}")
        print(f"ELEMENTO: {elemento} (LOD = {lod_info[elemento]})")
        print(f"{'='*70}")
        
        # Identificar muestras bajo LOD
        mask_lod = df_geo[elemento].isna()
        n_lod = mask_lod.sum()
        
        if n_lod == 0:
            print("Sin valores bajo LOD")
            continue
        
        print(f"Valores bajo LOD: {n_lod} de {len(df_geo)} ({n_lod/len(df_geo)*100:.1f}%)")
        
        # Crear tabla comparativa
        comparacion = pd.DataFrame({
            'Muestra': df_original.loc[mask_lod, 'Muestra_ID'] if 'Muestra_ID' in df_original.columns else range(n_lod),
            'Original': df_original.loc[mask_lod, elemento] if elemento in df_original.columns else ['<LOD']*n_lod
        })
        
        for metodo_id, df_result in resultados.items():
            if elemento in df_result.columns:
                comparacion[metodos_info[metodo_id]['nombre']] = df_result.loc[mask_lod, elemento].values
        
        print("\n--- Valores Reemplazados ---")
        print(comparacion.to_string(index=False))
        
        # Estadísticas comparativas
        print("\n--- Estadísticas de Reemplazo ---")
        stats_comp = {}
        for metodo_id, df_result in resultados.items():
            if elemento in df_result.columns:
                valores = df_result.loc[mask_lod, elemento].values
                stats_comp[metodos_info[metodo_id]['nombre']] = {
                    'Media': valores.mean(),
                    'Min': valores.min(),
                    'Max': valores.max(),
                    'Std': valores.std()
                }
        
        df_stats = pd.DataFrame(stats_comp).T
        print(df_stats.to_string())
        
        # Información específica de β-substitution
        if 'beta' in logs and not logs['beta'].empty:
            log_beta = logs['beta'][logs['beta']['columna'] == elemento]
            if not log_beta.empty:
                print("\n--- Detalles β-substitution ---")
                print(f"β_GM:   {log_beta.iloc[0]['beta_GM']:.4f}")
                print(f"β_MEAN: {log_beta.iloc[0]['beta_MEAN']:.4f}")
                print(f"Valor reemplazo: {log_beta.iloc[0]['valor_reemplazo']:.4f}")
                print(f"GM estimado: {log_beta.iloc[0]['gm_estimado']:.4f}")
                print(f"GSD estimado: {log_beta.iloc[0]['gsd_estimado']:.4f}")
                print(f"MEAN estimado: {log_beta.iloc[0]['mean_estimado']:.4f}")

# ========================================
# ANÁLISIS COMPARATIVO GENERAL
# ========================================
print("\n" + "="*70)
print("[6] ANÁLISIS COMPARATIVO DE FACTORES")
print("="*70)

print("\n¿Qué factor se usa en cada método?")
print("-" * 70)
print(f"{'Método':<35} {'Factor':<15} {'Para LOD=5':<15}")
print("-" * 70)
print(f"{'LOD/2':<35} {'0.5000':<15} {'2.5000':<15}")
print(f"{'LOD/√2':<35} {f'{1/np.sqrt(2):.4f}':<15} {f'{5/np.sqrt(2):.4f}':<15}")

if 'beta' in logs and not logs['beta'].empty:
    for _, row in logs['beta'].iterrows():
        col = row['columna']
        lod = row['lod']
        beta_gm = row['beta_GM']
        beta_mean = row['beta_MEAN']
        print(f"{'β-substitution (GM) - ' + col:<35} {f'{beta_gm:.4f}':<15} {f'{beta_gm*lod:.4f}':<15}")
        print(f"{'β-substitution (MEAN) - ' + col:<35} {f'{beta_mean:.4f}':<15} {f'{beta_mean*lod:.4f}':<15}")

print("-" * 70)

# ========================================
# GUARDAR RESULTADOS
# ========================================
print("\n" + "="*70)
print("[7] GUARDANDO RESULTADOS")
print("="*70)

try:
    if usar_gestor:
        from datetime import datetime
        sesion = f"comparacion_beta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ruta = gestor.guardar_resultados_imputacion(resultados, logs, sesion)
        print(f"✅ Resultados guardados en: {ruta}")
    else:
        for metodo, df in resultados.items():
            df.to_csv(f'resultado_{metodo}.csv', index=False)
        for metodo, log in logs.items():
            log.to_csv(f'log_{metodo}.csv', index=False)
        print("✅ Archivos guardados en directorio actual")
except Exception as e:
    print(f"⚠️  Error al guardar: {e}")

# ========================================
# RESUMEN FINAL
# ========================================
print("\n" + "="*70)
print("✅ COMPARACIÓN COMPLETADA")
print("="*70)

print("\n📊 Métodos probados:")
for metodo_id, info in metodos_info.items():
    if metodo_id in resultados:
        print(f"   ✓ {info['nombre']}")

print("\n💡 Recomendaciones según Ganser & Hewett (2010):")
print("   • β-substitution: Comparable a MLE, más fácil de calcular")
print("   • Bias cercano a cero en la mayoría de escenarios")
print("   • Especialmente bueno para muestras pequeñas (n<20)")
print("   • Superior a LOD/2 y LOD/√2 en precisión")

print("\n📚 Referencia:")
print("   Ganser, G.H., & Hewett, P. (2010). An Accurate Substitution Method")
print("   for Analyzing Censored Data. J. Occup. Environ. Hyg., 7:4, 233-244.")
print("   DOI: 10.1080/15459621003609713")