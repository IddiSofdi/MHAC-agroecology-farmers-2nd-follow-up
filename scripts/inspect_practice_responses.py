
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"

QUESTIONS = {
    "Select_the_list_of_crops_plant": "Crops planted",
    "Which_planting_techn_cticing_on_your_farm": "Planting technologies",
    "Which_soil_and_water_cticing_on_your_farm": "Soil and water conservation",
    "Which_soil_health_pr_cticing_on_your_farm": "Soil health practices",
    "Which_pest_and_disea_cticing_on_your_farm": "Pest and disease control",
    "Which_integrated_pest_manageme": "Integrated pest management"
}


def inspect_responses():

    files = list(CLEANED_DIR.glob("mhac_agroecology_cleaned_*.csv"))

    if not files:
        print("No cleaned dataset found.")
        return

    latest_file = max(files, key=lambda f: f.stat().st_mtime)

    df = pd.read_csv(latest_file, dtype=str)

    print("\n================================")
    print("ACTUAL FARMER PRACTICE RESPONSES")
    print("================================")
    print("Dataset:", latest_file.name)

    for field, question in QUESTIONS.items():

        print("\n\n" + "=" * 50)
        print(question)
        print("=" * 50)

        if field not in df.columns:
            print("Field not found.")
            continue

        responses = df[field].dropna().str.strip()
        responses = responses[responses != ""]

        print("Farmers with responses:", len(responses))
        print("\nMost common raw responses:")

        for answer, count in responses.value_counts().head(15).items():
            print(f"{count:>4} : {answer}")

    print("\n================================")
    print("RESPONSE INSPECTION COMPLETE")
    print("================================")


if __name__ == "__main__":
 inspect_responses()
