
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEANED = ROOT / "data" / "cleaned"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)

files = list(CLEANED.glob("mhac_agroecology_cleaned_*.csv"))
if not files:
    raise FileNotFoundError("Cleaned dataset not found.")

data_file = max(files, key=lambda f: f.stat().st_mtime)
df = pd.read_csv(data_file, dtype=str).fillna("")

checks = [
    ("Crops planted", "Select_the_list_of_crops_plant", "none"),
    ("Soil and water conservation", "Which_soil_and_water_cticing_on_your_farm", "none_1"),
    ("Soil health practices", "Which_soil_health_pr_cticing_on_your_farm", "none_1"),
    ("Integrated pest management", "Which_integrated_pest_manageme", "none_1"),
]

results = []

for category, field, code in checks:
    responses = df[field].str.strip()

    count = responses.str.split().apply(
        lambda values: code in values
    ).sum()

    results.append({
        "category": category,
        "issue": "Unlabelled choice",
        "choice_code": code,
        "submissions_affected": int(count),
        "status": "Flagged for review"
    })

# Planting technology conflict
field = "Which_planting_techn_cticing_on_your_farm"
responses = df[field].str.strip()

conflicts = responses.str.split().apply(
    lambda values: "none" in values and len(values) > 1
).sum()

results.append({
    "category": "Planting technologies",
    "issue": "Conflicting selection: none with another practice",
    "choice_code": "none + other",
    "submissions_affected": int(conflicts),
    "status": "Flagged for review"
})

audit = pd.DataFrame(results)

output = REPORTS / "mhac_data_quality_report.csv"
audit.to_csv(output, index=False)

print("\n==============================")
print("MHAC DATA QUALITY REPORT")
print("==============================")
print("Dataset:", data_file.name)
print("Total submissions:", len(df))
print("\n", audit.to_string(index=False))
print("\nReport saved to:", output)
