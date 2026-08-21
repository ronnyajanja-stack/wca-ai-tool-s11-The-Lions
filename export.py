"""Export utilities for the CBC Senior School Selection & Career Advisory Tool.

This module writes completed advisory sessions to local Markdown and JSON files.
Exports are stored outside the source code and contain no API keys.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_EXPORT_DIRECTORY = Path("exports")


def _safe_filename_part(value: str) -> str:
    """Return a filename-safe label without exposing personal information."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned.strip("_") or "advice"


def _as_text(value: Any) -> str:
    """Format lists and dictionaries neatly for the readable Markdown export."""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value) or "Not provided"
    if isinstance(value, dict):
        return "\n".join(f"- **{key.replace('_', ' ').title()}:** {item}" for key, item in value.items())
    return str(value) if value not in (None, "") else "Not provided"


def build_markdown_report(school_result: dict[str, Any], career_report: str) -> str:
    """Build a human-readable report from the two stages of the tool."""
    sections = [
        "# CBC Senior School Selection & Career Advisory Report",
        f"Generated: {datetime.now():%d %B %Y, %H:%M}",
        "",
        "## School Matching & Pathway Alignment",
    ]

    # The first API call is expected to produce these JSON keys. Missing keys are
    # shown as 'Not provided' so exporting never crashes after a partial response.
    labels = {
        "learner_profile": "Learner Profile",
        "pathway_alignment": "Pathway Alignment",
        "regional_considerations": "Regional Considerations",
        "recommended_school_characteristics": "Recommended School Characteristics",
        "subject_fit": "Subject Fit",
        "next_steps": "Next Steps",
        "verification_notes": "Verification Notes",
    }
    for key, label in labels.items():
        sections.extend([f"### {label}", _as_text(school_result.get(key)), ""])

    sections.extend(["## Career Opportunity & Industry Insights", career_report.strip() or "Not provided", ""])
    return "\n".join(sections)


def export_session(
    school_result: dict[str, Any],
    career_report: str,
    export_directory: Path | str = DEFAULT_EXPORT_DIRECTORY,
) -> dict[str, Path]:
    """Save the completed session as both Markdown and JSON.

    Returns the saved paths. The caller may show these paths to the user.
    No exception is suppressed: ``main.py`` should catch errors and give the user
    a clear retry message.
    """
    directory = Path(export_directory)
    directory.mkdir(parents=True, exist_ok=True)

    learner = school_result.get("learner_profile", {})
    pathway = learner.get("pathway", "cbc_advice") if isinstance(learner, dict) else "cbc_advice"
    stem = f"{datetime.now():%Y%m%d_%H%M%S}_{_safe_filename_part(str(pathway))}"

    markdown_path = directory / f"{stem}.md"
    json_path = directory / f"{stem}.json"
    payload = {"school_matching": school_result, "career_insights": career_report}

    # UTF-8 preserves Kenyan place names and makes files portable across systems.
    markdown_path.write_text(build_markdown_report(school_result, career_report), encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}
