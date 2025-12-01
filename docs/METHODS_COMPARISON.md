# Comparación de Métodos de Imputación LOD

## 📊 Tabla Comparativa Completa

| Característica | Simple | β-substitution | lrEM | IDW Espacial |
|----------------|--------|----------------|------|--------------|
| **Complejidad** | Baja | Media | Alta | Alta |
| **Velocidad** | ⚡⚡⚡ Muy rápida | ⚡⚡ Rápida | ⚡ Lenta (iterativo) | ⚡ Lenta |
| **Precisión** | ⭐⭐ Aceptable | ⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Estado del arte | ⭐⭐⭐ Muy buena |
| **Base teórica** | Empírica | Maximum Likelihood | Maximum Likelihood | Geoestadística |
| **Valores repetidos** | ❌ No (variación) | ❌ No | ❌ No | ❌ No |
| **Usa covarianza** | ❌ No | Parcial | ✅ Completa | ❌ No |
| **Preserva CoDa** | ❌ No | ❌ No | ✅ Sí | ❌ No |
| **Requiere coordenadas** | ❌ No | ❌ No | ❌ No | ✅ Sí |
| **Min. muestras** | n ≥ 5 | n ≥ 5 | n > p (vars) | n ≥ 5 |
| **Min. detectados** | 1 | 2 | Depende | 3 vecinos |
| **% censura max** | 80% | 50% | 50% | 50% |

---

## 🎯 Guía de Selección Rápida

### ¿Qué método usar?

```
┌─ ¿Tienes coordenadas espaciales?
│
├─ SÍ ─→ ¿Hay autocorrelación espacial?
│        │
│        ├─ SÍ ─→ IDW (mejor para zonación geológica)
│        │
│        └─ NO ─→ Continuar abajo
│
└─ NO ─→ ¿Es análisis composicional (CoDa)?
         │
         ├─ SÍ ─→ ¿n > p y tienes tiempo?
         │        │
         │        ├─ SÍ ─→ lrEM (estado del arte)
         │        │
         │        └─ NO ─→ β-substitution (robusto)
         │
         └─ NO ─→ ¿Necesitas rapidez/exploración?
                  │
                  ├─ SÍ ─→ Simple (rápido)
                  │
                  └─ NO ─→ β-substitution (recomendado)
```

---

## 📈 Casos de Uso Detallados

### 1. Simple Substitution

**✅ Usar cuando:**
- Análisis exploratorio rápido
- Presentaciones preliminares
- Datasets pequeños (n < 20)
- No necesitas máxima precisión
- Familiarizar usuarios con los datos

**❌ NO usar cuando:**
- Análisis final para publicación
- Datos composicionales (CoDa)
- Necesitas máxima precisión estadística

**Ejemplo:**
```python
# Exploración rápida de tendencias
df_result, _ = apply_imputation(df, lod_info, method='simple')
df_result.describe()  # Estadísticas preliminares
```

---

### 2. β-Substitution (Ganser & Hewett 2010) ⭐ RECOMENDADO

**✅ Usar cuando:**
- Análisis general (uso por defecto)
- Publicaciones científicas
- Necesitas balance precisión/simplicidad
- n < 100 (excelente para muestras pequeñas)
- No hay autocorrelación espacial fuerte
- No es análisis CoDa estricto

**❌ NO usar cuando:**
- Análisis CoDa requiere clausura estricta
- Tienes menos de 5 muestras
- Todos los valores de un elemento están censurados

**Ejemplo:**
```python
# Análisis estándar (recomendado)
df_result, log = apply_imputation(df, lod_info, method='beta')

# Examinar factores calculados
print(log[['columna', 'beta_GM', 'beta_MEAN', 'n_censored']])
```

**Ventajas científicas:**
- Publicado en journal peer-reviewed
- Bias comparable a MLE
- Más robusto que MLE para n pequeño
- Fácil de explicar en papers

---

### 3. Log-Ratio EM (lrEM) ⭐ ESTADO DEL ARTE CODA

**✅ Usar cuando:**
- **Análisis composicional (CoDa) formal**
- Publicaciones en revistas CoDa
- Necesitas máxima rigurosidad estadística
- n > 2p (al menos 2× más muestras que variables)
- Tienes tiempo computacional
- Datos multielementales correlacionados

**❌ NO usar cuando:**
- n ≤ p (pocas muestras vs variables)
- Solo 1-2 elementos
- Necesitas resultados inmediatos
- >80% de censura en algún elemento

**Ejemplo:**
```python
# Análisis CoDa riguroso
df_result, log = apply_imputation(
    df, lod_info, 
    method='lrem',
    tolerance=0.0001,  # Más estricto → más iteraciones
    max_iter=50
)

# Verificar convergencia
if log['converged'].values[0]:
    print(f"✅ Convergió en {log['iterations'].values[0]} iteraciones")
else:
    print("⚠️ No convergió - considerar revisar datos")
```

