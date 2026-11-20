
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

files = list(
    (ROOT / "data" / "cleaned").glob(
        "mhac_agroecology_cleaned_*.csv"
    )
)

latest = max(files, key=lambda f: f.stat().st_mtime)
df = pd.read_csv(latest, dtype=str).fillna("")

audits = {
    "Crops planted": (
        "Select_the_list_of_crops_plant", "none"
    ),
    "Soil and water conservation": (
        "Which_soil_and_water_cticing_on_your_farm", "none_1"
    ),
    "Soil health practices": (
        "Which_soil_health_pr_cticing_on_your_farm", "none_1"
    ),
    "Integrated pest management": (
        "Which_integrated_pest_manageme", "none_1"
    ),
    "Planting technology conflict": (
        "Which_planting_techn_cticing_on_your_farm", "none"
    )
}

print("\n================================")
print("REMAINING CHOICE RESPONSE AUDIT")
print("================================")

for category, (field, code) in audits.items():

    print("\n", category)

    responses = df[field].str.strip()

    matching = responses[
        responses.str.split().apply(
            lambda values: code in values
        )
    ]

    if matching.empty:
        print("No submissions.")
    else:
        print(matching.value_counts().to_string())

print("\n================================")
print("AUDIT COMPLETE")
print("================================")
