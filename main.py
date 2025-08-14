import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Ventas Interactivo",
    page_icon="📈",
    layout="wide"
)

# --- FUNCIÓN PARA GENERAR DATOS ---
@st.cache_data
def generar_datos(num_muestras=500):
    """
    Genera un DataFrame de ejemplo con datos de ventas más complejos.
    """
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    fechas = [start_date + timedelta(days=i) for i in range(num_muestras)]
    
    regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Central']
    vendedores = ['Ana', 'Luis', 'Carlos', 'Sofia', 'Maria', 'Juan']
    categorias = ['Electrónica', 'Ropa', 'Hogar', 'Juguetes', 'Libros', 'Deporte']
    canales = ['Online', 'Tienda Física']
    
    df = pd.DataFrame({
        'OrderID': [f'ORD-{1000+i}' for i in range(num_muestras)],
        'Fecha': np.random.choice(fechas, num_muestras),
        'Region': np.random.choice(regiones, num_muestras),
        'Vendedor': np.random.choice(vendedores, num_muestras),
        'Categoria': np.random.choice(categorias, num_muestras),
        'UnidadesVendidas': np.random.randint(1, 20, num_muestras),
        'PrecioUnitario': np.random.uniform(10.5, 200.0, num_muestras).round(2),
        'CanalVenta': np.random.choice(canales, num_muestras, p=[0.7, 0.3])
    })
    
    df['TotalVenta'] = (df['UnidadesVendidas'] * df['PrecioUnitario']).round(2)
    df['CostoUnitario'] = (df['PrecioUnitario'] * np.random.uniform(0.6, 0.8)).round(2)
    df['Ganancia'] = df['TotalVenta'] - (df['UnidadesVendidas'] * df['CostoUnitario'])
    
    return df.sort_values(by='Fecha').reset_index(drop=True)

# --- CARGA DE DATOS ---
datos = generar_datos()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("🎨 Filtros del Dashboard")

if st.sidebar.button('🔄 Recargar Datos Aleatorios'):
    st.cache_data.clear()
    st.rerun()

# Filtro por Región
regiones_seleccionadas = st.sidebar.multiselect(
    'Selecciona la Región:',
    options=datos['Region'].unique(),
    default=datos['Region'].unique()
)

# Filtro por Vendedor
vendedores_seleccionados = st.sidebar.multiselect(
    'Selecciona el Vendedor:',
    options=datos['Vendedor'].unique(),
    default=datos['Vendedor'].unique()
)

# Filtro por Rango de Fechas
fecha_min = datos['Fecha'].min()
fecha_max = datos['Fecha'].max()
fecha_inicio = st.sidebar.date_input('Fecha de inicio', fecha_min, min_value=fecha_min, max_value=fecha_max)
fecha_fin = st.sidebar.date_input('Fecha de fin', fecha_max, min_value=fecha_min, max_value=fecha_max)

# Aplicar filtros al DataFrame
df_filtrado = datos[
    (datos['Region'].isin(regiones_seleccionadas)) &
    (datos['Vendedor'].isin(vendedores_seleccionados)) &
    (datos['Fecha'] >= pd.to_datetime(fecha_inicio)) &
    (datos['Fecha'] <= pd.to_datetime(fecha_fin))
]

# --- PÁGINA PRINCIPAL ---
st.title("📈 Dashboard de Ventas Interactivo")
st.markdown("Explora las métricas de ventas de forma dinámica. Usa los filtros en la barra lateral para analizar los datos.")

# --- KPIs ---
total_ventas = df_filtrado['TotalVenta'].sum()
total_ganancia = df_filtrado['Ganancia'].sum()
total_unidades = df_filtrado['UnidadesVendidas'].sum()
ticket_promedio = total_ventas / len(df_filtrado) if len(df_filtrado) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"${total_ventas:,.2f}")
col2.metric("Ganancia Total", f"${total_ganancia:,.2f}")
col3.metric("Unidades Vendidas", f"{total_unidades:,}")
col4.metric("Ticket Promedio", f"${ticket_promedio:,.2f}")

st.markdown("---")

# --- VISUALIZACIONES ---
st.header("Análisis Visual")

# Checkboxes para mostrar/ocultar gráficos
mostrar_barras = st.checkbox('Mostrar Ventas por Categoría/Región', True)
mostrar_lineas = st.checkbox('Mostrar Tendencia de Ventas', True)
mostrar_dispersion = st.checkbox('Mostrar Correlación Ventas vs. Ganancia', False)
mostrar_circular = st.checkbox('Mostrar Distribución por Canal de Venta', True)

# --- Gráficos en columnas ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if mostrar_barras:
        st.subheader("Ventas por Dimensión")
        dimension = st.radio("Agrupar por:", ('Categoria', 'Region', 'Vendedor'), horizontal=True)
        
        ventas_agrupadas = df_filtrado.groupby(dimension)['TotalVenta'].sum().reset_index()
        
        bar_chart = alt.Chart(ventas_agrupadas).mark_bar().encode(
            x=alt.X(f'{dimension}:N', sort='-y', title=dimension),
            y=alt.Y('TotalVenta:Q', title='Total de Ventas ($)'),
            tooltip=[dimension, 'TotalVenta']
        ).interactive()
        st.altair_chart(bar_chart, use_container_width=True)

    if mostrar_dispersion:
        st.subheader("Ventas vs. Ganancia")
        scatter_plot = alt.Chart(df_filtrado).mark_circle(size=60).encode(
            x='TotalVenta',
            y='Ganancia',
            color='Region',
            tooltip=['OrderID', 'TotalVenta', 'Ganancia', 'Region']
        ).interactive()
        st.altair_chart(scatter_plot, use_container_width=True)

with col_graf2:
    if mostrar_lineas:
        st.subheader("Tendencia de Ventas en el Tiempo")
        df_filtrado['Mes'] = df_filtrado['Fecha'].dt.to_period('M').astype(str)
        ventas_temporales = df_filtrado.groupby('Mes')['TotalVenta'].sum().reset_index()
        
        line_chart = alt.Chart(ventas_temporales).mark_line(point=True).encode(
            x=alt.X('Mes:T', title='Mes'),
            y=alt.Y('TotalVenta:Q', title='Total de Ventas ($)'),
            tooltip=['Mes', 'TotalVenta']
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)

    if mostrar_circular:
        st.subheader("Ventas por Canal")
        canal_ventas = df_filtrado['CanalVenta'].value_counts().reset_index()
        canal_ventas.columns = ['CanalVenta', 'count']
        
        pie_chart = alt.Chart(canal_ventas).mark_arc().encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="CanalVenta", type="nominal"),
            tooltip=['CanalVenta', 'count']
        )
        st.altair_chart(pie_chart, use_container_width=True)

# --- TABLA DE DATOS ---
st.markdown("---")
with st.expander("Ver/Ocultar Tabla de Datos Filtrados"):
    st.dataframe(df_filtrado)
