"""
Script para crear datos de prueba geoquímicos
Ahora guarda automáticamente en cache/test_data/
"""

import pandas as pd
import numpy as np

print("="*60)
print("GENERACIÓN DE DATOS DE PRUEBA")
print("="*60)

# Intentar usar el gestor de archivos
try:
    from utils_output import GestorArchivos
    gestor = GestorArchivos()
    usar_gestor = True
    print("✅ Gestor de archivos activo")
except ImportError:
    gestor = None
    usar_gestor = False
    print("⚠️  Gestor no disponible. Guardando en directorio actual.")

# Configurar semilla para reproducibilidad
np.random.seed(42)

# Número de muestras
n_muestras = 20

print(f"\n📊 Generando {n_muestras} muestras de prueba...")

# Crear datos simulados
datos = {
    'Muestra_ID': [f'M{i:03d}' for i in range(1, n_muestras + 1)],
    'UTM_E': np.random.uniform(300000, 310000, n_muestras),
    'UTM_N': np.random.uniform(6200000, 6210000, n_muestras),
    'Cu': [],  # Cobre
    'Zn': [],  # Zinc
    'Pb': [],  # Plomo
    'Au': [],  # Oro
}

# Simular valores con algunos bajo LOD
# LOD típicos: Cu=5, Zn=10, Pb=3, Au=0.005

print("\n🔬 Generando valores con LOD...")
print("   Cu: LOD = 5 ppm (70% detectables)")
print("   Zn: LOD = 10 ppm (80% detectables)")
print("   Pb: LOD = 3 ppm (60% detectables)")
print("   Au: LOD = 0.005 ppm (50% detectables)")

# Cobre (70% detectables, 30% bajo LOD)
for i in range(n_muestras):
    if np.random.random() < 0.7:
        datos['Cu'].append(np.random.uniform(10, 150))
    else:
        datos['Cu'].append('<5')  # Bajo LOD

# Zinc (80% detectables, 20% bajo LOD)
for i in range(n_muestras):
    if np.random.random() < 0.8:
        datos['Zn'].append(np.random.uniform(20, 200))
    else:
        datos['Zn'].append('<10')  # Bajo LOD

# Plomo (60% detectables, 40% bajo LOD)
for i in range(n_muestras):
    if np.random.random() < 0.6:
        datos['Pb'].append(np.random.uniform(5, 80))
    else:
        datos['Pb'].append('<3')  # Bajo LOD

# Oro (50% detectables, 50% bajo LOD)
for i in range(n_muestras):
    if np.random.random() < 0.5:
        datos['Au'].append(np.random.uniform(0.01, 2.5))
    else:
        datos['Au'].append('<0.005')  # Bajo LOD

# Crear DataFrame
df = pd.DataFrame(datos)

print("\n✅ Datos generados exitosamente")

# Guardar CSV
if usar_gestor:
    ruta_guardado = gestor.guardar_datos_prueba(df)
    nombre_archivo = ruta_guardado.name
else:
    nombre_archivo = 'datos_prueba_geoquimicos.csv'
    df.to_csv(nombre_archivo, index=False)
    print(f"✅ Archivo guardado: {nombre_archivo}")

print(f"📁 Archivo: {nombre_archivo}")
print(f"📊 Muestras: {n_muestras}")

print("\n" + "="*60)
print("VISTA PREVIA DE LOS DATOS")
print("="*60)
print(df.head(10).to_string(index=False))

# Mostrar estadísticas de valores bajo LOD
print("\n" + "="*60)
print("ESTADÍSTICAS DE VALORES BAJO LOD")
print("="*60)
for col in ['Cu', 'Zn', 'Pb', 'Au']:
    n_lod = df[col].astype(str).str.contains('<').sum()
    porcentaje = (n_lod / n_muestras) * 100
    lod_value = df[col].astype(str).str.extract(r'<(\d+\.?\d*)')[0].dropna().astype(float).max()
    print(f"{col:>3}: {n_lod:2d} valores bajo LOD ({porcentaje:5.1f}%) | LOD = {lod_value}")

print("\n" + "="*60)
print("✅ GENERACIÓN COMPLETADA")
print("="*60)

if usar_gestor:
    print("\n📂 Los datos se guardaron en: cache/test_data/")
    print("💡 Para limpiar datos de prueba antiguos:")
    print("   from utils_output import GestorArchivos")
    print("   gestor = GestorArchivos()")
    print("   gestor.limpiar_cache('test_data')")
else:
    print("\n💡 Para mejor organización, agrega utils_output.py al proyecto")

print("\n👉 Siguiente paso: python 02_probar_imputation.py")