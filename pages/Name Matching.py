import streamlit as st
import pandas as pd
import numpy as np
from jellyfish import jaro_winkler_similarity
from io import BytesIO

def calculate_match(df1, df2, name_col1, name_col2, threshold):
    """Calculate matching scores between two dataframes using Jaro-Winkler similarity."""
    results = []
    
    for idx1, row1 in df1.iterrows():
        value1 = str(row1[name_col1])
        if value1 in df2[name_col2].astype(str).values:
            # Exact match found
            matching_row = df2[df2[name_col2].astype(str) == value1].iloc[0]
            result_dict = {
                'HF_Name_in_MFL': value1,
                'HF_Name_in_DHIS2': value1,
                'Match_Score': 100,
                'Match_Status': 'Match'
            }
            # Add all columns from both datasets
            for col in df1.columns:
                if col != name_col1:
                    result_dict[f'MFL_{col}'] = row1[col]
            for col in df2.columns:
                if col != name_col2:
                    result_dict[f'DHIS2_{col}'] = matching_row[col]
            results.append(result_dict)
        else:
            # Find best match
            best_score = 0
            best_match = None
            best_match_row = None
            
            for idx2, row2 in df2.iterrows():
                value2 = str(row2[name_col2])
                similarity = jaro_winkler_similarity(value1, value2) * 100
                if similarity > best_score:
                    best_score = similarity
                    best_match = value2
                    best_match_row = row2
            
            result_dict = {
                'HF_Name_in_MFL': value1,
                'HF_Name_in_DHIS2': best_match,
                'Match_Score': round(best_score, 2),
                'Match_Status': 'Unmatch' if best_score < threshold else 'Match'
            }
            # Add all columns from both datasets
            for col in df1.columns:
                if col != name_col1:
                    result_dict[f'MFL_{col}'] = row1[col]
            if best_match_row is not None:
                for col in df2.columns:
                    if col != name_col2:
                        result_dict[f'DHIS2_{col}'] = best_match_row[col]
            results.append(result_dict)
    
    # Handle unmatched facilities from DHIS2
    matched_dhis2_names = [r['HF_Name_in_DHIS2'] for r in results if r['HF_Name_in_DHIS2'] is not None]
    for idx2, row2 in df2.iterrows():
        if str(row2[name_col2]) not in matched_dhis2_names:
            result_dict = {
                'HF_Name_in_MFL': None,
                'HF_Name_in_DHIS2': row2[name_col2],
                'Match_Score': 0,
                'Match_Status': 'Unmatch'
            }
            # Add empty values for MFL columns
            for col in df1.columns:
                if col != name_col1:
                    result_dict[f'MFL_{col}'] = None
            # Add DHIS2 columns
            for col in df2.columns:
                if col != name_col2:
                    result_dict[f'DHIS2_{col}'] = row2[col]
            results.append(result_dict)
    
    return pd.DataFrame(results)

