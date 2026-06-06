import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Gráficas - COVID-19 España",
    layout="wide"
)

# Colores personalizados para títulos y descripciones de gráficas
BG = '#0d1117'
BG2 = '#161b22'
BORDER = '#21262d'
TEXT = 'white'
MUTED = 'gray'
RED = 'red'
BLUE = 'blue'
PURPLE = 'purple'

# Layout de plotly común para todas las gráficas
PLOTLY_LAYOUT = dict(
    font=dict(color=TEXT, family='DM Sans'),
    margin=dict(l=16, r=16, t=40, b=40),
    legend=dict(
        bgcolor=BG2, bordercolor=BORDER, borderwidth=1,
    )
)

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

# GRÁFICA 1: Evolución mensual nacional - Identificado vs Sospechoso
st.markdown('Evolución Mensual Nacional')

c_g1a, c_g1b = st.columns([2, 1]) # [2, 1] para dar más espacio a la gráfica
# La segunda columna es para el selector de modo (indetificado vs sospechoso o por género)
with c_g1b:
    modo_g1 = st.radio(
        "Mostrar",
        options=['Identificado vs Sospechoso', 'Por Género'],
    )

# la primera columna es para la gráfica, que cambia según el modo seleccionado
with c_g1a:

    # mostrar gráfica de mortalidad según si el COVID-19 es identificado o sospechoso
    if modo_g1 == 'Identificado vs Sospechoso':
        df_id = df[
            (df[col_ccaa] == 'National total') &
            (df['Covid-19'] == 'Identified Covid-19 virus') &
            (df['Gender'] == 'Total') &
            (df['Place of death'] == 'Total') &
            (df['Month of death'] != 'Total')
        ].copy()
        df_id['orden'] = df_id['Month of death'].apply(lambda x: orden_meses.index(x) if x in orden_meses else 99)
        df_id = df_id.sort_values('orden')

        df_sosp = df[
            (df[col_ccaa] == 'National total') &
            (df['Covid-19'] == 'Unidentified (suspected) COVID-19 virus') &
            (df['Gender'] == 'Total') &
            (df['Place of death'] == 'Total') &
            (df['Month of death'] != 'Total')
        ].copy()
        df_sosp['orden'] = df_sosp['Month of death'].apply(lambda x: orden_meses.index(x) if x in orden_meses else 99)
        df_sosp = df_sosp.sort_values('orden')

        fig1 = go.Figure()

        # linea 1 para el covid identificado
        fig1.add_trace(go.Scatter(
            x=df_id['Month of death'], y=df_id['Total'],
            name='Identificado', mode='lines+markers',
            line=dict(color=RED, width=2.5),
            marker=dict(size=7, color=RED),
        ))

        # linea 2 para el covid sospechoso
        fig1.add_trace(go.Scatter(
            x=df_sosp['Month of death'], y=df_sosp['Total'],
            name='Sospechoso', mode='lines+markers',
            line=dict(color=BLUE, width=2.5, dash='dash'),
            marker=dict(size=7, color=BLUE),
        ))
    else: # tasa de mortalidad por género
        df_hom = df[
            (df[col_ccaa] == 'National total') &
            (df['Covid-19'] == tipo_covid) &
            (df['Gender'] == 'Men') &
            (df['Place of death'] == 'Total') &
            (df['Month of death'] != 'Total')
        ].copy()
        df_hom['orden'] = df_hom['Month of death'].apply(lambda x: orden_meses.index(x) if x in orden_meses else 99)
        df_hom = df_hom.sort_values('orden')

        df_muj = df[
            (df[col_ccaa] == 'National total') &
            (df['Covid-19'] == tipo_covid) &
            (df['Gender'] == 'Women') &
            (df['Place of death'] == 'Total') &
            (df['Month of death'] != 'Total')
        ].copy()
        df_muj['orden'] = df_muj['Month of death'].apply(lambda x: orden_meses.index(x) if x in orden_meses else 99)
        df_muj = df_muj.sort_values('orden')

        fig1 = go.Figure()

        # linea 1 para hombres
        fig1.add_trace(go.Scatter(
            x=df_hom['Month of death'], y=df_hom['Total'],
            name='Hombres', mode='lines+markers',
            line=dict(color=BLUE, width=2.5),
            marker=dict(size=7, color=BLUE),
        ))

        # linea 2 para mujeres
        fig1.add_trace(go.Scatter(
            x=df_muj['Month of death'], y=df_muj['Total'],
            name='Mujeres', mode='lines+markers',
            line=dict(color=PURPLE, width=2.5, dash='dash'),
            marker=dict(size=7, color=PURPLE),
        ))

    # aplicamos layout común a la gráfica
    fig1.update_layout(
        **PLOTLY_LAYOUT,
        height=340,
        title=dict(text='Fallecidos por mes - Total Nacional', font=dict(size=13, color=MUTED), x=0.01),
        hovermode='x unified' # NOTE: https://plotly.com/python/hover-text-and-formatting/#unified-hover-mode
    )
    st.plotly_chart(fig1)

st.markdown("---")

# GRÁFICA 2: Ranking CCAA
st.markdown('Ranking por Comunidad Autónoma')
st.markdown('Total de fallecidos por CCAA. Filtra por mes y género para ver cómo cambia la distribución.')

cg2a, cg2b, cg2c = st.columns([1, 1, 2])

# Selector de género
with cg2a:
    genero_g2 = st.selectbox(
        "Género",
        options=['Total', 'Men', 'Women'],
        format_func=lambda x: {'Total': 'Total', 'Men': 'Hombres', 'Women': 'Mujeres'}[x],
        key='g2_genero'
    )

# Selector de mes
with cg2b:
    mes_g2 = st.selectbox(
        "Mes",
        options=['Total'] + meses_disp,
        format_func=lambda x: 'Año completo' if x == 'Total' else x,
        key='g2_mes'
    )

# Filtramos y ordenamos los datos para la gráfica de barras
df_ranking = df[
    (df['Covid-19'] == tipo_covid) &
    (df['Gender'] == genero_g2) &
    (df['Place of death'] == 'Total') &
    (df['Month of death'] == mes_g2) &
    (df[col_ccaa] != 'National total')
].groupby(col_ccaa, as_index=False)['Total'].sum()
df_ranking = df_ranking.sort_values('Total', ascending=True)

colors_bar = [RED if v == df_ranking['Total'].max() else '#30363d' for v in df_ranking['Total']] # rojo para la primera, el resto gris

fig2 = go.Figure(go.Bar(
    x=df_ranking['Total'], # num fallecidos
    y=df_ranking[col_ccaa], # CCAA
    orientation='h', # barras horizontales
    marker=dict(color=colors_bar, line=dict(width=0)),
    text=df_ranking['Total'].apply(lambda x: f'{int(x):,}'), # texto a mostrar en cada barra
    textposition='outside', # posición del texto
    textfont=dict(color=MUTED, size=11),
    hovertemplate='<b>%{y}</b><br>Fallecidos: %{x:,}'
))
fig2.update_layout(
    **PLOTLY_LAYOUT,
    height=480,
    title=dict(text='Fallecidos por CCAA', font=dict(size=13, color=MUTED), x=0.01),
    xaxis_title=None,
    yaxis_title=None,
)
st.plotly_chart(fig2)

st.markdown("---")

