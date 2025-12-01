"""
Basic workflow example for LOD imputation
"""

from lod_imputation import cargar_csv, detectar_lod, extraer_coordenadas, aplicar_reemplazo_lod

# 1. Load your geochemical data
df = cargar_csv('your_data.csv')
print(f"Loaded {len(df)} samples")

# 2. Detect LODs automatically
df_clean, lod_info = detectar_lod(df)
print(f"\nLODs detected: {lod_info}")

# 3. Separate coordinates from geochemical data
df_geo, df_coords = extraer_coordenadas(df_clean)

# 4. Apply imputation method
# Option A: β-substitution (recommended for general use)
df_result, log = aplicar_reemplazo_lod(df_geo, lod_info, method='beta')

# Option B: lrEM (recommended for compositional data analysis)
# df_result, log = aplicar_reemplazo_lod(df_geo, lod_info, method='lrem')

# Option C: IDW (if you have spatial data)
# df_result, log = aplicar_reemplazo_lod(
#     df_geo, lod_info, method='idw',
#     df_coords=df_coords,
#     power=2.0
# )

# 5. Examine results
print("\nImputation log:")
print(log)

# 6. Save results
df_result.to_csv('imputed_data.csv', index=False)
log.to_csv('imputation_log.csv', index=False)

print("\n✅ Imputation completed!")