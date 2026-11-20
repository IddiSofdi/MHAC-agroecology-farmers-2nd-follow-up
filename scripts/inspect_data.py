
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

def inspect_dataset():

    files = sorted(
        RAW_FOLDER.glob("mhac_agroecology_raw_*.json"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    if not files:
        print("No MHAC raw data file found.")
        return

    latest_file = files[0]

    with open(latest_file, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    records = dataset.get("records", [])

    print("\n================================")
    print("MHAC DATASET INSPECTION")
    print("================================")
    print("Project:", dataset.get("project_name"))
    print("Records:", len(records))

    if not records:
        print("No records available for inspection.")
        return

    # Identify all fields across the records
    all_fields = sorted({
        field
        for record in records
        for field in record.keys()
    })

    print("Total unique fields:", len(all_fields))
    print("--------------------------------")
    print("FIELD STRUCTURE")
    print("--------------------------------")

    for field in all_fields:

        values = [record.get(field) for record in records]

        missing = sum(
            value is None or value == "" or value == []
            for value in values
        )

        types = Counter(
            type(value).__name__
            for value in values
            if value is not None and value != ""
        )

        print(f"\nField: {field}")
        print(f"  Missing: {missing}/{len(records)}")
        print(f"  Types: {dict(types)}")

    print("\n================================")
    print("INSPECTION COMPLETE")
    print("================================")
    print("No individual farmer records were displayed.")

if __name__ == "__main__":
    inspect_dataset()
