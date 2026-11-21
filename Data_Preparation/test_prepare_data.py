import json
import unittest

import pandas as pd

from prepare_data import clean_data


class DataCleaningTests(unittest.TestCase):
    def test_blank_input_duplicates_and_missing_optional_fields(self):
        row = {
            "example_id": "1",
            "benchmark_split": "train",
            "transcript": [{"speaker": "Sam", "text": "  Send   the slides.  "}],
            "reference_action_items": [{"task": " Send the slides. ", "due_date": "unknown"}],
        }
        duplicate = dict(row, example_id="2", benchmark_split="test")
        blank = dict(row, example_id="3", transcript=[{"text": "  "}])
        cleaned, summary = clean_data(pd.DataFrame([row, duplicate, blank]))
        self.assertEqual(cleaned["split"].tolist(), ["test"])
        self.assertEqual(cleaned["meeting_text"].tolist(), ["Sam: Send the slides."])
        self.assertEqual(json.loads(cleaned.iloc[0]["reference_action_items"]), [
            {"task": "Send the slides.", "owner": None, "due_date": None}
        ])
        self.assertEqual(summary["invalid_rows_removed"], 1)
        self.assertEqual(summary["duplicate_rows_removed"], 1)

    def test_missing_required_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            clean_data(pd.DataFrame({"example_id": ["1"]}))
