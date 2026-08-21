"""Simple verification for Member 4's export module."""

from pathlib import Path
from tempfile import TemporaryDirectory

from export import export_session


def test_export_session_creates_both_files() -> None:
    school_result = {
        "learner_profile": {"pathway": "STEM"},
        "pathway_alignment": "Good alignment.",
        "regional_considerations": ["Confirm local school availability."],
        "recommended_school_characteristics": ["Appropriate facilities."],
        "subject_fit": "Suitable combination.",
        "next_steps": ["Discuss options with a guardian."],
        "verification_notes": ["Use official sources."],
    }
    with TemporaryDirectory() as folder:
        saved = export_session(school_result, "## Career Clusters\nEngineering", Path(folder))
        assert saved["markdown"].exists()
        assert saved["json"].exists()
        assert "Career Clusters" in saved["markdown"].read_text(encoding="utf-8")


if __name__ == "__main__":
    test_export_session_creates_both_files()
    print("Export test passed.")
