import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def create_adm1_subplots(shapefile, coordinates_data, longitude_col, latitude_col, 
                        point_color, point_size, point_alpha, background_color):
    """Create subplots for each ADM1 region."""
    # Get unique ADM1 values
    adm1_values = shapefile['ADM1'].unique()
    
    # Calculate subplot grid size
    n = len(adm1_values)
    nrows = int(np.ceil(np.sqrt(n)))
    ncols = int(np.ceil(n / nrows))
    
    # Create figure and subplots
    fig, axes = plt.subplots(nrows, ncols, figsize=(20, 20))
    axes_flat = axes.flatten()
    
    # Convert coordinates to GeoDataFrame
    geometry = [Point(xy) for xy in zip(coordinates_data[longitude_col], coordinates_data[latitude_col])]
    coordinates_gdf = gpd.GeoDataFrame(coordinates_data, geometry=geometry, crs="EPSG:4326")
    
    # Create subplot for each ADM1
    for idx, adm1 in enumerate(adm1_values):
        ax = axes_flat[idx]
        
        # Subset data for this ADM1
        shapefile_subset = shapefile[shapefile['ADM1'] == adm1]
        coordinates_subset = coordinates_gdf[coordinates_gdf['ADM1'] == adm1]
        
        # Plot shapefile subset
        shapefile_subset.plot(ax=ax, color=background_color, edgecolor='black', linewidth=0.5)
        
        # Plot points
        if len(coordinates_subset) > 0:
            coordinates_subset.plot(ax=ax, color=point_color, markersize=point_size, alpha=point_alpha)
        
        # Set title and remove axes
        ax.set_title(f"{adm1}", fontsize=12, pad=10)
        ax.axis('off')
        
        # Add facility count and coordinates range
        facility_count = len(coordinates_subset)
        stats_text = (f"Facilities: {facility_count}\n")
        if facility_count > 0:
            stats_text += (f"Lon: {coordinates_subset.geometry.x.min():.2f}° to {coordinates_subset.geometry.x.max():.2f}°\n"
                         f"Lat: {coordinates_subset.geometry.y.min():.2f}° to {coordinates_subset.geometry.y.max():.2f}°")
        ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, fontsize=8,
                bbox=dict(facecolor='white', alpha=0.8))
    
    # Remove empty subplots
    for idx in range(len(adm1_values), len(axes_flat)):
        fig.delaxes(axes_flat[idx])
    
    plt.tight_layout()
    return fig

