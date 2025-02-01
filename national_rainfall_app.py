import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np

def create_adm1_plots(shapefile, coordinates_data, longitude_col, latitude_col):
    """Create individual plots for each ADM1 region."""
    
    # Get unique ADM1 values
    adm1_values = shapefile['FIRST_DNAM'].unique()
    
    # Create a list to store all figure references
    figures = []
    
    for adm1 in adm1_values:
        try:
            # Create figure for this ADM1
            fig, ax = plt.subplots(figsize=(12, 12))
            
            # Subset data for this ADM1
            shapefile_subset = shapefile[shapefile['FIRST_DNAM'] == adm1]
            coordinates_subset = coordinates_data[coordinates_data['FIRST_DNAM'] == adm1]
            
            # Plot base shapefile with black boundaries
            shapefile_subset.plot(ax=ax, color='white', edgecolor='black', linewidth=0.5)
            
            # Add district labels
            for idx, row in shapefile_subset.iterrows():
                ax.text(row.geometry.centroid.x, 
                       row.geometry.centroid.y,
                       row['FIRST_CHIE'],
                       fontsize=10,
                       ha='center',
                       va='center',
                       bbox=dict(facecolor='white',
                               alpha=0.7,
                               edgecolor='none',
                               pad=1))
            
            # Customize appearance
            ax.set_title(f"{adm1}", fontsize=12, fontweight='bold', pad=20)
            ax.axis('off')
            
            # Add facility count and coordinates range
            facility_count = len(coordinates_subset)
            stats_text = f"Total Facilities: {facility_count}\n"
            if facility_count > 0:
                stats_text += (
                    f"Lon: {coordinates_subset[longitude_col].min():.2f}° to "
                    f"{coordinates_subset[longitude_col].max():.2f}°\n"
                    f"Lat: {coordinates_subset[latitude_col].min():.2f}° to "
                    f"{coordinates_subset[latitude_col].max():.2f}°"
                )
                
            ax.text(0.02, 0.02, stats_text,
                   transform=ax.transAxes,
                   fontsize=8,
                   bbox=dict(facecolor='white',
                            alpha=0.8,
                            edgecolor='none'))
            
            plt.tight_layout()
            figures.append((fig, f"Map for {adm1}"))
            
        except Exception as e:
            st.error(f"Error creating plot for {adm1}: {str(e)}")
    
    return figures

# Set up Streamlit page
st.set_page_config(layout="wide", page_title="Health Facility Map Generator")
st.title("Interactive Health Facility Map Generator")

# File upload columns
col1, col2 = st.columns(2)

with col1:
    st.header("Upload Shapefiles")
    shp_file = st.file_uploader("Upload .shp file", type=["shp"])
    shx_file = st.file_uploader("Upload .shx file", type=["shx"])
    dbf_file = st.file_uploader("Upload .dbf file", type=["dbf"])

with col2:
    st.header("Upload Health Facility Data")
    facility_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

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
        
        # Select coordinates columns
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
        
        # Create individual ADM1 plots
        figures = create_adm1_plots(
            shapefile=shapefile,
            coordinates_data=coordinates_data,
            longitude_col=longitude_col,
            latitude_col=latitude_col
        )
        
        # Display all figures
        for fig, caption in figures:
            st.pyplot(fig)
            
            # Save option for each figure
            output_filename = f"health_facility_map_{caption.replace(' ', '_')}.png"
            plt.savefig(output_filename, dpi=300, bbox_inches='tight', pad_inches=0.1)
            with open(output_filename, "rb") as file:
                st.download_button(
                    label=f"Download {caption} (PNG)",
                    data=file,
                    file_name=output_filename,
                    mime="image/png"
                )
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your input files and try again.")

else:
    st.info("Please upload all required files to generate the maps.")
