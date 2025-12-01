"""
Script de prueba para el sistema de reemplazo LOD
Ahora con organización automática de archivos
"""

print("="*60)
print("PRUEBA DEL SISTEMA DE REEMPLAZO LOD")
print("="*60)

# ========================================
# PASO 0: Inicializar gestor de archivos
# ========================================
print("\n[PASO 0] Inicializando sistema de archivos...")

try:
    from utils_output import GestorArchivos
    gestor = GestorArchivos()
    print("✅ Gestor de archivos inicializado")
    gestor.resumen_estructura()
except ImportError:
    print("⚠️  utils_output.py no encontrado. Los archivos se guardarán en el directorio actual.")
    gestor = None

# ========================================
# PASO 1: Importar las funciones necesarias
# ========================================
print("\n[PASO 1] Importando funciones...")

try:
    from reader import cargar_csv, detectar_lod, extraer_coordenadas
    from imputation import aplicar_reemplazo_lod
    print("✅ Importaciones exitosas")
except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("\nAsegúrate de que:")
    print("  1. Los archivos reader.py e imputation.py estén en la misma carpeta")
    print("  2. Has instalado las dependencias: pip install pandas numpy scipy")
    exit(1)

# ========================================
# PASO 2: Cargar datos de prueba
# ========================================
print("\n[PASO 2] Cargando datos de prueba...")

try:
    # Buscar archivo en cache si existe gestor
    if gestor:
        archivo = gestor.obtener_ruta_cache('test_data') / 'datos_prueba_geoquimicos.csv'
    else:
        archivo = 'datos_prueba_geoquimicos.csv'
    
    df_original = cargar_csv(str(archivo))
    print(f"✅ Datos cargados: {len(df_original)} muestras, {len(df_original.columns)} columnas")
    print(f"   Columnas: {list(df_original.columns)}")
except FileNotFoundError:
    print(f"❌ No se encontró el archivo '{archivo}'")
    print("\n👉 Primero ejecuta: python 01_crear_datos_prueba.py")
    exit(1)
except Exception as e:
    print(f"❌ Error al cargar datos: {e}")
    exit(1)

# ========================================
# PASO 3: Detectar valores bajo LOD
# ========================================
print("\n[PASO 3] Detectando valores bajo LOD...")

df_procesado, lod_info = detectar_lod(df_original)

print(f"✅ LOD detectados en {len(lod_info)} elementos:")
for elemento, lod_value in lod_info.items():
    n_bajo_lod = df_procesado[elemento].isna().sum()
    print(f"   • {elemento}: LOD = {lod_value} (detectados {n_bajo_lod} valores bajo LOD)")

# ========================================
# PASO 4: Separar coordenadas de datos geoquímicos
# ========================================
print("\n[PASO 4] Separando coordenadas...")

df_geo, df_coords = extraer_coordenadas(df_procesado)

print(f"✅ Datos separados:")
print(f"   • Datos geoquímicos: {df_geo.shape}")
print(f"   • Coordenadas: {df_coords.shape}")

# ========================================
# Preparar diccionarios para resultados
# ========================================
resultados = {}
logs = {}

# ========================================
# PASO 5: Probar MÉTODO SIMPLE
# ========================================
print("\n" + "="*60)
print("[PASO 5] Probando MÉTODO SIMPLE (LOD/√2)")
print("="*60)

try:
    df_simple, log_simple = aplicar_reemplazo_lod(
        df_geo, 
        lod_info, 
        metodo="simple",
        metodo_simple="sqrt2"
    )
    
    print("✅ Método simple aplicado exitosamente")
    print("\n--- Log de reemplazos ---")
    print(log_simple.to_string(index=False))
    
    # Verificar que no hay NaN
    n_nan_restantes = df_simple.isna().sum().sum()
    print(f"\n✅ Valores NaN restantes: {n_nan_restantes} (debería ser 0)")
    
    # Verificar media
    print("\n📊 Verificación de medias:")
    for _, row in log_simple.iterrows():
        print(f"   {row['columna']}: Media objetivo={row['valor_central_objetivo']:.4f}, "
              f"Obtenida={row['media_obtenida']:.4f}, "
              f"Desviación={row['desviacion_de_media_%']:.2f}%")
    
    resultados['simple'] = df_simple
    logs['simple'] = log_simple
    
