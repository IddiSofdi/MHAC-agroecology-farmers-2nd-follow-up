
import os
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SERVER = os.getenv("KOBO_SERVER", "").rstrip("/")
TOKEN = os.getenv("KOBO_TOKEN", "")

ASSET_UID = "aa9cBubvFxPHnUvDbwvSGs"


def inspect_form():

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

    print("\n================================")
    print("MHAC KOBO FORM STRUCTURE")
    print("================================")
    print("Form:", asset.get("name"))

    content = asset.get("content")

    if not isinstance(content, dict):
        print("Form definition not included.")
        return

    survey = content.get("survey", [])
    dictionary = []

    print("Total survey rows:", len(survey))

    for question in survey:

        name = question.get("name", "")
        label = question.get("label", "")
        question_type = question.get("type", "")

        if isinstance(label, (list, dict)):
            if isinstance(label, dict):
                label = " | ".join(str(x) for x in label.values())
            else:
                label = " | ".join(str(x) for x in label)

        if name:
            dictionary.append({
                "field_name": name,
                "question": label,
                "question_type": question_type
            })

            print(f"\nField: {name}")
            print(f"Question: {label}")
            print(f"Type: {question_type}")

    output_file = PROJECT_ROOT / "data" / "form_dictionary.csv"

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["field_name", "question", "question_type"]
        )
        writer.writeheader()
        writer.writerows(dictionary)

    print("\n================================")
    print("FORM INSPECTION COMPLETE")
    print("================================")
    print("Dictionary saved to:", output_file)


if __name__ == "__main__":
    try:
        inspect_form()
    except requests.exceptions.RequestException as error:
        print("Kobo API error:", error)
