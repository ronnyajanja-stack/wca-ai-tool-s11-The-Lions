import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from local .env
load_dotenv()

def get_openai_client() -> OpenAI:
    """Retrieves and validates the OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("Missing or unconfigured OPENAI_API_KEY in .env file.")
    return OpenAI(api_key=api_key)

def analyze_school_compatibility(pathway: str, location: str, subjects: str) -> dict:
    """
    Executes API Call #1 using the R-T-C-C-O Framework to analyze school compatibility.
    Returns structured JSON data.
    """
    try:
        client = get_openai_client()

        # R-T-C-C-O Framework System Prompt
        system_prompt = (
            "Role: Expert Kenyan CBC educational advisor.\n"
            "Task: Analyze student inputs (pathway, location/county, subject combinations) "
            "and evaluate institutional fit.\n"
            "Context: Grade 9 students needing data-driven recommendations for transitioning to Senior School.\n"
            "Constraints: Reference realistic Kenyan regions, strictly adhere to CBC guidelines, "
            "and ignore unverified data.\n"
            "Output Format: Respond STRICTLY with a valid JSON object."
        )

        user_prompt = f"""
        Evaluate senior school options for this student profile:
        - Preferred Pathway: {pathway}
        - Preferred Location/County: {location}
        - Preferred Subject Combinations: {subjects}

        Provide 3 recommended schools, their matching rationale, and key facility features.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except json.JSONDecodeError as e:
        print(f"[Error] Failed to parse API response into JSON: {e}")
        return {"error": "Invalid JSON format returned from API."}
    except ValueError as e:
        print(f"[Configuration Error] {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[API Error] An error occurred during processing: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Test execution
    print("Testing API Call #1...")
    result = analyze_school_compatibility(
        pathway="STEM",
        location="Nairobi",
        subjects="Physics, Chemistry, Computer Studies"
    )
    print(json.dumps(result, indent=2))