except Exception as e:
    print(f"❌ Error en método simple: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# PASO 6: Probar MÉTODO MULTIPLICATIVO (CoDa)
# ========================================
print("\n" + "="*60)
print("[PASO 6] Probando MÉTODO MULTIPLICATIVO (CoDa)")
print("="*60)

try:
    df_mult, log_mult = aplicar_reemplazo_lod(
        df_geo,
        lod_info,
        metodo="multiplicativo",
        delta=0.65
    )
    
    print("✅ Método multiplicativo aplicado exitosamente")
    print("\n--- Log de reemplazos ---")
    print(log_mult.to_string(index=False))
    
    # Verificar que no hay NaN
    n_nan_restantes = df_mult.isna().sum().sum()
    print(f"\n✅ Valores NaN restantes: {n_nan_restantes} (debería ser 0)")
    
    resultados['multiplicativo'] = df_mult
    logs['multiplicativo'] = log_mult
    
except Exception as e:
    print(f"❌ Error en método multiplicativo: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# PASO 7: Probar MÉTODO ESPACIAL (IDW Cuadrático)
# ========================================
print("\n" + "="*60)
print("[PASO 7] Probando MÉTODO ESPACIAL (IDW Cuadrático)")
print("="*60)

if df_coords.empty:
    print("⚠️  No hay coordenadas disponibles. Saltando método espacial.")
else:
    try:
        df_idw, log_idw = aplicar_reemplazo_lod(
            df_geo,
            lod_info,
            metodo="idw",
            df_coords=df_coords,
            power=2.0,
            max_distance=None,
            min_neighbors=3,
            metodo_c="div2"  # Método conservador
        )
        
        print("✅ Método IDW aplicado exitosamente")
        print("\n--- Log de reemplazos (primeros 10) ---")
        print(log_idw.head(10).to_string(index=False))
        
        # Verificar que no hay NaN
        n_nan_restantes = df_idw.isna().sum().sum()
        print(f"\n✅ Valores NaN restantes: {n_nan_restantes} (debería ser 0)")
        
        resultados['idw'] = df_idw
        logs['idw'] = log_idw
        
    except Exception as e:
        print(f"❌ Error en método IDW: {e}")
        import traceback
        traceback.print_exc()

# ========================================
# PASO 8: Comparar resultados
# ========================================
print("\n" + "="*60)
print("[PASO 8] Comparando resultados de los métodos")
print("="*60)

import pandas as pd

comparacion_df = None

if lod_info:
    elemento_comparar = list(lod_info.keys())[0]
    
    print(f"\n📊 Comparación para elemento: {elemento_comparar}")
    print(f"   LOD = {lod_info[elemento_comparar]}")
    
    comparacion = pd.DataFrame({
        'Muestra': df_original['Muestra_ID'] if 'Muestra_ID' in df_original.columns else range(len(df_geo)),
        'Original': df_original[elemento_comparar] if elemento_comparar in df_original.columns else df_geo[elemento_comparar],
    })
    
    if 'simple' in resultados:
        comparacion['Simple'] = resultados['simple'][elemento_comparar]
    if 'multiplicativo' in resultados:
        comparacion['Multiplicativo'] = resultados['multiplicativo'][elemento_comparar]
    if 'idw' in resultados:
        comparacion['IDW'] = resultados['idw'][elemento_comparar]
    
    # Mostrar solo filas que tenían valores bajo LOD
    mask_lod = df_geo[elemento_comparar].isna()
    print("\n--- Muestras que estaban bajo LOD ---")
    print(comparacion[mask_lod].to_string(index=False))
    
    comparacion_df = comparacion[mask_lod].copy()

# ========================================
# PASO 9: Guardar resultados ORGANIZADAMENTE
# ========================================
print("\n" + "="*60)
print("[PASO 9] Guardando resultados")
print("="*60)

try:
    if gestor:
        # Usar gestor para guardar organizadamente
        from datetime import datetime
        nombre_sesion = f"prueba_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        ruta_sesion = gestor.guardar_resultados_imputacion(
            resultados=resultados,
            logs=logs,
            sesion=nombre_sesion
        )
        
        if comparacion_df is not None:
            gestor.guardar_comparacion(comparacion_df, nombre_sesion)
        
        print(f"\n📁 Todos los archivos organizados en:")
        print(f"   {ruta_sesion}")
        print("\n📂 Estructura creada:")
        print(f"   {ruta_sesion}/")
        print(f"   ├── resultado_simple.csv")
        print(f"   ├── resultado_multiplicativo.csv")
        print(f"   ├── resultado_idw.csv")
        print(f"   ├── comparacion_metodos.csv")
        print(f"   └── logs/")
        print(f"       ├── log_simple.csv")
        print(f"       ├── log_multiplicativo.csv")
        print(f"       └── log_idw.csv")
        
    else:
        # Guardar en directorio actual (método antiguo)
        for metodo, df in resultados.items():
            df.to_csv(f'resultado_metodo_{metodo}.csv', index=False)
        
        for metodo, log in logs.items():
            log.to_csv(f'log_metodo_{metodo}.csv', index=False)
        
        if comparacion_df is not None:
            comparacion_df.to_csv('comparacion_metodos.csv', index=False)
        
        print("✅ Resultados guardados en directorio actual")
    
except Exception as e:
    print(f"❌ Error al guardar resultados: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# RESUMEN FINAL
# ========================================
print("\n" + "="*60)
print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
print("="*60)
print("\n📝 Resumen:")
print(f"   • Muestras procesadas: {len(df_geo)}")
print(f"   • Elementos con LOD: {len(lod_info)}")
print(f"   • Métodos probados: {len(resultados)}")

if gestor:
    print("\n💡 Para ver tus sesiones guardadas:")
    print("   from utils_output import GestorArchivos")
    print("   gestor = GestorArchivos()")
    print("   print(gestor.listar_sesiones())")
    print("\n💡 Para limpiar archivos temporales:")
    print("   gestor.limpiar_cache('temp')")
else:
    print("\n👉 Instala utils_output.py para mejor organización de archivos")