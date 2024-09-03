import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Function to process the files
def process_files(targets_file, bulk_file):
    # Read targets file
    targets_data = pd.read_excel(targets_file, sheet_name=None)
    
    # Initialize an empty DataFrame to store all target combinations with their source tab name
    target_combinations = pd.DataFrame()

    # Loop through each sheet to extract combinations and their source tab
    for sheet_name, sheet_data in targets_data.items():
        sheet_data['Source Tab'] = sheet_name
        target_combinations = pd.concat([target_combinations, sheet_data], ignore_index=True)
    
    # Convert to lower case for case insensitivity
    target_combinations['Ad ASIN'] = target_combinations['Ad ASIN'].str.lower()
    target_combinations['Target ASIN'] = target_combinations['Target ASIN'].str.lower()

    # Read bulk file and filter relevant sheet(s)
    bulk_data_all = pd.read_excel(bulk_file, sheet_name=None)
    bulk_data = None
    for sheet_name, sheet_data in bulk_data_all.items():
        if "Display" in sheet_name:
            bulk_data = sheet_data
            break

    # Step 1: Extract Ad ASIN and Target ASIN from the "Campaign Name (Informational only)"
    def extract_asins(campaign_name):
        asin_pattern = r'(b0[a-z0-9]{8})'
        found_asins = re.findall(asin_pattern, campaign_name.lower())
        if len(found_asins) >= 2:
            return found_asins[0], found_asins[1]
        elif len(found_asins) == 1:
            return found_asins[0], None
        else:
            return None, None

    bulk_data[['Ad ASIN', 'Target ASIN']] = bulk_data['Campaign Name (Informational only)'].apply(
        lambda x: pd.Series(extract_asins(x))
    )

    # Step 2: Merge with target combinations to add Source Tab information
    bulk_data = pd.merge(
        bulk_data,
        target_combinations,
        on=['Ad ASIN', 'Target ASIN'],
        how='left'
    )

    # Step 3: Filter to include only rows where "Source Tab" is not blank
    filtered_bulk_with_source = bulk_data[bulk_data['Source Tab'].notna()]

    # Step 4: Remove duplicate rows
    filtered_bulk_with_source = filtered_bulk_with_source.drop_duplicates()

    # Step 5: Identify missing combinations by checking for missing Source Tab values
    missing_combinations = target_combinations.merge(
        bulk_data[['Ad ASIN', 'Target ASIN']],
        on=['Ad ASIN', 'Target ASIN'],
        how='left',
        indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return filtered_bulk_with_source, missing_combinations

# Streamlit UI
st.title('SD_PRD Coverage Checker and Segmentation')

# Instruction for users
st.markdown("""
Before using this tool, please make a copy of the [Targets input template](https://docs.google.com/spreadsheets/d/1QVjTkjo-QyiMdxvhO8f2oCp6TqwgHphw0x_8unFGkSA/edit?gid=0#gid=0) to use as your Targets input file.
""")

# File uploader
targets_file = st.file_uploader("Upload Targets Excel File", type="xlsx")
bulk_file = st.file_uploader("Upload Bulk Excel File", type="xlsx")

if targets_file and bulk_file:
    # Process files
    filtered_bulk_with_source, missing_combinations = process_files(targets_file, bulk_file)
    
    # Display preview of filtered bulk data
    st.subheader("Filtered Bulk Data with Source Tab")
    st.dataframe(filtered_bulk_with_source.head())
    
    # Display preview of missing combinations
    st.subheader("Missing Combinations")
    st.dataframe(missing_combinations.head())
    
    # Download button for filtered bulk data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bulk_output_filename = f"filtered_bulk_with_source_{timestamp}.xlsx"
    
    with pd.ExcelWriter(bulk_output_filename) as writer:
        filtered_bulk_with_source.to_excel(writer, index=False)
    
    with open(bulk_output_filename, "rb") as file:
        st.download_button(
            label="Download Filtered Bulk Data with Source Tab",
            data=file,
            file_name=bulk_output_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Download button for missing combinations
    missing_output_filename = f"missing_combinations_{timestamp}.xlsx"
    
    with pd.ExcelWriter(missing_output_filename) as writer:
        missing_combinations.to_excel(writer, index=False)
    
    with open(missing_output_filename, "rb") as file:
        st.download_button(
            label="Download Missing Combinations",
            data=file,
            file_name=missing_output_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
