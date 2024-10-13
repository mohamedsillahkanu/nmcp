import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, to_hex

# Streamlit app title and image
st.title("Map Generator")
st.image("icf_sl (1).jpg", caption="MAP GENERATOR", use_column_width=True)

# File uploader for Excel files
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# Check if the file has been uploaded
if uploaded_file is not None:
    # Load the uploaded Excel file
    df = pd.read_excel(uploaded_file)

    # Load shapefile data
    gdf = gpd.read_file("https://raw.githubusercontent.com/mohamedsillahkanu/si/2b7f982174b609f9647933147dec2a59a33e736a/Chiefdom%202021.shp")

    # Automatically select the columns "FIRST_DNAM" and "FIRST_CHIE"
    shapefile_columns = ["FIRST_DNAM", "FIRST_CHIE"]

    # Filter out "FIRST_DNAM", "FIRST_CHIE", and "adm3" from df columns for map_column selection
    df_columns_filtered = [col for col in df.columns if col not in ["FIRST_DNAM", "FIRST_CHIE", "adm3"]]

    # User input for the map column and settings
    map_column = st.selectbox("Select Map Column:", df_columns_filtered)
    map_title = st.text_input("Map Title:")
    legend_title = st.text_input("Legend Title:")
    image_name = st.text_input("Image Name:", value="map_image")
    font_size = st.slider("Font Size (for Map Title):", min_value=8, max_value=24, value=15)
    color_palette_name = st.selectbox("Color Palette:", options=list(plt.colormaps()), index=list(plt.colormaps()).index('Set3'))

    line_color = st.selectbox("Select Default Line Color:", options=["White", "Black", "Red"], index=1)
    line_width = st.slider("Select Default Line Width:", min_value=0.5, max_value=5.0, value=2.5)

    missing_value_color = st.selectbox("Select Color for Missing Values:", options=["White", "Gray", "Red"], index=1)
    missing_value_label = st.text_input("Label for Missing Values:", value="No Data")

    # Initialize category_counts
    category_counts = {}

    variable_type = st.radio("Select the variable type:", options=["Categorical", "Numeric"])

    if variable_type == "Categorical":
        unique_values = sorted(df[map_column].dropna().unique().tolist())
        selected_categories = st.multiselect(f"Select Categories for the Legend of {map_column}:", unique_values, default=unique_values)
        category_counts = df[map_column].value_counts().to_dict()

        # Reorder the categories to match the selected categories order
        df[map_column] = pd.Categorical(df[map_column], categories=selected_categories, ordered=True)

        # Ensure the counts for each category remain consistent
        for category in selected_categories:
            if category not in category_counts:
                category_counts[category] = 0

    elif variable_type == "Numeric":
        bin_labels_input = st.text_input("Enter labels for bins (comma-separated, e.g., '10-20.5, 20.6-30.1, >30.2'): ")
        if bin_labels_input:
            bin_labels = [label.strip() for label in bin_labels_input.split(',')]
            bins = []
            for label in bin_labels:
                if '>' in label:
                    lower = float(label.replace('>', '').strip())
                    bins.append(lower)
                elif '-' in label:
                    lower, upper = map(float, label.split('-'))
                    bins.append(lower)
                    bins.append(upper)
                else:
                    st.error("Incorrect format. Please enter ranges as 'lower-upper' or '>lower'.")

            bins = sorted(list(set(bins)))
            if bins[-1] < df[map_column].max():
                bins.append(df[map_column].max() + 1)  # Adjust the max bin to include the max value

            df[map_column + "_bins"] = pd.cut(df[map_column], bins=bins, labels=bin_labels, include_lowest=True)
            map_column = map_column + "_bins"
            selected_categories = bin_labels
            category_counts = df[map_column].value_counts().to_dict()

    # Get colors from the selected palette (max 9 colors)
    cmap = plt.get_cmap(color_palette_name)
    num_colors = min(9, cmap.N)
    colors = [to_hex(cmap(i / (num_colors - 1))) for i in range(num_colors)]

    color_mapping = {category: colors[i % num_colors] for i, category in enumerate(selected_categories)}

    if st.checkbox("Select Colors for Columns"):
        for i, category in enumerate(selected_categories):
            color_mapping[category] = st.selectbox(f"Select Color for '{category}' in {map_column}:", options=colors, index=i)

    if st.button("Generate Map"):
        try:
            # Merge the shapefile and Excel data based on the selected columns
            merged_gdf = gdf.merge(df, left_on=shapefile_columns, right_on=shapefile_columns, how='left')

            if map_column not in merged_gdf.columns:
                st.error(f"The column '{map_column}' does not exist in the merged dataset.")
            else:
                # Plot the general map with the legend
                fig, ax = plt.subplots(1, 1, figsize=(12, 12))
                
                # Set default line color and width
                boundary_color = line_color.lower()
                boundary_width = line_width
                
                # Plot boundaries with the selected line width
                merged_gdf.boundary.plot(ax=ax, edgecolor=boundary_color, linewidth=boundary_width)
                
                # Apply custom colors if specified
                custom_cmap = ListedColormap([color_mapping.get(cat, missing_value_color.lower()) for cat in selected_categories])
                
                # Plot the map data with categories
                merged_gdf.plot(column=map_column, ax=ax, linewidth=boundary_width, edgecolor=boundary_color, cmap=custom_cmap,
                                legend=False, missing_kwds={'color': missing_value_color.lower(), 'edgecolor': boundary_color, 'label': missing_value_label})
                
                ax.set_title(f"{map_title} (General Map)", fontsize=font_size, fontweight='bold')
                ax.set_axis_off()
                
                # Create legend handles with category counts
                handles = []
                for cat in selected_categories:
                    label_with_count = f"{cat} ({category_counts.get(cat, 0)})"
                    handles.append(Patch(color=color_mapping.get(cat, missing_value_color.lower()), label=label_with_count))
                
                handles.append(Patch(color=missing_value_color.lower(), label=f"{missing_value_label} ({df[map_column].isna().sum()})"))
                
                ax.legend(handles=handles, title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')
                
                # Save or display the general map
                general_map_path = f"/tmp/{image_name}_general.png"
                plt.savefig(general_map_path, dpi=300, bbox_inches='tight')
                st.image(general_map_path, caption="General Map", use_column_width=True)
                plt.close(fig)

                # Plot each unique `FIRST_DNAM` separately
                first_dnam_values = merged_gdf['FIRST_DNAM'].unique()

                for value in first_dnam_values:
                    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
                    subset_gdf = merged_gdf[merged_gdf['FIRST_DNAM'] == value]

                    # Set default line color and width for subset
                    subset_boundary_color = line_color.lower()
                    subset_boundary_width = line_width

                    subset_gdf.boundary.plot(ax=ax, edgecolor=subset_boundary_color, linewidth=subset_boundary_width)
                    subset_gdf.plot(column=map_column, ax=ax, linewidth=subset_boundary_width, edgecolor=subset_boundary_color, cmap=custom_cmap,
                                    legend=False, missing_kwds={'color': missing_value_color.lower(), 'edgecolor': subset_boundary_color, 'label': missing_value_label})

                    # Add text labels for each `FIRST_CHIE`
                    for idx, row in subset_gdf.iterrows():
                        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, row['FIRST_CHIE'], fontsize=10, ha='center', color='black')

                    ax.set_title(f"{map_title} - {value}", fontsize=font_size, fontweight='bold')
                    ax.set_axis_off()

                    # Create legend handles with category counts
                    handles = []
                    for cat in selected_categories:
                        label_with_count = f"{cat} ({category_counts.get(cat, 0)})"
                        handles.append(Patch(color=color_mapping.get(cat, missing_value_color.lower()), label=label_with_count))

                    handles.append(Patch(color=missing_value_color.lower(), label=f"{missing_value_label} ({subset_gdf[map_column].isna().sum()})"))

                    ax.legend(handles=handles, title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')

                    # Save or display each subplot
                    subplot_path = f"/tmp/{image_name}_{value}.png"
                    plt.savefig(subplot_path, dpi=300, bbox_inches='tight')
                    st.image(subplot_path, caption=f"{map_title} - {value}", use_column_width=True)
                    plt.close(fig)
        except Exception as e:
            st.error(f"An error occurred while generating the map: {e}")
else:
    st.warning("Please upload an Excel file to proceed.")
