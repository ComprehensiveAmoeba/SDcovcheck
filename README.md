# SD_PRD Coverage Checker and Segmentation

This Streamlit app is designed to help you analyze and validate your advertising ASIN combinations for Sponsored Display Product (SD_PRD) campaigns. It allows you to upload a bulk file and a targets file to ensure that your Ad ASINs and Target ASINs are correctly matched according to your campaign strategy.

## Features
- **ASIN Matching**: Automatically extract Ad ASINs and Target ASINs from the bulk file and compare them with the combinations provided in the targets file.
- **Error Detection**: Identify and report any missing ASIN combinations that are present in the targets file but not found in the bulk file.
- **Duplicate Removal**: Ensures that the output contains no duplicate rows.

## How to Use

1. **Prepare Your Targets File**: Before using this app, make a copy of the [Targets input template](https://docs.google.com/spreadsheets/d/1QVjTkjo-QyiMdxvhO8f2oCp6TqwgHphw0x_8unFGkSA/edit?gid=0#gid=0). Populate the file with the correct Ad ASIN and Target ASIN combinations.

2. **Upload Files**:
    - Upload your `Targets` file in the Excel format (`.xlsx`).
    - Upload your `Bulk` file in the Excel format (`.xlsx`) that contains the campaign data.

3. **View Results**:
    - After processing, the app will display a preview of the filtered bulk data where correct ASIN combinations are found.
    - The app also shows any missing combinations that were present in the targets file but not matched in the bulk data.

4. **Download Outputs**:
    - Download the filtered bulk data with source tab information in Excel format.
    - Download the list of missing combinations in Excel format.

## Requirements

Ensure you have the following Python packages installed:

- `streamlit`
- `pandas`
- `openpyxl`

You can install these dependencies using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
