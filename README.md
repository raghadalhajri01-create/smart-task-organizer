# Smart Task Organizer
AI for Personal Productivity — ARTI303 Final Project

## Overview
Smart Task Organizer is a Python application that uses a
pretrained AI model to extract tasks from English notes
and meeting transcripts.

Users can enter text, upload a file, or combine both.
The application displays editable tasks, summary statistics,
a category chart, and a CSV download option.

## Problem and Target Users
Students and individuals may keep tasks in unstructured notes,
making responsibilities and deadlines difficult to track.

The application helps organize these notes into a clear task list.

## Features
- Accept written notes and TXT, PDF, DOCX, and CSV files.
- Combine written notes with uploaded file content.
- Extract tasks using Qwen2.5:7b-instruct through Ollama.
- Classify tasks as Study, Work, or Personal.
- Extract explicitly stated deadlines.
- Review and edit extracted results.
- Display task totals, category counts, and missing deadlines.
- Visualize task distribution by category.
- Export the latest edited table as CSV.

## Dataset
Source: Zarnite — Zarn Meeting to Actions
https://huggingface.co/datasets/zarnite/zarn-meeting-to-actions

License: Apache-2.0.
The data preparation script uses source revision 3eacff6.

The prepared dataset contains:
- 1,200 meeting examples.
- 900 training, 150 validation, and 150 test examples.
- 4,800 reference action items.

The reference actions include task, owner, and due_date.
They do not provide Study, Work, or Personal category labels.

See Data_Preparation/README_Data.md and
Data_Preparation/DATASET_NOTICE.md for preparation details
and dataset limitations.

## Data Processing Workflow
Load → Validate → Clean → Explore → Visualize →
Transform → Export → Summary

The preparation module validates the source schema,
normalizes whitespace, handles missing required information,
checks duplicates, and exports cleaned data and a summary.

The application transforms input text into structured tasks,
visualizes the results, and exports the edited task table.

## AI Method
The application uses the pretrained Qwen2.5:7b-instruct model
through a locally running Ollama service.

The model returns structured JSON containing:
- task
- category
- deadline

The Python module validates the response and rejects deadline
phrases that are absent from the input text.

No model training or fine-tuning is performed by this project.

## Requirements
- Python 3.10 or later.
- Ollama installed and running.
- Sufficient memory and storage to run the selected model.
- Internet access for initial package and model downloads.

## Installation
Clone the repository:

    git clone https://github.com/raghadalhajri01-create/smart-task-organizer.git
    cd smart-task-organizer

Create a virtual environment:

    python -m venv .venv

Activate it on Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

Activate it on macOS or Linux:

    source .venv/bin/activate

Install the application dependencies:

    python -m pip install -r requirements.txt

Install Ollama:
https://ollama.com/download

Download the model:

    ollama pull qwen2.5:7b-instruct

Ensure that Ollama is running before extracting tasks.

## Run the Application

    python -m streamlit run app.py

Open the local URL displayed in the terminal.

## Configuration
The AI module supports these environment variables:

- TASK_AI_MODEL: defaults to qwen2.5:7b-instruct
- TASK_AI_OLLAMA_URL: defaults to http://localhost:11434

The interface configuration is stored in .streamlit/config.toml.

## Example
Input:

    Study Chapter 4 tomorrow. Buy groceries.

Expected output:

| Task | Category | Deadline |
|---|---|---|
| Study Chapter 4 | Study | tomorrow |
| Buy groceries | Personal | Not specified |

An unstated deadline is stored as null and may appear as None
in the editable table.

## Tests
Run the data preparation tests:

    python -m unittest discover -s Data_Preparation -v

Install pytest to run the analysis tests:

    python -m pip install pytest

Run the analysis tests:

    python -m pytest tests/test_analysis.py -q

Run the AI evaluation with Ollama and the model available:

    python tests/evaluate_ai.py

## Evaluation
The recorded AI evaluation uses five manually prepared cases.
It compares task, category, and deadline values using strict
matching after normalizing capitalization and whitespace.

The recorded results are:
- Precision: 80%
- Recall: 80%
- F1 score: 80%

One deadline was returned as "Monday" instead of "on Monday",
which was counted as a mismatch.

These results describe the small evaluated set, not overall
accuracy across all possible inputs.

See:
- tests/evaluation_report.md
- tests/interface_test_report.md

## Limitations
- The project is designed and evaluated for English inputs.
- AI extraction and classification can contain errors.
- Deadline wording differences can affect strict evaluation.
- The public dataset does not contain category labels.
- The recorded AI evaluation covers only five cases.
- Long documents may exceed the processing time limit.
- Scanned PDFs may not provide extractable text.
- DOCX extraction currently reads paragraph text.
- Results should be reviewed before use.

## Team
- Mada Abdulrahman Alghamdi
- Raghad Obaid Alhajri
- Saba Mubarak Alzahrani
- Mashael Nazih Alnasr
- Noran Deya Almohsin

## AI Assistance
Development assistance is documented in AI_USAGE.md.
External datasets and models are acknowledged in the project.
