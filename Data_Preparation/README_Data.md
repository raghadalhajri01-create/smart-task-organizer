# Student 2 · Data preparation

**Project:** AI Personal Productivity — meeting notes to action items.

**Dataset:** Zarnite, *Zarn Meeting to Actions*, Apache-2.0.
https://huggingface.co/datasets/zarnite/zarn-meeting-to-actions
The script uses revision `3eacff6`. The exported CSV is a transformed subset
of the source schema. The benchmark uses authored English meeting examples.
Results on this benchmark may not generalize to real, noisy, or Arabic notes.

## Run from this folder

Requires Python 3.10+ and pandas (tested with pandas 2.2.3).

```sh
python -m pip install pandas
python prepare_data.py
python -m unittest test_prepare_data
```

The ZIP already includes the output, so downloading the source again is optional.
To regenerate using existing files, put `train.jsonl`, `validation.jsonl`, and
`test.jsonl` in one folder and run `python prepare_data.py --raw-dir PATH`.

## Cleaning and transformation

1. Load the three JSONL splits with pandas and validate the schema and split labels.
2. Normalize whitespace, retain speaker names, and remove empty turns.
3. Drop rows missing the ID, meeting text, or usable reference annotations.
   Keep explicitly empty action lists. Keep actions missing an assignee or
   deadline and represent those values as JSON null.
4. Remove duplicate meeting texts, favoring test over validation and validation
   over train if the same input crosses splits. Reject conflicting example IDs.
5. Standardize deadlines as YYYY-MM-DD and export the CSV and summary.

The source run produced 1,200 meetings (900 train, 150 validation, 150 test)
and 4,800 reference actions. No meeting rows were dropped in this run.

## Handoff to the model and Streamlit

Read `data/meetings_clean.csv` with `pd.read_csv`. Use `meeting_text` as model
input. Parse `reference_action_items` with `json.loads` for evaluation targets.
Each reference action has `task`, `owner`, and `due_date`. Use `split` to preserve
the source train, validation, and test partitions. Use `action_count` or split
counts for exploration. The app can produce a table with Task, Owner, Due Date.
