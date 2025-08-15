import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Consola de Ciberseguridad",
    page_icon="🛡️",
    layout="wide"
)

# --- DATOS GEOGRÁFICOS SIMULADOS ---
cities = {
    'USA': (38.9637, -95.7129), 'China': (35.8617, 104.1954),
    'Russia': (61.5240, 105.3188), 'Germany': (51.1657, 10.4515),
    'Brazil': (-14.2350, -51.9253), 'India': (20.5937, 78.9629),
    'UK': (55.3781, -3.4360), 'Japan': (36.2048, 138.2529),
    'Australia': (-25.2744, 133.7751), 'Canada': (56.1304, -106.3468)
}

# --- FUNCIÓN PARA GENERAR DATOS DE ATAQUES ---
@st.cache_data
def generar_ataques(num_muestras=700):
    np.random.seed(int(time.time()))
    attack_types = ['DDoS', 'Malware', 'Phishing', 'Ransomware', 'Inyección SQL', 'Zero-Day']
    severities = ['Baja', 'Media', 'Alta', 'Crítica']
    statuses = ['Bloqueado', 'Exitoso']
    
    data = []
    for _ in range(num_muestras):
        source_country, target_country = np.random.choice(list(cities.keys()), 2, replace=False)
        data.append({
            'Timestamp': pd.to_datetime('now', utc=True) - pd.Timedelta(days=np.random.randint(0, 30)),
            'TipoAtaque': np.random.choice(attack_types, p=[0.3, 0.2, 0.2, 0.15, 0.1, 0.05]),
            'Severidad': np.random.choice(severities, p=[0.3, 0.4, 0.2, 0.1]),
            'PaisOrigen': source_country, 'PaisDestino': target_country,
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
severidad_seleccionada = st.sidebar.multiselect('Severidad:', st.session_state.attack_data['Severidad'].unique(), default=st.session_state.attack_data['Severidad'].unique())
tipo_ataque_seleccionado = st.sidebar.multiselect('Tipo de Ataque:', st.session_state.attack_data['TipoAtaque'].unique(), default=st.session_state.attack_data['TipoAtaque'].unique())
estado_seleccionado = st.sidebar.multiselect('Estado del Ataque:', st.session_state.attack_data['Estado'].unique(), default=st.session_state.attack_data['Estado'].unique())
pais_origen_seleccionado = st.sidebar.multiselect('País de Origen:', st.session_state.attack_data['PaisOrigen'].unique(), default=[])
pais_destino_seleccionado = st.sidebar.multiselect('País de Destino:', st.session_state.attack_data['PaisDestino'].unique(), default=[])

# Aplicar filtros
df_filtrado = st.session_state.attack_data[
    (st.session_state.attack_data['Severidad'].isin(severidad_seleccionada)) &
    (st.session_state.attack_data['TipoAtaque'].isin(tipo_ataque_seleccionado)) &
    (st.session_state.attack_data['Estado'].isin(estado_seleccionado))
]
if pais_origen_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['PaisOrigen'].isin(pais_origen_seleccionado)]
if pais_destino_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['PaisDestino'].isin(pais_destino_seleccionado)]

# --- PÁGINA PRINCIPAL ---
st.title("🛡️ Consola de Monitoreo de Amenazas Cibernéticas Globales")

# --- INDICADOR DE NIVEL DE AMENAZA ---
recent_attacks = df_filtrado[df_filtrado['Timestamp'] > (pd.to_datetime('now', utc=True) - pd.Timedelta(days=1))]
critical_count = len(recent_attacks[recent_attacks['Severidad'] == 'Crítica'])
threat_level, threat_color = ("Bajo", "green")
if critical_count > 5: threat_level, threat_color = ("Crítico", "red")
elif critical_count > 0: threat_level, threat_color = ("Elevado", "orange")
st.markdown(f"Nivel de Amenaza (24h): <span style='color:{threat_color}; font-size: 24px; font-weight: bold;'>{threat_level}</span>", unsafe_allow_html=True)

