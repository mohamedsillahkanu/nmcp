import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from shapely.geometry import Point

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

        # Column selection
        st.header("Coordinate Column Selection")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            longitude_col = st.selectbox(
                "Select Longitude Column",
                facility_data.columns,
                index=facility_data.columns.get_loc("w_long") if "w_long" in facility_data.columns else 0
            )
        with col4:
            latitude_col = st.selectbox(
                "Select Latitude Column",
                facility_data.columns,
                index=facility_data.columns.get_loc("w_lat") if "w_lat" in facility_data.columns else 0
            )
        with col5:
            name_col = st.selectbox(
                "Select Facility Name Column",
                facility_data.columns,
                index=0
            )

        # Customization options
        st.header("Map Customization")
        col6, col7, col8 = st.columns(3)

        with col6:
            # Title customization
            map_title = st.text_input("Map Title", "Health Facility Distribution by Chiefdom")
            title_font_size = st.slider("Title Font Size", 12, 48, 24)
            title_spacing = st.slider("Title Top Spacing", 0, 200, 50, help="Adjust space above the title")
            point_size = st.slider("Point Size", 5, 20, 10)

        with col7:
            # Color selection
            point_colors = {
                "Red": "#FF4B4B",
                "Blue": "#47B5FF",
                "Green": "#2ECC71",
                "Purple": "#9B59B6",
                "Orange": "#E67E22",
                "Pink": "#FF69B4",
                "Yellow": "#F1C40F",
                "Teal": "#1ABC9C"
            }
            background_colors = {
                "White": "#FFFFFF",
                "Light Gray": "#F0F0F0",
                "Beige": "#F5F5DC",
                "Light Blue": "#E6F3FF",
                "Light Green": "#E8F5E9",
                "Light Yellow": "#FFFFF0",
                "Light Pink": "#FFE4E1"
            }
            
            point_color = st.selectbox(
                "Point Color",
                options=list(point_colors.keys()),
                index=0
            )
            point_color = point_colors[point_color]  # Convert name to hex
            
            background_color = st.selectbox(
                "Background Color",
                options=list(background_colors.keys()),
                index=0
            )
            background_color = background_colors[background_color]  # Convert name to hex

        with col8:
            # Additional options
            show_facility_count = st.checkbox("Show Facility Count", value=True)
            show_chiefdom_name = st.checkbox("Show Chiefdom Name", value=True)

        # Convert facility data to GeoDataFrame
        geometry = [Point(xy) for xy in zip(facility_data[longitude_col], facility_data[latitude_col])]
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
        
        # Calculate grid dimensions for 4x4 layout
        n_chiefdoms = len(chiefdoms)
        grid_size = min(4, max(2, int(np.ceil(np.sqrt(n_chiefdoms)))))
        
        # Create subplot figure
        subplot_titles = [f"{chiefdom}" for chiefdom in chiefdoms[:grid_size*grid_size]]
        fig = make_subplots(
            rows=grid_size,
            cols=grid_size,
            subplot_titles=subplot_titles,
            specs=[[{"type": "scattermapbox"} for _ in range(grid_size)] for _ in range(grid_size)]
        )

        # Create individual maps for each chiefdom
        individual_maps = {}
        
        # Plot each chiefdom
        for idx, chiefdom in enumerate(chiefdoms[:grid_size*grid_size]):
            row = idx // grid_size + 1
            col = idx % grid_size + 1
            
            # Filter shapefile for current chiefdom
            chiefdom_shapefile = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
            
            # Get chiefdom boundary coordinates
            bounds = chiefdom_shapefile.total_bounds
            
            # Spatial join to get facilities within the chiefdom
            chiefdom_facilities = gpd.sjoin(
                facilities_gdf,
                chiefdom_shapefile,
                how="inner",
                predicate="within"
            )
            
            if len(chiefdom_facilities) > 0:
                # Add scatter mapbox trace for facilities
                fig.add_trace(
                    go.Scattermapbox(
                        lat=chiefdom_facilities[latitude_col],
                        lon=chiefdom_facilities[longitude_col],
                        mode='markers',
                        marker=dict(
                            size=point_size,
                            color=point_color,
                        ),
                        text=chiefdom_facilities[name_col],
                        hovertemplate=(
                            f"Facility: %{{text}}<br>"
                            f"Latitude: %{{lat}}<br>"
                            f"Longitude: %{{lon}}<br>"
                            "<extra></extra>"
                        ),
                        name=chiefdom
                    ),
                    row=row,
                    col=col
                )

            # Create individual map for this chiefdom
            individual_fig = go.Figure()
            
            if len(chiefdom_facilities) > 0:
                individual_fig.add_trace(
                    go.Scattermapbox(
                        lat=chiefdom_facilities[latitude_col],
                        lon=chiefdom_facilities[longitude_col],
                        mode='markers',
                        marker=dict(
                            size=point_size * 1.5,  # Slightly larger points for individual view
                            color=point_color,
                        ),
                        text=chiefdom_facilities[name_col],
                        hovertemplate=(
                            f"Facility: %{{text}}<br>"
                            f"Latitude: %{{lat}}<br>"
                            f"Longitude: %{{lon}}<br>"
                            "<extra></extra>"
                        ),
                        name=chiefdom
                    )
                )
            
            # Update individual map layout
            individual_fig.update_layout(
                title={
                    'text': f"Health Facilities in {chiefdom}, {selected_district} District",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': title_font_size}
                },
                height=800,
                width=1200,
                showlegend=False,
                mapbox=dict(
                    style="carto-positron",
                    center=dict(
                        lat=np.mean([bounds[1], bounds[3]]),
                        lon=np.mean([bounds[0], bounds[2]])
                    ),
                    zoom=9
                ),
                margin=dict(t=title_spacing + title_font_size + 10, r=10, l=10, b=10)
            )
            
            # Save individual map
            individual_html = f"health_facility_map_{selected_district}_{chiefdom}.html"
            individual_fig.write_html(individual_html)
            individual_maps[chiefdom] = individual_html

        # Update overall layout with single margin definition
        fig.update_layout(
            height=1000,
            title={
                'text': f"{map_title}<br>{selected_district} District",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': title_font_size}
            },
            showlegend=False,
            margin=dict(t=title_spacing + title_font_size + 10, r=10, l=10, b=10)
        )

        # Add chiefdom selection for individual map viewing
        st.header("View Individual Chiefdom Maps")
        selected_chiefdom_view = st.selectbox(
            "Select a chiefdom to view in detail",
            ["None"] + chiefdoms
        )
        
        if selected_chiefdom_view != "None":
            # Filter data for selected chiefdom
            chiefdom_shapefile = district_shapefile[district_shapefile['FIRST_CHIE'] == selected_chiefdom_view]
            bounds = chiefdom_shapefile.total_bounds
            
            # Create detailed map for selected chiefdom
            detailed_fig = go.Figure()
            
            # Get facilities for this chiefdom
            chiefdom_facilities = gpd.sjoin(
                facilities_gdf,
                chiefdom_shapefile,
                how="inner",
                predicate="within"
            )
            
            if len(chiefdom_facilities) > 0:
                st.write(f"Number of facilities found in {selected_chiefdom_view}: {len(chiefdom_facilities)}")
                st.write("Coordinates being plotted:")
                st.write(chiefdom_facilities[[longitude_col, latitude_col, name_col]].head())
                
                detailed_fig.add_trace(
                    go.Scattermapbox(
                        lat=chiefdom_facilities[latitude_col],
                        lon=chiefdom_facilities[longitude_col],
                        mode='markers+text',  # Add text mode
                        marker=dict(
                            size=point_size * 1.5,
                            color=point_color,
                        ),
                        text=chiefdom_facilities[name_col],
                        textposition="top center",  # Position the text above the marker
                        hovertemplate=(
                            f"Facility: %{{text}}<br>"
                            f"Latitude: %{{lat}}<br>"
                            f"Longitude: %{{lon}}<br>"
                            "<extra></extra>"
                        ),
                        name=selected_chiefdom_view
                    )
                )
            else:
                st.warning(f"No facilities found in {selected_chiefdom_view} chiefdom")
            
            # Update detailed map layout
            detailed_fig.update_layout(
                title={
                    'text': f"Health Facilities in {selected_chiefdom_view}, {selected_district} District",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': title_font_size}
                },
                height=800,
                showlegend=False,
                mapbox=dict(
                    style="carto-positron",
                    center=dict(
                        lat=np.mean([bounds[1], bounds[3]]),
                        lon=np.mean([bounds[0], bounds[2]])
                    ),
                    zoom=10
                ),
                margin=dict(t=title_spacing + title_font_size + 10, r=10, l=10, b=10)
            )
            
            # Display detailed map
            st.plotly_chart(detailed_fig, use_container_width=True)

        # Download options
        col9, col10 = st.columns(2)
        
        with col9:
            # Save as HTML
            html_file = f"health_facility_map_{selected_district}.html"
            fig.write_html(html_file)
            with open(html_file, "rb") as file:
                st.download_button(
                    label="Download Interactive Map (HTML)",
                    data=file,
                    file_name=html_file,
                    mime="text/html"
                )

        with col10:
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
    - Longitude column
    - Latitude column
    - Facility name column
    
    The coordinates should be in decimal degrees format.
    """)
