
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHOICE_FILE = ROOT / "data" / "choice_dictionary.csv"

choices = pd.read_csv(
    CHOICE_FILE,
    dtype=str
).fillna("")

# Assign the confirmed meaning of the planting option
planting_mask = (
    (choices["list_name"] == "hv0kt31") &
    (choices["choice_name"] == "none")
)

choices.loc[
    planting_mask, "choice_label"
] = "No planting technology practiced"

# Resolve all other blank labels as None
blank_mask = choices["choice_label"].str.strip() == ""

choices.loc[
    blank_mask, "choice_label"
] = "None"

choices.to_csv(CHOICE_FILE, index=False)

print("\nCHOICE LABELS UPDATED")
print("==============================")

print(
    choices[
        choices["choice_name"].isin(["none", "none_1"])
    ][["list_name", "choice_name", "choice_label"]]
    .to_string(index=False)
)

print("\nTotal blank labels resolved:", blank_mask.sum())
