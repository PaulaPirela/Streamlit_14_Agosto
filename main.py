import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Consola de Ciberseguridad",
    page_icon="🛡️",
    layout="wide"
)

# --- DATOS GEOGRÁFICOS SIMULADOS ---
# Coordenadas de ciudades importantes para simular orígenes y destinos
cities = {
    'USA': (38.9637, -95.7129),
    'China': (35.8617, 104.1954),
    'Russia': (61.5240, 105.3188),
    'Germany': (51.1657, 10.4515),
    'Brazil': (-14.2350, -51.9253),
    'India': (20.5937, 78.9629),
    'UK': (55.3781, -3.4360),
    'Japan': (36.2048, 138.2529)
}

# --- FUNCIÓN PARA GENERAR DATOS DE ATAQUES ---
@st.cache_data
def generar_ataques(num_muestras=500):
    """
    Genera un DataFrame de ejemplo con datos de ciberataques simulados.
    """
    np.random.seed(int(time.time())) # Usar el tiempo para una nueva semilla cada vez
    
    attack_types = ['DDoS', 'Malware', 'Phishing', 'Ransomware', 'Inyección SQL']
    severities = ['Baja', 'Media', 'Alta', 'Crítica']
    statuses = ['Bloqueado', 'Exitoso']
    
    data = []
    for _ in range(num_muestras):
        source_country, target_country = np.random.choice(list(cities.keys()), 2, replace=False)
        
        data.append({
            'Timestamp': pd.to_datetime('now', utc=True) - pd.Timedelta(minutes=np.random.randint(0, 120)),
            'TipoAtaque': np.random.choice(attack_types, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
            'Severidad': np.random.choice(severities, p=[0.3, 0.4, 0.2, 0.1]),
            'PaisOrigen': source_country,
            'PaisDestino': target_country,
            'LatOrigen': cities[source_country][0] + np.random.normal(0, 2),
            'LonOrigen': cities[source_country][1] + np.random.normal(0, 2),
            'LatDestino': cities[target_country][0] + np.random.normal(0, 2),
            'LonDestino': cities[target_country][1] + np.random.normal(0, 2),
            'Estado': np.random.choice(statuses, p=[0.8, 0.2])
        })
        
    df = pd.DataFrame(data)
    return df.sort_values(by='Timestamp', ascending=False).reset_index(drop=True)

# --- CARGA DE DATOS ---
if 'attack_data' not in st.session_state:
    st.session_state.attack_data = generar_ataques()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2801/2801740.png", width=100)
st.sidebar.title("Panel de Control Táctico")

if st.sidebar.button('🚨 Simular Nueva Oleada de Ataques'):
    st.session_state.attack_data = generar_ataques()
    st.rerun()

st.sidebar.header("Filtros de Amenaza")
severidad_seleccionada = st.sidebar.multiselect(
    'Filtrar por Severidad:',
    options=st.session_state.attack_data['Severidad'].unique(),
    default=st.session_state.attack_data['Severidad'].unique()
)

tipo_ataque_seleccionado = st.sidebar.multiselect(
    'Filtrar por Tipo de Ataque:',
    options=st.session_state.attack_data['TipoAtaque'].unique(),
    default=st.session_state.attack_data['TipoAtaque'].unique()
)

# Aplicar filtros
df_filtrado = st.session_state.attack_data[
    (st.session_state.attack_data['Severidad'].isin(severidad_seleccionada)) &
    (st.session_state.attack_data['TipoAtaque'].isin(tipo_ataque_seleccionado))
]

# --- PÁGINA PRINCIPAL ---
st.title("🛡️ Consola de Monitoreo de Amenazas Cibernéticas Globales")

# --- INDICADOR DE NIVEL DE AMENAZA ---
recent_attacks = df_filtrado.head(50)
critical_count = len(recent_attacks[recent_attacks['Severidad'] == 'Crítica'])
high_count = len(recent_attacks[recent_attacks['Severidad'] == 'Alta'])
threat_level = "Bajo"
threat_color = "green"
if critical_count > 2 or high_count > 5:
    threat_level = "Crítico"
    threat_color = "red"
elif critical_count > 0 or high_count > 2:
    threat_level = "Elevado"
    threat_color = "orange"

st.markdown(f"Nivel de Amenaza Actual: <span style='color:{threat_color}; font-size: 24px; font-weight: bold;'>{threat_level}</span>", unsafe_allow_html=True)

# --- KPIs ---
total_ataques = len(df_filtrado)
bloqueados = df_filtrado[df_filtrado['Estado'] == 'Bloqueado'].shape[0]
tasa_bloqueo = (bloqueados / total_ataques * 100) if total_ataques > 0 else 0
top_target = df_filtrado['PaisDestino'].mode()[0] if not df_filtrado.empty else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Ataques Detectados", f"{total_ataques:,}")
col2.metric("Tasa de Bloqueo", f"{tasa_bloqueo:.1f}%")
col3.metric("País Más Atacado", top_target)

st.markdown("---")

# --- MAPA DE ATAQUES ---
st.subheader("Mapa Global de Amenazas en Tiempo Real")

# Definir colores para los arcos según la severidad
def get_color(severidad):
    if severidad == 'Crítica': return [255, 0, 0, 180]
    if severidad == 'Alta': return [255, 100, 0, 150]
    if severidad == 'Media': return [255, 255, 0, 120]
    return [0, 255, 0, 100]

df_filtrado['ColorArco'] = df_filtrado['Severidad'].apply(get_color)

view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.5, pitch=50)
arc_layer = pdk.Layer(
    'ArcLayer',
    data=df_filtrado,
    get_source_position='[LonOrigen, LatOrigen]',
    get_target_position='[LonDestino, LatDestino]',
    get_source_color='[0, 255, 0, 160]',
    get_target_color='ColorArco',
    get_width=2,
    auto_highlight=True
)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v9',
    initial_view_state=view_state,
    layers=[arc_layer],
    tooltip={"text": "Ataque {TipoAtaque}\nDe: {PaisOrigen} a {PaisDestino}\nSeveridad: {Severidad}"}
))

# --- GRÁFICOS Y FEED ---
col_graf1, col_graf2 = st.columns([2, 1])

with col_graf1:
    st.subheader("Distribución de Tipos de Ataque")
    chart_data = df_filtrado['TipoAtaque'].value_counts()
    st.bar_chart(chart_data)

with col_graf2:
    st.subheader("Feed de Actividad Reciente")
    st.dataframe(
        df_filtrado[['Timestamp', 'TipoAtaque', 'Severidad', 'PaisOrigen', 'PaisDestino']].head(10),
        hide_index=True,
        use_container_width=True
    )
