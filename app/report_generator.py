import pandas as pd
from datetime import datetime


def generate_report(df, output_path):

    df.columns = df.columns.str.strip()

    # ------------------------
    # Completed Sheet
    # ------------------------

    completed_df = df[df["Status"] == "Completed"]

    # ------------------------
    # Details Sheet (Incomplete)
    # ------------------------

    details_df = df[df["Status"] != "Completed"]

    # ------------------------
    # Counts Sheet
    # ------------------------

    total_tasks = len(df)
    completed_count = len(completed_df)
    in_progress = len(df[df["Status"] == "Testing In Progress"])
    not_started = len(df[df["Status"] == "Not Started"])
    past_due = len(df[df["Health"] == "Past Due"])

    summary_data = {
        "Metric": [
            "Total Tasks",
            "Completed",
            "In Progress",
            "Yet to Start",
            "Past Due",
        ],
        "Count": [
            total_tasks,
            completed_count,
            in_progress,
            not_started,
            past_due,
        ],
    }

    summary_df = pd.DataFrame(summary_data)

    # ------------------------
    # Tester Wise Summary
    # ------------------------

    tester_summary = (
        df.groupby(["TOE Tester(s)", "Status"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # ------------------------
    # Write Excel
    # ------------------------

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        df.to_excel(writer, sheet_name="Archer Search Report", index=False)

        details_df.to_excel(writer, sheet_name="Details", index=False)

        completed_df.to_excel(writer, sheet_name="Completed", index=False)

        summary_df.to_excel(writer, sheet_name="Counts", index=False)

        tester_summary.to_excel(writer, sheet_name="Tester Summary", index=False)