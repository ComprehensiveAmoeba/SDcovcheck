import streamlit as st
import pandas as pd
from datetime import datetime
import re
import os

# Function to process the files
def process_files(targets_file, bulk_file, add_tags):
    targets_data = pd.read_excel(targets_file, sheet_name=None)
    target_combinations = pd.DataFrame()

    for sheet_name, sheet_data in targets_data.items():
        sheet_data['Source Tab'] = sheet_name
        target_combinations = pd.concat([target_combinations, sheet_data], ignore_index=True)

    target_combinations['Ad ASIN'] = target_combinations['Ad ASIN'].str.lower()
    target_combinations['Target ASIN'] = target_combinations['Target ASIN'].str.lower()

    bulk_data_all = pd.read_excel(bulk_file, sheet_name=None)
    bulk_data = None
    for sheet_name, sheet_data in bulk_data_all.items():
        if "Display" in sheet_name:
            bulk_data = sheet_data
            break

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

    bulk_data = pd.merge(
        bulk_data,
        target_combinations,
        on=['Ad ASIN', 'Target ASIN'],
        how='left'
    )

    filtered_bulk_with_source = bulk_data[bulk_data['Source Tab'].notna()]
    filtered_bulk_with_source = filtered_bulk_with_source.drop_duplicates()

    if add_tags:
        filtered_bulk_with_source.loc[filtered_bulk_with_source['Entity'] == 'Campaign', 'Operation'] = 'update'
        filtered_bulk_with_source.loc[filtered_bulk_with_source['Entity'] == 'Campaign', 'Campaign Name'] = filtered_bulk_with_source.apply(
            lambda row: f"SD_{row['Source Tab']}_{row['Campaign Name']}" 
            if row['Entity'] == 'Campaign' and isinstance(row['Campaign Name'], str) and row['Campaign Name'].startswith("SD_") 
            else row['Campaign Name'], 
            axis=1
)


    missing_combinations = target_combinations.merge(
        bulk_data[['Ad ASIN', 'Target ASIN']],
        on=['Ad ASIN', 'Target ASIN'],
        how='left',
        indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return filtered_bulk_with_source, missing_combinations

# Function to generate defensive ASIN combinations
def generate_combinations(asins):
    combinations = [(ad, target) for ad in asins for target in asins if ad != target]
    return pd.DataFrame(combinations, columns=["Ad ASIN", "Target ASIN"])

# Streamlit app
st.title('SD_PRD Coverage Checker and Segmentation')
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio("Select a tab", ["SD_PRD Coverage Checker", "Defensive ASIN Combinations"])

if selected_tab == "SD_PRD Coverage Checker":
    st.header("SD_PRD Coverage Checker")
    st.markdown(
        """
        Before using this tool, please make a copy of the [Targets input template](https://docs.google.com/spreadsheets/d/1QVjTkjo-QyiMdxvhO8f2oCp6TqwgHphw0x_8unFGkSA/edit?gid=0#gid=0) 
        to use as your Targets input file.
        """
    )

    targets_file = st.file_uploader("Upload Targets Excel File", type="xlsx")
    bulk_file = st.file_uploader("Upload Bulk Excel File", type="xlsx")
    add_tags = st.checkbox("Add Tags to Campaign Names")

    if targets_file and bulk_file:
        filtered_bulk_with_source, missing_combinations = process_files(targets_file, bulk_file, add_tags)

        st.subheader("Filtered Bulk Data with Source Tab")
        st.dataframe(filtered_bulk_with_source.head())

        st.subheader("Missing Combinations")
        st.dataframe(missing_combinations.head())

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

elif selected_tab == "Defensive ASIN Combinations":
    st.header("Defensive ASIN Combinations")
    st.markdown("Enter a list of ASINs (one per row) to generate all possible combinations.")

    asin_input = st.text_area("Enter ASINs (one per row):")

    if asin_input:
        asins = [asin.strip() for asin in asin_input.split("\n") if asin.strip()]
        combinations_df = generate_combinations(asins)

        st.subheader("Generated Combinations")
        st.dataframe(combinations_df.head())

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combinations_output_filename = f"defensive_asin_combinations_{timestamp}.xlsx"

        with pd.ExcelWriter(combinations_output_filename) as writer:
            combinations_df.to_excel(writer, index=False)

        with open(combinations_output_filename, "rb") as file:
            st.download_button(
                label="Download Defensive ASIN Combinations",
                data=file,
                file_name=combinations_output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
