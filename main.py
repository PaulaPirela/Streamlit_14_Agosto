import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Consola de Astro-Navegación",
    page_icon="🔭",
    layout="wide"
)

# --- FUNCIÓN PARA GENERAR DATOS DE EXOPLANETAS ---
@st.cache_data
def generar_datos_exoplanetas(num_muestras=500):
    """
    Genera un DataFrame de ejemplo con datos de exoplanetas simulados,
    incluyendo un Índice de Similitud con la Tierra (IST).
    """
    np.random.seed(42)
    
    metodos = ['Tránsito', 'Velocidad Radial', 'Microlente Gravitacional', 'Imagen Directa']
    nombres_estrellas = ['Kepler', 'TRAPPIST', 'Proxima Centauri', 'Gliese', 'HD']
    
    data = []
    for i in range(num_muestras):
        masa = np.random.lognormal(mean=0.5, sigma=1.2)
        radio = np.random.lognormal(mean=0.1, sigma=0.9)
        
        # Fórmula simple para el Índice de Similitud con la Tierra (IST)
        # Basado en la cercanía a 1 en masa y radio.
        ist_masa = 1 - abs(masa - 1) / (masa + 1)
        ist_radio = 1 - abs(radio - 1) / (radio + 1)
        ist = np.sqrt(ist_masa * ist_radio) * 100
        
        data.append({
            'NombrePlaneta': f'Xylo-{i+1:03d}',
            'EstrellaAnfitriona': np.random.choice(nombres_estrellas),
            'MetodoDescubrimiento': np.random.choice(metodos, p=[0.6, 0.3, 0.05, 0.05]),
            'AnoDescubrimiento': np.random.randint(1995, 2025),
            'MasaTerrestre': round(masa, 2),
            'RadioTerrestre': round(radio, 2),
            'DistanciaAnosLuz': np.random.randint(4, 5000),
            'IST': round(ist, 2)
        })
        
    df = pd.DataFrame(data)
    return df.sort_values(by='AnoDescubrimiento').reset_index(drop=True)

# --- CARGA DE DATOS ---
datos = generar_datos_exoplanetas()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://www.transparentpng.com/thumb/planet/planet-hd-png-9.png", width=100)
st.sidebar.title("Panel de Navegación")
st.sidebar.header("Filtros de Misión")

if st.sidebar.button('🚀 ¡Generar Nuevo Sector!'):
    st.cache_data.clear()
    st.rerun()

# Filtro por IST (Potencialmente Habitable)
ist_range = st.sidebar.slider(
    'Índice de Similitud con la Tierra (IST):',
    min_value=0.0, max_value=100.0,
    value=(70.0, 100.0)
)

# Filtro por Método de Descubrimiento
metodos_seleccionados = st.sidebar.multiselect(
    'Método de Descubrimiento:',
    options=datos['MetodoDescubrimiento'].unique(),
    default=datos['MetodoDescubrimiento'].unique()
)

# Filtro por Distancia
distancia_range = st.sidebar.slider(
    'Rango de Distancia (años luz):',
    min_value=int(datos['DistanciaAnosLuz'].min()),
    max_value=int(datos['DistanciaAnosLuz'].max()),
    value=(int(datos['DistanciaAnosLuz'].min()), int(datos['DistanciaAnosLuz'].max()))
)

# Aplicar filtros
df_filtrado = datos[
    (datos['MetodoDescubrimiento'].isin(metodos_seleccionados)) &
    (datos['DistanciaAnosLuz'].between(distancia_range[0], distancia_range[1])) &
    (datos['IST'].between(ist_range[0], ist_range[1]))
]

# --- PÁGINA PRINCIPAL ---
st.title("🪐 Consola de Mando de Astro-Navegación")
st.markdown("### Explorando nuevos mundos en la vasta oscuridad del cosmos.")

