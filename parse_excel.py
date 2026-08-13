import json
import os
import pandas as pd

# List candidate files in project root or Downloads folder
candidate_files = [
    "Kenya_Secondary_Schools_Data_Only.xlsx",
    "Kenya_Secondary_Schools_Fully_Categorized_v3.xlsx",
    "Kenya_Secondary_Schools_With_Categories_v2.xlsx",
    "Kenya MOE Schools.xlsx",
    os.path.expanduser(
        "~/Downloads/Kenya_Secondary_Schools_Fully_Categorized_v3.xlsx"
    ),
    os.path.expanduser("~/Downloads/Kenya_Secondary_Schools_Data_Only.xlsx"),
    os.path.expanduser("~/Downloads/Kenya MOE Schools.xlsx"),
]

excel_file = None
for f in candidate_files:
    if os.path.exists(f):
        excel_file = f
        break

if not excel_file:
    raise FileNotFoundError(
        "Could not locate the Excel dataset in project root or Downloads folder."
    )

try:
    print(f"Loading Excel file from: {excel_file}...")
    xls = pd.ExcelFile(excel_file)

    # Check if 'Secondary Schools Data' sheet exists, otherwise load default sheet
    if "Secondary Schools Data" in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name="Secondary Schools Data")
    else:
        df = pd.read_excel(excel_file, sheet_name=0)

    # Filter for Secondary Schools if Level column is present, else use full dataframe
    if "Level" in df.columns:
        secondary_mask = (
            df["Level"]
            .astype(str)
            .str.upper()
            .str.contains("SECONDARY|SEC", na=False)
        )
        df_secondary = df[secondary_mask].copy()
    else:
        df_secondary = df.copy()

    # Format into structured JSON objects
    secondary_list = []
    for _, row in df_secondary.iterrows():
        # Retrieve Category from CATEGORY or default to C3
        cat_val = row.get("CATEGORY", row.get("category", "C3"))
        cat_str = str(cat_val).strip() if pd.notna(cat_val) else "C3"

        secondary_list.append(
            {
                "school_name": (
                    str(row.get("Name", "")).strip()
                    if pd.notna(row.get("Name"))
                    else ""
                ),
                "province": (
                    str(row.get("PROVINCE", "")).strip()
                    if pd.notna(row.get("PROVINCE"))
                    else ""
                ),
                "district": (
                    str(row.get("DISTRICT", "")).strip()
                    if pd.notna(row.get("DISTRICT"))
                    else ""
                ),
                "constituency": (
                    str(row.get("COSTITUENCY", "")).strip()
                    if pd.notna(row.get("COSTITUENCY"))
                    else ""
                ),
                "division": (
                    str(row.get("DIVISION", "")).strip()
                    if pd.notna(row.get("DIVISION"))
                    else ""
                ),
                "category": cat_str,  # Category C1-C4
                "location": (
                    str(row.get("LOCATION", "")).strip()
                    if pd.notna(row.get("LOCATION"))
                    else ""
                ),
                "sub_location": (
                    str(row.get("SUBLOCATIO", "")).strip()
                    if pd.notna(row.get("SUBLOCATIO"))
                    else ""
                ),
                "status": (
                    str(row.get("Status", "")).strip()
                    if pd.notna(row.get("Status"))
                    else ""
                ),
                "sponsor": (
                    str(row.get("Sponsor", "")).strip()
                    if pd.notna(row.get("Sponsor"))
                    else ""
                ),
                "longitude": (
                    float(row.get("Longitude"))
                    if pd.notna(row.get("Longitude"))
                    else None
                ),
                "latitude": (
                    float(row.get("Latitude"))
                    if pd.notna(row.get("Latitude"))
                    else None
                ),
            }
        )

    # Export to secondary_schools.json in project root
    output_json = "secondary_schools.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(secondary_list, f, indent=2)

    print(
        f"Success! Exported {len(secondary_list)} secondary schools to {output_json}."
    )

except Exception as e:
    print(f"Error parsing Excel file: {e}")