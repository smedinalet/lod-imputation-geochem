"""
LOD Imputation Methods for Geochemical Data

A library for handling left-censored geochemical data with multiple
statistical imputation methods.

Methods available:
- Simple substitution with controlled variance
- β-substitution (Ganser & Hewett, 2010)
- Log-Ratio EM (Palarea-Albaladejo & Martín-Fernández, 2015)
- Spatial IDW with quadratic weighting

Developed with assistance from Claude (Anthropic).
"""

__version__ = "0.1.0"
__author__ = "Tu Nombre"
__email__ = "tu.email@example.com"

from .reader import cargar_csv, detectar_lod, extraer_coordenadas
from .imputation import aplicar_reemplazo_lod

__all__ = [
    'cargar_csv',
    'detectar_lod',
    'extraer_coordenadas',
    'aplicar_reemplazo_lod'
]