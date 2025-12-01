# Log-Ratio EM Algorithm (lrEM)

## 📖 Descripción

El método **lrEM (Log-Ratio Expectation-Maximization)** es un algoritmo iterativo basado en modelos para imputar datos composicionales censurados (valores bajo LOD). Imputa valores no observados mediante su expectativa condicional a través de representación en coordenadas, incorporando la información de la estructura de covarianza relativa.

## 🎯 ¿Por Qué es Superior al Multiplicativo Simple?

| Aspecto | Multiplicativo Simple | lrEM |
|---------|----------------------|------|
| **Valores imputados** | Todos iguales (δ×LOD) | Únicos, basados en contexto |
| **Usa covarianza** | ❌ No | ✅ Sí |
| **Preserva estructura CoDa** | Parcial | ✅ Completo |
| **Valores repetidos** | ✅ Problema | ❌ No ocurre |
| **Base teórica** | Empírica | Maximum Likelihood |

## 🔬 Cómo Funciona

### Algoritmo Paso a Paso

```
1. Inicialización:
   - Imputar valores censurados con frac×LOD (típicamente 0.65)
   - O usar solo observaciones completas

2. Transformación:
   - Aplicar additive log-ratio (alr) transformation
   - Y = log(X[:, :-1] / X[:, -1])
   
3. E-Step (Expectation):
   - Estimar μ (media) y Σ (covarianza) en espacio alr
   - Aplicar corrección para datos censurados
   
4. M-Step (Maximization):
   - Para cada muestra con censura:
     * Calcular E[Y_censored | Y_observed]
     * Usar distribución condicional multivariada
   
5. Transformación Inversa:
   - Convertir de alr de vuelta a espacio original
   
6. Convergencia:
   - Si cambio < tolerance → STOP
   - Si no → volver a paso 3
```

### Transformación alr

El procedimiento se basa en la transformación oblicua additive log-ratio (alr) para simplificar cálculos y aligerar la carga computacional. Los mismos resultados se obtendrían usando una transformación isometric log-ratio (ilr).

**Fórmula alr:**
```
Y_i = log(X_i / X_D)
```
Donde `X_D` es el componente de referencia (última columna).

### Imputación Condicional

Para una muestra con componentes observados `Y_obs` y censurados `Y_cens`:

```
E[Y_cens | Y_obs] = μ_cens + Σ_co · Σ_oo^(-1) · (Y_obs - μ_obs)
```

Donde:
- `μ_cens`, `μ_obs` = medias de componentes censurados/observados
- `Σ_oo` = covarianza entre observados
- `Σ_co` = covarianza cruzada

## 💻 Uso en Python

### Ejemplo Básico

```python
from lrem import aplicar_lrem_robusto

# Datos con valores NaN para censurados
df_result, log = aplicar_lrem_robusto(
    df,
    lod_info,
    tolerance=0.0001,    # Criterio de convergencia
    max_iter=50,         # Máximo iteraciones
    frac=0.65,           # Fracción para inicialización
    ini_method="multRepl"  # Método de inicialización
)

print(log)
```

### Parámetros

- **tolerance** (float, default=0.0001): Criterio de convergencia
- **max_iter** (int, default=50): Máximo número de iteraciones
- **frac** (float, default=0.65): Fracción del LOD para inicialización
- **ini_method** (str): Método de inicialización
  - `"multRepl"`: Multiplicative simple (recomendado)
  - `"complete_obs"`: Solo observaciones completas

### Integración con Sistema Principal

```python
from imputation import aplicar_reemplazo_lod

df_result, log = aplicar_reemplazo_lod(
    df,
    lod_info,
    metodo="lrem",
    tolerance=0.0001,
    max_iter=50
)
```

## ⚠️ Requisitos y Limitaciones

### Requisitos:

1. **Mínimo 2 variables composicionales**
2. **n > p** (más muestras que variables)
3. **Al menos una columna completa** (sin censura total)

### Casos Especiales:

La imputación condicional basada en coordenadas log-ratio no puede conducirse cuando existen patrones de censura que incluyen muestras con solo un componente observado. Como solución, lrEM aplica multiplicative simple replacement (multRepl) en esos casos.

### Limitaciones:

| Situación | lrEM | Recomendación |
|-----------|------|---------------|
| n ≤ p | ❌ No funciona | Usar β-substitution |
| Una sola variable | ❌ No aplicable | Usar simple o β-substitution |
| >80% censura | ⚠️ Inestable | Revisar diseño analítico |
| Solo 1 observado/muestra | ⚠️ Fallback a multRepl | Automático |

