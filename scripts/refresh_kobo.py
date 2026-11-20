
import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
REPORTS_DIR = PROJECT_ROOT / "reports"


def latest_file(folder, pattern):
    files = list(folder.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def run_script(script_name):
    script_path = PROJECT_ROOT / "scripts" / script_name

    print(f"\nRunning {script_name}...")

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        check=True
    )


def refresh_kobo():

    start_time = time.time()

    print("\n================================")
    print("SOFDI MHAC KOBO DATA REFRESH")
    print("================================")

    # 1. Download fresh Kobo submissions
    run_script("download_data.py")

    raw_file = latest_file(
        RAW_DIR, "mhac_agroecology_raw_*.json"
    )

    if raw_file is None or raw_file.stat().st_mtime < start_time - 1:
        raise RuntimeError(
            "A new Kobo download could not be confirmed."
        )

    # 2. Clean downloaded submissions
    run_script("data_cleaning.py")

    cleaned_file = latest_file(
        CLEANED_DIR, "mhac_agroecology_cleaned_*.csv"
    )

    if cleaned_file is None or cleaned_file.stat().st_mtime < start_time - 1:
        raise RuntimeError("New cleaned data could not be confirmed.")

    # 3. Rebuild practice adoption indicators
    run_script("build_practice_indicators.py")

    indicator_file = latest_file(
        CLEANED_DIR, "mhac_practice_indicators_*.csv"
    )

    if indicator_file is None or indicator_file.stat().st_mtime < start_time - 1:
        raise RuntimeError("New practice indicators could not be confirmed.")

    # 4. Rebuild data quality report
    run_script("build_quality_report.py")

    quality_file = REPORTS_DIR / "mhac_data_quality_report.csv"

    if not quality_file.exists() or quality_file.stat().st_mtime < start_time - 1:
        raise RuntimeError("New quality report could not be confirmed.")

    print("\n================================")
    print("KOBO REFRESH SUCCESSFUL")
    print("================================")
    print("Raw file:", raw_file.name)
    print("Cleaned file:", cleaned_file.name)
    print("Indicator file:", indicator_file.name)
    print("Quality report:", quality_file.name)
    print("================================")


if __name__ == "__main__":
    try:
        refresh_kobo()
    except Exception as error:
        print("\nREFRESH FAILED:")
        print(error)
        sys.exit(1)