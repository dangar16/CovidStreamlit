import streamlit as st
import pandas as pd
import json
import geopandas as gpd

st.set_page_config(
    page_title="Mapa - COVID-19 España",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    """
    Igual que en el Inicio, cacheamos la carga de datos para evitar recargas innecesarias.
    """
    df = pd.read_csv('./49871.csv', sep=';', encoding='utf-8')
    df['Total'] = pd.to_numeric(
        df['Total'].astype(str).str.replace('.', '', regex=False).str.replace('..', ''),
        errors='coerce'
    ).fillna(0)

    # mapeo para adaptarlo al geojson
    mapeo = {
        'Andalucía': 'Andalucia', 'Aragón': 'Aragon',
        'Asturias, Principado de': 'Asturias', 'Balears, Illes': 'Baleares',
        'Castilla y León': 'Castilla-Leon', 'Comunitat Valenciana': 'Valencia',
        'Madrid, Comunidad de': 'Madrid', 'Murcia, Región de': 'Murcia',
        'Navarra, Comunidad Foral de': 'Navarra', 'País Vasco': 'Pais Vasco',
        'Rioja, La': 'La Rioja'
    }
    col = 'Autonomous city and community of death'
    df[col] = df[col].replace(mapeo)
    return df

@st.cache_data
def cargar_geojson():
    """
    Para no cargar el geojson cada vez, lo cacheamos también.
    """
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/spain-communities.geojson"
    gdf = gpd.read_file(url)
    return json.loads(gdf[['name', 'geometry']].to_json())

st.markdown("""
<h1 style="font-size:2.2rem">
    Mapa de Coropletas
</h1>
<p style="color:gray;">
    Distribución geográfica de fallecidos por COVID-19 en España 2020
</p>
""", unsafe_allow_html=True)
st.markdown("---")

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("No se ha encontrado el fichero 49871.csv")
    st.stop()

with st.spinner("Cargando el mapa de España"):
    geojson = cargar_geojson()
