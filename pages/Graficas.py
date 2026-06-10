import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Gráficas - COVID-19 España",
    layout="wide"
)

defaults = {
    'tipo_covid': 'Identified Covid-19 virus',
    'g1_modo': 'Identificado vs Sospechoso',
    'g2_genero': 'Total',
    'g2_mes': 'Total',
    'g3_mes': 'Total',
    'g4_genero': 'Total',
    'g5_genero': 'Total',
    'g5_ccaa': 'National total'
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = st.session_state.get(f'_bk_{k}', v)

# Colores personalizados para títulos y descripciones de gráficas
BG = '#0d1117'
BG2 = '#161b22'
BORDER = '#21262d'
TEXT = 'white'
MUTED = 'gray'
RED = 'red'
BLUE = 'blue'
PURPLE = 'purple'
GREEN = 'green'
ORANGE = 'orange'

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

opciones_covid = ['Identified Covid-19 virus', 'Unidentified (suspected) COVID-19 virus']

# Sidebar tipo covid
with st.sidebar:
    st.markdown("## Filtros globales")
    st.markdown("---")

    tipo_covid = st.selectbox(
        "Tipo de COVID-19",
        options=opciones_covid,
        key='tipo_covid',
        format_func=lambda x: "Sospechoso" if "Un" in x else "Identificado"
    )

col1, col2, _, _ = st.columns(4)

# Calcular totales
total_fallecidos = df[(df['Covid-19'] == tipo_covid) & 
                      (df[col_ccaa] == 'National total') & 
                      (df['Gender'] == 'Total') &
                      (df['Place of death'] == 'Total') &
                      (df['Month of death'] == 'Total')]['Total'].sum()

max_mes = df[(df['Covid-19'] == tipo_covid) & 
             (df[col_ccaa] == 'National total') & 
             (df['Gender'] == 'Total') &
             (df['Month of death'] != 'Total')].sort_values('Total', ascending=False).iloc[0]

with col1:
    st.metric("Total Fallecidos", f"{total_fallecidos:,}")
with col2:
    st.metric(
        label="Pico Mensual",
        value=f"{int(max_mes['Total']):,}",
        delta=f"{max_mes['Month of death']}",
        delta_color="off"
    )

# GRÁFICA 1: Evolución mensual nacional - Identificado vs Sospechoso
st.markdown('Evolución Mensual Nacional')

c_g1a, c_g1b = st.columns([2, 1]) # [2, 1] para dar más espacio a la gráfica
# La segunda columna es para el selector de modo (indetificado vs sospechoso o por género)
with c_g1b:
    opciones = ['Identificado vs Sospechoso', 'Por Género']
    modo_g1 = st.radio(
        "Mostrar",
        options=opciones,
        key='g1_modo'
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

opciones_genero = ['Total', 'Men', 'Women']

# Selector de género
with cg2a:
    genero_g2 = st.selectbox(
        "Género",
        options=opciones_genero,
        format_func=lambda x: {'Total': 'Total', 'Men': 'Hombres', 'Women': 'Mujeres'}[x],
        key='g2_genero'
    )

# Selector de mes

opciones_mes = ['Total'] + meses_disp

mapeo_meses = {
    "Total": "Año completo",
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre"
}

with cg2b:
    mes_g2 = st.selectbox(
        "Mes",
        options=opciones_mes,
        format_func=lambda x: mapeo_meses.get(x, x),
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
    hovertemplate='<b>%{y}</b><br>Fallecidos: %{x:,}<extra></extra>'
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

# GRÁFICA 3: Fallecidos por CCAA por género (barras apiladas)
st.markdown('Proporción de Género por CCAA')
st.markdown('Distribución porcentual de fallecidos hombres vs mujeres en cada Comunidad Autónoma.')

cg3a, _ = st.columns([1, 2])

# Selector de mes
with cg3a:
    mes_g3 = st.selectbox(
        "Mes",
        options=opciones_mes,
        format_func=lambda x: mapeo_meses.get(x, x),
        key='g3_mes'
    )

# Datos hombre CCAA
df_hom_cc = df[
    (df['Covid-19'] == tipo_covid) &
    (df['Gender'] == 'Men') &
    (df['Place of death'] == 'Total') &
    (df['Month of death'] == mes_g3) &
    (df[col_ccaa] != 'National total')
].groupby(col_ccaa, as_index=False)['Total'].sum().rename(columns={'Total': 'Hombres'})

# Datos mujer CCAA
df_muj_cc = df[
    (df['Covid-19'] == tipo_covid) &
    (df['Gender'] == 'Women') &
    (df['Place of death'] == 'Total') &
    (df['Month of death'] == mes_g3) &
    (df[col_ccaa] != 'National total')
].groupby(col_ccaa, as_index=False)['Total'].sum().rename(columns={'Total': 'Mujeres'})

# Unimos ambos dataframes para calcular totales y porcentajes
df_genero = df_hom_cc.merge(df_muj_cc, on=col_ccaa)
df_genero['total'] = df_genero['Hombres'] + df_genero['Mujeres']
df_genero['pct_hom'] = df_genero['Hombres'] / df_genero['total'] * 100
df_genero['pct_muj'] = df_genero['Mujeres'] / df_genero['total'] * 100
df_genero = df_genero.dropna().sort_values('pct_hom', ascending=True)

# Gráfica de barras apiladas 100%
fig3 = go.Figure()
fig3.add_trace(go.Bar(
    name='Hombres',
    x=df_genero['pct_hom'],
    y=df_genero[col_ccaa],
    orientation='h',
    marker_color=BLUE,
    text=df_genero['pct_hom'].apply(lambda x: f'{x:.1f}%'),
    textposition='inside',
    textfont=dict(color='white', size=10),
    hovertemplate='<b>%{y}</b><br>Hombres: %{x:.1f}%<extra></extra>'
))
fig3.add_trace(go.Bar(
    name='Mujeres',
    x=df_genero['pct_muj'],
    y=df_genero[col_ccaa],
    orientation='h',
    marker_color=PURPLE,
    text=df_genero['pct_muj'].apply(lambda x: f'{x:.1f}%'),
    textposition='inside',
    textfont=dict(color='white', size=10),
    hovertemplate='<b>%{y}</b><br>Mujeres: %{x:.1f}%<extra></extra>'
))
fig3.add_vline(x=50, line_dash='dash', line_color=MUTED, opacity=0.5)
fig3.update_layout(
    **PLOTLY_LAYOUT,
    barmode='stack',
    height=500,
    title=dict(text='Distribución por género (%) por CCAA', font=dict(size=13, color=MUTED), x=0.01),
)
st.plotly_chart(fig3, width='stretch')

st.markdown("---")

# GRÁFICA 4: Heatmap mensual por CCAA
st.markdown('Heatmap Mensual por CCAA')
st.markdown('Intensidad de fallecidos a lo largo del año para cada Comunidad Autónoma. ')

cg4a, _ = st.columns([1, 2])

# selector de género
with cg4a:
    genero_g4 = st.selectbox(
        "Género",
        options=opciones_genero,
        format_func=lambda x: {'Total': 'Total', 'Men': 'Hombres', 'Women': 'Mujeres'}[x],
        key='g4_genero'
    )

# Filtramos los datos para el heatmap
df_heat = df[
    (df['Covid-19'] == tipo_covid) &
    (df['Gender'] == genero_g4) &
    (df['Place of death'] == 'Total') &
    (df['Month of death'] != 'Total') &
    (df[col_ccaa] != 'National total')
].copy()

# Creamos una tabla pivote para el heatmap
pivot = df_heat.pivot_table(
    index=col_ccaa, columns='Month of death', values='Total'
).reindex(columns=[m for m in orden_meses if m in df_heat['Month of death'].unique()])

# Ordenar filas por total
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

fig4 = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns.tolist(),
    y=pivot.index.tolist(),
    colorscale='Reds',
    hoverongaps=False,
    hovertemplate='<b>%{y}</b><br>%{x}: <b>%{z:,}</b> fallecidos<extra></extra>',
    colorbar=dict(
        tickfont=dict(color=MUTED),
        title=dict(text='Fallecidos', font=dict(color=MUTED)),
        bgcolor=BG2,
        bordercolor=BORDER,
        borderwidth=1,
        outlinecolor=BORDER
    )
))
fig4.update_layout(
    **PLOTLY_LAYOUT,
    height=500,
    title=dict(text='Fallecidos por CCAA y mes', font=dict(size=13, color=MUTED), x=0.01),
)
st.plotly_chart(fig4)

st.markdown("---")

# GRÁFICA 5: Lugar de fallecimiento
st.markdown('Distribución por Lugar de Fallecimiento')
st.markdown('¿Dónde fallecieron las personas? Compara la distribución entre hospital, domicilio, residencia y otros.')

cg5a, cg5b, _ = st.columns([1, 1, 1])

# Selector de género
with cg5a:
    genero_g5 = st.selectbox(
        "Género",
        options=opciones_genero,
        format_func=lambda x: {'Total': 'Total', 'Men': 'Hombres', 'Women': 'Mujeres'}[x],
        key='g5_genero'
    )

# Selector de CCAA
with cg5b:
    ccaa_list = sorted([c for c in df[col_ccaa].unique() if c != 'National total'])
    opciones = ['National total'] + ccaa_list
    ccaa_g5 = st.selectbox(
        "Comunidad Autónoma",
        options=opciones,
        key='g5_ccaa'
    )

# Filtramos los datos para la gráfica de lugar de fallecimiento
lugares_excl = ['Total']
df_lugar = df[
    (df['Covid-19'] == tipo_covid) &
    (df['Gender'] == genero_g5) &
    (df['Month of death'] == 'Total') &
    (df[col_ccaa] == ccaa_g5) &
    (~df['Place of death'].isin(lugares_excl))
].groupby('Place of death', as_index=False)['Total'].sum()

df_lugar = df_lugar[df_lugar['Total'] > 0].sort_values('Total', ascending=False)

lugar_labels = {
    'Hospital centre': 'Hospital',
    'Home': 'Domicilio',
    'Health care home': 'Residencia',
    'Not specified': 'No especificado',
    'Other place': 'Otro lugar'
}
df_lugar['label'] = df_lugar['Place of death'].map(lugar_labels).fillna(df_lugar['Place of death'])

lugar_colors = [RED, BLUE, PURPLE, GREEN, ORANGE]

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=df_lugar['label'],
    y=df_lugar['Total'],
    marker=dict(
        color=lugar_colors[:len(df_lugar)],
        line=dict(width=0)
    ),
    text=df_lugar['Total'].apply(lambda x: f'{int(x):,}'),
    textposition='outside',
    textfont=dict(color=MUTED, size=11),
    hovertemplate='<b>%{x}</b><br>Fallecidos: %{y:,}<extra></extra>'
))
total_lugar = int(df_lugar['Total'].sum())
fig5.update_layout(
    **PLOTLY_LAYOUT,
    height=360,
    title=dict(text=f'Lugar de fallecimiento - {ccaa_g5} (Total: {total_lugar:,})',
               font=dict(size=13, color=MUTED), x=0.01),
    xaxis_title=None,
    yaxis_title='Fallecidos',
    showlegend=False
)
st.plotly_chart(fig5)

for k in defaults:
    st.session_state[f'_bk_{k}'] = st.session_state[k]