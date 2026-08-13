"""
CBC Senior School Selection & Career Advisory Tool
Section 2: System Menu Structure & User Choices
"""

import sys


def option_1_senior_school_matching():
    """
    Option 1: Senior School Matching & Pathway Alignment
    Evaluates student preferences (Preferred Pathway, Location/County,
    and Subject Combinations) to recommend matching institutions.
    """
    print("\n--- Senior School Matching & Pathway Alignment ---")

    pathway = input("Enter your preferred CBC pathway (e.g. STEM, Arts & Sports Science, Social Sciences): ")
    county = input("Enter your preferred location/county: ")
    subjects = input("Enter your subject combination (comma-separated): ")

    # TODO: Build R-T-C-C-O prompt using pathway, county, subjects
    # TODO: Send prompt to AI API (first of the two connected calls)
    # TODO: Parse and display recommended institutions
    # TODO: Optionally save results to a JSON file

    print("\n[Placeholder] Matching logic and AI API call go here.")
    print(f"Pathway: {pathway} | County: {county} | Subjects: {subjects}")


def option_2_career_opportunity_insights():
    """
    Option 2: Career Opportunity & Industry Insights
    Takes the selected CBC pathway and generates an in-depth
    professional roadmap.
    """
    print("\n--- Career Opportunity & Industry Insights ---")

    pathway = input("Enter the CBC pathway to explore career options for: ")

    # TODO: Build R-T-C-C-O prompt using the pathway
    # TODO: Send prompt to AI API (second of the two connected calls)
    # TODO: Display / save the generated career roadmap

    print("\n[Placeholder] Career roadmap generation and AI API call go here.")
    print(f"Pathway selected: {pathway}")


def option_3_exit_program(session_log=None):
    """
    Option 3: Exit Program
    Safely terminates the session and ensures all session artifacts are logged.
    """
    print("\n--- Exiting Program ---")

    # TODO: Write session_log (JSON) to a file before exiting
    # TODO: Handle any cleanup / error handling here

    print("Session artifacts logged. Goodbye!")
    sys.exit(0)


def display_menu():
    print("\n" + "=" * 55)
    print(" CBC SENIOR SCHOOL SELECTION & CAREER ADVISORY TOOL")
    print("=" * 55)
    print("1. Senior School Matching & Pathway Alignment")
    print("2. Career Opportunity & Industry Insights")
    print("3. Exit Program")


def main():
    session_log = []  # Collects data/results during the session for logging on exit

    while True:
        display_menu()
        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            option_1_senior_school_matching()
        elif choice == "2":
            option_2_career_opportunity_insights()
        elif choice == "3":
            option_3_exit_program(session_log)
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()



