from pathlib import Path
import json
import pandas as pd


def parse_schools_database(
    input_file=None, output_json="secondary_schools.json"
):
    # Auto-detect file if not explicitly passed
    if input_file is None:
        candidates = [
            "Kenya_Secondary_Schools_2026_Database.xlsx",
            "Kenya_Secondary_Schools_2026_Database.xls",
            "Kenya_Secondary_Schools_2026_Database.csv",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                input_file = candidate
                break

    if not input_file or not Path(input_file).exists():
        print(
            f"[-] Error: Could not locate database file in '{Path.cwd()}'. Ensure the file is in the project root."
        )
        return

    try:
        # Load based on extension
        if input_file.endswith(".csv"):
            df = pd.read_csv(input_file)
        else:
            df = pd.read_excel(input_file, engine="openpyxl")

        # Strip whitespace from column headers & normalize
        df.columns = [
            str(c).strip().lower().replace(" ", "_").replace("/", "_")
            for c in df.columns
        ]

        # Handle NaN values across data types
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str).str.strip()
            else:
                df[col] = df[col].fillna(0)

        records = df.to_dict(orient="records")

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        print(
            f"[+] Successfully converted {len(records)} school records from '{input_file}' to '{output_json}'."
        )

    except ModuleNotFoundError:
        print(
            "[-] Missing dependency. Please run: pip install openpyxl pandas"
        )
    except Exception as e:
        print(f"[-] Parsing failed: {e}")


if __name__ == "__main__":
    parse_schools_database()