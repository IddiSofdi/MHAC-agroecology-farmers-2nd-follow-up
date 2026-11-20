
import os
import json
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load project configuration
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

KOBO_SERVER = os.getenv("KOBO_SERVER", "").rstrip("/")
KOBO_TOKEN = os.getenv("KOBO_TOKEN", "")

ASSET_UID = "aa9cBubvFxPHnUvDbwvSGs"

def download_mhac_data():

    if not KOBO_SERVER or not KOBO_TOKEN:
        print("ERROR: Kobo credentials are missing.")
        return

    url = f"{KOBO_SERVER}/api/v2/assets/{ASSET_UID}/data/"

    headers = {
        "Authorization": f"Token {KOBO_TOKEN}"
    }

    all_records = []

    try:
        print("Connecting to KoboToolbox...")
        print("Downloading MHAC Agroecology submissions...")

        while url:
            response = requests.get(
                url,
                headers=headers,
                params={"page_size": 1000} if not all_records else None,
                timeout=60
            )

            response.raise_for_status()
            page = response.json()

            if isinstance(page, dict):
                all_records.extend(page.get("results", []))
                url = page.get("next")
            elif isinstance(page, list):
                all_records.extend(page)
                url = None
            else:
                raise ValueError("Unexpected Kobo API response format.")

        # Create a unique filename for each download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_folder = PROJECT_ROOT / "data" / "raw"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = (
            output_folder /
            f"mhac_agroecology_raw_{timestamp}.json"
        )

        # Preserve the original submission records
        output_data = {
            "project_name": "MHAC AGROECOLOGY FARMERS FOLLOW-UP",
            "project_uid": ASSET_UID,
            "downloaded_at": datetime.now().isoformat(),
            "record_count": len(all_records),
            "records": all_records
        }

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                output_data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("\n================================")
        print("DOWNLOAD SUCCESSFUL")
        print("================================")
        print("Project: MHAC Agroecology")
        print("Records downloaded:", len(all_records))
        print("Saved file:", output_file)
        print("================================")

    except requests.exceptions.RequestException as error:
        print("Kobo download error:", error)

    except (ValueError, KeyError) as error:
        print("Data processing error:", error)

if __name__ == "__main__":
    download_mhac_data()
