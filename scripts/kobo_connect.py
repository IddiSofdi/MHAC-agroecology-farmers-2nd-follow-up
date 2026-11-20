
import os
import requests
from dotenv import load_dotenv

load_dotenv()

KOBO_SERVER = os.getenv("KOBO_SERVER", "").rstrip("/")
KOBO_TOKEN = os.getenv("KOBO_TOKEN", "")


def get_kobo_projects():

    url = f"{KOBO_SERVER}/api/v2/assets/?asset_type=survey"

    headers = {
        "Authorization": f"Token {KOBO_TOKEN}"
    }

    projects = []

    try:
        while url:
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            page = response.json()

            projects.extend(page.get("results", []))
            url = page.get("next")

        print("\n================================")
        print("SOFDI KOBO PROJECT REGISTER")
        print("================================")

        print("Total projects:", len(projects))
        print("--------------------------------")

        for number, project in enumerate(projects, start=1):
            name = project.get("name", "Unnamed project")
            uid = project.get("uid", "No UID")
            submissions = project.get(
                "deployment__submission_count", "Not available"
            )

            print(f"\n{number}. {name}")
            print(f"   UID: {uid}")
            print(f"   Submissions: {submissions}")

        print("\n================================")
        print("PROJECT LIST RETRIEVED")
        print("================================")

    except requests.exceptions.RequestException as error:
        print("Kobo connection error:", error)


if __name__ == "__main__":
    get_kobo_projects()
