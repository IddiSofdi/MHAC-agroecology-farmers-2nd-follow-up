
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SERVER = os.getenv("KOBO_SERVER", "").rstrip("/")
TOKEN = os.getenv("KOBO_TOKEN", "")

ASSET_UID = "aa9cBubvFxPHnUvDbwvSGs"


def inspect_question_choices():

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
    survey = asset.get("content", {}).get("survey", [])

    print("\n================================")
    print("QUESTION AND ANSWER LIST MAPPING")
    print("================================")

    for question in survey:

        question_type = question.get("type", "")

        if question_type.startswith("select_multiple"):

            print("\n--------------------------------")
            print("Question:", question.get("label"))
            print("Field:", question.get("name"))

            for key, value in question.items():
                if key not in ["label", "name", "type"]:
                    print(f"{key}: {value}")

    print("\n================================")
    print("INSPECTION COMPLETE")
    print("================================")


if __name__ == "__main__":
    try:
        inspect_question_choices()
    except requests.exceptions.RequestException as error:
        print("Kobo API error:", error)
