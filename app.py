import streamlit as st
import pandas as pd

# Función para cargar datos desde el archivo CSV
@st.cache(ttl=600)
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except pd.errors.ParserError as e:
        st.error(f"Error al leer el archivo CSV: {e}")
        return pd.DataFrame()

# Ruta del archivo CSV
file_path = 'valenbisi.csv'

# Cargar los datos
data = load_data(file_path)

# Verificar si se cargaron datos correctamente
if not data.empty:
    st.success("Datos cargados correctamente.")
else:
    st.warning('No se pudieron cargar los datos. Por favor revisa el archivo CSV.')




# VISUALIZACIÓN DE DATOS
import streamlit as st
import pandas as pd
import plotly.express as px

# Función para cargar datos desde el archivo CSV
@st.cache(ttl=600)
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except pd.errors.ParserError as e:
        st.error(f"Error al leer el archivo CSV: {e}")
        return pd.DataFrame()

# Ruta del archivo CSV
file_path = 'valenbisi.csv'

# Cargar los datos
data = load_data(file_path)

# Verificar si se cargaron datos correctamente
if not data.empty:
    st.success("Datos cargados correctamente.")

    # Preparar los datos para el mapa
    if 'geo_point_2d' in data.columns:
        data['latitud'] = data['geo_point_2d'].apply(lambda x: float(x.split(',')[0]))
        data['longitud'] = data['geo_point_2d'].apply(lambda x: float(x.split(',')[1]))

        # Crear el mapa con Plotly
        fig = px.scatter_mapbox(data, lat='latitud', lon='longitud', hover_name='Direccion',
                                hover_data=['Bicis_disponibles', 'Espacios_totales', 'Espacios_libres'],
                                zoom=12, height=600)
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig)
    else:
        st.error("No se encontró la columna 'geo_point_2d' en el archivo CSV.")
else:
    st.warning('No se pudieron cargar los datos. Por favor revisa el archivo CSV.')
