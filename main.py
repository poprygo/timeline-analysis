import argparse
import json
import shutil
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser

# Argument parsing setup
arg_parser = argparse.ArgumentParser(
    description="Process location data from a ZIP archive."
)
arg_parser.add_argument(
    "zip_archive", type=str, help="Path to the ZIP archive containing the Takeout data."
)
arg_parser.add_argument(
    "--dates_to_skip",
    nargs="*",
    default=[],
    help="Dates to skip in the format 'YYYY-MM-DD'.",
)
args = arg_parser.parse_args()

# Unzipping the archive
with zipfile.ZipFile(args.zip_archive, "r") as zip_ref:
    zip_ref.extractall("Takeout")


def process_json_file(file_path, dates_to_skip):
    with open(file_path) as f:
        data = json.load(f)

    passenger_vehicle_activities = []
    for obj in data["timelineObjects"]:
        if "activitySegment" in obj:
            segment = obj["activitySegment"]
            activity_type = segment["activityType"]
            if activity_type == "IN_PASSENGER_VEHICLE":
                start_time = parser.parse(segment["duration"]["startTimestamp"])
                if start_time.strftime("%Y-%m-%d") in dates_to_skip:
                    continue
                if "distance" not in segment:
                    continue
                distance = segment["distance"]
                passenger_vehicle_activities.append(
                    {
                        "date": start_time.date(),
                        "distance": distance * 0.000621371,  # Convert meters to miles
                    }
                )

    return pd.DataFrame(passenger_vehicle_activities)


base_path = Path(
    "Takeout/Takeout/Location History (Timeline)/Semantic Location History"
)
all_dfs = []
for year_path in base_path.iterdir():
    if year_path.is_dir():
        for file_path in year_path.rglob("*.json"):
            df = process_json_file(file_path, args.dates_to_skip)
            all_dfs.append(df)

df = pd.concat(all_dfs, ignore_index=True)
df["date"] = pd.to_datetime(df["date"])
daily_distance = df.groupby("date")["distance"].sum().reset_index()
daily_distance["runs"] = (
    df.groupby("date")["date"].count().reset_index(name="counts")["counts"]
)

years = daily_distance["date"].dt.year.unique()

for year in years:
    yearly_data = daily_distance[daily_distance["date"].dt.year == year]
    months = yearly_data["date"].dt.month.unique()
    n_months = len(months)
    cols = 3  # Adjust based on preference
    rows = np.ceil(n_months / cols).astype(int)

    fig, axs = plt.subplots(rows, cols, figsize=(15, 4 * rows), constrained_layout=True)
    fig.suptitle(f"Daily Distance and Number of Runs in {year}")

    for i, month in enumerate(sorted(months)):
        monthly_data = yearly_data[yearly_data["date"].dt.month == month].copy()
        if monthly_data.empty:
            continue
        total_distance = monthly_data["distance"].sum()
        ax = axs.flat[i]
        bars = ax.bar(
            monthly_data["date"].astype(str),
            monthly_data["distance"],
            color="blue",
            label="Distance",
        )

        # Decrease the size of text and print only nonzero distances
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{int(height)}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        ax2 = ax.twinx()
        ax2.plot(
            monthly_data["date"].astype(str),
            monthly_data["runs"],
            color="red",
            label="Runs",
            marker="o",
        )

        # Use full dates as x-axis labels for nonzero dates
        ax.set_xticks(monthly_data["date"].astype(str))
        ax.set_xticklabels(
            [date.strftime("%Y-%m-%d") for date in monthly_data["date"]],
            rotation=45,
            ha="right",
            fontsize=8,
        )

        ax.set_title(
            f"{pd.to_datetime(str(month), format='%m').strftime('%B')} (Total: {total_distance:.2f} Miles)",
            fontsize=10,
        )
        ax.set_xlabel("Date", fontsize=9)
        ax.set_ylabel("Distance (Miles)", fontsize=9)
        ax2.set_ylabel("Number of Runs", fontsize=9)

        # Clean up the x-axis to show only dates with activities
        for label in ax.get_xticklabels():
            if label.get_text().endswith("-00"):
                label.set_visible(False)

        if i == 0:  # Only add legend to the first subplot for clarity
            fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9), fontsize=8)

    # Turn off unused subplots
    for j in range(i + 1, rows * cols):
        axs.flat[j].axis("off")

    plt.savefig(f"distance_runs_{year}.png")
    plt.close()

# remove directory and its contents
shutil.rmtree("Takeout")
