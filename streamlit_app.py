import streamlit as st
import pandas as pd
import plotly.express as px
from quakefeeds import QuakeFeed
from datetime import datetime

# -----------------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------------
st.set_page_config(layout="wide")
st.title("Datos en Tiempo Real de los Terremotos en Puerto Rico y en el Mundo")

st.markdown("<br><br>", unsafe_allow_html=True)

token_id = "pk.eyJ1IjoibWVjb2JpIiwiYSI6IjU4YzVlOGQ2YjEzYjE3NTcxOTExZTI2OWY3Y2Y1ZGYxIn0.LUg7xQhGH2uf3zA57szCyw"
px.set_mapbox_access_token(token_id)

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.header("Opciones")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

sev_es = st.sidebar.selectbox(
    "Severidad",
    ["todos", "significativo", "4.5", "2.5", "1.0"],
    index=0
)

per_es = st.sidebar.selectbox(
    "Período",
    ["mes", "semana", "día"],
    index=0
)

zona = st.sidebar.selectbox(
    "Zona Geográfica",
    ["Puerto Rico", "Mundo"],
    index=0
)

mostrar_mapa = st.sidebar.checkbox("Mostrar mapa", True)
mostrar_tabla = st.sidebar.checkbox("Mostrar tabla con eventos", True)

if mostrar_tabla:
    n_eventos = st.sidebar.slider("Cantidad de eventos", 5, 20, 5)

st.sidebar.markdown("---")

st.sidebar.write("**Aplicación desarrollada por:** Diego Borrero")
st.sidebar.write("**Curso:** INGE3016")
st.sidebar.write("**Universidad de Puerto Rico en Humacao**")

# -----------------------------------
# MAPEO ESPAÑOL → INGLÉS
# -----------------------------------
sev_map = {
    "todos": "all",
    "significativo": "significant",
    "4.5": "4.5",
    "2.5": "2.5",
    "1.0": "1.0"
}

per_map = {
    "mes": "month",
    "semana": "week",
    "día": "day"
}

sev = sev_map[sev_es]
per = per_map[per_es]

# -----------------------------------
# FUNCIONES
# -----------------------------------
def clasificacion(m):
    if m < 2: return "micro"
    elif m < 4: return "menor"
    elif m < 5: return "ligero"
    elif m < 6: return "moderado"
    elif m < 7: return "fuerte"
    elif m < 8: return "mayor"
    elif m < 10: return "extremo"
    else: return "legendario"

def generaTabla():
    feed = QuakeFeed(sev, per)

    df = pd.DataFrame({
        "fecha": list(feed.event_times),
        "lon": [feed.location(i)[0] for i in range(len(feed))],
        "lat": [feed.location(i)[1] for i in range(len(feed))],
        "localización": list(feed.places),
        "magnitud": list(feed.magnitudes),
        "prof": list(feed.depths)
    })

    df["magnitud"] = pd.to_numeric(df["magnitud"], errors="coerce")
    df["prof"] = pd.to_numeric(df["prof"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    df = df.dropna(subset=["magnitud", "lat", "lon"])

    df["clasificación"] = df["magnitud"].apply(clasificacion)

    df["size_mag"] = df["magnitud"].abs()
    df.loc[df["size_mag"] <= 0, "size_mag"] = 0.1

    if zona == "Puerto Rico":
        df = df[
            (df["lat"] >= 17) & (df["lat"] <= 19) &
            (df["lon"] >= -68) & (df["lon"] <= -64)
        ]

    return df

def generaMapa(df):
    if zona == "Puerto Rico":
        center = dict(lat=18.2, lon=-66.3)
        zoom = 7
    else:
        center = dict(lat=0, lon=0)
        zoom = 1

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="magnitud",
        size="size_mag",
        hover_name="localización",
        hover_data={
            "magnitud": True,
            "prof": True,
            "clasificación": True
        },
        color_continuous_scale="Reds",
        size_max=10,
        opacity=0.6,
        center=center,
        zoom=zoom,
        mapbox_style="dark"
    )

    return fig

# -----------------------------------
# EJECUCIÓN
# -----------------------------------
df = generaTabla()

if df.empty:
    st.warning("No hay eventos sísmicos para los filtros seleccionados.")
    st.stop()

st.markdown(
    f"""
    <div style="text-align:center; font-size:18px;">
        <p><strong>Fecha de petición:</strong> {datetime.now()}</p>
        <p><strong>Cantidad de eventos:</strong> {len(df)}</p>
        <p><strong>Promedio de magnitudes:</strong> {round(df["magnitud"].mean(), 2)}</p>
        <p><strong>Promedio de profundidades:</strong> {round(df["prof"].mean(), 2)}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------
# LAYOUT FINAL
# -----------------------------------
if mostrar_tabla:
    st.subheader("Eventos sísmicos")
    st.dataframe(
        df[["fecha", "localización", "magnitud", "clasificación"]].head(n_eventos),
        use_container_width=True
    )

st.markdown("<br><hr><br>", unsafe_allow_html=True)

col_hist1, col_hist2, col_mapa = st.columns([1, 1, 2])

with col_hist1:
    fig_mag = px.histogram(
        df,
        x="magnitud",
        title="Histograma de magnitudes",
        color_discrete_sequence=["red"]
    )
    st.plotly_chart(fig_mag, use_container_width=True)

with col_hist2:
    fig_prof = px.histogram(
        df,
        x="prof",
        title="Histograma de profundidades",
        color_discrete_sequence=["red"]
    )
    st.plotly_chart(fig_prof, use_container_width=True)

with col_mapa:
    if mostrar_mapa:
        st.plotly_chart(generaMapa(df), use_container_width=True)




        


