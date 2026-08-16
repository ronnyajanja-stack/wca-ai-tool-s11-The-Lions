"""
CBC Senior School Selection & Career Advisory Tool
Unified Application: RAG County Database & Career Advisory Engine
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# =====================================================================
# 1. INITIALIZATION & SETUP
# =====================================================================
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please check your configuration.")

client = OpenAI(api_key=api_key)


# =====================================================================
# 2. MEMBER 1 ENGINE: LOCAL RAG RETRIEVAL & COUNTY DIRECTORY
# =====================================================================
def load_schools_database(file_path="secondary_schools.json"):
    """Loads the local secondary school database."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Database file '{file_path}' not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieve_schools_by_county(schools_db, county_input, limit=20):
    """Searches the database and limits results to top N schools per county."""
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


def generate_county_school_report(county, candidates):
    """OpenAI generation for structured, numbered school directory."""
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


# =====================================================================
# 3. MEMBER 2 ENGINE: CAREER ROADMAP & INDUSTRY ADVISORY (R-T-C-C-O)
# =====================================================================
def generate_career_roadmap(pathway: str, subjects: str = "") -> str:
    """
    R-T-C-C-O Implementation for Career Opportunity & Industry Advisory
    - Role: Senior vocational/career guidance counselor.
    - Task: Generate career/industry analysis based on selected pathway.
    - Context: Evaluating long-term professional trajectories for Grade 9 CBC students.
    - Constraints: Provide concrete Kenyan local market data and progression routes.
    - Output: Well-formatted Markdown report.
    """
    system_prompt = (
        "Role: You are a senior vocational and career guidance counselor specializing in Kenya's CBC system.\n"
        "Task: Generate an in-depth career and industry analysis based on the student's selected CBC pathway.\n"
        "Context: Grade 9 CBC transitioning students evaluating long-term tertiary and professional trajectories.\n"
        "Constraints: Provide concrete local Kenyan market data, university degree/TVET entry requirements, "
        "emerging industries (e.g., Silicon Savannah, renewable energy, creative economy), and progression routes.\n"
        "Output: Provide a comprehensive, well-formatted Markdown report with clear headings, bullet points, and tables."
    )

    user_prompt = f"""Selected CBC Pathway: {pathway}
Related Subject Choices: {subjects if subjects else 'Standard pathway subjects'}

Generate an extensive professional roadmap, including:
1. Executive Pathway Summary
2. High-Demand Career Paths in Kenya & Regionally
3. University & TVET Progression Requirements
4. 5-Year Industry Outlook & Emerging Skill Demands
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


# =====================================================================
# 4. CLI MENU & LOGGING CONTROLLER
# =====================================================================
def option_1_county_school_rag(schools_db: list, session_log: list):
    """Option 1: County School RAG Directory"""
    print("\n" + "=" * 60)
    print(" Option 1: County Secondary School Directory (RAG Database)")
    print("=" * 60)

    county = input("Enter County Name (e.g., Nairobi, Siaya, Nakuru): ").strip()
    if not county:
        print("[!] County name cannot be empty.")
        return

    print(f"\n[RAG Engine] Querying secondary_schools.json for '{county}'...")
    candidates = retrieve_schools_by_county(schools_db, county, limit=20)

    if not candidates:
        print(f"[!] No schools found matching '{county}' in secondary_schools.json.")
        return

    print(f"[✓] Retrieved {len(candidates)} school(s). Generating numbered list via OpenAI...\n")

    try:
        report = generate_county_school_report(county, candidates)
        print("=" * 60)
        print(f"SCHOOLS DIRECTORY: {county.upper()} COUNTY (TOP {len(candidates)})")
        print("=" * 60)
        print(report)

        session_log.append({
            "timestamp": datetime.now().isoformat(),
            "option": "county_school_rag",
            "county_queried": county,
            "schools_found_count": len(candidates),
            "candidates_raw": candidates,
            "report_output": report
        })
    except Exception as e:
        print(f"[!] Error generating county school report: {e}")


def option_2_career_opportunity_insights(session_log: list):
    """Option 2: Career Opportunity & Industry Insights"""
    print("\n" + "=" * 60)
    print(" Option 2: Career Opportunity & Industry Insights")
    print("=" * 60)

    pathway = input("Enter the CBC pathway to explore (e.g., STEM, Arts & Sports, Social Sciences): ").strip()
    subjects = input("Enter relevant subject interests (optional): ").strip()

    if not pathway:
        print("[!] Pathway cannot be empty.")
        return

    print("\n[AI Processing] Generating professional career roadmap and industry analysis...")
    try:
        report_md = generate_career_roadmap(pathway, subjects)
        print("\n" + report_md + "\n")

        session_log.append({
            "timestamp": datetime.now().isoformat(),
            "option": "career_insights",
            "inputs": {"pathway": pathway, "subjects": subjects},
            "output": report_md
        })
    except Exception as e:
        print(f"[!] Error generating career insights: {e}")


def option_3_exit_program(session_log: list):
    """Option 3: Exit Program and save session artifacts"""
    print("\n" + "=" * 60)
    print(" Option 3: Exiting Program")
    print("=" * 60)

    if session_log:
        log_filename = "session_log.json"
        try:
            with open(log_filename, "w", encoding="utf-8") as f:
                json.dump(session_log, f, indent=2)
            print(f"[✓] Session artifacts successfully logged to '{log_filename}'.")
        except Exception as e:
            print(f"[!] Warning: Failed to write session log file: {e}")
    else:
        print("No actions performed during this session.")

    print("Goodbye!")
    sys.exit(0)


def display_menu():
    print("\n" + "=" * 60)
    print(" CBC SENIOR SCHOOL SELECTION & CAREER ADVISORY TOOL")
    print("=" * 60)
    print("1. Secondary Schools Directory by County (RAG Database - Top 20)")
    print("2. Career Opportunity & Industry Insights (CBC Pathways)")
    print("3. Exit Program")


def main():
    try:
        schools_db = load_schools_database("secondary_schools.json")
    except Exception as e:
        print(f"[!] Critical Error loading database: {e}")
        return

    session_log = []

    while True:
        display_menu()
        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            option_1_county_school_rag(schools_db, session_log)
        elif choice == "2":
            option_2_career_opportunity_insights(session_log)
        elif choice == "3":
            option_3_exit_program(session_log)
        else:
            print("\n[!] Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()