import pandas as pd


def get_task_summary(tasks_df: pd.DataFrame) -> dict:
    """
    Calculate task statistics from the organized tasks.
    """

    required_columns = {"task", "category", "deadline"}

    if not required_columns.issubset(tasks_df.columns):
        raise ValueError(
            "Data must contain task, category, and deadline columns."
        )

    # Count total tasks
    total_tasks = len(tasks_df)

    # Count tasks by category
    category_counts = (
        tasks_df["category"]
        .value_counts()
        .reindex(["Study", "Work", "Personal"], fill_value=0)
        .to_dict()
    )

    # Count tasks without deadlines
    missing_deadlines = (
        tasks_df["deadline"].isna()
        | tasks_df["deadline"].astype(str).str.strip().eq("")
    ).sum()

    return {
        "total_tasks": total_tasks,
        "category_counts": category_counts,
        "without_deadline": int(missing_deadlines)
    }
def get_category_chart_data(tasks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare category counts for visualization.
    """

    summary = get_task_summary(tasks_df)

    chart_data = pd.DataFrame({
        "Category": list(summary["category_counts"].keys()),
        "Number of Tasks": list(summary["category_counts"].values())
    })

    return chart_data.set_index("Category")
def export_tasks_to_csv(tasks_df: pd.DataFrame) -> bytes:
    """
    Convert the current tasks table into a downloadable CSV file.
    """

    required_columns = ["task", "category", "deadline"]

    if not all(column in tasks_df.columns for column in required_columns):
        raise ValueError(
            "Data must contain task, category, and deadline columns."
        )

    csv_data = tasks_df[required_columns].to_csv(
        index=False
    )

    return csv_data.encode("utf-8-sig")