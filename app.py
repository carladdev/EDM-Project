import streamlit as st
import pandas as pd

# Función para cargar datos desde el archivo CSV
@st.cache(ttl=600)
def load_data(file_path):
    try:
        # Leer el archivo CSV
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Crear una lista de filas válidas
        valid_lines = []
        for line in lines:
            if line.count(';') == 9:  # Asegúrate de que la línea tenga 10 campos separados por ';'
                valid_lines.append(line)

        # Crear un DataFrame a partir de las líneas válidas
        data = pd.read_csv(pd.compat.StringIO('\n'.join(valid_lines)), sep=';', error_bad_lines=False)

        return data

    except Exception as e:
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
        # Función para obtener latitud y longitud
        def get_coordinates(x):
            try:
                coordinates = eval(x)
                return coordinates[1], coordinates[0]  # Latitud, Longitud
            except Exception as e:
                st.error(f"Error al procesar las coordenadas: {e}")
                return None, None

        data[['latitud', 'longitud']] = data['geo_point_2d'].apply(get_coordinates).apply(pd.Series)

        # Filtrar filas donde no se pudieron obtener las coordenadas
        data = data.dropna(subset=['latitud', 'longitud'])

        # Crear el mapa con Plotly
        import plotly.express as px
        fig = px.scatter_mapbox(data, lat='latitud', lon='longitud', hover_name='Direccion',
                                hover_data=['Bicis_disponibles', 'Espacios_totales', 'Espacios_libres'],
                                zoom=12, height=600)
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig)
    else:
        st.error("No se encontró la columna 'geo_point_2d' en el archivo CSV.")
else:
    st.warning('No se pudieron cargar los datos. Por favor revisa el archivo CSV.')