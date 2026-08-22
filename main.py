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


# =====================================================================
# CONFIGURATION
# =====================================================================

# Load environment variables from the local .env file
load_dotenv()

# Check that the API key exists before initializing the client.
if not os.getenv("OPENAI_API_KEY"):
    print("[!] OPENAI_API_KEY was not found.")
    print("[!] Create a .env file and add:")
    print("    OPENAI_API_KEY=your_api_key_here")
    sys.exit(1)

# Initialize OpenAI client.
# It automatically looks for the OPENAI_API_KEY environment variable.
client = OpenAI()


# =====================================================================
# API CALL #1: School Selection & Compatibility
# R-T-C-C-O Framework
# =====================================================================

def generate_school_recommendations(
    pathway: str,
    county: str,
    subjects: str,
    category: str = "Any",
    accommodation: str = "Any"
) -> dict:
    """
    R-T-C-C-O Implementation for API Call #1:
    School Selection & Compatibility Analysis

    Role:
        Expert Kenyan CBC educational advisor.

    Task:
        Analyze inputs and evaluate institutional fit.

    Context:
        Transitioning Grade 9 students needing data-driven
        recommendations.

    Constraints:
        Reference realistic Kenyan regions/schools and avoid
        presenting unverified information as fact.

    Output:
        Structured JSON object.
    """

    system_prompt = (
        "Role: You are an expert Kenyan CBC educational advisor.\n"

        "Task: Analyze student inputs including preferred pathway, "
        "location/county, subject combinations, school category and "
        "accommodation preference, then evaluate institutional fit "
        "against senior secondary schools.\n"

        "Context: Transitioning Grade 9 students needing realistic "
        "school placement guidance.\n"

        "Constraints: Reference realistic Kenyan regions/schools, "
        "follow the supplied CBC category framework, and do not "
        "invent unverified school information, fees, admissions or "
        "availability.\n"

        "Output: Return strictly a valid JSON object matching "
        "this schema:\n"

        "{\n"
        '  "recommended_schools": [\n'
        "    {\n"
        '      "school_name": "string",\n'
        '      "category": "C1/C2/C3/C4",\n'
        '      "county": "string",\n'
        '      "matching_rationale": "string",\n'
        '      "recommended_cbc_electives": '
        '["subject1", "subject2", "subject3"]\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"""
Student Profile:

- Target CBC Pathway: {pathway}
- Preferred County / Location: {county}
- Subject Combination: {subjects}
- Preferred Category: {category}
- Accommodation: {accommodation}

Generate suitable senior secondary school recommendations
matching this profile.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "API Call #1 returned an empty response."
        )

    try:
        return json.loads(content)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"API Call #1 returned invalid JSON: {e}"
        )


# =====================================================================
# API CALL #2: Career Opportunity & Industry Insights
# R-T-C-C-O Framework
# =====================================================================