## 📊 Comparación con Otros Métodos

### Ventajas de lrEM:

✅ **No genera valores repetidos**
✅ **Usa estructura de covarianza** entre elementos
✅ **Base teórica sólida** (Maximum Likelihood)
✅ **Preserva propiedades composicionales**
✅ **Validado empíricamente** en literatura

### Cuándo NO usar lrEM:

❌ Pocas muestras (n < 20)
❌ Muchas variables (p cercano a n)
❌ Datos no composicionales
❌ Necesitas rapidez (usa β-substitution)

## 🔬 Validación y Convergencia

### Verificar Convergencia:

```python
df_result, log = aplicar_lrem_robusto(df, lod_info)

# Revisar log
print(f"Convergió: {log['converged'].values[0]}")
print(f"Iteraciones: {log['iterations'].values[0]}")
print(f"Cambio final: {log['tolerance_achieved'].values[0]}")
```

### Qué Hacer si No Converge:

1. **Aumentar max_iter**: `max_iter=100`
2. **Relajar tolerance**: `tolerance=0.001`
3. **Cambiar inicialización**: `ini_method="complete_obs"`
4. **Verificar datos**: ¿Hay outliers extremos?

## 📚 Referencias

### Paper Principal:

```bibtex
@article{palarea2015zcompositions,
  title={zCompositions—R package for multivariate imputation of 
         left-censored data under a compositional approach},
  author={Palarea-Albaladejo, Javier and Mart{\'i}n-Fern{\'a}ndez, Josep Antoni},
  journal={Chemometrics and Intelligent Laboratory Systems},
  volume={143},
  pages={85--96},
  year={2015},
  publisher={Elsevier}
}
```

### Desarrollo del Método:

```bibtex
@article{martin2012model,
  title={Model-based replacement of rounded zeros in compositional data: 
         classical and robust approaches},
  author={Mart{\'i}n-Fern{\'a}ndez, Josep Antoni and Hron, Karel and 
          Templ, Matthias and Filzmoser, Peter and Palarea-Albaladejo, Javier},
  journal={Computational Statistics \& Data Analysis},
  volume={56},
  number={9},
  pages={2688--2704},
  year={2012},
  publisher={Elsevier}
}

@article{palarea2008modified,
  title={A modified EM alr-algorithm for replacing rounded zeros in 
         compositional data sets},
  author={Palarea-Albaladejo, Javier and Mart{\'i}n-Fern{\'a}ndez, Josep Antoni},
  journal={Computers \& Geosciences},
  volume={34},
  number={8},
  pages={902--917},
  year={2008},
  publisher={Elsevier}
}
```

## 🎯 Ejemplo Completo

```python
import pandas as pd
from reader import cargar_csv, detectar_lod
from lrem import aplicar_lrem_robusto

# 1. Cargar datos
df = cargar_csv('muestras_geoquimicas.csv')

# 2. Detectar LODs
df_clean, lod_info = detectar_lod(df)

# 3. Aplicar lrEM
df_result, log = aplicar_lrem_robusto(
    df_clean,
    lod_info,
    tolerance=0.0001,
    max_iter=50,
    ini_method="multRepl"
)

# 4. Verificar resultados
if log['converged'].values[0]:
    print("✅ Algoritmo convergió exitosamente")
    print(f"   Iteraciones: {log['iterations'].values[0]}")
    
    # Examinar valores imputados por columna
    for col in lod_info.keys():
        col_log = log[log['columna'] == col]
        if not col_log.empty:
            print(f"\n{col}:")
            print(f"  N censurados: {col_log['n_censored'].values[0]}")
            print(f"  Media imputada: {col_log['mean_imputed'].values[0]:.4f}")
            print(f"  Rango: [{col_log['min_imputed'].values[0]:.4f}, "
                  f"{col_log['max_imputed'].values[0]:.4f}]")
else:
    print("⚠️ No convergió. Considera:")
    print("   - Aumentar max_iter")
    print("   - Relajar tolerance")
    print("   - Revisar calidad de datos")

# 5. Guardar
df_result.to_csv('datos_imputados_lrem.csv', index=False)
```

## 💡 Tips Prácticos

1. **Inicialización**: `"multRepl"` funciona mejor en la mayoría de casos
2. **Convergencia**: Típicamente converge en 5-15 iteraciones
3. **Datos problemáticos**: Si no converge, revisa outliers extremos
4. **Interpretación**: Valores imputados reflejan contexto multivariado
5. **Comparación**: Siempre compara con β-substitution para validar

---

**Implementado para Eutectik App con base en zCompositions (R package)**