def create_single_map(shapefile, coordinates_data, map_title, longitude_col, latitude_col,
                     point_color, point_size, point_alpha, background_color):
    """Create a single map with all facilities."""
    # Create figure
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Plot shapefile
    shapefile.plot(ax=ax, color=background_color, edgecolor='black', linewidth=0.5)
    
    # Convert coordinates to GeoDataFrame
    geometry = [Point(xy) for xy in zip(coordinates_data[longitude_col], coordinates_data[latitude_col])]
    coordinates_gdf = gpd.GeoDataFrame(coordinates_data, geometry=geometry, crs="EPSG:4326")
    
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
    
    # Plot points
    coordinates_gdf.plot(ax=ax, color=point_color, markersize=point_size, alpha=point_alpha)
    
    # Customize appearance
    plt.title(map_title, fontsize=20, pad=20)
    plt.axis('off')
    
    # Add statistics
    stats_text = (
        f"Total Facilities: {len(coordinates_data)}\n"
        f"Coordinates Range:\n"
        f"Longitude: {coordinates_data[longitude_col].min():.2f}° to {coordinates_data[longitude_col].max():.2f}°\n"
        f"Latitude: {coordinates_data[latitude_col].min():.2f}° to {coordinates_data[latitude_col].max():.2f}°"
    )
    plt.figtext(0.02, 0.02, stats_text, fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
    
    return fig

# Set up Streamlit page
st.set_page_config(layout="wide", page_title="Health Facility Map Generator")
st.title("Interactive Health Facility Map Generator")
st.write("Upload your shapefiles and health facility data to generate a customized map.")

# File upload columns
col1, col2 = st.columns(2)

with col1:
    st.header("Upload Shapefiles")
    shp_file = st.file_uploader("Upload .shp file", type=["shp"], key="shp")
    shx_file = st.file_uploader("Upload .shx file", type=["shx"], key="shx")
    dbf_file = st.file_uploader("Upload .dbf file", type=["dbf"], key="dbf")

with col2:
    st.header("Upload Health Facility Data")
    facility_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"], key="facility")

# Process files if all are uploaded
if all([shp_file, shx_file, dbf_file, facility_file]):
    try:
        # Read files
        with open("temp.shp", "wb") as f:
            f.write(shp_file.read())
        with open("temp.shx", "wb") as f:
            f.write(shx_file.read())
        with open("temp.dbf", "wb") as f:
            f.write(dbf_file.read())
        
        shapefile = gpd.read_file("temp.shp")
        coordinates_data = pd.read_excel(facility_file)
        
        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(coordinates_data.head())
        
        # Map customization options
        st.header("Map Customization")
        
        # Select display type
        display_type = st.radio("Select Display Type", ["Single Map", "ADM1 Subplots"])
        
        # Customization columns
        col3, col4, col5 = st.columns(3)
        
        with col3:
            longitude_col = st.selectbox(
                "Select Longitude Column",
                coordinates_data.columns,
                index=coordinates_data.columns.get_loc("longitude") if "longitude" in coordinates_data.columns else 0
            )
            latitude_col = st.selectbox(
                "Select Latitude Column",
                coordinates_data.columns,
                index=coordinates_data.columns.get_loc("latitude") if "latitude" in coordinates_data.columns else 0
            )

        with col4:
            map_title = st.text_input("Map Title", "Health Facility Distribution")
            point_size = st.slider("Point Size", 10, 200, 50)
            point_alpha = st.slider("Point Transparency", 0.1, 1.0, 0.7)

        with col5:
            background_colors = ["white", "lightgray", "beige", "lightblue"]
            point_colors = ["#47B5FF", "red", "green", "purple", "orange"]
            background_color = st.selectbox("Background Color", background_colors)
            point_color = st.selectbox("Point Color", point_colors)
        
        # Data processing
        coordinates_data = coordinates_data.dropna(subset=[longitude_col, latitude_col])
        coordinates_data = coordinates_data[
            (coordinates_data[longitude_col].between(-180, 180)) &
            (coordinates_data[latitude_col].between(-90, 90))
        ]
        
        if len(coordinates_data) == 0:
            st.error("No valid coordinates found in the data after filtering.")
            st.stop()
            
        # Ensure consistent CRS
        if shapefile.crs is None:
            shapefile = shapefile.set_crs(epsg=4326)
        else:
            shapefile = shapefile.to_crs(epsg=4326)
        
        # Create map based on selected display type
        if display_type == "Single Map":
            fig = create_single_map(shapefile, coordinates_data, map_title, longitude_col, 
                                  latitude_col, point_color, point_size, point_alpha, 
                                  background_color)
            output_filename = "health_facility_map.png"
        else:
            fig = create_adm1_subplots(shapefile, coordinates_data, longitude_col, 
                                     latitude_col, point_color, point_size, point_alpha, 
                                     background_color)
            output_filename = "health_facility_map_adm1.png"
        
        # Display map
        st.pyplot(fig)
        
        # Download options
        col6, col7 = st.columns(2)
        
        with col6:
            plt.savefig(output_filename, dpi=300, bbox_inches='tight', pad_inches=0.1)
            with open(output_filename, "rb") as file:
                st.download_button(
                    label=f"Download Map (PNG)",
                    data=file,
                    file_name=output_filename,
                    mime="image/png"
                )
        
        with col7:
            csv = coordinates_data.to_csv(index=False)
            st.download_button(
                label="Download Processed Data (CSV)",
                data=csv,
                file_name="processed_coordinates.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your input files and try again.")

else:
    st.info("Please upload all required files to generate the map.")
    
    st.subheader("Expected Data Format")
    st.write("""
    Your Excel file should contain at minimum:
    - A column for longitude (decimal degrees)
    - A column for latitude (decimal degrees)
    - ADM1 column for administrative level 1 regions
    """)
