def create_adm1_plots(shapefile, coordinates_data, map_column, longitude_col, latitude_col,
                   point_color, point_size, point_alpha, background_color, custom_cmap,
                   line_color='black', line_width=0.5, missing_value_color='gray',
                   missing_value_label='Missing', font_size=12):
    """Create individual plots for each ADM1 region with enhanced features."""
    
    from matplotlib.patches import Patch
    
    # Get unique ADM1 values
    adm1_values = shapefile['FIRST_DNAM'].unique()
    
    # Create a list to store all figure references
    figures = []
    
    # Calculate category counts for the entire dataset
    if map_column in coordinates_data.columns:
        category_counts = coordinates_data[map_column].value_counts().to_dict()
        selected_categories = coordinates_data[map_column].dropna().unique()
    else:
        category_counts = {}
        selected_categories = []
    
    # Create color mapping for categories
    color_mapping = {cat: custom_cmap(i/len(selected_categories)) 
                    for i, cat in enumerate(selected_categories)}
    
    for adm1 in adm1_values:
        try:
            # Create figure for this ADM1
            fig, ax = plt.subplots(figsize=(12, 12))
            
            # Subset data for this ADM1
            shapefile_subset = shapefile[shapefile['FIRST_DNAM'] == adm1]
            coordinates_subset = coordinates_data[coordinates_data['FIRST_DNAM'] == adm1]
            
            # Plot base shapefile
            shapefile_subset.boundary.plot(ax=ax, edgecolor=line_color, 
                                        linewidth=line_width)
            
            # Plot choropleth if map_column exists
            if map_column in coordinates_subset.columns:
                shapefile_subset.plot(column=map_column, ax=ax, 
                                    linewidth=line_width,
                                    edgecolor=line_color,
                                    cmap=custom_cmap,
                                    legend=False,
                                    missing_kwds={'color': missing_value_color,
                                                'edgecolor': line_color,
                                                'label': missing_value_label})
            
            # Add district labels
            for idx, row in shapefile_subset.iterrows():
                ax.text(row.geometry.centroid.x, 
                       row.geometry.centroid.y,
                       row['FIRST_CHIE'],
                       fontsize=font_size-2,
                       ha='center',
                       va='center',
                       color='black',
                       bbox=dict(facecolor='white',
                               alpha=0.7,
                               edgecolor='none',
                               pad=1))
            
            # Create legend handles with category counts
            handles = []
            for cat in selected_categories:
                # Count categories for this ADM1 only
                adm1_count = len(coordinates_subset[coordinates_subset[map_column] == cat])
                label_with_count = f"{cat} ({adm1_count})"
                handles.append(Patch(color=color_mapping.get(cat, missing_value_color),
                                   label=label_with_count))
            
            # Add missing values to legend
            missing_count = coordinates_subset[map_column].isna().sum()
            if missing_count > 0:
                handles.append(Patch(color=missing_value_color,
                                   label=f"{missing_value_label} ({missing_count})"))
            
            # Add legend
            if handles:
                ax.legend(handles=handles,
                         title=map_column,
                         bbox_to_anchor=(1.05, 1),
                         loc='upper left')
            
            # Customize appearance
            ax.set_title(f"{adm1}", fontsize=font_size, fontweight='bold', pad=20)
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

# In the main Streamlit app, modify the ADM1 plotting section:
if display_type == "ADM1 Plots":
    figures = create_adm1_plots(
        shapefile=shapefile,
        coordinates_data=coordinates_data,
        map_column=selected_column,  # Add this to your UI
        longitude_col=longitude_col,
        latitude_col=latitude_col,
        point_color=point_color,
        point_size=point_size,
        point_alpha=point_alpha,
        background_color=background_color,
        custom_cmap=plt.cm.get_cmap('viridis'),  # Or let user select
        line_color='black',
        line_width=0.5,
        missing_value_color='gray',
        missing_value_label='Missing',
        font_size=12
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
