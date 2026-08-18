"""
CBC Senior School Selection & Career Advisory Tool
Integrated CLI & Dual-API Engine (R-T-C-C-O Prompt Framework)
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================================
# API CALL #1: School Selection & Compatibility (R-T-C-C-O Framework)
# =====================================================================
def generate_school_recommendations(pathway: str, county: str, subjects: str, category: str = "Any", accommodation: str = "Any") -> dict:
    """
    R-T-C-C-O Implementation for API Call #1: School Selection & Compatibility Analysis
    - Role: Expert Kenyan CBC educational advisor.
    - Task: Analyze inputs and evaluate institutional fit.
    - Context: Transitioning Grade 9 students needing data-driven recommendations.
    - Constraints: Reference realistic Kenyan regions, adhere to CBC guidelines.
    - Output: Structured JSON object.
    """
    system_prompt = (
        "Role: You are an expert Kenyan CBC educational advisor.\n"
        "Task: Analyze student inputs (preferred pathway, location/county, subject combinations) "
        "and evaluate institutional fit against senior secondary schools.\n"
        "Context: Transitioning Grade 9 students needing realistic, data-driven school placement recommendations.\n"
        "Constraints: Reference realistic Kenyan regions/schools, strictly adhere to Kenyan CBC guidelines "
        "(C1=National, C2=Extra-County, C3=County, C4=Sub-County/Private), and ignore unverified data.\n"
        "Output: Return strictly a valid JSON object matching this schema:\n"
        "{\n"
        '  "recommended_schools": [\n'
        "    {\n"
        '      "school_name": "string",\n'
        '      "category": "C1/C2/C3/C4",\n'
        '      "county": "string",\n'
        '      "matching_rationale": "string",\n'
        '      "recommended_cbc_electives": ["subject1", "subject2", "subject3"]\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"""Student Profile:
- Target CBC Pathway: {pathway}
- Preferred County / Location: {county}
- Subject Combination: {subjects}
- Preferred Category: {category}
- Accommodation: {accommodation}

Generate the top recommended senior secondary schools matching this profile.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    return json.loads(response.choices[0].message.content)


# =====================================================================
# API CALL #2: Career Opportunity & Industry Insights (R-T-C-C-O Framework)
# =====================================================================
def generate_career_roadmap(pathway: str, subjects: str = "") -> str:
    """
    R-T-C-C-O Implementation for API Call #2: Career Opportunity & Industry Advisory
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
# SYSTEM MENU HANDLERS
# =====================================================================
def option_1_senior_school_matching(session_log: list):
    """Option 1: Senior School Matching & Pathway Alignment"""
    print("\n" + "=" * 60)
    print(" Option 1: Senior School Matching & Pathway Alignment")
    print("=" * 60)

    pathway = input("Enter preferred CBC pathway (e.g. STEM, Arts & Sports, Social Sciences): ").strip()
    county = input("Enter preferred location/county (e.g. Siaya, Nairobi, Any): ").strip()
    subjects = input("Enter subject combination (comma-separated): ").strip()
    category = input("Enter preferred category (C1, C2, C3, C4, or Any) [Default: Any]: ").strip() or "Any"

    if not pathway or not county:
        print("[!] Pathway and County are required.")
        return

    print("\n[AI Processing] Analyzing school compatibility and ranking placements...")
    try:
        results = generate_school_recommendations(pathway, county, subjects, category)
        print("\n--- RECOMMENDED SCHOOLS ---")
        print(json.dumps(results, indent=2))

        # Save to session log
        session_log.append({
            "timestamp": datetime.now().isoformat(),
            "option": "school_matching",
            "inputs": {"pathway": pathway, "county": county, "subjects": subjects, "category": category},
            "output": results
        })
    except Exception as e:
        print(f"[!] Error generating school recommendations: {e}")


def option_2_career_opportunity_insights(session_log: list):
    """Option 2: Career Opportunity & Industry Insights"""
    print("\n" + "=" * 60)
    print(" Option 2: Career Opportunity & Industry Insights")
    print("=" * 60)

    pathway = input("Enter the CBC pathway to explore career options for: ").strip()
    subjects = input("Enter relevant subject interests (optional): ").strip()

    if not pathway:
        print("[!] Pathway cannot be empty.")
        return

    print("\n[AI Processing] Generating professional career roadmap and industry analysis...")
    try:
        report_md = generate_career_roadmap(pathway, subjects)
        print("\n" + report_md + "\n")

        # Save to session log
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
    print("1. Senior School Matching & Pathway Alignment")
    print("2. Career Opportunity & Industry Insights")
    print("3. Exit Program")


def main():
    session_log = []

    while True:
        display_menu()
        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            option_1_senior_school_matching(session_log)
        elif choice == "2":
            option_2_career_opportunity_insights(session_log)
        elif choice == "3":
            option_3_exit_program(session_log)
        else:
            print("\n[!] Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
    