# --- KPIs y Planeta Destacado ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Informe de Misión")
    total_planetas = len(df_filtrado)
    st.metric("Objetivos Identificados", f"{total_planetas:,}")
    
    planeta_destacado = df_filtrado.loc[df_filtrado['IST'].idxmax()] if not df_filtrado.empty else None
    
    if planeta_destacado is not None:
        st.metric("Mejor Candidato", f"{planeta_destacado['NombrePlaneta']}")
        st.metric("Similitud con la Tierra", f"{planeta_destacado['IST']}%")
    else:
        st.warning("No se encontraron candidatos con los filtros actuales.")

with col2:
    if planeta_destacado is not None:
        st.subheader(f"Perfil del Objetivo: {planeta_destacado['NombrePlaneta']}")
        st.markdown(f"""
        - **Estrella Anfitriona:** `{planeta_destacado['EstrellaAnfitriona']}`
        - **Masa:** `{planeta_destacado['MasaTerrestre']}` M⊕ (Masas Terrestres)
        - **Radio:** `{planeta_destacado['RadioTerrestre']}` R⊕ (Radios Terrestres)
        - **Distancia:** `{planeta_destacado['DistanciaAnosLuz']:,}` años luz
        - **Descubierto en:** `{planeta_destacado['AnoDescubrimiento']}` vía `{planeta_destacado['MetodoDescubrimiento']}`
        """)

st.markdown("---")

# --- VISUALIZACIONES ---
st.header("Análisis de Datos del Sector")

col_graf1, col_graf2 = st.columns(2)

# Paleta de colores cósmica
color_scheme = alt.Scale(domain=['Tránsito', 'Velocidad Radial', 'Microlente Gravitacional', 'Imagen Directa'],
                         range=['#4C78A8', '#F58518', '#E45756', '#72B7B2'])

with col_graf1:
    st.subheader("Frecuencia de Métodos de Detección")
    metodos_chart = alt.Chart(df_filtrado).mark_bar(cornerRadius=5).encode(
        x=alt.X('MetodoDescubrimiento:N', sort='-y', title=None),
        y=alt.Y('count():Q', title='Planetas Descubiertos'),
        color=alt.Color('MetodoDescubrimiento:N', scale=color_scheme, legend=None),
        tooltip=['MetodoDescubrimiento', 'count()']
    ).interactive()
    st.altair_chart(metodos_chart, use_container_width=True)

    st.subheader("Línea Temporal de Descubrimientos")
    descubrimientos_temporales = df_filtrado.groupby('AnoDescubrimiento').size().reset_index(name='count')
    line_chart = alt.Chart(descubrimientos_temporales).mark_area(
        line={'color':'#4C78A8'},
        gradient='linear',
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0),
                   alt.GradientStop(color='#4C78A8', offset=1)]
        )
    ).encode(
        x=alt.X('AnoDescubrimiento:O', title='Año'),
        y=alt.Y('count:Q', title='Número de Descubrimientos'),
        tooltip=['AnoDescubrimiento', 'count']
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)

with col_graf2:
    st.subheader("Diagrama de Masa-Radio Planetario")
    scatter_plot = alt.Chart(df_filtrado).mark_circle(size=80, opacity=0.8).encode(
        x=alt.X('MasaTerrestre:Q', title='Masa (Masa Terrestre)', scale=alt.Scale(type="log")),
        y=alt.Y('RadioTerrestre:Q', title='Radio (Radio Terrestre)', scale=alt.Scale(type="log")),
        color=alt.Color('MetodoDescubrimiento:N', scale=color_scheme, title='Método'),
        size=alt.Size('IST:Q', title='Similitud con la Tierra (%)'),
        tooltip=['NombrePlaneta', 'MasaTerrestre', 'RadioTerrestre', 'IST']
    ).interactive()
    st.altair_chart(scatter_plot, use_container_width=True)
    st.caption("El tamaño de los puntos indica la similitud con la Tierra. Ambos ejes en escala logarítmica.")

# --- TABLA DE DATOS ---
st.markdown("---")
with st.expander("🛰️ Acceder a la Base de Datos Estelar Completa"):
    st.dataframe(df_filtrado)
