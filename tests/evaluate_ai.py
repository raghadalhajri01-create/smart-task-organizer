import json
import sys
from pathlib import Path

# Allow importing task_ai.py from the project root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from task_ai import extract_tasks


def normalize(value):
    """Normalize text for fair comparison."""
    if value is None:
        return None

    return " ".join(str(value).lower().split())


def compare_tasks(expected, predicted):
    """Compare expected and AI-generated tasks."""

    expected_set = {
        (
            normalize(task["task"]),
            normalize(task["category"]),
            normalize(task["deadline"])
        )
        for task in expected
    }

    predicted_set = {
        (
            normalize(task["task"]),
            normalize(task["category"]),
            normalize(task["deadline"])
        )
        for task in predicted
    }

    correct = expected_set & predicted_set
    missing = expected_set - predicted_set
    extra = predicted_set - expected_set

    return {
        "correct": len(correct),
        "missing": len(missing),
        "extra": len(extra),
        "missing_tasks": sorted(missing, key=str),
        "extra_tasks": sorted(extra, key=str)
    }


def main():

    cases_path = Path(__file__).parent / "evaluation_cases.json"

    with open(cases_path, encoding="utf-8") as file:
        cases = json.load(file)

    total_correct = 0
    total_expected = 0
    total_predicted = 0

    for case in cases:

        print(f"\nTesting Case {case['id']}")

        predicted = extract_tasks(case["input"])
        expected = case["expected"]

        result = compare_tasks(expected, predicted)

        total_correct += result["correct"]
        total_expected += len(expected)
        total_predicted += len(predicted)

        print("Expected:", expected)
        print("Predicted:", predicted)
        print("Correct:", result["correct"])
        print("Missing:", result["missing"])
        print("Extra:", result["extra"])

        if result["missing_tasks"]:
            print("Missing tasks:", result["missing_tasks"])

        if result["extra_tasks"]:
            print("Extra tasks:", result["extra_tasks"])

    precision = (
        total_correct / total_predicted
        if total_predicted else 0
    )

    recall = (
        total_correct / total_expected
        if total_expected else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    print("\n===== FINAL AI EVALUATION =====")
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1 Score: {f1:.2%}")


if __name__ == "__main__":
    main()