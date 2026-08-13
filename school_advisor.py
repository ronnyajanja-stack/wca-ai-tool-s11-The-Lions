import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("Missing or unconfigured OPENAI_API_KEY in .env file.")
    return OpenAI(api_key=api_key)


def load_real_secondary_schools(
    location_query: str, target_category: str = "Any"
) -> list:
    """Retrieves verified school names and location data strictly from local secondary_schools.json (RAG)."""
    db_file = "secondary_schools.json"
    if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
        print(
            f"[Error] Database file '{db_file}' is missing or empty. Run 'python parse_excel.py' first."
        )
        return []

    try:
        with open(db_file, "r", encoding="utf-8") as f:
            all_schools = json.load(f)
    except json.JSONDecodeError:
        print(
            f"[Error] '{db_file}' contains invalid JSON. Re-run 'python parse_excel.py'."
        )
        return []

    loc = location_query.strip().lower()
    target_cat = target_category.strip().upper()

    # Filter local database for location matches
    location_matches = [
        s
        for s in all_schools
        if loc in s.get("district", "").lower()
        or loc in s.get("constituency", "").lower()
        or loc in s.get("location", "").lower()
        or loc in s.get("sub_location", "").lower()
        or loc in s.get("province", "").lower()
    ]

    # Apply strict category filtering if specified (e.g. C1, C2, C3, C4)
    if target_cat != "ANY":
        category_filtered = [
            s
            for s in location_matches
            if s.get("category", "").upper() == target_cat
        ]
        # Use category-filtered results if found; otherwise fallback to location matches
        candidates = (
            category_filtered if category_filtered else location_matches
        )
    else:
        candidates = location_matches

    # Format list for prompt context
    matched = [
        {
            "school_name": s.get("school_name", s.get("Name", "")),
            "province": s.get("province", s.get("PROVINCE", "")),
            "district": s.get("district", s.get("DISTRICT", "")),
            "constituency": s.get("constituency", s.get("COSTITUENCY", "")),
            "category": s.get("category", s.get("CATEGORY", "C3")),
            "status": s.get("status", s.get("Status", "")),
            "sponsor": s.get("sponsor", s.get("Sponsor", "")),
        }
        for s in candidates
    ]

    return matched


def analyze_school_compatibility(
    pathway: str,
    location: str,
    subjects: str,
    category: str,
    accommodation: str,
    school_type: str,
) -> dict:
    try:
        # 1. RAG STEP: Pull real school entities matching location and target category from local dataset
        candidate_schools = load_real_secondary_schools(location, category)

        if not candidate_schools:
            return {
                "error": f"No real secondary schools found in local database for location '{location}'."
            }

        client = get_openai_client()

        # 2. ENRICHMENT STEP: Calibrated system prompt for accurate placement and matching
        system_prompt = (
            "Role: Expert Kenyan CBC & Senior School Educational Placement Advisor.\n"
            "STRICT RULES:\n"
            "1. NO HALLUCINATED NAMES: You MUST ONLY select school names that exist in the provided JSON candidate list. DO NOT invent non-existent schools.\n"
            "2. CATEGORY MATCHING & ACCURACY:\n"
            "   - Prioritize schools matching the requested target category preference.\n"
            "   - Maintain accurate MoE placement codes in the response (C1=National, C2=Extra-County, C3=County, C4=Private/Sub-County).\n"
            "   - If a school's category differs from the user preference, explain the reason clearly in the matching_rationale.\n"
            "3. CBC SUBJECT COMBINATIONS: Recommend 3 valid elective CBC subject choices matching the target pathway.\n"
            "4. OUTPUT FORMAT: Respond STRICTLY with a valid JSON object."
        )

        user_prompt = f"""
        Student Profile Criteria:
        - Target Pathway: {pathway}
        - Desired Location: {location}
        - Preferred Subjects: {subjects}
        - Target Category Preference: {category} (C1=National, C2=Extra-County, C3=County, C4=Private/Sub-County)
        - Accommodation: {accommodation}
        - School Type / Gender: {school_type}

        Verified Schools Retrieved from Local RAG Database:
        {json.dumps(candidate_schools[:40], indent=2)}

        Task:
        Select the best 5 matching schools from the candidate list above.
        For each selected school, return:
        1. school_name (from candidate list)
        2. district & constituency (from candidate list)
        3. category (Accurate C1, C2, C3, or C4 tier)
        4. recommended_subject_combinations (3 elective CBC subjects aligned with {pathway})
        5. rank (1 to 5)
        6. matching_rationale (Why this school fits the pathway, category, and subject combination)
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,  # Deterministic output
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("--- Senior School Career & Placement Advisor ---\n")

    pathway = input(
        "Preferred pathway (STEM, Social Sciences, Arts & Sports): "
    ).strip()
    location = input(
        "Location/County/District (e.g., Siaya, Nakuru, Nairobi): "
    ).strip()
    school_type = input("School type (Boys, Girls, or Mixed): ").strip()
    subjects = input(
        "Preferred subject choices (e.g., Physics, Chemistry, Computer Studies): "
    ).strip()
    category = input(
        "Preferred category (C1, C2, C3, C4, or Any): "
    ).strip()
    accommodation = input("Day or Boarding? (Day/Boarding/Any): ").strip()

    print(
        f"\n[1/2] Retrieving real schools from local database for '{location}' (Target Tier: {category})..."
    )
    print(
        f"[2/2] Enriching with C1-C4 tiers, CBC subject combinations, and rankings...\n"
    )

    result = analyze_school_compatibility(
        pathway=pathway,
        location=location,
        subjects=subjects,
        category=category,
        accommodation=accommodation,
        school_type=school_type,
    )

    print(json.dumps(result, indent=2))