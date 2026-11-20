
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

FIELDS_TO_PROFILE = [
    "Region",
    "Do_you_attend_cluster_meetings",
    "Do_you_attend_cluster_meetings_001",
    "Do_you_attend_cluster_meetings_002",
    "Do_you_attend_cluster_meetings_003",
    "Do_you_attend_cluster_meetings_004",
    "Is_your_group_active_in_VSLA",
    "Do_you_keep_any_farm_records",
    "Do_you_sell_surplus_oduce_from_your_farm",
    "How_would_you_rate_t_r_cluster_activities",
    "Select_the_list_of_crops_plant",
    "Which_integrated_pest_manageme",
    "Which_planting_techn_cticing_on_your_farm",
    "Which_soil_and_water_cticing_on_your_farm",
    "Which_soil_health_pr_cticing_on_your_farm",
    "Which_pest_and_disea_cticing_on_your_farm",
    "Which_is_the_main_ch_ecological_practices",
    "Other_Sustainable_Farming_Practices"
]


def profile_responses():

    files = sorted(
        RAW_FOLDER.glob("mhac_agroecology_raw_*.json"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    if not files:
        print("No raw dataset found.")
        return

    with open(files[0], "r", encoding="utf-8") as file:
        dataset = json.load(file)

    records = dataset.get("records", [])

    print("\n================================")
    print("MHAC RESPONSE CATEGORY PROFILE")
    print("================================")

    for field in FIELDS_TO_PROFILE:

        values = [
            record.get(field)
            for record in records
            if record.get(field) not in (None, "", [])
        ]

        if not values:
            print(f"\n{field}: No responses")
            continue

        counts = Counter(str(value) for value in values)

        print(f"\nFIELD: {field}")
        print("Responses:", len(values))
        print("Distinct answers:", len(counts))

        for answer, count in counts.most_common(15):
            display_answer = answer[:120]
            print(f"  {display_answer}: {count}")

        if len(counts) > 15:
            print("  ... additional answer categories omitted")

    print("\n================================")
    print("RESPONSE PROFILING COMPLETE")
    print("================================")


if __name__ == "__main__":
    profile_responses()
