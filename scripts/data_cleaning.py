
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
REPORT_DIR = PROJECT_ROOT / "reports"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def get_records(payload):

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ["records", "results", "data"]:
            if isinstance(payload.get(key), list):
                return payload[key]

    raise ValueError(
        "Could not identify the Kobo submission records in the JSON file."
    )


def clean_value(value):

    if isinstance(value, str):
        value = value.strip()

        if value.lower() in ["", "na", "n/a", "null", "nan"]:
            return pd.NA

    return value


def clean_data():

    raw_files = list(RAW_DIR.glob("mhac_agroecology_raw_*.json"))

    if not raw_files:
        print("ERROR: No MHAC raw JSON file found.")
        return

    latest_file = max(raw_files, key=lambda file: file.stat().st_mtime)

    print("\n================================")
    print("MHAC DATA CLEANING")
    print("================================")
    print("Raw file:", latest_file.name)

    with open(latest_file, "r", encoding="utf-8") as file:
        payload = json.load(file)

    records = get_records(payload)

    df = pd.DataFrame(records)

    original_rows = len(df)
    original_columns = len(df.columns)

    # Standardise whitespace and blank values.
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].map(clean_value)

    # Check duplicate submission identifiers without deleting records.
    duplicate_uuid_rows = 0

    if "_uuid" in df.columns:
        duplicate_uuid_rows = int(
            df["_uuid"].duplicated(keep=False).sum()
        )

    duplicate_id_rows = 0

    if "_id" in df.columns:
        duplicate_id_rows = int(
            df["_id"].duplicated(keep=False).sum()
        )

    # Count missing values.
    missing_counts = df.isna().sum()
    missing_fields = missing_counts[missing_counts > 0]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = (
        CLEANED_DIR /
        f"mhac_agroecology_cleaned_{timestamp}.csv"
    )

    report_file = (
        REPORT_DIR /
        f"mhac_cleaning_report_{timestamp}.txt"
    )

    # Save cleaned data without changing the raw JSON.
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    # Generate cleaning report.
    with open(report_file, "w", encoding="utf-8") as report:

        report.write("MHAC AGROECOLOGY DATA CLEANING REPORT\n")
        report.write("=" * 45 + "\n\n")

        report.write(f"Source file: {latest_file.name}\n")
        report.write(f"Total records: {original_rows}\n")
        report.write(f"Total fields: {original_columns}\n")
        report.write(f"Duplicate UUID rows: {duplicate_uuid_rows}\n")
        report.write(f"Duplicate ID rows: {duplicate_id_rows}\n\n")

        report.write("MISSING VALUES BY FIELD\n")
        report.write("-" * 45 + "\n")

        for field, count in missing_fields.items():
            report.write(f"{field}: {count}\n")

        report.write("\nCleaning actions:\n")
        report.write("- Removed leading and trailing whitespace.\n")
        report.write("- Standardised blank values as missing.\n")
        report.write("- Preserved all original submission records.\n")
        report.write("- Preserved original field names.\n")
        report.write("- Did not delete possible duplicate submissions.\n")

    print("\nCLEANING SUCCESSFUL")
    print("--------------------------------")
    print("Records:", original_rows)
    print("Fields:", original_columns)
    print("Duplicate UUID rows:", duplicate_uuid_rows)
    print("Duplicate ID rows:", duplicate_id_rows)
    print("\nCleaned dataset:", output_file)
    print("Cleaning report:", report_file)


if __name__ == "__main__":
    try:
        clean_data()
    except Exception as error:
        print("\nCLEANING ERROR:", error)
