
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
DATA_DIR = PROJECT_ROOT / "reference_data"

QUESTIONS = {
    "Select_the_list_of_crops_plant": {
        "category": "Crops planted",
        "list_name": "yw8lr28"
    },
    "Which_planting_techn_cticing_on_your_farm": {
        "category": "Planting technologies",
        "list_name": "hv0kt31"
    },
    "Which_soil_and_water_cticing_on_your_farm": {
        "category": "Soil and water conservation",
        "list_name": "ke6oy89"
    },
    "Which_soil_health_pr_cticing_on_your_farm": {
        "category": "Soil health practices",
        "list_name": "vp6qr49"
    },
    "Which_pest_and_disea_cticing_on_your_farm": {
        "category": "Pest and disease control",
        "list_name": "kv0rn37"
    },
    "Which_integrated_pest_manageme": {
        "category": "Integrated pest management",
        "list_name": "ln4si39"
    },
    "Other_Sustainable_Farming_Practices": {
        "category": "Other sustainable farming practices",
        "list_name": "ck6fu99"
    }
}


def main():

    raw_files = list(CLEANED_DIR.glob("mhac_agroecology_cleaned_*.csv"))

    if not raw_files:
        print("No cleaned dataset found.")
        return

    data_file = max(raw_files, key=lambda f: f.stat().st_mtime)

    choice_file = DATA_DIR / "choice_dictionary.csv"

    if not choice_file.exists():
        print("Choice dictionary not found.")
        return

    df = pd.read_csv(data_file, dtype=str)
    choices = pd.read_csv(choice_file, dtype=str).fillna("")

    results = []

    print("\n================================")
    print("MHAC PRACTICE ADOPTION INDICATORS")
    print("================================")
    print("Dataset:", data_file.name)

    for field, details in QUESTIONS.items():

        category = details["category"]
        list_name = details["list_name"]

        if field not in df.columns:
            print(f"\nWARNING: Field not found: {field}")
            continue

        responses = df[field].fillna("").str.strip()

        answered = responses[responses != ""]
        answered_count = len(answered)

        selected_codes = []

        for response in answered:
            selected_codes.extend(set(response.split()))

        counts = pd.Series(selected_codes).value_counts()

        category_choices = choices[
            choices["list_name"] == list_name
        ]

        known_codes = set(category_choices["choice_name"])

        for _, option in category_choices.iterrows():

            code = option["choice_name"]
            label = option["choice_label"].strip()

            count = int(counts.get(code, 0))

            if not label or label.lower() == "nan":
                label = f"UNLABELLED OPTION ({code})"
                status = "REVIEW LABEL"
            else:
                status = "Label available"

            percentage = (
                count / answered_count * 100
                if answered_count else 0
            )

            results.append({
                "category": category,
                "field_name": field,
                "choice_code": code,
                "practice_or_crop": label,
                "respondents_selected": count,
                "respondents_answered": answered_count,
                "percentage_of_respondents_answered": round(percentage, 1),
                "label_status": status
            })

        unknown_codes = set(counts.index) - known_codes

        for code in sorted(unknown_codes):

            count = int(counts[code])

            percentage = (
                count / answered_count * 100
                if answered_count else 0
            )

            results.append({
                "category": category,
                "field_name": field,
                "choice_code": code,
                "practice_or_crop": f"UNKNOWN CODE ({code})",
                "respondents_selected": count,
                "respondents_answered": answered_count,
                "percentage_of_respondents_answered": round(percentage, 1),
                "label_status": "REVIEW CODE"
            })

        print(f"\n{category}")
        print("Respondents who answered:", answered_count)

    output = pd.DataFrame(results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = (
        CLEANED_DIR /
        f"mhac_practice_indicators_{timestamp}.csv"
    )

    output.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\n================================")
    print("INDICATORS GENERATED")
    print("================================")
    print("Total indicator rows:", len(output))
    print("Saved to:", output_file)

    print("\nOptions requiring label review:")
    print(
        output[output["label_status"] != "Label available"][
            ["category", "choice_code", "practice_or_crop",
             "respondents_selected"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
