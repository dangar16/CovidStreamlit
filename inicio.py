import streamlit as st

st.set_page_config(
    page_title="COVID-19 España - Dashboard",
    layout="wide", # wide para que el texto ocupe el ancho de la página
)
st.markdown("""
<div>
  <p style="font-size:2.2rem">COVID-19 España</p>
  <p>
    Página web de streamlit para visualizar información sobre la mortalidad por COVID-19 por Comunidad Autónoma, género y período.<br>
    Datos del INE - Año 2020.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

import pandas as pd

@st.cache_data
def cargar_datos():
    """
    Cargamos los datos del csv y utilizamos @st.cache_data para almacenar en caché el resultado y evitar recargas innecesarias.
    """
    df = pd.read_csv('./49871.csv', sep=';', encoding='utf-8')

    # limpieza columna Total, eliminamos puntos de la columna total y convertimos a numérico
    df['Total'] = pd.to_numeric(
        df['Total'].astype(str).str.replace('.', '', regex=False).str.replace('..', ''),
        errors='coerce'
    ).fillna(0)

    return df

IDENTIFICADO = "Identified Covid-19 virus"
SOSP = "Unidentified (suspected) COVID-19 virus"
TOTAL = "Total"
NATIONAL_TOTAL = "National total"
HOMBRES = "Men"
MUJERES = "Women"

try:
    df = cargar_datos()
    col = 'Autonomous city and community of death'

    # total de fallecidos identificados
    total_id = int(df[
        (df['Covid-19'] == IDENTIFICADO) &
        (df['Gender'] == TOTAL) &
        (df['Place of death'] == TOTAL) &
        (df['Month of death'] == TOTAL) &
        (df[col] == NATIONAL_TOTAL)
    ]['Total'].sum())

    # total de fallecidos por covid sospechoso
    total_sosp = int(df[
        (df['Covid-19'] == SOSP) &
        (df['Gender'] == TOTAL) &
        (df['Place of death'] == TOTAL) &
        (df['Month of death'] == TOTAL) &
        (df[col] == NATIONAL_TOTAL)
    ]['Total'].sum())

    # hombres fallecidos por covid identificado
    total_hom = int(df[
        (df['Covid-19'] == IDENTIFICADO) &
        (df['Gender'] == HOMBRES) &
        (df['Place of death'] == TOTAL) &
        (df['Month of death'] == TOTAL) &
        (df[col] == NATIONAL_TOTAL)
    ]['Total'].sum())

    # mujeres fallecidas por covid identificado
    total_muj = int(df[
        (df['Covid-19'] == IDENTIFICADO) &
        (df['Gender'] == MUJERES) &
        (df['Place of death'] == TOTAL) &
        (df['Month of death'] == TOTAL) &
        (df[col] == NATIONAL_TOTAL)
    ]['Total'].sum())

    # Creamos las 4 columnas para mostrar métricas principales del dataset.
    # se usa metric para mostrar el número total y el porcentaje respecto al total de fallecidos identificados, con delta para mostrar el porcentaje en verde.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fallecidos identificados", f"{total_id:,}")
    c2.metric("Casos sospechosos", f"{total_sosp:,}")
    c3.metric("Hombres", f"{total_hom:,}", delta=f"{total_hom/total_id*100:.0f}% del total") # delta para mostrar en verde el porcentaje respecto al total
    c4.metric("Mujeres", f"{total_muj:,}", delta=f"{total_muj/total_id*100:.0f}% del total") # lo mismo que arriba

except FileNotFoundError:
    st.warning("49871.csv no se ha encontrado")
