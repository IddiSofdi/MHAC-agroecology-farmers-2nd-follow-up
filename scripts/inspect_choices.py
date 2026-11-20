
import os
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SERVER = os.getenv("KOBO_SERVER", "").rstrip("/")
TOKEN = os.getenv("KOBO_TOKEN", "")

ASSET_UID = "aa9cBubvFxPHnUvDbwvSGs"


def inspect_choices():

    url = f"{SERVER}/api/v2/assets/{ASSET_UID}/"

    headers = {
        "Authorization": f"Token {TOKEN}"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    asset = response.json()
    content = asset.get("content", {})

    choices = content.get("choices", [])

    if not choices:
        print("No choices found in the form definition.")
        return

    output_file = PROJECT_ROOT / "data" / "choice_dictionary.csv"

    rows = []

    for choice in choices:

        label = choice.get("label", "")

        if isinstance(label, list):
            label = " | ".join(str(x) for x in label)

        rows.append({
            "list_name": choice.get("list_name", ""),
            "choice_name": choice.get("name", ""),
            "choice_label": label
        })

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "list_name",
                "choice_name",
                "choice_label"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n================================")
    print("KOBO CHOICE DICTIONARY")
    print("================================")

    print("Total answer options:", len(rows))

    list_counts = Counter(
        row["list_name"] for row in rows
    )

    for list_name, count in list_counts.items():
        print(f"{list_name}: {count} options")

    print("\nSaved to:", output_file)
    print("\nCHOICE EXTRACTION COMPLETE")


if __name__ == "__main__":
    try:
        inspect_choices()
    except requests.exceptions.RequestException as error:
        print("Kobo API error:", error)


