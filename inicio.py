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
