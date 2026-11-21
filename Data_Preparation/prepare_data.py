"""Validate and flatten the Zarn Meeting to Actions benchmark."""
import argparse
import json
import logging
from pathlib import Path

import pandas as pd

SOURCE = "https://huggingface.co/datasets/zarnite/zarn-meeting-to-actions"
REVISION = "3eacff6"
SPLITS = ("train", "validation", "test")
COLUMNS = ("example_id", "benchmark_split", "transcript", "reference_action_items")


def clean_text(value):
    return " ".join(value.split()) if isinstance(value, str) else ""


def flatten_transcript(turns):
    lines = []
    if isinstance(turns, list):
        for turn in turns:
            if isinstance(turn, dict) and (text := clean_text(turn.get("text"))):
                speaker = clean_text(turn.get("speaker"))
                lines.append(f"{speaker}: {text}" if speaker else text)
    return "\n".join(lines)


def clean_actions(items):
    if not isinstance(items, list):
        return None
    actions = []
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not (task := clean_text(item.get("task"))):
            continue
        owner = clean_text(item.get("owner")) or None
        date = clean_text(item.get("due_date"))
        parsed_date = pd.to_datetime(date, errors="coerce")
        due_date = None if pd.isna(parsed_date) else parsed_date.date().isoformat()
        key = (task, owner, due_date)
        if key not in seen:
            actions.append(dict(task=task, owner=owner, due_date=due_date))
            seen.add(key)
    # Explicit [] means zero reference actions. An unusable annotation is missing.
    return json.dumps(actions, ensure_ascii=False) if actions or not items else None


def clean_data(raw):
    missing = set(COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    data = raw.loc[:, list(COLUMNS)].copy()
    data["example_id"] = data["example_id"].map(clean_text)
    data["benchmark_split"] = data["benchmark_split"].map(clean_text)
    data["transcript"] = data["transcript"].map(flatten_transcript)
    data["reference_action_items"] = data["reference_action_items"].map(clean_actions)
    valid = (
        data["example_id"].ne("")
        & data["benchmark_split"].isin(SPLITS)
        & data["transcript"].ne("")
        & data["reference_action_items"].notna()
    )
    usable = data.loc[valid].drop_duplicates()
    if usable["example_id"].duplicated().any():
        raise ValueError("Conflicting records share the same example ID.")

    # Preserve the holdout splits when the same model input is repeated.
    priority = {"test": 0, "validation": 1, "train": 2}
    ordered = usable.sort_values("benchmark_split", key=lambda s: s.map(priority), kind="stable")
    cleaned = ordered.drop_duplicates(subset="transcript").sort_index().reset_index(drop=True)
    if cleaned.empty:
        raise ValueError("No usable meetings remain after cleaning.")
    cleaned = cleaned.rename(columns={"benchmark_split": "split", "transcript": "meeting_text"})
    cleaned["action_count"] = cleaned["reference_action_items"].map(lambda value: len(json.loads(value)))
    summary = {
        "input_rows": len(raw),
        "invalid_rows_removed": int((~valid).sum()),
        "duplicate_rows_removed": int(valid.sum() - len(cleaned)),
        "output_rows": len(cleaned),
        "reference_actions": int(cleaned["action_count"].sum()),
        "rows_by_split": {split: int(cleaned["split"].eq(split).sum()) for split in SPLITS},
    }
    return cleaned, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, help="Directory containing the three JSONL files")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        frames = []
        for split in SPLITS:
            source = (
                args.raw_dir / f"{split}.jsonl"
                if args.raw_dir
                else f"{SOURCE}/resolve/{REVISION}/data/{split}.jsonl"
            )
            frame = pd.read_json(source, lines=True)
            if "benchmark_split" not in frame or not frame["benchmark_split"].eq(split).all():
                raise ValueError(f"Unexpected split labels in {split}.jsonl")
            frames.append(frame)
        cleaned, summary = clean_data(pd.concat(frames, ignore_index=True))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(args.output_dir / "meetings_clean.csv", index=False, encoding="utf-8")
        (args.output_dir / "cleaning_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError) as error:
        logging.error("%s", error)
        return 1
    logging.info("Exported %s cleaned meetings to %s", len(cleaned), args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
