import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis Exploratorio Básico",
    page_icon="📊",
    layout="wide"
)

# --- FUNCIÓN PARA GENERAR DATOS ---
@st.cache_data # Usamos cache para que los datos no se regeneren en cada interacción
def generar_datos():
    """
    Genera un DataFrame de ejemplo con datos aleatorios de ventas.
    """
    np.random.seed(42) # Semilla para reproducibilidad
    fechas = pd.to_datetime(pd.date_range(start="2023-01-01", periods=100, freq='D'))
    categorias = np.random.choice(['Electrónica', 'Ropa', 'Hogar', 'Juguetes'], 100)
    ventas = np.random.randint(50, 500, 100)
    
    df = pd.DataFrame({
        'Fecha': fechas,
        'Categoria': categorias,
        'Ventas': ventas
    })
    return df

# --- TÍTULO Y DESCRIPCIÓN ---
st.title("📊 Análisis Exploratorio de Datos (EDA)")
st.write("Esta aplicación genera datos aleatorios de ventas y crea dos visualizaciones básicas para su análisis.")

# --- CARGA Y MUESTRA DE DATOS ---
df = generar_datos()

st.header("Conjunto de Datos Generado")
st.write("A continuación se muestran los primeros 10 registros del conjunto de datos aleatorio.")
st.dataframe(df.head(10))

# --- VISUALIZACIONES ---
st.header("Visualizaciones")

# --- 1. GRÁFICO DE BARRAS: VENTAS TOTALES POR CATEGORÍA ---
st.subheader("Total de Ventas por Categoría")

# Agrupar datos para el gráfico de barras
ventas_por_categoria = df.groupby('Categoria')['Ventas'].sum().reset_index()

bar_chart = alt.Chart(ventas_por_categoria).mark_bar().encode(
    x=alt.X('Categoria:N', title='Categoría de Producto'),
    y=alt.Y('Ventas:Q', title='Total de Ventas ($)'),
    color=alt.Color('Categoria:N', legend=None), # Color por categoría
    tooltip=['Categoria', 'Ventas'] # Muestra info al pasar el mouse
).properties(
    title='Comparativa de Ventas por Categoría'
)

st.altair_chart(bar_chart, use_container_width=True)
st.write("Este gráfico de barras muestra el rendimiento de ventas acumulado para cada categoría de producto.")

# --- 2. GRÁFICO DE LÍNEAS: TENDENCIA DE VENTAS EN EL TIEMPO ---
st.subheader("Tendencia de Ventas a lo Largo del Tiempo")

line_chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('Fecha:T', title='Fecha'),
    y=alt.Y('Ventas:Q', title='Ventas Diarias ($)'),
    tooltip=['Fecha', 'Ventas']
).properties(
    title='Evolución de las Ventas Diarias'
).interactive() # Permite hacer zoom y pan

st.altair_chart(line_chart, use_container_width=True)
st.write("Este gráfico de líneas muestra cómo han variado las ventas totales día a día.")
