"""
Sistema de organización de archivos de salida para Eutectik App
Maneja la creación de carpetas y guardado organizado de resultados
"""

import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Optional, Dict, List

class GestorArchivos:
    """
    Gestiona la organización de archivos de entrada/salida del proyecto.
    
    Estructura de carpetas:
    ----------------------
    eutectik/
    ├── data/
    │   ├── raw/              # Datos originales
    │   ├── processed/        # Datos procesados (resultados de imputación)
    │   └── logs/             # Logs de operaciones
    ├── cache/                # Archivos temporales/prueba
    │   ├── test_data/        # Datos de prueba generados
    │   └── temp/             # Archivos temporales
    └── output/               # Resultados finales por sesión
        └── YYYYMMDD_HHMMSS/  # Carpeta por fecha/hora de ejecución
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Inicializa el gestor de archivos.
        
        Parameters:
        -----------
        base_dir : str, optional
            Directorio base del proyecto. Si es None, usa el directorio actual.
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self._crear_estructura()
    
    def _crear_estructura(self):
        """Crea la estructura de carpetas si no existe."""
        carpetas = [
            'data/raw',
            'data/processed',
            'data/logs',
            'cache/test_data',
            'cache/temp',
            'output'
        ]
        
        for carpeta in carpetas:
            (self.base_dir / carpeta).mkdir(parents=True, exist_ok=True)
    
    def obtener_ruta_cache(self, tipo: str = 'temp') -> Path:
        """
        Obtiene la ruta de una carpeta de caché.
        
        Parameters:
        -----------
        tipo : str
            'test_data' o 'temp'
        
        Returns:
        --------
        Path : Ruta completa a la carpeta de caché
        """
        return self.base_dir / 'cache' / tipo
    
    def obtener_ruta_data(self, tipo: str = 'processed') -> Path:
        """
        Obtiene la ruta de una carpeta de datos.
        
        Parameters:
        -----------
        tipo : str
            'raw', 'processed', o 'logs'
        
        Returns:
        --------
        Path : Ruta completa a la carpeta de datos
        """
        return self.base_dir / 'data' / tipo
    
    def crear_sesion_output(self, nombre_sesion: Optional[str] = None) -> Path:
        """
        Crea una carpeta para una sesión de procesamiento.
        
        Parameters:
        -----------
        nombre_sesion : str, optional
            Nombre personalizado. Si es None, usa timestamp.
        
        Returns:
        --------
        Path : Ruta a la carpeta de la sesión
        """
        if nombre_sesion is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_sesion = timestamp
        
        ruta_sesion = self.base_dir / 'output' / nombre_sesion
        ruta_sesion.mkdir(parents=True, exist_ok=True)
        
        return ruta_sesion
    
    def guardar_datos_prueba(self, df: pd.DataFrame, nombre: str = 'datos_prueba_geoquimicos.csv'):
        """
        Guarda datos de prueba en cache/test_data.
        
        Parameters:
        -----------
        df : DataFrame
            Datos a guardar
        nombre : str
            Nombre del archivo
        """
        ruta = self.obtener_ruta_cache('test_data') / nombre
        df.to_csv(ruta, index=False)
        print(f"✅ Datos de prueba guardados: {ruta}")
        return ruta
    
    def guardar_resultados_imputacion(
        self,
        resultados: Dict[str, pd.DataFrame],
        logs: Dict[str, pd.DataFrame],
        sesion: Optional[str] = None
    ) -> Path:
        """
        Guarda todos los resultados de imputación organizadamente.
        
        Parameters:
        -----------
        resultados : dict
            {'simple': df_simple, 'multiplicativo': df_mult, 'idw': df_idw}
        logs : dict
            {'simple': log_simple, 'multiplicativo': log_mult, 'idw': log_idw}
        sesion : str, optional
            Nombre de la sesión
        
        Returns:
        --------
        Path : Ruta a la carpeta de la sesión
        """
        # Crear carpeta de sesión
        ruta_sesion = self.crear_sesion_output(sesion)
        
        # Guardar resultados
        for metodo, df in resultados.items():
            if df is not None:
                archivo = ruta_sesion / f'resultado_{metodo}.csv'
                df.to_csv(archivo, index=False)
                print(f"✅ Guardado: {archivo.name}")
        
        # Guardar logs
        carpeta_logs = ruta_sesion / 'logs'
        carpeta_logs.mkdir(exist_ok=True)
        
        for metodo, log in logs.items():
            if log is not None and not log.empty:
                archivo = carpeta_logs / f'log_{metodo}.csv'
                log.to_csv(archivo, index=False)
                print(f"✅ Log guardado: {archivo.name}")
        
        print(f"\n📁 Todos los archivos guardados en: {ruta_sesion}")
        return ruta_sesion
    
    def guardar_comparacion(
        self,
        df_comparacion: pd.DataFrame,
        sesion: Optional[str] = None
    ):
        """
        Guarda tabla de comparación de métodos.
        
        Parameters:
        -----------
        df_comparacion : DataFrame
            Tabla comparativa de métodos
        sesion : str, optional
            Nombre de la sesión. Si es None, busca la última carpeta en output.
        """
        if sesion is None:
            # Buscar última carpeta en output
            carpetas = sorted((self.base_dir / 'output').glob('*'))
            if carpetas:
                ruta_sesion = carpetas[-1]
            else:
                ruta_sesion = self.crear_sesion_output()
        else:
            ruta_sesion = self.base_dir / 'output' / sesion
        
        archivo = ruta_sesion / 'comparacion_metodos.csv'
        df_comparacion.to_csv(archivo, index=False)
        print(f"✅ Comparación guardada: {archivo}")
        return archivo
    
    def limpiar_cache(self, tipo: str = 'temp'):
        """
        Limpia archivos de caché.
        
        Parameters:
        -----------
        tipo : str
            'temp' (solo temporales) o 'all' (todo el caché)
        """
        if tipo == 'temp':
            carpeta = self.obtener_ruta_cache('temp')
            archivos = list(carpeta.glob('*'))
        else:  # all
            carpeta = self.base_dir / 'cache'
            archivos = list(carpeta.glob('**/*'))
            archivos = [a for a in archivos if a.is_file()]
        
        for archivo in archivos:
            archivo.unlink()
            print(f"🗑️  Eliminado: {archivo.name}")
        
        print(f"✅ Caché limpiado: {len(archivos)} archivos eliminados")
    
    def listar_sesiones(self) -> List[str]:
        """
        Lista todas las sesiones de procesamiento guardadas.
        
        Returns:
        --------
        List[str] : Lista de nombres de sesiones
        """
        carpeta_output = self.base_dir / 'output'
        sesiones = [d.name for d in carpeta_output.glob('*') if d.is_dir()]
        return sorted(sesiones, reverse=True)
    
    def resumen_estructura(self):
        """
        Imprime un resumen de la estructura de archivos.
        """
        print("\n" + "="*60)
        print("📂 ESTRUCTURA DE ARCHIVOS")
        print("="*60)
        
        def contar_archivos(ruta: Path) -> int:
            return len(list(ruta.glob('*'))) if ruta.exists() else 0
        
        secciones = [
            ("📁 Datos Originales", self.base_dir / 'data' / 'raw'),
            ("📊 Datos Procesados", self.base_dir / 'data' / 'processed'),
            ("📝 Logs", self.base_dir / 'data' / 'logs'),
            ("🧪 Datos de Prueba", self.base_dir / 'cache' / 'test_data'),
            ("⏰ Temporales", self.base_dir / 'cache' / 'temp'),
        ]
        
        for nombre, ruta in secciones:
            n_archivos = contar_archivos(ruta)
            print(f"{nombre:.<40} {n_archivos} archivos")
        
        # Sesiones
        sesiones = self.listar_sesiones()
        print(f"{'📦 Sesiones de Output':.<40} {len(sesiones)} sesiones")
        
        if sesiones:
            print("\n  Últimas 3 sesiones:")
            for sesion in sesiones[:3]:
                print(f"    • {sesion}")
        
        print("="*60)


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def inicializar_gestor() -> GestorArchivos:
    """
    Inicializa el gestor de archivos.
    Uso en otros scripts: from utils_output import inicializar_gestor
    """
    gestor = GestorArchivos()
    return gestor


def guardar_sesion_completa(
    resultados: Dict[str, pd.DataFrame],
    logs: Dict[str, pd.DataFrame],
    comparacion: Optional[pd.DataFrame] = None,
    nombre_sesion: Optional[str] = None
) -> Path:
    """
    Guarda una sesión completa de imputación.
    
    Parameters:
    -----------
    resultados : dict
        Diccionario con DataFrames de resultados por método
    logs : dict
        Diccionario con logs por método
    comparacion : DataFrame, optional
        Tabla de comparación de métodos
    nombre_sesion : str, optional
        Nombre personalizado para la sesión
    
    Returns:
    --------
    Path : Ruta a la carpeta de la sesión
    """
    gestor = GestorArchivos()
    
    # Guardar resultados y logs
    ruta_sesion = gestor.guardar_resultados_imputacion(resultados, logs, nombre_sesion)
    
    # Guardar comparación si existe
    if comparacion is not None:
        gestor.guardar_comparacion(comparacion, ruta_sesion.name)
    
    return ruta_sesion


if __name__ == "__main__":
    # Demo del sistema
    gestor = GestorArchivos()
    gestor.resumen_estructura()
    
    print("\n💡 Ejemplo de uso:")
    print("""
    from utils_output import GestorArchivos
    
    # Inicializar
    gestor = GestorArchivos()
    
    # Guardar resultados
    gestor.guardar_resultados_imputacion(
        resultados={'simple': df_simple, 'multiplicativo': df_mult},
        logs={'simple': log_simple, 'multiplicativo': log_mult},
        sesion='analisis_Cu_2024'
    )
    
    # Limpiar caché temporal
    gestor.limpiar_cache('temp')
    """)