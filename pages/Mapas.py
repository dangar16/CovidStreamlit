import streamlit as st
import pandas as pd
import json
import geopandas as gpd
import plotly.express as px

st.set_page_config(
    page_title="Mapa - COVID-19 España",
    layout="wide"
)

defaults = {
    'tipo_covid_mapa': 'Identified Covid-19 virus',
    'genero': 'Total',
    'mes': 'Total',
    'color': 'Reds'
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = st.session_state.get(f'_bk_{k}', v)

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

orden_meses = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

with st.sidebar:
    st.markdown("## Filtros del Mapa")
    st.markdown("---")

    # selector de tipo de COVID-19
    opciones_covid = ['Identified Covid-19 virus', 'Unidentified (suspected) COVID-19 virus']
    tipo_covid = st.selectbox(
        "Tipo de COVID-19",
        options=opciones_covid,
        key='tipo_covid_mapa',
        format_func=lambda x: "Sospechoso" if "Unidentified" in x else "Identificado" # Function to modify the display of the options. NOTE: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
    )

    # Selector de género
    opciones_genero = ['Total', 'Men', 'Women']
    genero = st.selectbox(
        "Género",
        options=opciones_genero,
        key='genero',
        format_func=lambda x: {'Total': 'Total', 'Men': 'Hombres', 'Women': 'Mujeres'}[x]
    )

    lugar = "Total"

    # Mostrar selector de meses
    meses_disponibles = [m for m in orden_meses if m in df['Month of death'].unique()]
    opciones_mes = ['Total'] + meses_disponibles
    mes_sel = st.selectbox(
        "Mes",
        options=opciones_mes,
        key='mes',
        format_func=lambda x: 'Año completo' if x == 'Total' else x
    )

    st.markdown("---")
    # escala del color para el mapa
    color_opciones = ['Reds', 'YlOrRd', 'OrRd', 'PuRd', 'Reds_r']
    escala_color = st.selectbox(
        "Escala de color",
        options=color_opciones,
        key='color'
    )

col = 'Autonomous city and community of death'

@st.cache_data
def obtener_df_filtrado(df, tipo_covid, genero, lugar, mes_sel, col):
    df_filtrado = df[
        (df['Covid-19'] == tipo_covid) &
        (df['Gender'] == genero) &
        (df['Place of death'] == lugar) &
        (df['Month of death'] == mes_sel) &
        (df[col] != 'National total')
    ].groupby(col, as_index=False)['Total'].sum()

    df_filtrado = df_filtrado.rename(columns={col: 'name'}) # cambiamos el nombre para que coincida con el geojson

    return df_filtrado

df_filtrado = obtener_df_filtrado(df, tipo_covid, genero, lugar, mes_sel, col)

# Añadir CCAA sin datos con 0
nombres_geo = [f['properties']['name'] for f in geojson['features']]
df_completo = pd.DataFrame({'name': nombres_geo})
df_completo = df_completo.merge(df_filtrado, on='name', how='left') # merge 
df_completo['Total'] = df_completo['Total'].fillna(0) # rellenamos con 0 las CCAA sin datos

total_nacional = int(df_filtrado['Total'].sum()) # total de fallecidos para el filtro seleccionado
ccaa_max = df_filtrado.loc[df_filtrado['Total'].idxmax(), 'name'] if not df_filtrado.empty and df_filtrado['Total'].max() > 0 else "-" # CCAA con más fallecidos
val_max = int(df_filtrado['Total'].max()) if not df_filtrado.empty else 0 # Valor máximo de fallecidos según el filtro
ccaa_min_data = df_filtrado[df_filtrado['Total'] > 0] # obtenemos solo las CCAA con más de 0 fallecidos para el mínimo
ccaa_min = ccaa_min_data.loc[ccaa_min_data['Total'].idxmin(), 'name'] if not ccaa_min_data.empty else "-" # CCAA con menos fallecidos

# métricas a mostrar extraidas de arriba
m1, m2, m3 = st.columns(3)
m1.metric("Total nacional", f"{total_nacional:,}")
m2.metric("CCAA con más fallecidos", ccaa_max, f"{val_max:,}")
m3.metric("CCAA con menos (>0)", ccaa_min)

fig = px.choropleth(
    df_completo,
    geojson=geojson,
    locations='name',
    featureidkey='properties.name',
    color='Total', # el color se basa en el número de fallecidos
    color_continuous_scale=escala_color, # escala de color que se selecciona en el sidebar
    hover_name='name', # mostrar el nombre de la CCAA en el hover
    hover_data={'Total': ':,'}, # formatear numero cuando se muestra en el hover
    labels={'Total': 'Fallecidos'}, # etiqueta para la leyenda del color
)

# Ajustar el mapa para que se centre en españa y no muestre todo el mundo
fig.update_geos(
    fitbounds="locations",
    visible=False,
)

fig.update_layout(
    geo_bgcolor='#0d1117', # fondo del mapa
    height=550,
    coloraxis_colorbar=dict(
        borderwidth=1,
    )
)

fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Fallecidos: %{z:,}"
)

st.plotly_chart(fig)

with st.expander("Ver tabla de datos completa"):
    df_tabla = df_filtrado.sort_values('Total', ascending=False).copy()
    df_tabla['Total'] = df_tabla['Total'].astype(int)
    df_tabla.columns = ['Comunidad Autónoma', 'Fallecidos']
    df_tabla = df_tabla.reset_index(drop=True)
    df_tabla.index = df_tabla.index + 1
    st.dataframe(
        df_tabla,
        column_config={
            # Añadimos una barra de progreso para visualizar mejor la diferencia entre CCAA.
            "Fallecidos": st.column_config.ProgressColumn(
                "Fallecidos",
                min_value=0,
                max_value=int(df_tabla['Fallecidos'].max()),
                format="%d"
            )
        }
    )


for k in defaults:
    st.session_state[f'_bk_{k}'] = st.session_state[k]