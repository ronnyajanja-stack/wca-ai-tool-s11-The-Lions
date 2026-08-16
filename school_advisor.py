import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please add it to your .env file.")

# Initialize the OpenAI Client
client = OpenAI(api_key=api_key)

# 2. Load Local Secondary Schools Database (RAG source)
def load_schools_database(file_path="secondary_schools.json"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Database file '{file_path}' not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 3. Retrieve Schools by County (Limited to 20)
def retrieve_schools_by_county(schools_db, county_input, limit=20):
    q = county_input.strip().lower()
    if not q:
        return []

    matched = []
    for school in schools_db:
        county_field = str(school.get("county") or school.get("County") or school.get("location") or "").lower()
        full_text = " ".join(str(v).lower() for v in school.values())

        if q in county_field or q in full_text:
            matched.append(school)

    return matched[:limit]

# 4. Generate Numbered List via OpenAI
def generate_county_school_report(county, candidates):
    schools_context = json.dumps(candidates, indent=2)

    system_instructions = (
        "You are an educational data assistant for Kenyan Secondary Schools. "
        "Your task is to present schools in a clean, strictly numbered list based on provided records."
    )

    user_prompt = f"""
TARGET COUNTY: {county.title()}

RETRIEVED SCHOOLS FROM DATABASE:
{schools_context}

TASK:
1. List the retrieved schools in a strict numbered format (1., 2., 3., ... up to {len(candidates)}).
2. For each numbered item, show:
   - School Name
   - Category/Tier (e.g., National, Extra County, County, Sub-County, C1-C4)
   - Gender/Type (e.g., Boys, Girls, Mixed)
   - Accommodation (e.g., Boarding, Day)
3. End with a 1-sentence note stating the total number of schools listed for {county.title()}.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

# 5. CLI Execution Loop
def main():
    print("=" * 60)
    print("🏫 Kenyan Secondary Schools Directory by County")
    print("=" * 60 + "\n")

    try:
        schools_db = load_schools_database("secondary_schools.json")
    except Exception as e:
        print(f"Error loading database: {e}")
        return

    county = input("Enter County Name (e.g., Nairobi, Siaya, Nakuru): ").strip()
    if not county:
        print("No county provided. Exiting.")
        return

    print(f"\nSearching database for up to 20 schools in '{county}'...")
    candidates = retrieve_schools_by_county(schools_db, county, limit=20)

    if not candidates:
        print(f"No schools found for '{county}' in secondary_schools.json.")
        return

    print(f"Found {len(candidates)} school(s). Formatting numbered list...\n")

    try:
        report = generate_county_school_report(county, candidates)
        print("=" * 60)
        print(f"SCHOOLS DIRECTORY: {county.upper()} COUNTY (TOP {len(candidates)})")
        print("=" * 60)
        print(report)
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    main()