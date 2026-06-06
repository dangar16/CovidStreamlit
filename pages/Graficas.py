import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Gráficas - COVID-19 España",
    layout="wide"

@st.cache_data
def cargar_datos():
    """
    Cargamos los datos del csv y utilizamos @st.cache_data para almacenar en caché el resultado y evitar recargas innecesarias.
    """
    df = pd.read_csv('./49871.csv', sep=';', encoding='utf-8')
    df['Total'] = pd.to_numeric(
        df['Total'].astype(str).str.replace('.', '', regex=False).str.replace('..', ''),
        errors='coerce'
    ).fillna(0)
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

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo `49871.csv`. Colócalo en el directorio raíz de la app.")
    st.stop()

col_ccaa = 'Autonomous city and community of death'
orden_meses = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
meses_disp = [m for m in orden_meses if m in df['Month of death'].unique()]

st.markdown("""
<h1 style="font-size:2.2rem">Análisis y Gráficas</h1>
<p>Explora la mortalidad COVID-19</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Sidebar tipo covid
with st.sidebar:
    st.markdown("## Filtros globales")
    st.markdown("---")

    tipo_covid = st.selectbox(
        "Tipo de COVID-19",
        options=['Identified Covid-19 virus', 'Unidentified (suspected) COVID-19 virus'],
        format_func=lambda x: "Sospechoso" if "Un" in x else "Identificado"
    )