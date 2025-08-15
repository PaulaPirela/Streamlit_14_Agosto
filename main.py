import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Actividad Sísmica",
    page_icon="🌍",
    layout="wide"
)

# --- FUNCIÓN PARA GENERAR DATOS SÍSMICOS ---
@st.cache_data
def generar_datos_sismicos(num_muestras=500):
    """
    Genera un DataFrame de ejemplo con datos sísmicos simulados.
    """
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    fechas = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(num_muestras)]
    
    # Coordenadas aproximadas de zonas sísmicas
    regiones = {
        'Cinturón de Fuego del Pacífico': [(np.random.uniform(-50, 50), np.random.uniform(120, 290))],
        'Cinturón Alpino-Himalayo': [(np.random.uniform(10, 50), np.random.uniform(0, 100))],
        'Dorsal Mesoatlántica': [(np.random.uniform(-30, 60), np.random.uniform(-30, -10))]
    }
    
    data = []
    for _ in range(num_muestras):
        region_nombre = np.random.choice(list(regiones.keys()))
        lat, lon = regiones[region_nombre][0]
        data.append({
            'Fecha': np.random.choice(fechas),
            'Latitud': lat + np.random.normal(0, 10),
            'Longitud': lon + np.random.normal(0, 20),
            'Magnitud': np.random.uniform(2.5, 8.0),
            'Profundidad': np.random.randint(1, 700),
            'RegionTectonica': region_nombre
        })
        
    df = pd.DataFrame(data)
    df['Magnitud'] = df['Magnitud'].round(1)
    return df.sort_values(by='Fecha').reset_index(drop=True)

# --- CARGA DE DATOS ---
datos = generar_datos_sismicos()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("🔬 Filtros de Análisis")

if st.sidebar.button('🔄 Regenerar Datos Sísmicos'):
    st.cache_data.clear()
    st.rerun()

# Filtro por Magnitud
magnitud_range = st.sidebar.slider(
    'Filtrar por Magnitud (Escala de Richter):',
    min_value=float(datos['Magnitud'].min()),
    max_value=float(datos['Magnitud'].max()),
    value=(float(datos['Magnitud'].min()), float(datos['Magnitud'].max()))
)

# Filtro por Profundidad
profundidad_range = st.sidebar.slider(
    'Filtrar por Profundidad (km):',
    min_value=int(datos['Profundidad'].min()),
    max_value=int(datos['Profundidad'].max()),
    value=(int(datos['Profundidad'].min()), int(datos['Profundidad'].max()))
)

# Aplicar filtros
df_filtrado = datos[
    (datos['Magnitud'] >= magnitud_range[0]) &
    (datos['Magnitud'] <= magnitud_range[1]) &
    (datos['Profundidad'] >= profundidad_range[0]) &
    (datos['Profundidad'] <= profundidad_range[1])
]

# --- PÁGINA PRINCIPAL ---
st.title("🌍 Dashboard de Monitoreo de Actividad Sísmica Global")
st.markdown("Análisis interactivo de eventos sísmicos simulados a nivel mundial.")

# --- KPIs ---
total_sismos = len(df_filtrado)
max_magnitud = df_filtrado['Magnitud'].max() if not df_filtrado.empty else 0
max_profundidad = df_filtrado['Profundidad'].max() if not df_filtrado.empty else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total de Sismos Registrados", f"{total_sismos:,}")
col2.metric("Magnitud Máxima", f"{max_magnitud:.1f} Richter")
col3.metric("Profundidad Máxima", f"{max_profundidad:,} km")

st.markdown("---")

# --- VISUALIZACIONES ---
st.header("Visualización Geoespacial y Estadística")

# --- MAPA DE SISMOS ---
st.subheader("Mapa de Epicentros")
st.map(df_filtrado[['Latitud', 'Longitud']], zoom=1)
st.caption("Ubicación de los epicentros de los sismos filtrados. El zoom es interactivo.")

# --- Gráficos en columnas ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Distribución de Magnitudes")
    hist_magnitud = alt.Chart(df_filtrado).mark_bar().encode(
        alt.X('Magnitud:Q', bin=alt.Bin(maxbins=20), title='Magnitud (Richter)'),
        alt.Y('count()', title='Número de Sismos'),
        tooltip=[alt.X('Magnitud', bin=True), 'count()']
    ).interactive()
    st.altair_chart(hist_magnitud, use_container_width=True)

    st.subheader("Actividad Sísmica en el Tiempo")
    df_filtrado['Mes'] = df_filtrado['Fecha'].dt.to_period('M').astype(str)
    eventos_temporales = df_filtrado.groupby('Mes').size().reset_index(name='count')
    
    line_chart = alt.Chart(eventos_temporales).mark_line(point=True).encode(
        x=alt.X('Mes:T', title='Mes'),
        y=alt.Y('count:Q', title='Número de Sismos'),
        tooltip=['Mes', 'count']
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)

with col_graf2:
    st.subheader("Relación Magnitud vs. Profundidad")
    scatter_plot = alt.Chart(df_filtrado).mark_circle(size=60, opacity=0.7).encode(
        x=alt.X('Magnitud:Q', title='Magnitud'),
        y=alt.Y('Profundidad:Q', title='Profundidad (km)'),
        color=alt.Color('RegionTectonica:N', title='Región Tectónica'),
        tooltip=['Fecha', 'Magnitud', 'Profundidad', 'RegionTectonica']
    ).interactive()
    st.altair_chart(scatter_plot, use_container_width=True)

# --- TABLA DE DATOS ---
st.markdown("---")
with st.expander("Ver/Ocultar Tabla de Datos Detallados"):
    st.dataframe(df_filtrado)
