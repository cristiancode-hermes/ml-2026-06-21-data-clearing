# Learnings — 2026-06-21

## Qué se hizo
Proyecto de Data Cleaning: limpieza de una base de datos de clientes con problemas reales (nulos, duplicados, texto inconsistente, outliers, tipos de datos incorrectos, emails inválidos).

## Conceptos nuevos
- [x] Detectar valores nulos con `isnull()` y visualizarlos con `sns.heatmap()`
- [x] Eliminar duplicados exactos con `drop_duplicates()`
- [x] Limpiar textos: `strip()`, `title()`, `replace()` con regex
- [x] Convertir tipos de datos: `pd.to_numeric()`, `pd.to_datetime()`
- [x] Detectar outliers con boxplots y reglas de negocio (edad < 0)
- [x] Imputar nulos con `fillna()` usando mediana y moda
- [x] Validar emails con `re.match()` y regex
- [ ] Merge y join de datasets (pendiente para el próximo)

## Dificultades encontradas
- Los emails inválidos requieren un patrón regex robusto — algunos emails rotos no se pueden recuperar
- La columna 'activo' tenía múltiples formatos (TRUE, True, true, si, False) — mapear todos manualmente fue tedioso
- Los valores 'nan' como strings (cuando se convierten a str) pueden confundirse con NaN reales
- La imputación de outliers requiere criterio: no siempre la mediana es la mejor opción

## Notas para el próximo proyecto
- Completar Nivel 1 con el skill Merge/Join
- Luego avanzar a Nivel 2 (EDA: correlaciones, heatmaps, pairplots, estadística)
- Para el próximo proyecto, usar datasets más grandes (1000+ filas)
- Incluir más visualizaciones estadísticas
