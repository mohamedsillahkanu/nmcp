# -*- coding: utf-8 -*-
"""zara1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ruDQIhZWiO3_4_RIIA1bCJ6PkfAh0_Xz
"""

import streamlit as st
import geopandas as gpd
import rasterio
import rasterio.mask
import numpy as np
import os
import requests
import gzip
import shutil
import tempfile
from io import BytesIO
from matplotlib import pyplot as plt

# Function to load and process the shapefile
def load_shapefile(shp_file, shx_file, dbf_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save the uploaded files to a temporary directory
        for file, ext in zip([shp_file, shx_file, dbf_file], ['.shp', '.shx', '.dbf']):
            with open(os.path.join(tmpdir, f"file{ext}"), "wb") as f:
                f.write(file.getbuffer())

        # Load the shapefile using GeoPandas
        shapefile_path = os.path.join(tmpdir, "file.shp")
        gdf = gpd.read_file(shapefile_path)

    # Check if the CRS is set, if not, set it manually
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")  # Assuming WGS84; replace with correct CRS if different

    return gdf

# Function to download, unzip, and process CHIRPS data
def process_chirps_data(gdf, year, month):
    # Define the link for CHIRPS data
    link = f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs/chirps-v2.0.{year}.{month:02d}.tif.gz"

    # Download the .tif.gz file
    response = requests.get(link)
    with tempfile.TemporaryDirectory() as tmpdir:
        zipped_file_path = os.path.join(tmpdir, "chirps.tif.gz")
        unzipped_file_path = os.path.join(tmpdir, "chirps.tif")

        with open(zipped_file_path, "wb") as f:
            f.write(response.content)

        # Unzip the file
        with gzip.open(zipped_file_path, "rb") as f_in:
            with open(unzipped_file_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Open the unzipped .tif file with Rasterio
        with rasterio.open(unzipped_file_path) as src:
            # Reproject shapefile to match CHIRPS data CRS
            gdf = gdf.to_crs(src.crs)

            # Mask the CHIRPS data using the shapefile geometry
            out_image, out_transform = rasterio.mask.mask(src, gdf.geometry, crop=True)

            # Flatten the masked array and calculate mean excluding masked values
            mean_rains = []
            for geom in gdf.geometry:
                masked_data, _ = rasterio.mask.mask(src, [geom], crop=True)
                masked_data = masked_data.flatten()
                masked_data = masked_data[masked_data != src.nodata]  # Exclude nodata values
                mean_rains.append(masked_data.mean())

            gdf['mean_rain'] = mean_rains

    return gdf

# Streamlit app layout
st.title("CHIRPS Data Analysis and Map Generation")

# Upload shapefile components
uploaded_shp = st.file_uploader("Upload .shp file", type="shp")
uploaded_shx = st.file_uploader("Upload .shx file", type="shx")
uploaded_dbf = st.file_uploader("Upload .dbf file", type="dbf")

# Year and month selection
year = st.selectbox("Select Year", range(1981, 2025))
month = st.selectbox("Select Month", range(1, 13))

# Colormap selection
cmap = st.selectbox("Select Colormap", ['Blues', 'Greens', 'Reds', 'Purples', 'Oranges', 'YlGnBu', 'cividis', 'plasma', 'viridis'])

if uploaded_shp and uploaded_shx and uploaded_dbf and year and month:
    # Load and process the shapefile
    with st.spinner("Loading and processing shapefile..."):
        gdf = load_shapefile(uploaded_shp, uploaded_shx, uploaded_dbf)

    st.success("Shapefile loaded successfully!")

    # Process CHIRPS data
    with st.spinner("Processing CHIRPS data..."):
        gdf = process_chirps_data(gdf, year, month)

    st.success("CHIRPS data processed successfully!")

    # Display the mean rainfall data
    st.write(gdf[['geometry', 'mean_rain']])

    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Plotting the GeoDataFrame with shortened legend
    gdf.plot(column='mean_rain', ax=ax, legend=True, cmap=cmap, edgecolor="black", legend_kwds={'shrink': 0.5})

    # Remove axis boxes
    ax.set_axis_off()

    # Add a title to the plot
    plt.title(f"Mean Rainfall for {year}-{month:02d}", fontsize=16)

    # Display the map in Streamlit
    st.pyplot(fig)

    # Download button for the processed data
    output_csv = BytesIO()
    gdf.to_csv(output_csv)
    st.download_button(label="Download Mean Rainfall Data",
                       data=output_csv.getvalue(),
                       file_name=f"mean_rainfall_{year}_{month:02d}.csv",
                       mime="text/csv")

    # Download button for the image
    image_output = BytesIO()
    fig.savefig(image_output, format='png')
    st.download_button(label="Download Map Image",
                       data=image_output.getvalue(),
                       file_name=f"mean_rainfall_{year}_{month:02d}.png",
                       mime="image/png")