# --- KPIs ---
total_ataques, bloqueados = len(df_filtrado), df_filtrado[df_filtrado['Estado'] == 'Bloqueado'].shape[0]
tasa_bloqueo = (bloqueados / total_ataques * 100) if total_ataques > 0 else 0
top_target = df_filtrado['PaisDestino'].mode()[0] if not df_filtrado.empty else "N/A"
col1, col2, col3 = st.columns(3)
col1.metric("Ataques Detectados", f"{total_ataques:,}")
col2.metric("Tasa de Bloqueo", f"{tasa_bloqueo:.1f}%")
col3.metric("País Más Atacado", top_target)

st.markdown("---")

# --- MAPA Y FEED ---
col_map, col_feed = st.columns([3, 1])
with col_map:
    st.subheader("Mapa Global de Amenazas")
    def get_color(severidad):
        if severidad == 'Crítica': return [255, 0, 0, 180]
        if severidad == 'Alta': return [255, 100, 0, 150]
        if severidad == 'Media': return [255, 255, 0, 120]
        return [0, 255, 0, 100]
    df_filtrado['ColorArco'] = df_filtrado['Severidad'].apply(get_color)
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.5, pitch=50)
    arc_layer = pdk.Layer('ArcLayer', data=df_filtrado, get_source_position='[LonOrigen, LatOrigen]', get_target_position='[LonDestino, LatDestino]', get_source_color='[0, 255, 0, 160]', get_target_color='ColorArco', get_width=2, auto_highlight=True)
    st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/dark-v9', initial_view_state=view_state, layers=[arc_layer], tooltip={"text": "{TipoAtaque}\nDe: {PaisOrigen} a {PaisDestino}\nSeveridad: {Severidad}"}))

with col_feed:
    st.subheader("Feed de Actividad")
    st.dataframe(df_filtrado[['Timestamp', 'TipoAtaque', 'Severidad', 'PaisOrigen', 'PaisDestino']].head(15), hide_index=True, use_container_width=True)

st.markdown("---")
st.header("Análisis Detallado de Amenazas")

# --- GRÁFICOS ADICIONALES ---
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.subheader("Vectores de Ataque Principales")
    heatmap_data = df_filtrado.groupby(['PaisOrigen', 'PaisDestino']).size().reset_index(name='count')
    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X('PaisOrigen:N', title='País de Origen', sort='-color'),
        y=alt.Y('PaisDestino:N', title='País de Destino', sort='-color'),
        color=alt.Color('count:Q', title='Nº de Ataques', scale=alt.Scale(scheme='redyellowblue', reverse=True)),
        tooltip=['PaisOrigen', 'PaisDestino', 'count']
    ).interactive()
    st.altair_chart(heatmap, use_container_width=True)

    st.subheader("Efectividad de Contención")
    status_data = df_filtrado['Estado'].value_counts().reset_index()
    donut_chart = alt.Chart(status_data).mark_arc(innerRadius=70).encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="Estado", type="nominal", scale=alt.Scale(domain=['Bloqueado', 'Exitoso'], range=['#32a852', '#d9453b'])),
        tooltip=['Estado', 'count']
    )
    st.altair_chart(donut_chart, use_container_width=True)

with col_g2:
    st.subheader("Línea de Tiempo por Severidad")
    df_filtrado['Fecha'] = df_filtrado['Timestamp'].dt.date
    timeline_data = df_filtrado.groupby(['Fecha', 'Severidad']).size().reset_index(name='count')
    timeline = alt.Chart(timeline_data).mark_area().encode(
        x=alt.X('Fecha:T', title='Fecha'),
        y=alt.Y('count:Q', title='Número de Ataques', stack='normalize'),
        color=alt.Color('Severidad:N', scale=alt.Scale(domain=['Crítica', 'Alta', 'Media', 'Baja'], range=['#e03131', '#f76707', '#fcc419', '#40c057'])),
        tooltip=['Fecha', 'Severidad', 'count']
    ).interactive()
    st.altair_chart(timeline, use_container_width=True)
