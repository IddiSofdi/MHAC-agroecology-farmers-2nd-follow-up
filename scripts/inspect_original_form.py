
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORM_FILE = ROOT / "data" / "MHAC_Agroecology_Form.xlsx"

if not FORM_FILE.exists():
    raise FileNotFoundError(f"Form not found: {FORM_FILE}")

# Read the original XLSForm
excel = pd.ExcelFile(FORM_FILE)

print("\n==============================")
print("ORIGINAL KOBO FORM INSPECTION")
print("==============================")

print("\nWorksheets found:")
for sheet in excel.sheet_names:
    print("-", sheet)

if "choices" not in excel.sheet_names:
    raise ValueError("The XLSForm has no 'choices' worksheet.")

choices = pd.read_excel(FORM_FILE, sheet_name="choices").fillna("")

print("\nPLANTING TECHNOLOGY CHOICES")
print("==============================")

planting = choices[
    choices["list_name"] == "hv0kt31"
]

print(planting.to_string(index=False))
print("\nChoices worksheet columns:")
print(list(choices.columns))

# Inspect the options with missing labels
print("\n==============================")
print("OPTIONS WITH NONE CODES")
print("==============================")

if "name" in choices.columns:
    result = choices[
        choices["name"].astype(str).str.strip().isin(
            ["none", "none_1"]
        )
    ]

    columns = [
        col for col in ["list_name", "name", "label"]
        if col in choices.columns
    ]

    print(result[columns].to_string(index=False))
else:
    print("Could not find the expected 'name' column.")


print("\n==============================")
print("RELEVANT SURVEY QUESTIONS")
print("==============================")

survey = pd.read_excel(
    FORM_FILE,
    sheet_name="survey"
).fillna("")

for _, row in survey.iterrows():

    name = str(row.get("name", "")).strip()
    label = str(row.get("label", "")).strip()

    if name in [
        "Select_the_list_of_crops_plant",
        "Which_planting_techn_cticing_on_your_farm",
        "Which_soil_and_water_cticing_on_your_farm",
        "Which_soil_health_pr_cticing_on_your_farm",
        "Which_integrated_pest_manageme"
    ]:

        print("\nField:", name)
        print("Question:", label)
        print("Type:", row.get("type", ""))
        print("Relevant settings:")

        for column in ["required", "relevant", "hint"]:
            if column in survey.columns:
                print(column + ":", row.get(column, ""))

print("\n==============================")
print("PLANTING TECHNOLOGY RESPONSE AUDIT")
print("==============================")

cleaned_files = list(
    (ROOT / "data" / "cleaned").glob(
        "mhac_agroecology_cleaned_*.csv"
    )
)

if not cleaned_files:
    raise FileNotFoundError("Cleaned data not found.")

latest_file = max(
    cleaned_files,
    key=lambda f: f.stat().st_mtime
)

df = pd.read_csv(latest_file, dtype=str).fillna("")

field = "Which_planting_techn_cticing_on_your_farm"

responses = df[field].str.strip()

none_only = (responses == "none").sum()

none_with_other = responses[
    responses.str.split().apply(
        lambda codes: "none" in codes and len(codes) > 1
    )
].count()

other_practices = responses[
    responses.str.split().apply(
        lambda codes: "none" not in codes and len(codes) > 0
    )
].count()

blank_responses = (responses == "").sum()

print("Total submissions:", len(df))
print("Selected none only:", none_only)
print("Selected none with other options:", none_with_other)
print("Selected named practices:", other_practices)
print("Blank responses:", blank_responses)

print("\nExamples of responses selecting none:")
print(
    responses[
        responses.str.split().apply(
            lambda codes: "none" in codes
        )
    ].head(10).to_string(index=False)
)
print("\n==============================")
print("INSPECTION COMPLETE")
print("==============================")
