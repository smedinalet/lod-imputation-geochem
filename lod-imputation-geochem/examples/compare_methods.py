"""
Compare different imputation methods
"""

from lod_imputation import cargar_csv, detectar_lod, extraer_coordenadas, aplicar_reemplazo_lod
import pandas as pd

# Load data
df = cargar_csv('your_data.csv')
df_clean, lod_info = detectar_lod(df)
df_geo, df_coords = extraer_coordenadas(df_clean)

# Apply all methods
methods = ['simple', 'beta', 'lrem']
results = {}

for method in methods:
    print(f"\nApplying {method}...")
    df_result, log = aplicar_reemplazo_lod(df_geo, lod_info, method=method)
    results[method] = df_result
    print(f"  Completed: {method}")

# Compare results for a specific element
element = list(lod_info.keys())[0]  # First element with LOD
print(f"\n\nComparison for {element} (LOD = {lod_info[element]}):")

comparison = pd.DataFrame({
    'Sample': df_geo.index,
    'Original': df_geo[element],
    'Simple': results['simple'][element],
    'Beta': results['beta'][element],
    'lrEM': results['lrem'][element]
})

# Show only samples that were below LOD
mask_lod = df_geo[element].isna()
print(comparison[mask_lod])

# Save comparison
comparison.to_csv('methods_comparison.csv', index=False)
print("\n✅ Comparison saved to methods_comparison.csv")
```

---

## 📂 CARPETA RAÍZ (archivos principales)

### **1. `.gitignore`**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*.sublime-project
*.sublime-workspace

# OS
.DS_Store
Thumbs.db
*.bak

# Data files (don't commit user data)
*.csv
*.xlsx
*.xls
!examples/sample_data.csv

# Cache and output
cache/
output/
*.cache
*.log

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Documentation builds
docs/_build/
docs/.doctrees/