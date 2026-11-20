
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
DATA_DIR = PROJECT_ROOT / "data"

def validate_data():

    files = list(CLEANED_DIR.glob("mhac_agroecology_cleaned_*.csv"))

    if not files:
        print("ERROR: No cleaned dataset found.")
        return

    latest_file = max(files, key=lambda f: f.stat().st_mtime)

    df = pd.read_csv(latest_file)

    dictionary_file = DATA_DIR / "form_dictionary.csv"

    print("\n================================")
    print("MHAC DATA VALIDATION")
    print("================================")

    print("Dataset:", latest_file.name)
    print("Total records:", len(df))
    print("Total fields:", len(df.columns))

    print("\n1. DUPLICATE CHECK")
    print("--------------------------------")

    for field in ["_uuid", "_id"]:
        if field in df.columns:
            print(
                f"{field} duplicates:",
                df[field].duplicated().sum()
            )

    print("\n2. IMPORTANT FIELD COMPLETENESS")
    print("--------------------------------")

    important_fields = [
        "Region",
        "Interviewer",
        "Name_of_the_Group",
        "Lead_Farmer_Contact",
        "GPS_location",
        "Is_your_group_active_in_VSLA",
        "Do_you_keep_any_farm_records"
    ]

    for field in important_fields:
        if field in df.columns:
            missing = df[field].isna().sum()
            complete = len(df) - missing
            percentage = (complete / len(df)) * 100

            print(
                f"{field}: {complete}/{len(df)} "
                f"complete ({percentage:.1f}%)"
            )
        else:
            print(f"{field}: NOT FOUND")

    print("\n3. FIELDS WITH MOST MISSING VALUES")
    print("--------------------------------")

    missing = df.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0].head(15)

    for field, count in missing.items():
        print(f"{field}: {count}")

    print("\n4. MULTI-SELECT QUESTIONS")
    print("--------------------------------")

    if dictionary_file.exists():

        dictionary = pd.read_csv(dictionary_file)

        multi_select = dictionary[
            dictionary["question_type"] == "select_multiple"
        ]

        for _, row in multi_select.iterrows():
            print(f"\nField: {row['field_name']}")
            print(f"Question: {row['question']}")

    else:
        print("Form dictionary not found.")

    print("\n5. REGION VALUES")
    print("--------------------------------")

    if "Region" in df.columns:
        print(df["Region"].value_counts(dropna=False).to_string())

    print("\n================================")
    print("VALIDATION COMPLETE")
    print("================================")


if __name__ == "__main__":
    validate_data()
