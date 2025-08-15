import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Exoplanetas",
    page_icon="🪐",
    layout="wide"
)

# --- FUNCIÓN PARA GENERAR DATOS DE EXOPLANETAS ---
@st.cache_data
def generar_datos_exoplanetas(num_muestras=500):
    """
    Genera un DataFrame de ejemplo con datos de exoplanetas simulados.
    """
    np.random.seed(42)
    
    metodos = ['Tránsito', 'Velocidad Radial', 'Microlente Gravitacional', 'Imagen Directa']
    nombres_estrellas = ['Kepler', 'TRAPPIST', 'Proxima Centauri', 'Gliese', 'HD']
    
    data = []
    for i in range(num_muestras):
        metodo = np.random.choice(metodos, p=[0.6, 0.3, 0.05, 0.05])
        ano = np.random.randint(1995, 2024)
        masa = np.random.lognormal(mean=1.5, sigma=1.5)
        radio = np.random.lognormal(mean=0.8, sigma=0.8)
        
        data.append({
            'NombrePlaneta': f'Exo-{i+1:03d}',
            'EstrellaAnfitriona': np.random.choice(nombres_estrellas),
            'MetodoDescubrimiento': metodo,
            'AnoDescubrimiento': ano,
            'MasaTerrestre': round(masa, 2),
            'RadioTerrestre': round(radio, 2),
            'DistanciaAnosLuz': np.random.randint(4, 5000)
        })
        
    df = pd.DataFrame(data)
    return df.sort_values(by='AnoDescubrimiento').reset_index(drop=True)

# --- CARGA DE DATOS ---
datos = generar_datos_exoplanetas()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("🔭 Filtros de Exploración")

if st.sidebar.button('✨ Generar Nuevo Universo'):
    st.cache_data.clear()
    st.rerun()

# Filtro por Método de Descubrimiento
metodos_seleccionados = st.sidebar.multiselect(
    'Método de Descubrimiento:',
    options=datos['MetodoDescubrimiento'].unique(),
    default=datos['MetodoDescubrimiento'].unique()
)

# Filtro por Distancia
distancia_range = st.sidebar.slider(
    'Distancia a la Tierra (años luz):',
    min_value=int(datos['DistanciaAnosLuz'].min()),
    max_value=int(datos['DistanciaAnosLuz'].max()),
    value=(int(datos['DistanciaAnosLuz'].min()), int(datos['DistanciaAnosLuz'].max()))
)

# Aplicar filtros
df_filtrado = datos[
    (datos['MetodoDescubrimiento'].isin(metodos_seleccionados)) &
    (datos['DistanciaAnosLuz'] >= distancia_range[0]) &
    (datos['DistanciaAnosLuz'] <= distancia_range[1])
]

# --- PÁGINA PRINCIPAL ---
st.title("🪐 Dashboard de Exploración de Exoplanetas")
st.markdown("Un viaje interactivo a través de los mundos descubiertos más allá de nuestro sistema solar.")

# --- KPIs ---
total_planetas = len(df_filtrado)
planeta_masivo = df_filtrado.loc[df_filtrado['MasaTerrestre'].idxmax()] if not df_filtrado.empty else None
planeta_lejano = df_filtrado.loc[df_filtrado['DistanciaAnosLuz'].idxmax()] if not df_filtrado.empty else None

col1, col2, col3 = st.columns(3)
col1.metric("Planetas en Catálogo", f"{total_planetas:,}")
if planeta_masivo is not None:
    col2.metric("Planeta Más Masivo", f"{planeta_masivo['NombrePlaneta']} ({planeta_masivo['MasaTerrestre']:.2f} M⊕)")
if planeta_lejano is not None:
    col3.metric("Planeta Más Lejano", f"{planeta_lejano['NombrePlaneta']} ({planeta_lejano['DistanciaAnosLuz']:,} años luz)")

st.markdown("---")

# --- VISUALIZACIONES ---
st.header("Análisis del Cosmos")

# --- Gráficos en columnas ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Métodos de Descubrimiento")
    metodos_chart = alt.Chart(df_filtrado).mark_bar().encode(
        x=alt.X('MetodoDescubrimiento:N', sort='-y', title='Método'),
        y=alt.Y('count():Q', title='Número de Planetas Descubiertos'),
        color='MetodoDescubrimiento:N',
        tooltip=['MetodoDescubrimiento', 'count()']
    ).interactive()
    st.altair_chart(metodos_chart, use_container_width=True)

    st.subheader("Descubrimientos a Través del Tiempo")
    descubrimientos_temporales = df_filtrado.groupby('AnoDescubrimiento').size().reset_index(name='count')
    
    line_chart = alt.Chart(descubrimientos_temporales).mark_line(point=True).encode(
        x=alt.X('AnoDescubrimiento:O', title='Año'),
        y=alt.Y('count:Q', title='Número de Descubrimientos'),
        tooltip=['AnoDescubrimiento', 'count']
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)

with col_graf2:
    st.subheader("Clasificación de Planetas (Masa vs. Radio)")
    # Líneas de referencia para clasificación
    ref_data = pd.DataFrame({
        'Masa': [0.1, 10, 10, 3000],
        'Radio': [0.1, 2, 2, 25],
        'Texto': ['Rocosos', 'Supertierras / Minineptunos', '', 'Gigantes Gaseosos']
    })

    scatter_plot = alt.Chart(df_filtrado).mark_circle(size=80, opacity=0.7).encode(
        x=alt.X('MasaTerrestre:Q', title='Masa (Masa Terrestre)', scale=alt.Scale(type="log")),
        y=alt.Y('RadioTerrestre:Q', title='Radio (Radio Terrestre)', scale=alt.Scale(type="log")),
        color=alt.Color('MetodoDescubrimiento:N', title='Método'),
        tooltip=['NombrePlaneta', 'MasaTerrestre', 'RadioTerrestre', 'MetodoDescubrimiento']
    ).interactive()
    
    st.altair_chart(scatter_plot, use_container_width=True)
    st.caption("Ambos ejes están en escala logarítmica para una mejor visualización.")


# --- TABLA DE DATOS ---
st.markdown("---")
with st.expander("Ver/Ocultar Catálogo de Exoplanetas"):
    st.dataframe(df_filtrado)
