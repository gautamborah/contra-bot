import pandas as pd
import json
from pathlib import Path
import math

RAW_FILE = Path(
    "./app/data/raw/covid-19-vaccines-administered-by-demographics-by-county.csv"
)
DAILY_FILE = Path(
    "./app/data/processed/daily_chunks_by_county.jsonl"
)
WEEKLY_FILE = Path(
    "./app/data/processed/weekly_chunks_by_county.jsonl"
)

def get_int(val):
    """Convert safely to int, handling NaN/None."""
    if pd.isna(val) or val is None or (isinstance(val, float) and math.isnan(val)):
        return 0
    return int(val)

def make_chunks():
    # Load CSV
    df = pd.read_csv(RAW_FILE)

    # Parse dates
    df["ADMINISTERED_DATE"] = pd.to_datetime(df["ADMINISTERED_DATE"], errors="coerce")

    daily_chunks = []
    weekly_chunks = []

    # --- DAILY: group by COUNTY + DATE + DEMOGRAPHIC ---
    grouped = df.groupby(["COUNTY", "ADMINISTERED_DATE", "DEMOGRAPHIC_CATEGORY", "DEMOGRAPHIC_VALUE"])
    for (county, date, demo_cat, demo_val), group in grouped:
        agg = group.sum(numeric_only=True)
        text = (
            f"On {date.date()}, in {county}, for {demo_cat}: {demo_val}, "
            f"{get_int(agg.get('PARTIALLY_VACCINATED'))} partially vaccinated, "
            f"{get_int(agg.get('FULLY_VACCINATED'))} fully vaccinated, "
            f"{get_int(agg.get('AT_LEAST_ONE_DOSE'))} with at least one dose, "
            f"and {get_int(agg.get('UP_TO_DATE_COUNT'))} up-to-date. "
            f"Cumulative totals: {get_int(agg.get('CUMULATIVE_FULLY_VACCINATED'))} fully vaccinated, "
            f"{get_int(agg.get('CUMULATIVE_AT_LEAST_ONE_DOSE'))} with at least one dose, "
            f"{get_int(agg.get('CUMULATIVE_UP_TO_DATE_COUNT'))} up-to-date."
        )
        daily_chunks.append({
            "text": text,
            "metadata": {
                "county": county,
                "date": str(date.date()),
                "demographic_category": demo_cat,
                "demographic_value": demo_val,
                "granularity": "daily"
            }
        })

    # --- WEEKLY: group by COUNTY + DEMOGRAPHIC ---
    for (county, demo_cat, demo_val), group in df.groupby(["COUNTY", "DEMOGRAPHIC_CATEGORY", "DEMOGRAPHIC_VALUE"]):
        group = group.sort_values("ADMINISTERED_DATE").set_index("ADMINISTERED_DATE")
        weekly = group.resample("W").sum(numeric_only=True)

        for date, row in weekly.iterrows():
            text = (
                f"In the week ending {date.date()}, in {county}, for {demo_cat}: {demo_val}, "
                f"{get_int(row.get('PARTIALLY_VACCINATED'))} partially vaccinated, "
                f"{get_int(row.get('FULLY_VACCINATED'))} fully vaccinated, "
                f"{get_int(row.get('AT_LEAST_ONE_DOSE'))} with at least one dose, "
                f"and {get_int(row.get('UP_TO_DATE_COUNT'))} up-to-date. "
                f"Cumulative totals: {get_int(row.get('CUMULATIVE_FULLY_VACCINATED'))} fully vaccinated, "
                f"{get_int(row.get('CUMULATIVE_AT_LEAST_ONE_DOSE'))} with at least one dose, "
                f"{get_int(row.get('CUMULATIVE_UP_TO_DATE_COUNT'))} up-to-date."
            )
            weekly_chunks.append({
                "text": text,
                "metadata": {
                    "county": county,
                    "week_ending": str(date.date()),
                    "demographic_category": demo_cat,
                    "demographic_value": demo_val,
                    "granularity": "weekly"
                }
            })

    # Save outputs
    DAILY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DAILY_FILE, "w") as f:
        for chunk in daily_chunks:
            f.write(json.dumps(chunk) + "\n")

    with open(WEEKLY_FILE, "w") as f:
        for chunk in weekly_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"✅ Saved {len(daily_chunks)} daily chunks with demographics → {DAILY_FILE}")
    print(f"✅ Saved {len(weekly_chunks)} weekly chunks with demographics → {WEEKLY_FILE}")

if __name__ == "__main__":
    make_chunks()
