import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, to_hex
import io


# Displaying the images
st.image("icf_sl (1).jpg", caption="MAP GENERATOR", use_column_width=True)

# Load the shapefile
gdf = gpd.read_file("https://raw.githubusercontent.com/mohamedsillahkanu/si/2b7f982174b609f9647933147dec2a59a33e736a/Chiefdom%202021.shp")

# File upload (Excel or CSV)
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    # Read the uploaded file (Excel or CSV)
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Exclude certain columns from being selectable for the map
    excluded_columns = ['FIRST_DNAM', 'FIRST_CHIE', 'adm3']
    available_columns = [col for col in df.columns if col not in excluded_columns]

    # UI elements for selecting map settings
    map_column = st.selectbox("Select Map Column:", available_columns)
    map_title = st.text_input("Map Title:")
    legend_title = st.text_input("Legend Title:")
    image_name = st.text_input("Image Name:", value="Generated_Map")
    font_size = st.slider("Font Size (for Map Title):", min_value=8, max_value=24, value=15)

    show_image = st.checkbox('Check this box to display the Color Palette')

    # Display the image when the checkbox is checked
    if show_image:
        st.image('Color palette.png', caption='Color Palette')

    color_palette_name = st.selectbox("Color Palette:", options=list(plt.colormaps()), index=list(plt.colormaps()).index('Set3'))

    # Default line color and width settings
    line_color = st.selectbox("Select Default Line Color:", options=["White", "Black", "Red"], index=1)
    line_width = st.slider("Select Default Line Width:", min_value=0.5, max_value=5.0, value=2.5)

    # Missing value settings
    missing_value_color = st.selectbox("Select Color for Missing Values:", options=["White", "Gray", "Red"], index=1)
    missing_value_label = st.text_input("Label for Missing Values:", value="No Data")

    # Initialize category_counts dictionary for managing category counts
    category_counts = {}
    selected_categories = []  # Initialize selected_categories

    # Categorical or Numeric variable selection
    variable_type = st.radio("Select the variable type:", options=["Categorical", "Numeric"])

    if variable_type == "Categorical":
        unique_values = sorted(df[map_column].dropna().unique().tolist())
        selected_categories = st.multiselect(f"Select Categories for the Legend of {map_column}:", unique_values, default=unique_values)
        category_counts = df[map_column].value_counts().to_dict()

        # Reorder the categories
        df[map_column] = pd.Categorical(df[map_column], categories=selected_categories, ordered=True)

    elif variable_type == "Numeric":
        # Select number of bins
        num_bins = st.selectbox("Select Number of Bins:", options=[2, 3, 4, 5, 6, 7])

        # Create custom labels for bins
        bin_labels_input = st.text_input("Enter labels for bins (comma-separated):")
        bin_labels = [label.strip() for label in bin_labels_input.split(',')] if bin_labels_input else []

        # Validate the number of bin labels
        if len(bin_labels) != num_bins - 1:
            st.error(f"The number of valid bin labels must match {num_bins - 1}. You provided {len(bin_labels)} labels.")
        else:
            # Create bin edges based on user-defined labels
            bins = [df[map_column].min()]  # Start with the minimum value
            
            # Generate bins dynamically based on user input
            for i in range(num_bins - 1):
                lower_limit = df[map_column].min() + (i * (df[map_column].max() - df[map_column].min()) / (num_bins - 1))
                upper_limit = df[map_column].min() + ((i + 1) * (df[map_column].max() - df[map_column].min()) / (num_bins - 1))
                bins.append(lower_limit)
                bins.append(upper_limit)

            bins.append(df[map_column].max())  # End with the maximum value

            # Perform binning
            if bins:
                bins = sorted(set(bins))  # Ensure bins are unique and sorted
                df[map_column + "_bins"] = pd.cut(df[map_column], bins=bins, labels=bin_labels, include_lowest=True)
                map_column += "_bins"
                selected_categories = bin_labels
                category_counts = df[map_column].value_counts().to_dict()

    # Proceed with map generation if categories are selected
    if selected_categories:
        # Color mapping
        cmap = plt.get_cmap(color_palette_name)
        num_colors = min(9, cmap.N)
        colors = [to_hex(cmap(i / (num_colors - 1))) for i in range(num_colors)]
        color_mapping = {category: colors[i % num_colors] for i, category in enumerate(selected_categories)}

        # Optional color customization for categories
        if st.checkbox("Select Colors for Categories"):
            for i, category in enumerate(selected_categories):
                color_mapping[category] = st.selectbox(f"Select Color for '{category}' in {map_column}:", options=colors, index=i)

        # Column1 and Column2 are selected automatically in the background
        shapefile_columns = ['FIRST_DNAM', 'FIRST_CHIE']
        excel_columns = ['FIRST_DNAM', 'FIRST_CHIE']

        # Check if two columns are selected for merging
        if len(shapefile_columns) == 2 and len(excel_columns) == 2:
            column1_line_color = st.selectbox(f"Select Line Color for '{shapefile_columns[0]}' boundaries:", options=["White", "Black", "Red"], index=1)
            column1_line_width = st.slider(f"Select Line Width for '{shapefile_columns[0]}' boundaries:", min_value=0.5, max_value=10.0, value=2.5)
            column2_line_color = st.selectbox(f"Select Line Color for '{shapefile_columns[1]}' boundaries:", options=["White", "Black", "Red"], index=1)
            column2_line_width = st.slider(f"Select Line Width for '{shapefile_columns[1]}' boundaries:", min_value=0.5, max_value=10.0, value=2.5)

        # Generate the map upon button click
        if st.button("Generate Map"):
            try:
                # Merge the shapefile and Excel data
                merged_gdf = gdf.merge(df, left_on=shapefile_columns, right_on=excel_columns, how='left')

                if map_column not in merged_gdf.columns:
                    st.error(f"The column '{map_column}' does not exist in the merged dataset.")
                else:
                    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

                    # Apply custom colors
                    custom_cmap = ListedColormap([color_mapping[cat] for cat in selected_categories])

                    # Plot the map
                    merged_gdf.plot(column=map_column, ax=ax, linewidth=line_width, edgecolor=line_color.lower(), cmap=custom_cmap,
                                    legend=False, missing_kwds={'color': missing_value_color.lower(), 'edgecolor': line_color.lower(), 'label': missing_value_label})
                    ax.set_title(map_title, fontsize=font_size, fontweight='bold')
                    ax.set_axis_off()

                    # Add boundaries for 'FIRST_DNAM' and 'FIRST_CHIE'
                    dissolved_gdf1 = merged_gdf.dissolve(by=shapefile_columns[0])
                    dissolved_gdf1.boundary.plot(ax=ax, edgecolor=column1_line_color.lower(), linewidth=column1_line_width)

                    dissolved_gdf2 = merged_gdf.dissolve(by=shapefile_columns[1])
                    dissolved_gdf2.boundary.plot(ax=ax, edgecolor=column2_line_color.lower(), linewidth=column2_line_width)

                    # Check for missing data in the map column
                    if merged_gdf[map_column].isnull().sum() > 0:
                        # Add missing data to the legend
                        handles = [Patch(color=color_mapping[cat], label=f"{cat} ({category_counts.get(cat, 0)})") for cat in selected_categories]
                        handles.append(Patch(color=missing_value_color.lower(), label=f"{missing_value_label} ({merged_gdf[map_column].isnull().sum()})"))
                    else:
                        # Normal legend without missing data
                        handles = [Patch(color=color_mapping[cat], label=f"{cat} ({category_counts.get(cat, 0)})") for cat in selected_categories]

                    # Create legend with bold text
                    legend = ax.legend(handles=handles, title=legend_title, fontsize=10, loc='lower left', bbox_to_anchor=(-0.5, 0), frameon=True)
                    plt.setp(legend.get_title(), fontsize=10, fontweight='bold')
                    plt.setp(legend.get_texts(), fontweight='bold')

                    # Save the map to a BytesIO object for downloading
                    img_bytes = io.BytesIO()
                    plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0.1)
                    img_bytes.seek(0)

                    # Display the map
                    st.pyplot(fig)

                    # Download button for the generated image
                    st.download_button("Download Map", img_bytes, file_name=f"{image_name}.png", mime="image/png")

            except Exception as e:
                st.error(f"An error occurred while generating the map: {e}")
