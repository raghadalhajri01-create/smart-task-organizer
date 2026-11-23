import pandas as pd

from analysis import (
    get_task_summary,
    get_category_chart_data,
    export_tasks_to_csv,
)


def test_task_summary():

    tasks = pd.DataFrame([
        {
            "task": "Study Python",
            "category": "Study",
            "deadline": "tomorrow"
        },
        {
            "task": "Attend meeting",
            "category": "Work",
            "deadline": None
        },
        {
            "task": "Buy groceries",
            "category": "Personal",
            "deadline": ""
        }
    ])

    result = get_task_summary(tasks)

    assert result["total_tasks"] == 3
    assert result["category_counts"]["Study"] == 1
    assert result["category_counts"]["Work"] == 1
    assert result["category_counts"]["Personal"] == 1
    assert result["without_deadline"] == 2


def test_category_chart():

    tasks = pd.DataFrame([
        {
            "task": "Study Python",
            "category": "Study",
            "deadline": "tomorrow"
        },
        {
            "task": "Attend meeting",
            "category": "Work",
            "deadline": None
        }
    ])

    result = get_category_chart_data(tasks)

    assert result.loc["Study", "Number of Tasks"] == 1
    assert result.loc["Work", "Number of Tasks"] == 1
    assert result.loc["Personal", "Number of Tasks"] == 0


def test_csv_export():

    tasks = pd.DataFrame([
        {
            "task": "Study Python",
            "category": "Study",
            "deadline": "tomorrow"
        }
    ])

    csv_data = export_tasks_to_csv(tasks)

    csv_text = csv_data.decode("utf-8-sig")

    assert "task,category,deadline" in csv_text
    assert "Study Python,Study,tomorrow" in csv_text