def main():
    st.title("Health Facility Name Matching Tool")
    
    # Introduction
    st.markdown("""
    ### Why Health Facility Name Matching?
    
    Maintaining consistent health facility names across different information systems is crucial for:
    
    🏥 **Data Quality**: Ensures accurate reporting and analysis by linking facility data correctly across systems
    
    📊 **Resource Management**: Helps track and allocate resources efficiently by maintaining a single source of truth
    
    🔄 **System Integration**: Enables seamless data exchange between the Master Facility List (MFL) and DHIS2
    
    🎯 **Decision Making**: Supports evidence-based decision making with reliable facility-level data
    
    This tool uses advanced string matching algorithms to automatically identify and reconcile differences 
    between facility names in the MFL and DHIS2, saving time and reducing errors in data harmonization.
    """)

    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'master_hf_list' not in st.session_state:
        st.session_state.master_hf_list = None
    if 'health_facilities_dhis2_list' not in st.session_state:
        st.session_state.health_facilities_dhis2_list = None

    # Rest of your existing code for Step 1...
    if st.session_state.step == 1:
        st.header("Step 1: Upload Files")
        mfl_file = st.file_uploader("Upload Master HF List (CSV, Excel):", type=['csv', 'xlsx', 'xls'])
        dhis2_file = st.file_uploader("Upload DHIS2 HF List (CSV, Excel):", type=['csv', 'xlsx', 'xls'])

        if mfl_file and dhis2_file:
            try:
                # Read files
                if mfl_file.name.endswith('.csv'):
                    st.session_state.master_hf_list = pd.read_csv(mfl_file)
                else:
                    st.session_state.master_hf_list = pd.read_excel(mfl_file)

                if dhis2_file.name.endswith('.csv'):
                    st.session_state.health_facilities_dhis2_list = pd.read_csv(dhis2_file)
                else:
                    st.session_state.health_facilities_dhis2_list = pd.read_excel(dhis2_file)

                st.success("Files uploaded successfully!")
                
                # Display previews
                st.subheader("Preview of Master HF List")
                st.dataframe(st.session_state.master_hf_list.head())
                st.subheader("Preview of DHIS2 HF List")
                st.dataframe(st.session_state.health_facilities_dhis2_list.head())

                if st.button("Proceed to Column Renaming"):
                    st.session_state.step = 2
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"Error reading files: {e}")

    # Step 2: Column Renaming
    elif st.session_state.step == 2:
        st.header("Step 2: Rename Columns (Optional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Master HF List Columns")
            mfl_renamed_columns = {}
            for col in st.session_state.master_hf_list.columns:
                new_col = st.text_input(f"Rename '{col}' to:", key=f"mfl_{col}", value=col)
                mfl_renamed_columns[col] = new_col

        with col2:
            st.subheader("DHIS2 HF List Columns")
            dhis2_renamed_columns = {}
            for col in st.session_state.health_facilities_dhis2_list.columns:
                new_col = st.text_input(f"Rename '{col}' to:", key=f"dhis2_{col}", value=col)
                dhis2_renamed_columns[col] = new_col

        if st.button("Apply Changes and Continue"):
            st.session_state.master_hf_list = st.session_state.master_hf_list.rename(columns=mfl_renamed_columns)
            st.session_state.health_facilities_dhis2_list = st.session_state.health_facilities_dhis2_list.rename(
                columns=dhis2_renamed_columns)
            st.session_state.step = 3
            st.experimental_rerun()

        if st.button("Skip Renaming"):
            st.session_state.step = 3
            st.experimental_rerun()

    # Step 3: Column Selection and Matching
    elif st.session_state.step == 3:
        st.header("Step 3: Select Columns for Matching")
        
        mfl_col = st.selectbox("Select HF Name column in Master HF List:", 
                              st.session_state.master_hf_list.columns)
        dhis2_col = st.selectbox("Select HF Name column in DHIS2 HF List:", 
                                st.session_state.health_facilities_dhis2_list.columns)
        
        threshold = st.slider("Set Match Threshold (0-100):", 
                            min_value=0, max_value=100, value=70,
                            help="Higher threshold means stricter matching criteria")

        if st.button("Perform Matching"):
            # Process data
            master_hf_list_clean = st.session_state.master_hf_list.copy()
            dhis2_list_clean = st.session_state.health_facilities_dhis2_list.copy()
            
            master_hf_list_clean[mfl_col] = master_hf_list_clean[mfl_col].astype(str)
            master_hf_list_clean = master_hf_list_clean.drop_duplicates(subset=[mfl_col])
            dhis2_list_clean[dhis2_col] = dhis2_list_clean[dhis2_col].astype(str)

            st.write("### Counts of Health Facilities")
            st.write(f"Count of HFs in DHIS2 list: {len(dhis2_list_clean)}")
            st.write(f"Count of HFs in MFL list: {len(master_hf_list_clean)}")

            # Perform matching
            with st.spinner("Performing matching..."):
                hf_name_match_results = calculate_match(
                    master_hf_list_clean,
                    dhis2_list_clean,
                    mfl_col,
                    dhis2_col,
                    threshold
                )
                
                # Add suggested name column
                hf_name_match_results['Suggested_HF_Name'] = np.where(
                    hf_name_match_results['Match_Score'] >= threshold,
                    hf_name_match_results['HF_Name_in_DHIS2'],
                    hf_name_match_results['HF_Name_in_MFL']
                )

                # Display results
                st.write("### Matching Results")
                st.dataframe(hf_name_match_results)
                
                # Add summary statistics
                total_facilities = len(hf_name_match_results)
                matched = len(hf_name_match_results[hf_name_match_results['Match_Status'] == 'Match'])
                unmatched = total_facilities - matched
                
                st.write("### Summary Statistics")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Facilities", total_facilities)
                col2.metric("Matched", matched)
                col3.metric("Unmatched", unmatched)

                # Download results
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    hf_name_match_results.to_excel(writer, index=False)
                output.seek(0)

                st.download_button(
                    label="Download Matching Results as Excel",
                    data=output,
                    file_name="hf_name_matching_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.master_hf_list = None
            st.session_state.health_facilities_dhis2_list = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
