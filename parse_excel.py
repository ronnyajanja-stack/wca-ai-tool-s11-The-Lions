import json
import os
import pandas as pd


# ============================================================
# 1. LOCATE THE EXCEL DATABASE
# ============================================================

project_dir = os.path.dirname(os.path.abspath(__file__))

excel_file = os.path.join(
    project_dir,
    "Kenya_Secondary_Schools_2026_Database.xlsx"
)

output_json = os.path.join(
    project_dir,
    "secondary_schools.json"
)


# ============================================================
# 2. CHECK THAT THE EXCEL FILE EXISTS
# ============================================================

if not os.path.exists(excel_file):
    raise FileNotFoundError(
        f"Excel database not found:\n{excel_file}"
    )


print("=" * 70)
print("KENYA SECONDARY SCHOOLS DATABASE PARSER")
print("=" * 70)

print(f"\nLoading Excel file:")
print(excel_file)


# ============================================================
# 3. LOAD EXCEL FILE
# ============================================================

try:
    df = pd.read_excel(excel_file)

except Exception as e:
    raise RuntimeError(
        f"Could not read the Excel file: {e}"
    )


print(f"\nExcel file loaded successfully.")
print(f"Rows found: {len(df)}")
print(f"Columns found: {len(df.columns)}")


# ============================================================
# 4. DISPLAY THE ACTUAL EXCEL COLUMNS
# ============================================================

print("\nExcel columns detected:")

for number, column in enumerate(df.columns, start=1):
    print(f"{number}. {column}")


# ============================================================
# 5. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Name",
    "School Category (C1-C4)",
    "Pathways Offered",
    "Subject Combinations Offered",
    "PROVINCE",
    "DISTRICT",
    "COSTITUENCY",
    "DIVISION",
    "LOCATION",
    "SUBLOCATIO",
    "Level",
    "Status",
    "Sponsor",
    "Longitude",
    "Latitude",
    "# Classrooms",
    "Online Verification Status"
]


# ============================================================
# 6. CHECK FOR MISSING COLUMNS
# ============================================================

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\n[!] WARNING: The following columns are missing:")

    for column in missing_columns:
        print(f"   - {column}")

    raise ValueError(
        "The Excel file does not contain all expected columns."
    )


print("\n[✓] All expected Excel columns were found.")


# ============================================================
# 7. HELPER FUNCTION
# ============================================================

def clean_value(value):
    """
    Converts pandas values into JSON-safe Python values.

    Empty/NaN values become None.
    Strings are stripped of unnecessary spaces.
    """

    if pd.isna(value):
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

        return value

    return value


# ============================================================
# 8. CONVERT EXCEL DATA TO JSON RECORDS
# ============================================================

schools = []

for _, row in df.iterrows():

    school = {

        # ----------------------------------------------------
        # SCHOOL IDENTIFICATION
        # ----------------------------------------------------

        "school_name": clean_value(
            row["Name"]
        ),

        "category": clean_value(
            row["School Category (C1-C4)"]
        ),

        # ----------------------------------------------------
        # CBC PATHWAYS
        # ----------------------------------------------------

        "pathways_offered": clean_value(
            row["Pathways Offered"]
        ),

        "subject_combinations_offered": clean_value(
            row["Subject Combinations Offered"]
        ),

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        "province": clean_value(
            row["PROVINCE"]
        ),

        "district": clean_value(
            row["DISTRICT"]
        ),

        "constituency": clean_value(
            row["COSTITUENCY"]
        ),

        "division": clean_value(
            row["DIVISION"]
        ),

        "location": clean_value(
            row["LOCATION"]
        ),

        "sub_location": clean_value(
            row["SUBLOCATIO"]
        ),

        # ----------------------------------------------------
        # SCHOOL INFORMATION
        # ----------------------------------------------------

        "level": clean_value(
            row["Level"]
        ),

        "status": clean_value(
            row["Status"]
        ),

        "sponsor": clean_value(
            row["Sponsor"]
        ),

        # ----------------------------------------------------
        # GEOGRAPHICAL DATA
        # ----------------------------------------------------

        "longitude": clean_value(
            row["Longitude"]
        ),

        "latitude": clean_value(
            row["Latitude"]
        ),

        # ----------------------------------------------------
        # SCHOOL CAPACITY
        # ----------------------------------------------------

        "classrooms": clean_value(
            row["# Classrooms"]
        ),

        # ----------------------------------------------------
        # DATA VERIFICATION
        # ----------------------------------------------------

        "online_verification_status": clean_value(
            row["Online Verification Status"]
        )
    }

    schools.append(school)


# ============================================================
# 9. SAVE JSON DATABASE
# ============================================================

with open(
    output_json,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        schools,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# 10. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CONVERSION COMPLETE")
print("=" * 70)

print(f"\n[✓] Schools exported: {len(schools)}")
print(f"[✓] JSON file created:")
print(output_json)


# ============================================================
# 11. CATEGORY SUMMARY
# ============================================================

print("\nSchool Category Summary:")

category_counts = (
    df["School Category (C1-C4)"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
    .value_counts()
)

for category, count in category_counts.items():
    print(f"   {category}: {count}")


# ============================================================
# 12. PATHWAY SUMMARY
# ============================================================

print("\nPathway data check:")

pathway_count = (
    df["Pathways Offered"]
    .notna()
    .sum()
)

subject_count = (
    df["Subject Combinations Offered"]
    .notna()
    .sum()
)

print(
    f"   Schools with pathway information: {pathway_count}"
)

print(
    f"   Schools with subject combination information: {subject_count}"
)


# ============================================================
# 13. SHOW SAMPLE RECORD
# ============================================================

print("\nSample JSON record:")

if schools:

    print(
        json.dumps(
            schools[0],
            indent=2,
            ensure_ascii=False
        )
    )

print("\n" + "=" * 70)
print("READY FOR app.py")
print("=" * 70)