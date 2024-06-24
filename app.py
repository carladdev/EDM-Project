import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import seaborn as sns

# Leer datos desde el archivo CSV
file_path = "valenbisi.csv"
data = pd.read_csv(file_path, sep=";")

# Procesar las coordenadas
data[['lat', 'long']] = data['geo_point_2d'].str.split(', ', expand=True)
data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
data['long'] = pd.to_numeric(data['long'], errors='coerce')

# Imprimir datos originales para verificar
#st.write("Datos originales:")
#st.write(data.head())

# Definir la interfaz de usuario
st.title("Disponibilidad de Bicicletas en Estaciones Valenbisi")

view = st.sidebar.selectbox("Seleccione una opción:", ("Mapa", "Tabla"))

bicis_range = st.sidebar.slider("Bicis disponibles:", min_value=0, max_value=int(data['Bicis_disponibles'].max()),
                                value=(0, int(data['Bicis_disponibles'].max())))
espacios_range = st.sidebar.slider("Espacios libres:", min_value=0, max_value=int(data['Espacios_libres'].max()),
                                   value=(0, int(data['Espacios_libres'].max())))
activo = st.sidebar.checkbox("Mostrar solo estaciones activas", value=True)

# Filtrar datos en función de la entrada del usuario
filtered_data = data[
    (pd.to_numeric(data['Bicis_disponibles'], errors='coerce').fillna(0).astype(int) >= bicis_range[0]) &
    (pd.to_numeric(data['Bicis_disponibles'], errors='coerce').fillna(0).astype(int) <= bicis_range[1]) &
    (pd.to_numeric(data['Espacios_libres'], errors='coerce').fillna(0).astype(int) >= espacios_range[0]) &
    (pd.to_numeric(data['Espacios_libres'], errors='coerce').fillna(0).astype(int) <= espacios_range[1])]

if activo:
    filtered_data = filtered_data[filtered_data['Activo'] == 'T']

# Limpiar NaNs en coordenadas
filtered_data = filtered_data.dropna(subset=['lat', 'long'])

# Depuración: Imprimir datos filtrados para verificar
st.write("Datos filtrados:")
st.write(filtered_data.head())

# Renderizar el mapa
if view == "Mapa":
    st.subheader("Mapa")

    if not filtered_data.empty:
        # Crear el mapa centrado en el promedio de las coordenadas filtradas
        m = folium.Map(location=[filtered_data['lat'].mean(), filtered_data['long'].mean()], zoom_start=13)

        # Agregar cluster de marcadores
        marker_cluster = MarkerCluster().add_to(m)

        # Iterar sobre los datos filtrados para agregar marcadores al mapa
        for idx, row in filtered_data.iterrows():
            # Configurar marcador con detalles específicos de cada estación
            folium.CircleMarker(location=[row['lat'], row['long']],
                                radius=5,
                                color='green' if int(row['Bicis_disponibles']) > 0 else 'red',
                                popup=f"Dirección: {row['Direccion']}<br>Bicis disponibles: {row['Bicis_disponibles']}<br>Espacios totales: {row['Espacios_totales']}<br>Espacios libres: {row['Espacios_libres']}"
                                ).add_to(marker_cluster)

        # Mostrar el mapa en Streamlit
        folium_static(m)
    else:
        st.warning("No hay datos disponibles para mostrar en el mapa.")

# Renderizar la tabla de datos
elif view == "Tabla":
    st.subheader("Tabla")
    st.dataframe(filtered_data)