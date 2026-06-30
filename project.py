#!/usr/bin/env python3
"""
===========================================================
🧹 DATA CLEANING — Limpieza de datos de clientes
===========================================================
Nivel: 1 | Skill: Data cleaning (nulos, duplicados, outliers)

En este proyecto vamos a aprender a LIMPIAR datos del mundo real.
Porque en la vida real, los datos NUNCA llegan limpios 😅

Vamos a trabajar con una base de datos de clientes que tiene:
✅ Valores nulos (celdas vacías)
✅ Filas duplicadas exactas y casi duplicadas
✅ Textos inconsistentes (MAYÚSCULAS, minúsculas, espacios)
✅ Tipos de datos incorrectos (edad como texto)
✅ Valores atípicos (outliers: edad negativa, salarios imposibles)
✅ Formato de fechas inconsistente
✅ Email inválidos

Al final tendremos un dataset limpio y listo para análisis.
===========================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from datetime import datetime

# ===========================================================
# CONFIGURACIÓN
# ===========================================================
# Crear carpeta para gráficos si no existe
os.makedirs('docs', exist_ok=True)

# Configurar estilo de los gráficos
plt.style.use('ggplot')
sns.set_theme(style='whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 120

# Para mostrar más columnas en pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 30)

print("=" * 70)
print("🧹 PROYECTO: LIMPIEZA DE DATOS DE CLIENTES")
print("=" * 70)

# ===========================================================
# PASO 1: CARGAR LOS DATOS
# ===========================================================
print("\n" + "=" * 70)
print("📂 PASO 1: CARGAR LOS DATOS CRUDOS")
print("=" * 70)

# Cargamos el CSV con pandas
df_raw = pd.read_csv('data/clientes_raw.csv')

print(f"\n📊 Dimensiones del dataset: {df_raw.shape[0]} filas × {df_raw.shape[1]} columnas")
print("\n🔍 Primeras 10 filas (vista previa):")
print(df_raw.head(10).to_string(index=True))

print("\n🔍 Últimas 5 filas:")
print(df_raw.tail(5).to_string(index=True))

# ===========================================================
# PASO 2: EXPLORACIÓN INICIAL — ENTENDER EL DESASTRE 🤯
# ===========================================================
print("\n" + "=" * 70)
print("🔎 PASO 2: EXPLORACIÓN INICIAL — ¿QUÉ TAN SUCIOS ESTÁN LOS DATOS?")
print("=" * 70)

print("\n📋 Información del DataFrame (tipos de datos y nulos):")
# info() nos dice los tipos de dato y cuántos valores NO nulos hay por columna
df_raw.info()

print("\n📊 Estadísticas descriptivas (solo columnas numéricas):")
print(df_raw.describe().to_string())

print("\n📊 Tipos de datos de cada columna:")
print(df_raw.dtypes.to_string())

print("\n🔢 Valores nulos por columna:")
print(df_raw.isnull().sum().to_string())

print(f"\n📊 Total de celdas vacías: {df_raw.isnull().sum().sum()} de {df_raw.size}")

# ===========================================================
# PASO 3: DETECTAR VALORES NULOS (MISSING VALUES)
# ===========================================================
print("\n" + "=" * 70)
print("⚠️  PASO 3: DETECTAR VALORES NULOS")
print("=" * 70)

# Calcular porcentaje de nulos por columna
nulos_porcentaje = (df_raw.isnull().sum() / len(df_raw)) * 100
print("\n📊 Porcentaje de valores nulos por columna:")
for col, pct in nulos_porcentaje.items():
    if pct > 0:
        print(f"   ❌ {col}: {pct:.1f}% nulos ({df_raw[col].isnull().sum()} de {len(df_raw)})")
    else:
        print(f"   ✅ {col}: 0% nulos")

# VISUALIZACIÓN 1: Mapa de valores nulos (heatmap)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Heatmap de nulos — cada celda blanca = nulo, negra = dato presente
sns.heatmap(df_raw.isnull(), cbar=False, cmap='viridis', ax=axes[0], yticklabels=False)
axes[0].set_title('🧩 Mapa de valores nulos (blanco = nulo)', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Columnas')
axes[0].set_ylabel('Filas')

# Gráfico de barras con conteo de nulos
nulos_count = df_raw.isnull().sum()
nulos_count = nulos_count[nulos_count > 0]  # solo columnas con nulos
if len(nulos_count) > 0:
    colors_nulos = ['#e74c3c' if v > 0 else '#2ecc71' for v in nulos_count]
    axes[1].bar(nulos_count.index, nulos_count.values, color=colors_nulos, edgecolor='white', linewidth=0.8)
    axes[1].set_title('📊 Cantidad de valores nulos por columna', fontsize=13, fontweight='bold')
    axes[1].set_xlabel('Columnas')
    axes[1].set_ylabel('Cantidad de nulos')
    axes[1].tick_params(axis='x', rotation=45)
    for i, v in enumerate(nulos_count.values):
        axes[1].text(i, v + 0.3, str(v), ha='center', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('docs/01_valores_nulos.png', bbox_inches='tight', dpi=120)
print("\n   ✅ Gráfico guardado: docs/01_valores_nulos.png")
plt.close()

# ===========================================================
# PASO 4: DETECTAR FILAS DUPLICADAS
# ===========================================================
print("\n" + "=" * 70)
print("👯 PASO 4: DETECTAR FILAS DUPLICADAS")
print("=" * 70)

# duplicated() marca las filas que son copias de otra anterior (keep='first' marca la 2da en adelante)
duplicados_exactos = df_raw.duplicated(keep='first').sum()
print(f"\n📊 Filas exactamente duplicadas: {duplicados_exactos}")

# Mostrar las filas duplicadas
if duplicados_exactos > 0:
    print("\n🔍 Mostrando filas duplicadas:")
    duplicated_rows = df_raw[df_raw.duplicated(keep='first')]
    print(duplicated_rows.to_string())

# También buscamos "casi duplicados" — filas que son iguales excepto espacios
# Por ejemplo, "Pedro Sánchez" vs "  Pedro Sánchez  " con espacios extra
print("\n🔍 Buscando duplicados parciales (mismo nombre, mismo email)...")
# Agrupamos por nombre_normalizado y email para encontrar posibles duplicados
df_temp = df_raw.copy()
df_temp['nombre_limpio'] = df_temp['nombre'].str.strip().str.lower()
posibles_dup = df_temp.groupby(['nombre_limpio', 'email']).size().reset_index(name='conteo')
posibles_dup = posibles_dup[posibles_dup['conteo'] > 1]
if len(posibles_dup) > 0:
    print(f"   ⚠️  Se encontraron {len(posibles_dup)} grupos de posibles duplicados:")
    for _, row in posibles_dup.iterrows():
        print(f"      - '{row['nombre_limpio']}' con email '{row['email']}' aparece {row['conteo']} veces")
else:
    print("   ✅ No se encontraron duplicados parciales adicionales")

# ===========================================================
# PASO 5: DETECTAR INCONSISTENCIAS EN TEXTO
# ===========================================================
print("\n" + "=" * 70)
print("🔤 PASO 5: DETECTAR INCONSISTENCIAS EN TEXTO")
print("=" * 70)

print("\n📍 Valores únicos en la columna 'ciudad':")
print(df_raw['ciudad'].unique())

print("\n📍 Valores únicos en la columna 'pais':")
print(df_raw['pais'].unique())

print("\n📍 Valores únicos en la columna 'activo':")
print(df_raw['activo'].unique())

# Encontrar espacios al inicio/final
print("\n🔍 Detectando espacios extra en columnas de texto...")
for col in ['nombre', 'ciudad', 'email']:
    con_espacios = df_raw[col].astype(str).str.contains(r'^\s+|\s+$', na=False).sum()
    if con_espacios > 0:
        print(f"   ⚠️  '{col}': {con_espacios} valores con espacios al inicio o final")
    else:
        print(f"   ✅ '{col}': sin espacios extra")

# ===========================================================
# PASO 6: DETECTAR OUTLIERS (VALORES ATÍPICOS)
# ===========================================================
print("\n" + "=" * 70)
print("📈 PASO 6: DETECTAR OUTLIERS (VALORES SOSPECHOSOS)")
print("=" * 70)

# --- Edad ---
print("\n🔍 Analizando columna 'edad':")
# Primero convertimos a numérico para analizar (los strings como 'abc' se vuelven NaN)
edad_numeric = pd.to_numeric(df_raw['edad'], errors='coerce')
print(f"   Valores: {df_raw['edad'].tolist()}")
print(f"   Valores no numéricos (ej: 'abc'): {df_raw['edad'].isna().sum() - pd.to_numeric(df_raw['edad'], errors='coerce').isna().sum()}")
# Valores inválidos: negativos o > 120
edades_invalidas = edad_numeric[(edad_numeric < 0) | (edad_numeric > 120)]
if len(edades_invalidas) > 0:
    print(f"   ❌ Edades fuera de rango (0-120 años): {edades_invalidas.tolist()}")

# --- Saldo ---
print("\n🔍 Analizando columna 'saldo':")
print(f"   Valores: {df_raw['saldo'].tolist()}")
saldo_negativo = df_raw[df_raw['saldo'] < 0]
if len(saldo_negativo) > 0:
    print(f"   ❌ Saldos negativos: {saldo_negativo['saldo'].tolist()}")

# --- Email ---
print("\n🔍 Analizando columna 'email':")
for idx, email in df_raw['email'].items():
    if pd.isna(email):
        print(f"   ❌ Fila {idx}: email faltante")
    elif '@' not in str(email):
        print(f"   ❌ Fila {idx}: email inválido '{email}' (falta @)")
    elif not str(email).endswith('.com') and not str(email).endswith('.es') and not str(email).endswith('.org'):
        # Tiene @ pero termina en algo raro
        print(f"   ❌ Fila {idx}: email incompleto '{email}' (sin dominio completo)")

# --- Fechas ---
print("\n🔍 Analizando columna 'fecha_registro':")
print(f"   Valores: {df_raw['fecha_registro'].tolist()}")
print(f"   Tipo de dato actual: {df_raw['fecha_registro'].dtype}")

# --- Teléfono ---
print("\n🔍 Analizando columna 'telefono':")
vacios = df_raw['telefono'].isna().sum()
print(f"   Teléfonos faltantes: {vacios}")

# ===========================================================
# VISUALIZACIÓN 2: Boxplots para detectar outliers
# ===========================================================
print("\n   📊 Generando boxplots para detectar outliers...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Boxplot de edad (convertida a numérico)
edad_clean = pd.to_numeric(df_raw['edad'], errors='coerce')
bp1 = axes[0].boxplot(edad_clean.dropna(), patch_artist=True, widths=0.4)
bp1['boxes'][0].set_facecolor('#3498db')
axes[0].set_title('📊 Distribución de Edad', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Edad (años)')
# Anotar outliers
outliers_edad = edad_clean[(edad_clean < 0) | (edad_clean > 100)].dropna()
for val in outliers_edad:
    axes[0].annotate(f'⚠️ {val}', xy=(1, val), ha='left', va='bottom',
                     fontsize=10, color='red', fontweight='bold')

# Boxplot de saldo
bp2 = axes[1].boxplot(df_raw['saldo'].dropna(), patch_artist=True, widths=0.4)
bp2['boxes'][0].set_facecolor('#2ecc71')
axes[1].set_title('📊 Distribución de Saldo', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Saldo (€)')
outliers_saldo = df_raw[df_raw['saldo'] < 0]['saldo']
for val in outliers_saldo:
    axes[1].annotate(f'⚠️ {val}', xy=(1, val), ha='left', va='bottom',
                     fontsize=10, color='red', fontweight='bold')

# Gráfico de barras: distribución de ciudades (para ver inconsistencias)
ciudades_counts = df_raw['ciudad'].value_counts()
bars = axes[2].bar(ciudades_counts.index, ciudades_counts.values,
                    color=['#e74c3c' if c == c.upper() and c.lower() != c else '#2ecc71' if c[0].isupper() else '#f39c12'
                           for c in ciudades_counts.index],
                    edgecolor='white', linewidth=0.8)
axes[2].set_title('📊 Distribución de Ciudades (inconsistencias)', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Ciudad')
axes[2].set_ylabel('Cantidad')
axes[2].tick_params(axis='x', rotation=45)
# Leyenda
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2ecc71', label='Formato correcto'),
    Patch(facecolor='#f39c12', label='Minúsculas/mixto'),
    Patch(facecolor='#e74c3c', label='TODO MAYÚSCULAS')
]
axes[2].legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig('docs/02_deteccion_outliers.png', bbox_inches='tight', dpi=120)
print("   ✅ Gráfico guardado: docs/02_deteccion_outliers.png")
plt.close()

# ===========================================================
# PASO 7: ¡A LIMPIAR! — PRIMERA RONDA
# ===========================================================
print("\n" + "=" * 70)
print("🧼 PASO 7: LIMPIEZA — MANOS A LA OBRA 🧽")
print("=" * 70)

# Hacemos una copia para no modificar los datos originales
df_clean = df_raw.copy()

# --- 7.1: Eliminar DUPLICADOS exactos ---
print("\n📌 7.1 Eliminando duplicados exactos...")
print(f"   Filas antes: {len(df_clean)}")

df_clean = df_clean.drop_duplicates(keep='first')

print(f"   Filas después: {len(df_clean)}")
print(f"   🗑️  Duplicados eliminados: {len(df_raw) - len(df_clean)}")

# --- 7.2: Limpiar ESPACIOS extra en texto ---
print("\n📌 7.2 Limpiando espacios extra en columnas de texto...")
columnas_texto = ['nombre', 'email', 'ciudad']
for col in columnas_texto:
    # strip() elimina espacios al inicio y final
    df_clean[col] = df_clean[col].astype(str).str.strip()
    # También reemplazamos espacios múltiples por uno solo
    df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
    # Reemplazamos 'nan' literal por NaN real
    df_clean[col] = df_clean[col].replace('nan', np.nan)

print("   ✅ Espacios extra eliminados")

# --- 7.3: Estandarizar TEXTO (capitalización) ---
print("\n📌 7.3 Estandarizando capitalización de ciudades...")

# Función para capitalizar correctamente nombres de ciudad
def capitalizar_ciudad(ciudad):
    if pd.isna(ciudad):
        return ciudad
    # Si está todo en mayúsculas, capitalizamos cada palabra
    if ciudad.isupper():
        return ciudad.title()
    # Si empieza con minúscula, capitalizamos primera letra
    if ciudad[0].islower():
        return ciudad.capitalize()
    return ciudad

df_clean['ciudad'] = df_clean['ciudad'].apply(capitalizar_ciudad)

print(f"   Ciudades después de estandarizar: {df_clean['ciudad'].unique()}")

# --- 7.4: Estandarizar columna 'activo' a booleano ---
print("\n📌 7.4 Estandarizando columna 'activo' a True/False...")
print(f"   Valores originales: {df_clean['activo'].unique()}")

# Mapeamos varios formatos a booleano
mapa_activo = {
    'TRUE': True, 'True': True, 'true': True, 'TRUE ': True,
    'FALSE': False, 'False': False, 'false': False,
    'si': True, 'no': False,
    'sí': True, 'SI': True, 'NO': False,
}
df_clean['activo'] = df_clean['activo'].astype(str).str.strip().str.title()
# title() convierte 'true' -> 'True', 'false' -> 'False', manejamos 'Si' también
df_clean['activo'] = df_clean['activo'].replace({'Si': True, 'No': False})
df_clean['activo'] = df_clean['activo'].map({'True': True, 'False': False})
# Si quedó algo raro, lo dejamos como NaN
df_clean['activo'] = df_clean['activo'].astype(object)

print(f"   Valores después: {df_clean['activo'].unique()}")

# --- 7.5: Estandarizar columna 'pais' ---
print("\n📌 7.5 Estandarizando columna 'pais'...")
print(f"   Valores originales: {df_raw['pais'].unique()}")

# Capitalizamos y rellenamos vacíos
df_clean['pais'] = df_clean['pais'].astype(str).str.strip().str.title()
df_clean['pais'] = df_clean['pais'].replace('España', 'España')
# Corregimos 'España' con Ñ si se perdió
df_clean['pais'] = df_clean['pais'].replace('Espana', 'España')
df_clean['pais'] = df_clean['pais'].replace('nan', np.nan)

print(f"   Valores después: {df_clean['pais'].unique()}")

# ===========================================================
# PASO 8: LIMPIEZA AVANZADA — TIPOS DE DATOS Y OUTLIERS
# ===========================================================
print("\n" + "=" * 70)
print("🔧 PASO 8: CORREGIR TIPOS DE DATOS Y OUTLIERS")
print("=" * 70)

# --- 8.1: Convertir EDAD a numérico ---
print("\n📌 8.1 Convirtiendo 'edad' a númerico...")
print(f"   Antes: dtype={df_clean['edad'].dtype}, valores={df_clean['edad'].tolist()}")

# Valores como 'abc' se convierten a NaN con errors='coerce'
df_clean['edad'] = pd.to_numeric(df_clean['edad'], errors='coerce')

print(f"   Después de conversión: {df_clean['edad'].tolist()}")

# Ahora manejamos outliers en edad: negativos o > 120
print(f"\n   🔍 Buscando outliers en edad...")
outliers_edad_mask = (df_clean['edad'] < 0) | (df_clean['edad'] > 120)
n_outliers_edad = outliers_edad_mask.sum()
if n_outliers_edad > 0:
    print(f"   ❌ Encontrados {n_outliers_edad} outliers:")
    print(f"      {df_clean[outliers_edad_mask][['id_cliente', 'nombre', 'edad']].to_string()}")
    
    # Calculamos la mediana de edades VÁLIDAS (sin outliers)
    edad_valida = df_clean.loc[~outliers_edad_mask, 'edad'].median()
    print(f"   📊 Mediana de edades válidas: {edad_valida:.0f} años")
    
    # Reemplazamos outliers con la mediana
    df_clean.loc[outliers_edad_mask, 'edad'] = edad_valida
    print(f"   ✅ Outliers reemplazados por la mediana ({edad_valida:.0f})")

# --- 8.2: Convertir FECHA_REGISTRO a datetime ---
print("\n📌 8.2 Convirtiendo 'fecha_registro' a formato fecha...")
print(f"   Antes: dtype={df_clean['fecha_registro'].dtype}")
print(f"   Valores actuales: {df_clean['fecha_registro'].tolist()}")

# Intentamos varios formatos de fecha automaticamente
df_clean['fecha_registro'] = pd.to_datetime(df_clean['fecha_registro'], errors='coerce')

print(f"   Después: dtype={df_clean['fecha_registro'].dtype}")
print(f"   Valores convertidos: {df_clean['fecha_registro'].tolist()}")

# --- 8.3: Corregir SALDOS negativos ---
print("\n📌 8.3 Corrigiendo saldos negativos...")
saldo_negativo_mask = df_clean['saldo'] < 0
n_saldo_neg = saldo_negativo_mask.sum()
if n_saldo_neg > 0:
    print(f"   ❌ Saldos negativos encontrados: {df_clean.loc[saldo_negativo_mask, 'saldo'].tolist()}")
    # Convertimos a positivo (probablemente es un error de signo)
    df_clean.loc[saldo_negativo_mask, 'saldo'] = df_clean.loc[saldo_negativo_mask, 'saldo'].abs()
    print(f"   ✅ Corregidos a positivo (valor absoluto)")

# --- 8.4: Validar EMAIL ---
print("\n📌 8.4 Validando emails...")

def validar_email(email):
    """Verifica si un email tiene formato válido: algo@dominio.ext"""
    if pd.isna(email):
        return np.nan
    email_str = str(email).strip()
    # Patrón simple de email: algo@algo.algo
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(patron, email_str):
        return email_str
    else:
        return np.nan  # Email inválido → lo marcamos como nulo

emails_originales = df_clean['email'].copy()
df_clean['email'] = df_clean['email'].apply(validar_email)

corregidos = (emails_originales.notna() & df_clean['email'].isna()).sum()
print(f"   📧 Emails inválidos que fueron marcados como nulos: {corregidos}")
if corregidos > 0:
    print(f"      Ejemplos de emails inválidos:")
    for idx in df_clean.index[emails_originales.notna() & df_clean['email'].isna()]:
        print(f"      - '{emails_originales[idx]}'")

# --- 8.5: Estandarizar TELÉFONO ---
print("\n📌 8.5 Aseguramos que teléfono sea string...")
df_clean['telefono'] = df_clean['telefono'].astype(object)
# Reemplazamos 'nan' string por NaN real
df_clean['telefono'] = df_clean['telefono'].replace('nan', np.nan)
nulos_telefono = df_clean['telefono'].isna().sum()
print(f"   📞 Teléfonos disponibles: {len(df_clean) - nulos_telefono} de {len(df_clean)}")

# ===========================================================
# PASO 9: MANEJAR VALORES NULOS RESTANTES
# ===========================================================
print("\n" + "=" * 70)
print("🩹 PASO 9: IMPUTAR VALORES NULOS RESTANTES")
print("=" * 70)

print(f"\n📊 Nulos ANTES de imputar:")
print(df_clean.isnull().sum().to_string())

# --- 9.1: Imputar edad faltante con la MEDIANA ---
nulos_edad = df_clean['edad'].isna().sum()
if nulos_edad > 0:
    mediana_edad = df_clean['edad'].median()
    df_clean['edad'] = df_clean['edad'].fillna(mediana_edad)
    print(f"\n📌 9.1 Edad: {nulos_edad} valores nulos → rellenados con mediana ({mediana_edad:.0f})")

# --- 9.2: Imputar email faltante ---
nulos_email = df_clean['email'].isna().sum()
if nulos_email > 0:
    print(f"\n📌 9.2 Email: {nulos_email} valores siguen nulos")
    print(f"      ⚠️  No podemos inventar emails, los dejamos como NaN")
    print(f"      (Mejor tener NaN que un email falso)")

# --- 9.3: Imputar ciudad faltante con la MODA ---
nulos_ciudad = df_clean['ciudad'].isna().sum()
if nulos_ciudad > 0:
    moda_ciudad = df_clean['ciudad'].mode()[0]  # la ciudad más frecuente
    df_clean['ciudad'] = df_clean['ciudad'].fillna(moda_ciudad)
    print(f"\n📌 9.3 Ciudad: {nulos_ciudad} valores nulos → rellenados con moda ({moda_ciudad})")

# --- 9.4: Imputar teléfono faltante ---
nulos_telefono = df_clean['telefono'].isna().sum()
if nulos_telefono > 0:
    print(f"\n📌 9.4 Teléfono: {nulos_telefono} valores nulos")
    print(f"      ⚠️  No inventamos números, los dejamos como NaN")

# --- 9.5: Rellenar país faltante ---
nulos_pais = df_clean['pais'].isna().sum()
if nulos_pais > 0:
    # Asumimos España porque la mayoría son de España
    df_clean['pais'] = df_clean['pais'].fillna('España')
    print(f"\n📌 9.5 País: {nulos_pais} valores nulos → rellenados con 'España' (mayoría)")

# --- 9.6: Rellenar activo faltante ---
nulos_activo = df_clean['activo'].isna().sum()
if nulos_activo > 0:
    moda_activo = df_clean['activo'].mode()[0]
    df_clean['activo'] = df_clean['activo'].fillna(moda_activo)
    print(f"\n📌 9.6 Activo: {nulos_activo} valores nulos → rellenados con moda ({moda_activo})")

print(f"\n📊 Nulos DESPUÉS de imputar:")
print(df_clean.isnull().sum().to_string())

# ===========================================================
# PASO 10: REINDEXAR Y ORDENAR
# ===========================================================
print("\n" + "=" * 70)
print("🔄 PASO 10: REINDEXAR Y ORDENAR")
print("=" * 70)

# Resetear los índices después de eliminar filas
df_clean = df_clean.reset_index(drop=True)

# Aseguramos que id_cliente sea entero
df_clean['id_cliente'] = df_clean['id_cliente'].astype(int)

# Ordenamos por id_cliente
df_clean = df_clean.sort_values('id_cliente').reset_index(drop=True)

print(f"\n✅ Dataset limpio y ordenado: {len(df_clean)} filas × {len(df_clean.columns)} columnas")

# ===========================================================
# PASO 11: VERIFICACIÓN FINAL
# ===========================================================
print("\n" + "=" * 70)
print("✅ PASO 11: VERIFICACIÓN FINAL DEL DATASET LIMPIO")
print("=" * 70)

print(f"\n📊 Dimensiones finales: {df_clean.shape}")
print(f"\n🔍 Primeras 5 filas del dataset limpio:")
print(df_clean.head().to_string())

print(f"\n🔍 Últimas 5 filas:")
print(df_clean.tail().to_string())

print(f"\n📋 Información del dataset limpio:")
df_clean.info()

print(f"\n📊 Estadísticas descriptivas del dataset limpio:")
print(df_clean.describe(include='all').to_string())

# ===========================================================
# VISUALIZACIÓN 3: Comparación ANTES vs DESPUÉS
# ===========================================================
print("\n   📊 Generando visualización comparativa...")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# 1. Nulos antes vs después
nulos_antes = df_raw.isnull().sum().sum()
nulos_despues = df_clean.isnull().sum().sum()
bars = axes[0, 0].bar(['Antes de limpiar', 'Después de limpiar'],
                       [nulos_antes, nulos_despues],
                       color=['#e74c3c', '#2ecc71'],
                       edgecolor='white', linewidth=1.5, width=0.5)
axes[0, 0].set_title('🧩 Valores Nulos: Antes vs Después', fontsize=13, fontweight='bold')
axes[0, 0].set_ylabel('Total de celdas nulas')
# Etiquetas sobre barras
for bar, val in zip(bars, [nulos_antes, nulos_despues]):
    axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                     str(val), ha='center', fontweight='bold', fontsize=12)

# 2. Duplicados antes vs después
dup_antes = df_raw.duplicated(keep='first').sum()
dup_despues = df_clean.duplicated(keep='first').sum()
bars = axes[0, 1].bar(['Antes de limpiar', 'Después de limpiar'],
                       [dup_antes, dup_despues],
                       color=['#e74c3c', '#2ecc71'],
                       edgecolor='white', linewidth=1.5, width=0.5)
axes[0, 1].set_title('👯 Filas Duplicadas: Antes vs Después', fontsize=13, fontweight='bold')
axes[0, 1].set_ylabel('Filas duplicadas')
for bar, val in zip(bars, [dup_antes, dup_despues]):
    axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     str(val), ha='center', fontweight='bold', fontsize=12)

# 3. Distribución de edad limpia (histograma)
axes[0, 2].hist(df_clean['edad'].dropna(), bins=15, color='#3498db',
                 edgecolor='white', alpha=0.7)
axes[0, 2].axvline(df_clean['edad'].median(), color='red', linestyle='--',
                    linewidth=2, label=f'Mediana: {df_clean["edad"].median():.0f}')
axes[0, 2].set_title('📊 Distribución de Edad (limpia)', fontsize=13, fontweight='bold')
axes[0, 2].set_xlabel('Edad (años)')
axes[0, 2].set_ylabel('Frecuencia')
axes[0, 2].legend()

# 4. Distribución de saldo (limpia)
axes[1, 0].hist(df_clean['saldo'], bins=15, color='#2ecc71',
                 edgecolor='white', alpha=0.7)
axes[1, 0].axvline(df_clean['saldo'].median(), color='red', linestyle='--',
                    linewidth=2, label=f'Mediana: {df_clean["saldo"].median():.0f}€')
axes[1, 0].set_title('📊 Distribución de Saldo (limpia)', fontsize=13, fontweight='bold')
axes[1, 0].set_xlabel('Saldo (€)')
axes[1, 0].set_ylabel('Frecuencia')
axes[1, 0].legend()

# 5. Ciudades después de limpiar
ciudades_counts = df_clean['ciudad'].value_counts()
axes[1, 1].bar(ciudades_counts.index, ciudades_counts.values,
                color=['#3498db', '#2ecc71', '#9b59b6', '#f39c12', '#e74c3c'],
                edgecolor='white', linewidth=0.8)
axes[1, 1].set_title('📍 Ciudades (después de limpiar)', fontsize=13, fontweight='bold')
axes[1, 1].set_xlabel('Ciudad')
axes[1, 1].set_ylabel('Clientes')
axes[1, 1].tick_params(axis='x', rotation=45)

# 6. Activo vs Inactivo
activo_counts = df_clean['activo'].value_counts()
colores = {True: '#2ecc71', False: '#e74c3c'}
etiquetas = {True: 'Activo ✅', False: 'Inactivo ❌'}
bars = axes[1, 2].bar([etiquetas[k] for k in activo_counts.index],
                       activo_counts.values,
                       color=[colores[k] for k in activo_counts.index],
                       edgecolor='white', linewidth=1.5, width=0.5)
axes[1, 2].set_title('📊 Clientes Activos vs Inactivos', fontsize=13, fontweight='bold')
axes[1, 2].set_ylabel('Cantidad')
for bar, val in zip(bars, activo_counts.values):
    axes[1, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                     str(val), ha='center', fontweight='bold', fontsize=12)

plt.suptitle('🧹 ANTES VS DESPUÉS DE LA LIMPIEZA DE DATOS', fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('docs/03_comparacion_antes_despues.png', bbox_inches='tight', dpi=120)
print("   ✅ Gráfico guardado: docs/03_comparacion_antes_despues.png")
plt.close()

# ===========================================================
# PASO 12: GUARDAR DATASET LIMPIO
# ===========================================================
print("\n" + "=" * 70)
print("💾 PASO 12: GUARDAR DATASET LIMPIO")
print("=" * 70)

output_path = 'data/clientes_clean.csv'
df_clean.to_csv(output_path, index=False)
print(f"\n✅ Dataset limpio guardado en: {output_path}")

# ===========================================================
# VISUALIZACIÓN 4: Resumen del pipeline de limpieza
# ===========================================================
print("\n   📊 Generando resumen visual de la limpieza...")

fig, ax = plt.subplots(figsize=(14, 4))

# Datos para el pipeline
pasos = ['Carga inicial', 'Duplicados', 'Espacios', 'Texto', 'Tipos', 'Outliers', 'Nulos', 'Dataset limpio']
datos_antes = [len(df_raw), len(df_raw), df_raw.isnull().sum().sum(),
               (df_raw['ciudad'].str.upper() != df_raw['ciudad']).sum(),
               df_raw['edad'].dtype == 'object',
               (pd.to_numeric(df_raw['edad'], errors='coerce') < 0).sum() + (df_raw['saldo'] < 0).sum(),
               df_raw.isnull().sum().sum(), 0]
datos_despues = [len(df_clean), 0, 0, 0, True, 0, df_clean.isnull().sum().sum(), len(df_clean)]

# Lo simplificamos como una línea de progreso
pasos_limpios = ['✅'] * 8
etapas = [
    f"{len(df_raw)} filas",
    f"{-df_raw.duplicated(keep='first').sum()} dup",
    f"Espacios 🧹",
    f"Texto 📝",
    f"Dtypes 🎯",
    f"Outliers 🚫",
    f"Nulos {df_raw.isnull().sum().sum()}",
    f"{len(df_clean)} filas ✅"
]

ax.axis('off')
ax.set_title('🧹 Pipeline de Limpieza — Resumen Visual', fontsize=15, fontweight='bold', pad=20)

# Crear tabla personalizada
table_data = []
table_data.append(['Paso', 'Antes', 'Después', 'Estado'])
table_data.append(['1. Cargar datos', str(len(df_raw)), str(len(df_clean)), '✅'])
table_data.append(['2. Duplicados', str(df_raw.duplicated(keep='first').sum()), '0', '✅'])
table_data.append(['3. Texto (espacios, capitalización)', 'Inconsistente', 'Uniforme', '✅'])
table_data.append(['4. Tipos de datos', 'Mixtos/incorrectos', 'Correctos', '✅'])
table_data.append(['5. Valores atípicos (edad, saldo)', f'{int((pd.to_numeric(df_raw["edad"], errors="coerce") < 0).sum() + (df_raw["saldo"] < 0).sum())}', '0', '✅'])
table_data.append(['6. Valores nulos', str(df_raw.isnull().sum().sum()), str(df_clean.isnull().sum().sum()), '✅'])
table_data.append(['7. Dataset final', f'{len(df_raw)} filas →', f'{len(df_clean)} filas', '✅'])

table = ax.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.25, 0.2, 0.2, 0.1])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.8)

# Colorear cabecera
for j in range(4):
    table[0, j].set_facecolor('#2c3e50')
    table[0, j].set_text_props(color='white', fontweight='bold')
for i in range(1, len(table_data)):
    table[i, 3].set_facecolor('#d5f5e3')  # verde claro

plt.savefig('docs/04_pipeline_resumen.png', bbox_inches='tight', dpi=120)
print("   ✅ Gráfico guardado: docs/04_pipeline_resumen.png")
plt.close()

# ===========================================================
# 🧠 RESUMEN FINAL
# ===========================================================
print("\n" + "=" * 70)
print("🧠 RESUMEN: ¿QUÉ APRENDISTE HOY?")
print("=" * 70)

print("""
🎯 OBJETIVO: Limpiar un dataset realista con datos de clientes

