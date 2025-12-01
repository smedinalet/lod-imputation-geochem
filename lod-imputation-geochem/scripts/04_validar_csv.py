"""
Script para validar el formato de archivos CSV antes de procesarlos
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

def validar_csv(ruta_archivo):
    """
    Valida que un archivo CSV tenga el formato correcto para Eutectik App.
    
    Parameters:
    -----------
    ruta_archivo : str
        Ruta al archivo CSV
    
    Returns:
    --------
    tuple: (es_valido: bool, errores: list, advertencias: list, info: dict)
    """
    errores = []
    advertencias = []
    info = {}
    
    print("="*70)
    print("VALIDACIÓN DE FORMATO CSV")
    print("="*70)
    print(f"\nArchivo: {ruta_archivo}\n")
    
    # ========================================
    # 1. Verificar que el archivo existe
    # ========================================
    archivo = Path(ruta_archivo)
    if not archivo.exists():
        errores.append(f"❌ El archivo no existe: {ruta_archivo}")
        return False, errores, advertencias, info
    
    print("✅ Archivo encontrado")
    
    # Verificar extensión
    if archivo.suffix.lower() != '.csv':
        advertencias.append(f"⚠️  Extensión no es .csv: {archivo.suffix}")
    
    # ========================================
    # 2. Intentar cargar el archivo
    # ========================================
    try:
        df = pd.read_csv(ruta_archivo)
        print(f"✅ Archivo CSV cargado correctamente")
        print(f"   Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
    except Exception as e:
        errores.append(f"❌ Error al leer CSV: {e}")
        return False, errores, advertencias, info
    
    # ========================================
    # 3. Verificar estructura básica
    # ========================================
    print("\n" + "-"*70)
    print("ESTRUCTURA BÁSICA")
    print("-"*70)
    
    # Verificar que hay columnas
    if len(df.columns) < 2:
        errores.append("❌ El archivo debe tener al menos 2 columnas")
    else:
        print(f"✅ Columnas: {len(df.columns)}")
    
    # Verificar que hay filas
    if len(df) < 5:
        advertencias.append(f"⚠️  Pocas muestras ({len(df)}). Recomendado: ≥ 20")
    else:
        print(f"✅ Muestras: {len(df)}")
    
    # Listar columnas
    print(f"\nColumnas detectadas:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    # ========================================
    # 4. Identificar tipos de columnas
    # ========================================
    print("\n" + "-"*70)
    print("IDENTIFICACIÓN DE COLUMNAS")
    print("-"*70)
    
    # Columnas de identificación (texto)
    cols_id = []
    for col in df.columns:
        if df[col].dtype == 'object':
            # Verificar si es texto o contiene símbolos <
            tiene_lod = df[col].astype(str).str.contains('<', na=False).any()
            if not tiene_lod:
                cols_id.append(col)
    
    if cols_id:
        print(f"✅ Columnas de identificación: {', '.join(cols_id)}")
        info['cols_identificacion'] = cols_id
    else:
        advertencias.append("⚠️  No se detectaron columnas de identificación (recomendado)")
    
    # Columnas de coordenadas
    cols_coord = []
    coord_keywords = ['utm_e', 'utm_n', 'easting', 'northing', 'x', 'y']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in coord_keywords):
            if pd.api.types.is_numeric_dtype(df[col]):
                cols_coord.append(col)
    
    if len(cols_coord) >= 2:
        print(f"✅ Columnas de coordenadas: {', '.join(cols_coord[:2])}")
        info['cols_coordenadas'] = cols_coord[:2]
        info['metodo_idw_disponible'] = True
    else:
        advertencias.append("⚠️  No se detectaron coordenadas. Método IDW no disponible.")
        info['metodo_idw_disponible'] = False
    
    # Columnas geoquímicas (con posibles LOD)
    cols_geo = []
    lod_detectados = {}
    
    for col in df.columns:
        if col not in cols_id and col not in cols_coord:
            # Verificar si es numérica o contiene valores <LOD
            tiene_lod = df[col].astype(str).str.contains('<', na=False).any()
            es_numerica = pd.api.types.is_numeric_dtype(df[col])
            
            if tiene_lod or es_numerica:
                cols_geo.append(col)
                
                # Detectar LODs
                if tiene_lod:
                    valores_lod = df[col].astype(str).str.extract(r'<\s*(\d+\.?\d*)')[0]
                    valores_lod = valores_lod.dropna().astype(float)
                    if len(valores_lod) > 0:
                        lod_detectados[col] = valores_lod.max()
    
    if cols_geo:
        print(f"✅ Columnas geoquímicas: {len(cols_geo)}")
        for col in cols_geo:
            n_total = len(df[col])
            n_lod = df[col].astype(str).str.contains('<', na=False).sum()
            n_null = df[col].isna().sum()
            n_valid = n_total - n_lod - n_null
            
            info_str = f"   • {col}: {n_valid} detectados"
            if n_lod > 0:
                pct_lod = (n_lod / n_total) * 100
                info_str += f", {n_lod} bajo LOD ({pct_lod:.1f}%)"
                if col in lod_detectados:
                    info_str += f" [LOD={lod_detectados[col]}]"
            if n_null > 0:
                info_str += f", {n_null} nulos"
            
            print(info_str)
        
        info['cols_geoquimicas'] = cols_geo
        info['lod_detectados'] = lod_detectados
    else:
        errores.append("❌ No se detectaron columnas geoquímicas")
    
    # ========================================
    # 5. Validar formato de valores
    # ========================================
    print("\n" + "-"*70)
    print("VALIDACIÓN DE VALORES")
    print("-"*70)
    
    problemas_formato = []
    
    for col in cols_geo:
        # Verificar valores con coma decimal
        tiene_coma = df[col].astype(str).str.contains(',', na=False).any()
        if tiene_coma:
            problemas_formato.append(f"{col}: usa coma (,) en lugar de punto (.)")
        
        # Verificar formato de LOD
        valores = df[col].astype(str)
        lods_mal_formato = valores[
            valores.str.contains('lod|bdl|nd|menor|bajo', case=False, na=False) &
            ~valores.str.contains('<', na=False)
        ]
        if len(lods_mal_formato) > 0:
            problemas_formato.append(f"{col}: valores LOD sin formato '<valor'")
    
    if problemas_formato:
        for problema in problemas_formato:
            errores.append(f"❌ {problema}")
    else:
        print("✅ Formato de valores correcto")
    
    # ========================================
    # 6. Verificar % de censura
    # ========================================
    print("\n" + "-"*70)
    print("ANÁLISIS DE CENSURA")
    print("-"*70)
    
    for col in cols_geo:
        n_total = len(df[col])
        n_lod = df[col].astype(str).str.contains('<', na=False).sum()
        pct_censura = (n_lod / n_total) * 100
        
        if pct_censura > 50:
            advertencias.append(f"⚠️  {col}: {pct_censura:.1f}% censura (>50%). Considerar métodos no paramétricos.")
        elif pct_censura > 0:
            print(f"✅ {col}: {pct_censura:.1f}% censura (aceptable)")
    
    # ========================================
    # 7. Resumen de métodos disponibles
    # ========================================
    print("\n" + "-"*70)
    print("MÉTODOS DISPONIBLES")
    print("-"*70)
    
    metodos = []
    if len(cols_geo) > 0:
        metodos.extend(['Simple', 'β-substitution', 'Multiplicativo (CoDa)'])
        print("✅ Simple (LOD/√2)")
        print("✅ β-substitution (Ganser & Hewett 2010)")
        print("✅ Multiplicativo (CoDa)")
    
    if info.get('metodo_idw_disponible', False):
        metodos.append('IDW Cuadrático')
        print("✅ IDW Cuadrático (requiere coordenadas)")
    else:
        print("⚠️  IDW no disponible (faltan coordenadas)")
    
    info['metodos_disponibles'] = metodos
    
    # ========================================
    # 8. Resumen final
    # ========================================
    print("\n" + "="*70)
    print("RESUMEN DE VALIDACIÓN")
    print("="*70)
    
    es_valido = len(errores) == 0
    
    if es_valido:
        print("\n✅ EL ARCHIVO ES VÁLIDO")
        print(f"\nPuedes procesar este archivo con {len(metodos)} métodos disponibles.")
    else:
        print("\n❌ EL ARCHIVO TIENE ERRORES")
        print("\nErrores encontrados:")
        for error in errores:
            print(f"   {error}")
    
    if advertencias:
        print("\n⚠️  ADVERTENCIAS:")
        for adv in advertencias:
            print(f"   {adv}")
    
    print("\n" + "="*70)
    
    return es_valido, errores, advertencias, info


def ejemplo_csv_correcto():
    """Genera un archivo CSV de ejemplo con formato correcto."""
    
    datos_ejemplo = {
        'Muestra_ID': ['M001', 'M002', 'M003', 'M004', 'M005'],
        'UTM_E': [305234.5, 305456.2, 305678.9, 305901.6, 306124.3],
        'UTM_N': [6201234.8, 6201567.3, 6201890.1, 6202213.5, 6202536.9],
        'Cu': [45.3, '<10', 78.9, 123.4, '<10'],
        'Zn': [120.5, 95.2, '<50', 180.3, 210.7],
        'Pb': ['<5', 8.4, 12.6, '<5', 15.8],
        'Au': [0.125, '<0.01', 0.089, '<0.01', 0.234]
    }
    
    df = pd.DataFrame(datos_ejemplo)
    df.to_csv('ejemplo_formato_correcto.csv', index=False)
    
    print("✅ Archivo de ejemplo creado: ejemplo_formato_correcto.csv")
    print("   Puedes usarlo como referencia para formatear tus datos.\n")


if __name__ == "__main__":
    import sys
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "VALIDADOR DE FORMATO CSV - EUTECTIK" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    # Verificar si se proporcionó archivo
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        es_valido, errores, advertencias, info = validar_csv(archivo)
    else:
        print("📝 Uso:")
        print("   python 04_validar_csv.py ruta/a/tu/archivo.csv")
        print()
        print("¿Quieres generar un archivo CSV de ejemplo? (s/n): ", end="")
        respuesta = input().strip().lower()
        
        if respuesta == 's':
            ejemplo_csv_correcto()
        else:
            print("\n💡 Ejecuta el script con la ruta a tu archivo CSV para validarlo.")
            print("   Ejemplo: python 04_validar_csv.py datos.csv")