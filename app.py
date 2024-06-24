import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Define the interface title
st.title("Valenbisi App")

# Sidebar options
view = st.sidebar.selectbox("Choose an option:", ("Introduction", "Map", "Table", "Graph"))

# Introduction page
if view == "Introduction":
    st.subheader("Introduction")
    # Add the image
    st.image("valenbisi.jpg")  # Reemplaza "valenbisi_image.jpg" con el nombre o la URL de tu imagen
    st.markdown("""
    **Valencia is a bicycle-friendly city with a well-established bike-sharing system called Valenbisi.**  
    With over 276 stations and 2,500 bicycles, Valenbisi offers a convenient and eco-friendly mode of transportation for locals and tourists alike.  
    To enhance the user experience and promote sustainable transportation, we propose a comprehensive mobile application that provides real-time information on Valenbisi bike availability and docking station status.
    In this application, you will find a map, an interactive table, and a bar chart.
    """)

# Load data from CSV file
file_path = "valenbisi.csv"
data = pd.read_csv(file_path, sep=";")

# Process coordinates
data[['lat', 'long']] = data['geo_point_2d'].str.split(', ', expand=True)
data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
data['long'] = pd.to_numeric(data['long'], errors='coerce')

if view in ["Map", "Table", "Graph"]:
    # Filter settings in sidebar
    bicis_range = st.sidebar.slider("Available Bikes:", min_value=0, max_value=int(data['Bicis_disponibles'].max()),
                                    value=(0, int(data['Bicis_disponibles'].max())))
    espacios_range = st.sidebar.slider("Free Spaces:", min_value=0, max_value=int(data['Espacios_libres'].max()),
                                       value=(0, int(data['Espacios_libres'].max())))
    activo = st.sidebar.checkbox("Show only active stations", value=True)

    # Filter data based on user input
    filtered_data = data[
        (pd.to_numeric(data['Bicis_disponibles'], errors='coerce').fillna(0).astype(int) >= bicis_range[0]) &
        (pd.to_numeric(data['Bicis_disponibles'], errors='coerce').fillna(0).astype(int) <= bicis_range[1]) &
        (pd.to_numeric(data['Espacios_libres'], errors='coerce').fillna(0).astype(int) >= espacios_range[0]) &
        (pd.to_numeric(data['Espacios_libres'], errors='coerce').fillna(0).astype(int) <= espacios_range[1])
    ]

    if activo:
        filtered_data = filtered_data[filtered_data['Activo'] == 'T']

    # Clean NaNs in coordinates
    filtered_data = filtered_data.dropna(subset=['lat', 'long'])

    # Render the map
    if view == "Map":
        st.subheader("Map")
        st.markdown("""
            **The map view provides an interactive visualization of bike stations in Valencia.**  
             It displays markers for each station, color-coded based on the availability
            of free spaces. 
            Users can click on markers to view detailed information about the station,
            including the number of available bikes and free spaces.  
            """)

        if not filtered_data.empty:
            # Create map centered at the average of filtered coordinates
            m = folium.Map(location=[filtered_data['lat'].mean(), filtered_data['long'].mean()], zoom_start=13)

            # Add marker cluster
            marker_cluster = MarkerCluster().add_to(m)

            # Iterate over filtered data to add markers to the map
            for idx, row in filtered_data.iterrows():
                # Configure marker with specific details of each station
                folium.CircleMarker(location=[row['lat'], row['long']],
                                    radius=5,
                                    color='green' if int(row['Bicis_disponibles']) > 0 else 'red',
                                    popup=f"Dirección: {row['Direccion']}<br>Bicis disponibles: {row['Bicis_disponibles']}<br>Espacios totales: {row['Espacios_totales']}<br>Espacios libres: {row['Espacios_libres']}"
                                    ).add_to(marker_cluster)

            # Show the map in Streamlit
            folium_static(m)
        else:
            st.warning("No data available to display on the map.")

    # Render the data table
    elif view == "Table":
        st.subheader("Table")
        st.markdown("""
                    **The table view presents the bike station data in a sortable and searchable tabular format**  
                    This view is particularly useful for users who prefer to see all the data immediately and need to sort or search for specific information.  
                    """)
        st.dataframe(filtered_data)

    # Render the graph of the top 10 stations with the most total space
    elif view == "Graph":
        st.subheader("Top 10 Stations with Most Total Space")
        st.markdown("""The graph is a bar chart representing the 10 Valenbisi stations with the highest total spaces for bicycles.""")
        # Get the top 10 stations with the most total space
        top_10 = filtered_data.nlargest(10, 'Espacios_totales')

        # Create the graph using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(top_10['Direccion'], top_10['Espacios_totales'], color='lightblue')
        ax.set_xticklabels(top_10['Direccion'], rotation=90)
        ax.set_xlabel('Stations')
        ax.set_ylabel('Total Spaces')
        ax.set_title('Top 10 Stations with Most Total Space')

        # Show the graph in Streamlit
        st.pyplot(fig)