✅ Habilidades practicadas:
   1. DETECTAR VALORES NULOS → isnull(), info(), heatmap visual
   2. ELIMINAR DUPLICADOS → duplicated(), drop_duplicates()
   3. LIMPIAR TEXTO → strip(), title(), replace(), regex
   4. CORREGIR TIPOS → to_numeric(), to_datetime()
   5. DETECTAR OUTLIERS → boxplots, reglas de negocio (edad > 120)
   6. IMPUTAR VALORES → fillna() con mediana/moda

🔥 Conceptos clave:
   - Datos sucios ≈ datos reales. Limpiar es el 80% del trabajo en ML
   - Nunca elimines datos sin entender POR QUÉ están mal
   - La mediana es mejor que el promedio para imputar (resistente a outliers)
   - Siempre guarda una copia de los datos originales antes de limpiar
   - Documenta cada decisión de limpieza (por qué imputaste, por qué eliminaste)

📊 Resultados:
   - Dataset original:  {len(df_raw)} filas con {df_raw.isnull().sum().sum()} celdas nulas
   - Duplicados eliminados: {df_raw.duplicated(keep='first').sum()}
   - Dataset limpio: {len(df_clean)} filas con {df_clean.isnull().sum().sum()} celdas nulas
   - Outliers corregidos: edad, saldo
""")

print("=" * 70)
print("📂 Ruta del proyecto: /opt/data/ml-projects/2026-06-21-data-clearing/")
print("=" * 70)
