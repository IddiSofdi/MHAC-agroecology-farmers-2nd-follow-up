
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
CLEANED = DATA / "cleaned"

choice_file = DATA / "choice_dictionary.csv"

data_files = list(
    CLEANED.glob("mhac_agroecology_cleaned_*.csv")
)

if not data_files:
    raise FileNotFoundError("Cleaned dataset not found.")

data_file = max(data_files, key=lambda f: f.stat().st_mtime)

df = pd.read_csv(data_file, dtype=str).fillna("")
choices = pd.read_csv(choice_file, dtype=str).fillna("")

question_mapping = {
    "yw8lr28": "Select_the_list_of_crops_plant",
    "hv0kt31": "Which_planting_techn_cticing_on_your_farm",
    "ke6oy89": "Which_soil_and_water_cticing_on_your_farm",
    "vp6qr49": "Which_soil_health_pr_cticing_on_your_farm",
    "ln4si39": "Which_integrated_pest_manageme"
}

print("\n================================")
print("UNLABELLED CHOICE AUDIT")
print("================================")

for list_name, field in question_mapping.items():

    selected_choices = choices[
        (choices["list_name"] == list_name) &
        (choices["choice_label"].str.strip() == "")
    ]

    if selected_choices.empty:
        continue

    print("\nQuestion field:", field)

    for _, choice in selected_choices.iterrows():

        code = choice["choice_name"]
        count = 0

        if field in df.columns:

            for response in df[field]:
                codes = response.split()

                if code in codes:
                    count += 1

        print("Answer code:", code)
        print("Submissions selecting it:", count)

print("\n================================")
print("AUDIT COMPLETE")
print("================================")
