import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mapping standard category codes to common database naming conventions
CATEGORY_MAP = {
    "c1": ["national", "c1", "tier 1"],
    "c2": ["extra-county", "extra county", "c2", "tier 2"],
    "c3": ["county", "c3", "tier 3"],
    "c4": ["sub-county", "sub county", "private", "c4", "tier 4"]
}


def load_database(filepath="secondary_schools.json"):
    """Loads the secondary schools JSON database."""
    if not os.path.exists(filepath):
        print(f"Error: Database file '{filepath}' not found.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON database.")
            return []


def retrieve_candidates(schools, location, school_type, category, accommodation, max_candidates=40):
    """
    RAG candidate retrieval with category-strict priority.
    """
    loc_clean = location.strip().lower()
    type_clean = school_type.strip().lower()
    cat_clean = category.strip().lower()
    acc_clean = accommodation.strip().lower()

    valid_cat_aliases = CATEGORY_MAP.get(cat_clean, [cat_clean])

    def matches_category(s):
        s_cat = str(s.get("category", "")).strip().lower()
        return any(alias in s_cat for alias in valid_cat_aliases) if cat_clean != "any" else True

    def matches_gender(s):
        s_gender = str(s.get("gender", s.get("type", ""))).strip().lower()
        if type_clean in ["any", "all"]:
            return True
        if type_clean in ["girls", "girl"]:
            return "girl" in s_gender or "female" in s_gender
        if type_clean in ["boys", "boy"]:
            return "boy" in s_gender or "male" in s_gender
        if type_clean in ["mixed", "co-ed"]:
            return "mixed" in s_gender or "co-ed" in s_gender
        return type_clean in s_gender

    def matches_location(s):
        s_loc = str(s.get("county", s.get("location", ""))).strip().lower()
        return loc_clean in s_loc if loc_clean not in ["any", "all"] else True

    def matches_accommodation(s):
        s_acc = str(s.get("accommodation", s.get("boarding_status", ""))).strip().lower()
        if acc_clean in ["any", "all"]:
            return True
        return acc_clean in s_acc

    # Stage 1: Exact matches (Category + Gender + Location + Accommodation)
    stage1_candidates = [
        s for s in schools 
        if matches_category(s) and matches_gender(s) and matches_location(s) and matches_accommodation(s)
    ]

    if stage1_candidates:
        return stage1_candidates[:max_candidates]

    # Stage 2: If C1 (National) has no local match in that county, search C1 nationwide
    if cat_clean == "c1":
        print(f"[*] Note: No exact C1 school found in '{location}'. Expanding C1 search nationwide...")
        stage2_candidates = [
            s for s in schools 
            if matches_category(s) and matches_gender(s) and matches_accommodation(s)
        ]
        if stage2_candidates:
            return stage2_candidates[:max_candidates]

    # Stage 3: Relax accommodation filter if still empty
    stage3_candidates = [
        s for s in schools 
        if matches_category(s) and matches_gender(s) and matches_location(s)
    ]
    if stage3_candidates:
        return stage3_candidates[:max_candidates]

    # Stage 4: Fallback to all schools matching gender and location
    print(f"[*] Note: Strict category '{category.upper()}' had zero matches. Returning closest county matches...")
    fallback_candidates = [
        s for s in schools 
        if matches_gender(s) and matches_location(s)
    ]
    return fallback_candidates[:max_candidates]


def analyze_school_compatibility(pathway, location, subjects, category, accommodation, school_type, candidate_schools):
    """Sends retrieved RAG candidates to OpenAI for ranking and CBC subject enrichment."""
    system_prompt = (
        "You are an expert secondary school advisor specializing in Kenya's Competency-Based Curriculum (CBC) "
        "and Senior School Placement (C1=National, C2=Extra-County, C3=County, C4=Sub-County/Private).\n\n"
        "RULES:\n"
        "1. STRICT CATEGORY COMPLIANCE: Prioritize schools that strictly match the requested target tier.\n"
        "2. Do NOT invent schools. Select only from the candidate list provided in the prompt.\n"
        "3. CBC SUBJECT COMBINATIONS: Recommend 3 valid elective CBC subject choices matching the target pathway.\n"
        "4. OUTPUT FORMAT: Respond STRICTLY with a valid JSON object matching this schema:\n"
        "{\n"
        '  "recommended_schools": [\n'
        "    {\n"
        '      "school_name": "string",\n'
        '      "category": "C1/C2/C3/C4",\n'
        '      "county": "string",\n'
        '      "gender": "string",\n'
        '      "boarding_status": "string",\n'
        '      "matching_rationale": "string",\n'
        '      "recommended_cbc_electives": ["subject1", "subject2", "subject3"]\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"""Student Profile Criteria:
- Target Pathway: {pathway}
- Desired Location: {location}
- Preferred Subjects: {subjects}
- Target Category Preference: {category} (C1=National, C2=Extra-County, C3=County, C4=Private/Sub-County)
- Accommodation: {accommodation}
- School Type / Gender: {school_type}

Verified Schools Retrieved from Local RAG Database:
{json.dumps(candidate_schools[:40], indent=2)}

Task:
Select the top 5 best matching schools from the candidate list above.
Return the output strictly in JSON format.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"OpenAI API request failed: {str(e)}"})


def main():
    print("=" * 60)
    print("   KENYAN CBC SENIOR SECONDARY SCHOOL ADVISOR (RAG)   ")
    print("=" * 60)

    schools_db = load_database("secondary_schools.json")
    if not schools_db:
        print("Please check that secondary_schools.json is present and not empty.")
        return

    pathway = input("Target Pathway (e.g., STEM, Arts & Sports, Social Sciences): ").strip() or "STEM"
    location = input("Preferred County / Location (e.g., Siaya, Nairobi, Any): ").strip() or "Siaya"
    school_type = input("School type (Boys, Girls, or Mixed): ").strip() or "Girls"
    subjects = input("Preferred subject choices (e.g., Mathematics, Physics, Chemistry): ").strip() or "Mathematics, Physics, Chemistry"
    category = input("Preferred category (C1, C2, C3, C4, or Any): ").strip().lower() or "c1"
    accommodation = input("Day or Boarding? (Day/Boarding/Any): ").strip() or "Boarding"

    print(f"\n[1/2] Retrieving real schools from local database for '{location}' (Target Tier: {category.upper()})...")
    candidates = retrieve_candidates(schools_db, location, school_type, category, accommodation)

    if not candidates:
        print(f"No candidate schools matched your criteria in the database.")
        return

    print(f"      Found {len(candidates)} candidate school(s).")
    print(f"[2/2] Enriching with {category.upper()} tiers, CBC subject combinations, and rankings...\n")

    result = analyze_school_compatibility(pathway, location, subjects, category, accommodation, school_type, candidates)
    
    # Pretty print the final JSON
    try:
        parsed_json = json.loads(result)
        print(json.dumps(parsed_json, indent=2))
    except json.JSONDecodeError:
        print(result)


if __name__ == "__main__":
    main()