**Ventajas para geoquímica:**
- Preserva relaciones log-ratio (ej: Cu/Zn)
- Ideal para diagramas ternarios
- Respeta clausura composicional
- Usado en software R (zCompositions)

**Limitaciones importantes:**
- Requiere matriz de datos "regular" (n > p)
- Puede no converger con outliers extremos
- Más lento (iterativo)

---

### 4. IDW Espacial (Cuadrático)

**✅ Usar cuando:**
- Datos georreferenciados (UTM, coordenadas)
- Existe autocorrelación espacial clara
- Zonación geológica conocida
- Análisis de anomalías espaciales
- Mapeo geoquímico

**❌ NO usar cuando:**
- No tienes coordenadas
- Muestras muy dispersas (>10 km)
- No hay continuidad geológica
- Pocas muestras (<15)

**Ejemplo:**
```python
# Análisis espacial
df_result, log = apply_imputation(
    df_geo, lod_info,
    method='idw',
    df_coords=coords,
    power=2.0,           # Típico para geoquímica
    max_distance=5000,   # Radio en metros
    min_neighbors=3,
    metodo_c='div2'      # Conservador
)

# Examinar contexto espacial
print(log[['columna', 'peso_w', 'distancia_media', 'n_vecinos']])
```

**Parámetros críticos:**
- `power=2.0`: Estándar (más alto = más peso a cercanos)
- `max_distance`: Según escala de muestreo
- `min_neighbors=3`: Mínimo estadístico

---

## 🔬 Comparación de Resultados

### Ejemplo: Cu con LOD = 5 ppm

Supongamos 10 muestras bajo LOD:

| Método | Media | Min | Max | Desv.Std | Valores Únicos |
|--------|-------|-----|-----|----------|----------------|
| Simple | 3.54 | 2.83 | 4.25 | 0.35 | 10 ✅ |
| β-substitution | 2.87 | 2.35 | 3.21 | 0.28 | 10 ✅ |
| lrEM | 2.94 | 1.82 | 4.15 | 0.75 | 10 ✅ |
| IDW | 3.12 | 2.10 | 4.45 | 0.68 | 10 ✅ |

**Observaciones:**
- β-substitution: Más conservador (valores menores)
- lrEM: Mayor varianza (refleja covarianza real)
- IDW: Refleja contexto espacial
- Todos evitan repetidos

---

## 📊 Recomendaciones por Disciplina

### Geoquímica de Exploración
**Recomendado**: β-substitution + IDW (si hay coordenadas)
- Balancecosto/beneficio óptimo
- Rápido para reportes
- Adecuado para mapeo

### Geoquímica Ambiental
**Recomendado**: lrEM (si CoDa) o β-substitution
- Rigurosidad para regulaciones
- Preserva composición para risk assessment

### Petrogénesis / Geoquímica Ígnea
**Recomendado**: lrEM
- Análisis CoDa esencial
- Diagramas de variación
- Ratios entre elementos

### Investigación Académica
**Recomendado**: lrEM (preferido) o β-substitution
- Máximo rigor científico
- Métodos publicados peer-reviewed
- Reproducible

---

## ⚠️ Advertencias Importantes

### Todos los Métodos:

1. **No son magia**: No pueden recuperar información perdida
2. **Sesgo inevitable**: Valores imputados son estimaciones
3. **Validación esencial**: Comparar métodos, análisis de sensibilidad
4. **Documentación**: Siempre reportar método usado en publicaciones

### Limitaciones Generales:

| Situación | Problema | Solución |
|-----------|----------|----------|
| >50% censura | Alta incertidumbre | Revisar diseño analítico |
| LOD variable | Complejidad | Normalizar o estratificar |
| Outliers extremos | Sesgo en covarianza | Análisis robusto previo |
| Datos no-lognormales | Supuestos violados | Transformaciones previas |

---

## 🎓 Referencias por Método

### Simple
- Hornung & Reed (1990). Estimation of average concentration in the presence of nondetectable values.

### β-substitution
- **Ganser & Hewett (2010)**. An Accurate Substitution Method for Analyzing Censored Data. *J. Occup. Environ. Hyg.*, 7:4, 233-244.

### lrEM
- **Palarea-Albaladejo & Martín-Fernández (2015)**. zCompositions – R package for multivariate imputation. *Chemom. Intell. Lab. Syst.*, 143, 85-96.
- Martín-Fernández et al. (2012). Model-based replacement of rounded zeros. *Comput. Stat. Data Anal.*, 56:9, 2688-2704.

### IDW
- Shepard (1968). A two-dimensional interpolation function for irregularly-spaced data.

---

## 💡 Consejos Prácticos

1. **Siempre compara métodos** para un subconjunto de datos
2. **Documenta parámetros** usados (para reproducibilidad)
3. **Examina logs** para entender decisiones del algoritmo
4. **Valida resultados** con conocimiento geológico
5. **Reporta limitaciones** en publicaciones

---

**Última actualización**: 2024
**Implementación**: Eutectik App - LOD Imputation Library