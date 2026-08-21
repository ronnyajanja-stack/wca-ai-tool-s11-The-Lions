# CBC Senior School Selection & Career Advisory Tool

A Python command-line tool that helps Kenyan Grade 9 learners and their families explore CBC senior-school pathways, school-fit considerations and possible career directions.

## What the tool does

1. **Senior School Matching & Pathway Alignment** - collects the learner's preferred pathway, county/location and subject combinations, then returns structured school-fit guidance.
2. **Career Opportunity & Industry Insights** - uses the selected pathway to generate a readable career roadmap, including skills, training routes and practical next steps.
3. **Safe exit and export** - saves a completed advisory session locally as Markdown and JSON.

The advice is educational guidance only. Users must confirm school admissions, availability, fees and programme details with official sources.

## Requirements

- Python 3.10 or later
- An API key stored locally in `.env`
- Packages listed in `requirements.txt`

## Setup

```bash
git clone <your-repository-url>
cd <repository-folder>
python -m venv venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`, then add the API key locally. Never commit `.env`.

## Run the tool

```bash
python main.py
```

Choose option 1 to complete school matching before choosing option 2 for career insights. Completed sessions are saved in `exports/`.

## Project structure

```text
main.py          # CLI menu and application flow
prompts.py       # R-T-C-C-O prompt templates
ai_client.py     # AI API call and network error handling
parsers.py       # Validates structured school-matching JSON
exporter.py      # Member 4: local Markdown and JSON export
exports/         # Generated reports; ignored by Git
```

## Security and responsible use

- Keep API keys in `.env`, never in source code or GitHub.
- Do not place a learner's full name, phone number or other sensitive identifiers in prompts or exports.
- Treat generated guidance as a starting point, not an official admission or employment decision.
- Verify institution and labour-market information using official sources.

## Team responsibilities

| Member | Responsibility |
|---|---|
| Member 1 | Environment setup, `.gitignore`, exception handling, API Call #1 |
| Member 2 | API Call #2, R-T-C-C-O prompts and career engine |
| Member 3 | CLI menu, validation, error management and pipeline |
| Member 4 | File export, code comments, README and final project checks |

## Member 4 final checklist

- [ ] `exporter.py` writes Markdown and JSON reports to `exports/`
- [ ] `README.md` has been updated with the final GitHub URL and run instructions
- [ ] `.env`, `venv/`, `__pycache__/` and `exports/` are ignored by Git
- [ ] No API keys or real learner data appear in commits
- [ ] The group has tested export after both advisory stages
- [ ] Run `git status`, commit the final changes and push from the repository folder
