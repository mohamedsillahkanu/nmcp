import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Title of the app
st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

# Function to load and display image with error handling
def load_and_display_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(
                image,
                caption="Sierra Leone Administrative Map",
                use_container_width=True
            )
        else:
            st.error(f"Failed to load image. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        st.info("Please ensure the image URL is accessible and valid.")

# Display the image using the GitHub raw URL with error handling
image_url = "https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png"
load_and_display_image(image_url)

# Overview Section
st.header("Overview")
st.write("""
Before now, the Sub-National Tailoring (SNT) process took a considerable amount of time to complete analysis. Based on the experience of the 2023 SNT implementation, we have developed an automated tool using the same validated codes with additional enhanced features. This innovation aims to build the capacity of National Malaria Control Program (NMCP) to conduct SNT easily on a yearly basis and monitor activities effectively using this tool. The tool is designed to be user-friendly and offers high processing speed.

The integration of automation in geospatial analysis significantly enhances the efficiency and effectiveness of data management and visualization tasks. With the introduction of this automated system, analysis time has been drastically reduced from one year to one week. This shift not only streamlines operations but also allows analysts to focus on interpreting results rather than being bogged down by technical processes.
""")

# Objectives Section
st.header("Objectives")
st.write("""
The main objectives of implementing automated systems for geospatial analysis and data management are:
1. **Reduce Time and Effort**: Significantly decrease the time required to create maps and analyze data, enabling quicker decision-making.
2. **Enhance Skill Accessibility**: Provide tools that can be used effectively by individuals without extensive technical training.
3. **Improve Data Management Efficiency**: Streamline data management processes that currently can take days to complete, allowing for more timely implementation of programs.
4. **Facilitate Rapid Analysis**: Enable automated analysis of uploaded datasets within minutes, transforming how organizations approach data-driven decisions.
""")

# Scope Section
st.header("Scope")
st.write("""
The scope of this project encompasses:
- The development and implementation of an automated system that simplifies the creation of geospatial visualizations.
- A comprehensive automated data analysis tool that processes datasets quickly and efficiently, enabling analysts to obtain insights in less than 20 minutes.
- Training and support for users to maximize the benefits of these tools, ensuring that even those with limited technical skills can leverage automation for their analytical needs.
""")

# Target Audience Section
st.header("Target Audience")
st.write("""
The target audience includes:
- Public health officials and analysts working within NMCPs who require efficient mapping and data analysis solutions.
- Data managers and decision-makers seeking to improve operational efficiency and responsiveness to health challenges.
- Organizations interested in integrating automation into their workflows to enhance data-driven decision-making capabilities.
""")

# Conclusion Section
st.header("Conclusion")
st.write("""
The adoption of this automated system for SNT analysis represents a transformative opportunity for NMCPs. By significantly reducing the time and effort required for these tasks, programs can enhance their efficiency, improve the quality of their analyses, and ultimately lead to more timely and informed decision-making. This tool, built on the experience of the 2023 SNT implementation, not only addresses existing operational challenges but also empowers analysts to focus on deriving insights rather than getting lost in technical details. The user-friendly interface and high processing speed make it an invaluable asset for regular SNT updates and monitoring of malaria control activities.
""")
