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

# Customization options
st.header("Map Customization")
col3, col4, col5 = st.columns(3)

with col3:
    # Visual customization
    map_title = st.text_input("Map Title", "Health Facility Distribution by Chiefdom")
    point_size = st.slider("Point Size", 10, 200, 50)
    point_alpha = st.slider("Point Transparency", 0.1, 1.0, 0.7)

with col4:
    # Color selection
    background_colors = ["white", "lightgray", "beige", "lightblue"]
    point_colors = ["#47B5FF", "red", "green", "purple", "orange"]
    
    background_color = st.selectbox("Background Color", background_colors)
    point_color = st.selectbox("Point Color", point_colors)

with col5:
    # Additional options
    show_facility_count = st.checkbox("Show Facility Count", value=True)
    show_chiefdom_name = st.checkbox("Show Chiefdom Name", value=True)

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

        # Convert facility data to GeoDataFrame
        geometry = [Point(xy) for xy in zip(facility_data['w_long'], facility_data['w_lat'])]
        facilities_gdf = gpd.GeoDataFrame(
            facility_data, 
            geometry=geometry,
            crs="EPSG:4326"
        )

        # Get unique districts from shapefile
        districts = sorted(shapefile['FIRST_DNAM'].unique())
        selected_district = st.selectbox("Select District", districts)

        # Filter shapefile for selected district
        district_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district]
        
        # Get unique chiefdoms for the selected district
        chiefdoms = sorted(district_shapefile['FIRST_CHIE'].unique())
        
        # Set the grid size to 5 rows and 4 columns
        n_rows = 5
        n_cols = 4
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 25))  # Increased height to accommodate 5 rows
        fig.suptitle(map_title, fontsize=24, y=0.98)  # Increased y value for more space

        # Plot each chiefdom
        for idx, chiefdom in enumerate(chiefdoms[:20]):  # Limit to 20 chiefdoms (5x4 grid)
            if idx >= n_rows * n_cols:
                break
                
            # Create subplot
            ax = plt.subplot(n_rows, n_cols, idx + 1)
            
            # Filter shapefile for current chiefdom
            chiefdom_shapefile = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
            
            # Plot chiefdom boundary
            chiefdom_shapefile.plot(ax=ax, color=background_color, edgecolor='black', linewidth=0.5)
            
            # Spatial join to get facilities within the chiefdom
            chiefdom_facilities = gpd.sjoin(
                facilities_gdf,
                chiefdom_shapefile,
                how="inner",
                predicate="within"
            )
            
            # Plot facilities
            if len(chiefdom_facilities) > 0:
                chiefdom_facilities.plot(
                    ax=ax,
                    color=point_color,
                    markersize=point_size,
                    alpha=point_alpha
                )
            
            # Set title
            title = ""
            if show_chiefdom_name:
                title += f"{chiefdom}"
            if show_facility_count:
                title += f"\n({len(chiefdom_facilities)} facilities)"
            
            ax.set_title(title, fontsize=12, pad=10)
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

        # Adjust layout with more space at the top
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)  # Adjust this value to control space between title and plots
        
        # Display the map
        st.pyplot(fig)

        # Download options
        col6, col7 = st.columns(2)
        
        with col6:
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

        with col7:
            # Export facility data
            if len(chiefdom_facilities) > 0:
                csv = chiefdom_facilities.to_csv(index=False)
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
