import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np

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
        facility_data = pd.read_excel(facility_file)

        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(facility_data.head())

        # Get unique districts from shapefile
        districts = sorted(shapefile['FIRST_DNAM'].unique())
        selected_district = st.selectbox("Select District", districts)

        # Filter shapefile for selected district
        district_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district]
        
        # Get unique chiefdoms for the selected district
        chiefdoms = sorted(district_shapefile['FIRST_CHIE'].unique())
        
        # Calculate grid dimensions for 4x4 layout
        n_chiefdoms = len(chiefdoms)
        grid_size = min(4, max(2, int(np.ceil(np.sqrt(n_chiefdoms)))))
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 20))
        fig.suptitle(f'Health Facilities in {selected_district} District', fontsize=24, y=0.95)

        # Plot each chiefdom
        for idx, chiefdom in enumerate(chiefdoms[:16]):  # Limit to 16 chiefdoms (4x4 grid)
            if idx >= grid_size * grid_size:
                break
                
            # Create subplot
            ax = plt.subplot(grid_size, grid_size, idx + 1)
            
            # Filter shapefile for current chiefdom
            chiefdom_shapefile = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
            
            # Plot chiefdom boundary
            chiefdom_shapefile.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)
            
            # Filter facility data for current chiefdom
            chiefdom_facilities = facility_data[
                (facility_data['w_long'].notna()) & 
                (facility_data['w_lat'].notna())
            ]
            
            if len(chiefdom_facilities) > 0:
                # Create GeoDataFrame for facilities
                geometry = [Point(xy) for xy in zip(chiefdom_facilities['w_long'], 
                                                  chiefdom_facilities['w_lat'])]
                facilities_gdf = gpd.GeoDataFrame(
                    chiefdom_facilities, 
                    geometry=geometry,
                    crs="EPSG:4326"
                )
                
                # Plot facilities
                facilities_gdf.plot(
                    ax=ax,
                    color='red',
                    markersize=50,
                    alpha=0.7
                )
            
            # Set title and remove axes
            ax.set_title(f'{chiefdom}\n({len(chiefdom_facilities)} facilities)', 
                        fontsize=12, pad=10)
            ax.axis('off')
            
            # Calculate and set aspect ratio
            bounds = chiefdom_shapefile.total_bounds
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
            
            # Zoom to chiefdom bounds
            ax.set_xlim(bounds[0], bounds[2])
            ax.set_ylim(bounds[1], bounds[3])

        # Adjust layout
        plt.tight_layout()
        
        # Display the map
        st.pyplot(fig)

        # Download options
        col3, col4 = st.columns(2)
        
        with col3:
            # Save high-resolution PNG
            output_path_png = "health_facility_map.png"
            plt.savefig(output_path_png, dpi=300, bbox_inches='tight', pad_inches=0.1)
            with open(output_path_png, "rb") as file:
                st.download_button(
                    label="Download Map (PNG)",
                    data=file,
                    file_name=f"health_facility_map_{selected_district}.png",
                    mime="image/png"
                )

        with col4:
            # Export coordinates as CSV
            csv = facility_data.to_csv(index=False)
            st.download_button(
                label="Download Processed Data (CSV)",
                data=csv,
                file_name=f"health_facilities_{selected_district}.csv",
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
    Shapefile should contain:
    - FIRST_DNAM (District Name)
    - FIRST_CHIE (Chiefdom Name)
    
    Excel file should contain:
    - w_long (Longitude)
    - w_lat (Latitude)
    
    The coordinates should be in decimal degrees format.
    """)
