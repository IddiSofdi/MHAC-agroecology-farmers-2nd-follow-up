
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHOICE_FILE = PROJECT_ROOT / "data" / "choice_dictionary.csv"

QUESTION_LISTS = {
    "yw8lr28": "Crops planted",
    "hv0kt31": "Planting technologies",
    "ke6oy89": "Soil and water conservation",
    "vp6qr49": "Soil health practices",
    "kv0rn37": "Pest and disease control",
    "ln4si39": "Integrated pest management",
    "ck6fu99": "Other sustainable farming practices"
}


def view_options():

    df = pd.read_csv(CHOICE_FILE)

    print("\n================================")
    print("MHAC PRACTICE ANSWER OPTIONS")
    print("================================")

    for list_name, question in QUESTION_LISTS.items():

        selected = df[df["list_name"] == list_name]

        print(f"\n\n{question}")
        print("-" * 45)

        if selected.empty:
            print("No options found.")
            continue

        for _, row in selected.iterrows():
            print(
                f"{row['choice_name']} : "
                f"{row['choice_label']}"
            )

    print("\n================================")
    print("OPTIONS INSPECTION COMPLETE")
    print("================================")


if __name__ == "__main__":
    view_options()