def generate_career_roadmap(
    pathway: str,
    subjects: str,
    school_matching_result: dict
) -> str:
    """
    R-T-C-C-O Implementation for API Call #2:
    Career Opportunity & Industry Advisory

    IMPORTANT:
        This API call uses the actual structured result produced
        by API Call #1.

    Role:
        Senior vocational/career guidance counselor.

    Task:
        Generate career and industry analysis based on the
        selected pathway, subjects and school-matching result.

    Context:
        Grade 9 CBC students evaluating long-term tertiary and
        professional trajectories.

    Constraints:
        Provide useful Kenyan context without inventing specific
        admission, fee or employment guarantees.

    Output:
        Well-formatted Markdown report.
    """

    # Convert the API #1 result into readable JSON so it can be
    # supplied directly to API #2.
    school_result_json = json.dumps(
        school_matching_result,
        indent=2,
        ensure_ascii=False
    )

    system_prompt = (
        "Role: You are a senior vocational and career guidance "
        "counselor specializing in Kenya's CBC system.\n"

        "Task: Generate an in-depth career and industry analysis "
        "based on the student's selected CBC pathway, subjects and "
        "the school-matching result generated by API Call #1.\n"

        "Context: Grade 9 CBC transitioning students evaluating "
        "long-term tertiary and professional trajectories.\n"

        "Constraints: Use the supplied school-matching result. "
        "Do not ignore API Call #1. Do not invent specific "
        "admission requirements, fees, employment guarantees or "
        "school availability.\n"

        "Output: Provide a professional Markdown report with "
        "clear headings, bullet points and tables."
    )

    user_prompt = f"""
Student Profile:

Selected CBC Pathway:
{pathway}

Related Subject Choices:
{subjects if subjects else "Not specified"}

School-Matching Result From API Call #1:
{school_result_json}

Using the information above, generate a professional career
and industry roadmap including:

1. Executive Pathway Summary
2. Connection to the School-Matching Result
3. High-Demand Career Paths in Kenya and Regionally
4. Relevant Skills
5. University and TVET Progression Routes
6. Emerging Industry Opportunities
7. Practical Next Steps
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.4
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "API Call #2 returned an empty response."
        )

    return content


# =====================================================================
# SYSTEM MENU HANDLERS
# =====================================================================

def option_1_senior_school_matching(session_log: list):
    """
    Option 1:
    Senior School Matching & Pathway Alignment.
    """

    print("\n" + "=" * 60)
    print(" Option 1: Senior School Matching & Pathway Alignment")
    print("=" * 60)

    pathway = input(
        "Enter preferred CBC pathway "
        "(e.g. STEM, Arts & Sports, Social Sciences): "
    ).strip()

    county = input(
        "Enter preferred location/county "
        "(e.g. Siaya, Nairobi, Any): "
    ).strip()

    subjects = input(
        "Enter subject combination (comma-separated): "
    ).strip()

    category = input(
        "Enter preferred category "
        "(C1, C2, C3, C4, or Any) [Default: Any]: "
    ).strip() or "Any"

    accommodation = input(
        "Enter accommodation preference "
        "(Boarding, Day, Any) [Default: Any]: "
    ).strip() or "Any"

    if not pathway:
        print("[!] Pathway is required.")
        return

    if not county:
        print("[!] County/location is required.")
        return

    print(
        "\n[AI Processing] "
        "Analyzing school compatibility and ranking placements..."
    )

    try:

        results = generate_school_recommendations(
            pathway=pathway,
            county=county,
            subjects=subjects,
            category=category,
            accommodation=accommodation
        )

        print("\n--- RECOMMENDED SCHOOLS ---")

        print(
            json.dumps(
                results,
                indent=2,
                ensure_ascii=False
            )
        )

        # Save API Call #1 result to the session.
        # API Call #2 will use this result.
        session_log.append({
            "timestamp": datetime.now().isoformat(),
            "option": "school_matching",
            "inputs": {
                "pathway": pathway,
                "county": county,
                "subjects": subjects,
                "category": category,
                "accommodation": accommodation
            },
            "output": results
        })

        print(
            "\n[✓] School-matching result saved."
        )

        print(
            "[✓] You can now select Option 2 to generate "
            "career insights from this result."
        )

    except Exception as e:

        print(
            f"[!] Error generating school recommendations: {e}"
        )


def option_2_career_opportunity_insights(session_log: list):
    """
    Option 2:
    Career Opportunity & Industry Insights.

    API Call #2 requires a successful API Call #1 result.
    """

    print("\n" + "=" * 60)
    print(" Option 2: Career Opportunity & Industry Insights")
    print("=" * 60)

    # Find successful school-matching results.
    school_matching_entries = [
        entry
        for entry in session_log
        if entry.get("option") == "school_matching"
    ]

    # Do not allow API Call #2 to run without API Call #1.
    if not school_matching_entries:

        print(
            "\n[!] Please complete Option 1 first."
        )

        print(
            "[!] Career insights require the school-matching "
            "result from API Call #1."
        )

        return

    # Use the most recent school-matching result.
    latest_school_match = school_matching_entries[-1]

    school_matching_result = latest_school_match["output"]

    previous_inputs = latest_school_match["inputs"]

    pathway = previous_inputs.get(
        "pathway",
        ""
    )

    subjects = previous_inputs.get(
        "subjects",
        ""
    )

    print(
        "\n[✓] Using the school-matching result "
        "from API Call #1."
    )

    print(
        f"[✓] Pathway: {pathway}"
    )

    print(
        f"[✓] Subjects: "
        f"{subjects if subjects else 'Not specified'}"
    )

    print(
        "\n[AI Processing] "
        "Generating professional career roadmap "
        "using the school-matching result..."
    )

    try:

        report_md = generate_career_roadmap(
            pathway=pathway,
            subjects=subjects,
            school_matching_result=school_matching_result
        )

        print(
            "\n" + report_md + "\n"
        )

        # Save API Call #2 result and the API #1 result
        # that was used to generate it.
        session_log.append({
            "timestamp": datetime.now().isoformat(),
            "option": "career_insights",
            "inputs": {
                "pathway": pathway,
                "subjects": subjects
            },
            "input_from_api_call_1": school_matching_result,
            "output": report_md
        })

        print(
            "[✓] Career advisory result saved."
        )

    except Exception as e:

        print(
            f"[!] Error generating career insights: {e}"
        )


def option_3_exit_program(session_log: list):
    """
    Option 3:
    Exit Program and save session artifacts.
    """

    print("\n" + "=" * 60)
    print(" Option 3: Exiting Program")
    print("=" * 60)

    if not session_log:

        print(
            "[!] No session data was generated."
        )

        print(
            "Goodbye!"
        )

        sys.exit(0)

    log_filename = "session_log.json"

    try:

        with open(
            log_filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                session_log,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(
            f"[✓] Session artifacts successfully logged "
            f"to '{log_filename}'."
        )

        print(
            "[✓] Goodbye!"
        )

    except Exception as e:

        print(
            f"[!] Error saving session log: {e}"
        )

    sys.exit(0)


# =====================================================================
# MAIN RUNNER
# =====================================================================

if __name__ == "__main__":

    session_log = []

    while True:

        print("\n" + "═" * 60)
        print(
            " KENYAN CBC SENIOR SCHOOL & CAREER ADVISORY TOOL"
        )
        print("═" * 60)

        print(
            "1. Senior School Matching & Pathway Alignment"
        )

        print(
            "2. Career Opportunity & Industry Insights"
        )

        print(
            "3. Exit Program"
        )

        print("═" * 60)

        choice = input(
            "Select an option (1-3): "
        ).strip()

        if choice == "1":

            option_1_senior_school_matching(
                session_log
            )

        elif choice == "2":

            option_2_career_opportunity_insights(
                session_log
            )

        elif choice == "3":

            option_3_exit_program(
                session_log
            )

        else:

            print(
                "[!] Invalid option. "
                "Please enter 1, 2, or 3."
            )
