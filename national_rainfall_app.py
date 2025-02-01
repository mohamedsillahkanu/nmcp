import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(layout="wide", page_title="Health Facility Map Generator")

st.title("Interactive Health Facility Map Generator")
st.write("Upload your shapefiles and health facility data to generate a customized map.")

# Create two columns for file uploads
col1, col2 = st.columns(2)

with col1:
    st.header("Upload Shapefiles")
    shp_file = st.file_uploader("Upload .shp file", type=["shp"], key="shp")
    shx_file = st.file_uploader("Upload .shx file", type=["shx"], key="shx")
    dbf_file = st.file_uploader("Upload .dbf file", type=["dbf"], key="dbf")

with col2:
    st.header("Upload Health Facility Data")
    facility_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"], key="facility")

# Check if all required files are uploaded
if all([shp_file, shx_file, dbf_file, facility_file]):
    try:
        # Read shapefiles
        with open("temp.shp", "wb") as f:
            f.write(shp_file.read())
        with open("temp.shx", "wb") as f:
            f.write(shx_file.read())
        with open("temp.dbf", "wb") as f:
            f.write(dbf_file.read())
        shapefile = gpd.read_file("temp.shp")

        # Read facility data
        coordinates_data = pd.read_excel(facility_file)

        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(coordinates_data.head())

        # District and Chiefdom Selection
        st.header("Area Selection")
        col3, col4 = st.columns(2)
        
        with col3:
            # Select District
            districts = sorted(coordinates_data['FIRST_DNAM'].unique())
            selected_district = st.selectbox("Select District", districts)
            
        # Filter data for selected district
        district_data = coordinates_data[coordinates_data['FIRST_DNAM'] == selected_district]
        
        with col4:
            # Select Chiefdom
            chiefdoms = sorted(district_data['FIRST_CHIE'].unique())
            selected_chiefdom = st.selectbox("Select Chiefdom", chiefdoms)

        # Filter data for selected chiefdom
        filtered_data = district_data[district_data['FIRST_CHIE'] == selected_chiefdom]

        # Map customization options
        st.header("Map Customization")
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            # Coordinate column selection
            longitude_col = st.selectbox(
                "Select Longitude Column",
                filtered_data.columns,
                index=filtered_data.columns.get_loc("w_long") if "w_long" in filtered_data.columns else 0
            )
            latitude_col = st.selectbox(
                "Select Latitude Column",
                filtered_data.columns,
                index=filtered_data.columns.get_loc("w_lat") if "w_lat" in filtered_data.columns else 0
            )

        with col6:
            # Visual customization
            map_title = st.text_input("Map Title", f"Health Facilities in {selected_chiefdom}, {selected_district}")
            point_size = st.slider("Point Size", 10, 200, 50)
            point_alpha = st.slider("Point Transparency", 0.1, 1.0, 0.7)
            show_labels = st.checkbox("Show Facility Names", value=True)

        with col7:
            # Color selection
            background_colors = ["white", "lightgray", "beige", "lightblue"]
            point_colors = ["#47B5FF", "red", "green", "purple", "orange"]
            
            background_color = st.selectbox("Background Color", background_colors)
            point_color = st.selectbox("Point Color", point_colors)

        # Data processing
        # Remove missing coordinates
        filtered_data = filtered_data.dropna(subset=[longitude_col, latitude_col])
        
        # Filter invalid coordinates
        filtered_data = filtered_data[
            (filtered_data[longitude_col].between(-180, 180)) &
            (filtered_data[latitude_col].between(-90, 90))
        ]

        if len(filtered_data) == 0:
            st.error("No valid coordinates found in the data after filtering.")
            st.stop()

        # Convert to GeoDataFrame
        geometry = [Point(xy) for xy in zip(filtered_data[longitude_col], filtered_data[latitude_col])]
        coordinates_gdf = gpd.GeoDataFrame(filtered_data, geometry=geometry, crs="EPSG:4326")

        # Ensure consistent CRS
        if shapefile.crs is None:
            shapefile = shapefile.set_crs(epsg=4326)
        else:
            shapefile = shapefile.to_crs(epsg=4326)

        # Create the map with fixed aspect
        fig, ax = plt.subplots(figsize=(15, 10))

        # Plot shapefile with custom style
        shapefile.plot(ax=ax, color=background_color, edgecolor='black', linewidth=0.5)

        # Calculate and set appropriate aspect ratio
        bounds = shapefile.total_bounds
        mid_y = np.mean([bounds[1], bounds[3]])
        aspect = 1.0
        
        if -90 < mid_y < 90:
            try:
                aspect = 1 / np.cos(np.radians(mid_y))
                if not np.isfinite(aspect) or aspect <= 0:
                    aspect = 1.0
            except:
                aspect = 1.0
        
        ax.set_aspect(aspect)

        # Plot points with custom style
        coordinates_gdf.plot(
            ax=ax,
            color=point_color,
            markersize=point_size,
            alpha=point_alpha
        )

        # Add facility name labels if enabled
        if show_labels:
            for idx, row in coordinates_gdf.iterrows():
                ax.annotate(
                    row['FIRST_CHIE'],
                    xy=(row.geometry.x, row.geometry.y),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=8,
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                )

        # Customize map appearance
        plt.title(map_title, fontsize=20, pad=20)
        plt.axis('off')

        # Add statistics
        stats_text = (
            f"District: {selected_district}\n"
            f"Chiefdom: {selected_chiefdom}\n"
            f"Total Facilities: {len(filtered_data)}\n"
            f"Coordinates Range:\n"
            f"Longitude: {filtered_data[longitude_col].min():.2f}° to {filtered_data[longitude_col].max():.2f}°\n"
            f"Latitude: {filtered_data[latitude_col].min():.2f}° to {filtered_data[latitude_col].max():.2f}°"
        )
        plt.figtext(0.02, 0.02, stats_text, fontsize=8, bbox=dict(facecolor='white', alpha=0.8))

        # Display the map
        st.pyplot(fig)

        # Download options
        col8, col9 = st.columns(2)
        
        with col8:
            # Save high-resolution PNG
            output_path_png = "health_facility_map.png"
            plt.savefig(output_path_png, dpi=300, bbox_inches='tight', pad_inches=0.1)
            with open(output_path_png, "rb") as file:
                st.download_button(
                    label="Download Map (PNG)",
                    data=file,
                    file_name=f"health_facility_map_{selected_district}_{selected_chiefdom}.png",
                    mime="image/png"
                )

        with col9:
            # Export coordinates as CSV
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download Processed Data (CSV)",
                data=csv,
                file_name=f"health_facilities_{selected_district}_{selected_chiefdom}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your input files and try again.")

else:
    st.info("Please upload all required files to generate the map.")
    
    # Show example data format
    st.subheader("Expected Data Format")
    st.write("""
    Your Excel file should contain the following columns:
    - FIRST_DNAM (District Name)
    - FIRST_CHIE (Chiefdom Name)
    - Longitude column (e.g., 'w_long')
    - Latitude column (e.g., 'w_lat')
    
    The coordinates should be in decimal degrees format.
    """)
