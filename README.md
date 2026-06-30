# 🎯 Data Cleaning — Limpieza de datos de clientes
**Nivel:** 1 | **Skill:** Data cleaning (nulos, duplicados, outliers, texto inconsistente)

---

## 📖 Qué vas a aprender

En el mundo real, los datos **nunca** llegan limpios. Antes de hacer cualquier análisis o modelo de Machine Learning, hay que **limpiar los datos**. Este paso consume ~80% del tiempo de un científico de datos.

En este proyecto vas a aprender a detectar y corregir los problemas más comunes:

| Problema | ¿Cómo se ve? | ¿Cómo lo arreglamos? |
|----------|-------------|---------------------|
| **Valores nulos** | Celdas vacías (NaN) | `fillna()` con mediana/moda |
| **Duplicados** | Misma fila repetida | `drop_duplicates()` |
| **Texto inconsistente** | "MADRID", "Madrid", "  Madrid  " | `strip()`, `title()` |
| **Tipos incorrectos** | Edad como texto ("32" o "abc") | `pd.to_numeric()` |
| **Outliers** | Edad -5, saldo -500€ | Boxplots + reglas de negocio |
| **Emails inválidos** | "carlos@" o "maria@empresa" | Regex `re.match()` |

## 📂 Dataset

Trabajamos con **clientes_raw.csv**, una base de datos de clientes con 20 filas y 10 columnas. Los datos están **intencionalmente sucios** para simular un caso real:

- Nombres con espacios extra → `"  Pedro Sánchez  "`
- Edades inválidas → -5 años, "abc" (texto)
- Emails incompletos → "carlos@", "elena.torres@"
- Ciudades en diferentes formatos → "MADRID", "madrid", "Madrid"
- Fechas en formatos mixtos → "2024-03-15", "2024/05/20"
- Filas duplicadas exactas → Juan Pérez aparece 3 veces
- Saldos negativos → -500€
- Clientes sin nombre, sin email, sin ciudad

## 🧪 Código paso a paso

### 1️⃣ Cargar datos
```python
df_raw = pd.read_csv('data/clientes_raw.csv')
```
Pandas lee el CSV y lo convierte en un DataFrame. Usamos `head()` para ver las primeras filas.

### 2️⃣ Exploración inicial
```python
df_raw.info()           # Tipos de datos y nulos
df_raw.isnull().sum()   # Conteo de nulos por columna
```
El método `info()` es tu mejor amigo: te dice qué columnas tienen nulos y qué tipo de dato tiene cada una.

### 3️⃣ Detectar nulos (visual)
```python
sns.heatmap(df_raw.isnull(), cmap='viridis')
```
Creamos un mapa de calor donde las celdas blancas = valor faltante. ¡Se ve al instante qué columnas están peor!

### 4️⃣ Detectar duplicados
```python
df_raw.duplicated(keep='first')  # Marca True en la 2da ocurrencia
df_raw.drop_duplicates(keep='first')  # Elimina duplicados
```

### 5️⃣ Limpiar textos
```python
df['nombre'] = df['nombre'].str.strip()  # Quita espacios extra
df['ciudad'] = df['ciudad'].str.title()  # "MADRID" → "Madrid"
```

### 6️⃣ Convertir tipos de datos
```python
df['edad'] = pd.to_numeric(df['edad'], errors='coerce')  # "abc" → NaN
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
```

### 7️⃣ Manejar outliers
```python
# Edad negativa o > 120 años → reemplazar con mediana
mediana = df['edad'].median()
df.loc[df['edad'] < 0, 'edad'] = mediana
```

### 8️⃣ Imputar valores nulos
```python
df['edad'].fillna(df['edad'].median(), inplace=True)   # Mediana
df['ciudad'].fillna(df['ciudad'].mode()[0], inplace=True)  # Moda
```

## 📊 Resultados

### Antes de limpiar:
| Problema | Cantidad |
|----------|----------|
| Filas totales | 20 |
| Celdas nulas | ~15+ |
| Duplicados | 3+ |
| Edades inválidas | 2+ |
| Saldos negativos | 1+ |

### Después de limpiar:
| Métrica | Valor |
|---------|-------|
| Filas sin duplicados | ~16 |
| Nulos restantes | Mínimos (solo emails) |
| Datos listos para análisis | ✅ |

### Visualizaciones generadas:
1. `docs/01_valores_nulos.png` — Mapa de calor de nulos + barras
2. `docs/02_deteccion_outliers.png` — Boxplots de edad, saldo + ciudades
3. `docs/03_comparacion_antes_despues.png` — Comparativa antes/después
4. `docs/04_pipeline_resumen.png` — Tabla resumen del pipeline

## 💡 Conceptos clave

- **NaN ≠ 0**: Un valor nulo es un dato que no existe, no es cero
- **Mediana > Promedio**: Para imputar, la mediana es mejor porque no se afecta por outliers
- **Moda**: Para datos categóricos, el valor más frecuente es buena opción
- **No todo se imputa**: Los emails inválidos no se pueden inventar — mejor dejarlos como NaN
- **Documenta todo**: Cada decisión de limpieza debe estar documentada
- **Copia de seguridad**: Siempre guarda los datos originales antes de limpiar
- **Regla del 80/20**: El 80% del tiempo se va en preparar datos, 20% en modelar

## 🚀 Siguiente paso

Una vez que sabes limpiar datos, el siguiente skill del Nivel 1 es **Merge y Join de datasets** — combinar múltiples fuentes de datos (como SQL JOIN pero en pandas). Después de eso, saltamos al **Nivel 2: Análisis Exploratorio (EDA)** con correlaciones, pairplots y estadística descriptiva.

---

> "Datos limpios → Modelos confiables. Datos sucios → Basura entra, basura sale (GIGO)."
