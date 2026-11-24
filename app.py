import streamlit as st
import pandas as pd
import io

from pypdf import PdfReader
from docx import Document

from task_ai import extract_tasks
from analysis import (
    get_task_summary,
    get_category_chart_data,
    export_tasks_to_csv
)
from pathlib import Path

#Detect and extract text from uploaded files

def extract_text_from_file(uploaded_file):

    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    # TXT files
    if file_name.endswith(".txt"):
        return file_bytes.decode("utf-8-sig")

    # PDF files
    elif file_name.endswith(".pdf"):
        pdf = PdfReader(io.BytesIO(file_bytes))

        pages = []
        for page in pdf.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    # DOCX files
    elif file_name.endswith(".docx"):
        document = Document(io.BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    # CSV files
    elif file_name.endswith(".csv"):
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            encoding="utf-8-sig"
        )

        # Prefer columns containing note text
        preferred_columns = [
            "meeting_text",
            "text",
            "notes",
            "note",
            "content",
            "description"
        ]

        matching_columns = {
            column.lower(): column
            for column in df.columns
        }

        for column in preferred_columns:
            if column in matching_columns:
                selected = matching_columns[column]
                return "\n".join(
                    df[selected].dropna().astype(str)
                )

        # If no suitable column exists, read all columns
        return df.fillna("").to_string(index=False)

    else:
        raise ValueError("Unsupported file format.")


# Page configuration
st.set_page_config(
    page_title="Smart Task Organizer",
    layout="wide"
)

st.divider()


# Load external CSS
css_file = Path(__file__).parent / "style.css"

with open(css_file, encoding="utf-8") as file:
    st.markdown(
        f"<style>{file.read()}</style>",
        unsafe_allow_html=True
    )
# Title

st.markdown("""
<div class="main-title">
    Smart Task Organizer
</div>
<div class="subtitle">
    Organize your tasks. Simplify your day.
</div>
""", unsafe_allow_html=True)


# Input section
st.markdown(
    '<h2 style="color:#26345C;">Enter Your Notes</h2>',
    unsafe_allow_html=True
)

note = st.text_area(
    "Write your notes here:",
    placeholder="Example: Study Chapter 4 tomorrow. Buy groceries.",
    height=180
)

# Upload text file
uploaded_file = st.file_uploader(
    "Upload your notes or document",
    type=["txt", "pdf", "docx", "csv"],
    help="Supported formats: TXT, PDF, DOCX, and CSV"
)


# Organize button
if st.button(
    "✨ Organize My Tasks",
    type="primary",
    key="organize_tasks_button"
):
    try:
        if uploaded_file is not None:
            file_text = extract_text_from_file(uploaded_file)
            note = "\n\n".join(
                part.strip()
                for part in [note, file_text]
                if part and part.strip()
            )

        if not note or not note.strip():
            st.warning("Please enter notes or upload a file.")

        elif len(note) > 30000:
            st.error("Your notes are too long.")

        else:
            with st.spinner("AI is organizing your tasks..."):
                tasks = extract_tasks(note)

            if tasks:
                # Convert new AI results into a DataFrame
                new_tasks = pd.DataFrame(tasks)

                # Reset editor state before updating the table
                st.session_state.pop("task_editor", None)

                if "tasks" in st.session_state:
                    # Combine existing tasks with newly extracted tasks
                    combined_tasks = pd.concat(
                        [st.session_state["tasks"], new_tasks],
                        ignore_index=True
                    )

                    # Remove duplicate tasks (case-insensitive)
                    combined_tasks["_task_key"] = (
                        combined_tasks["task"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .str.replace(r"\s+", " ", regex=True)
                    )

                    combined_tasks = combined_tasks.drop_duplicates(
                        subset=["_task_key"],
                        keep="first"
                    )

                    combined_tasks = combined_tasks.drop(
                        columns=["_task_key"]
                    )

                    # Save unique tasks
                    st.session_state["tasks"] = combined_tasks.reset_index(
                        drop=True
                    )

                else:
                    st.session_state["tasks"] = new_tasks.drop_duplicates(
                        subset=["task"],
                        keep="first"
                    ).reset_index(drop=True)

                st.success("Tasks organized successfully!")

            else:
                st.warning("No tasks were found.")

    except Exception as e:
        st.error(f"An error occurred: {e}")


# Results section
if "tasks" in st.session_state:

    st.divider()

    left_col, right_col = st.columns([4, 1])

    with left_col:
        st.header("📝 Organized Tasks")

    with right_col:
        if st.button("🗑️ Clear All", key="clear_all_button"):
            st.session_state.pop("tasks", None)
            st.session_state.pop("task_editor", None)
            st.rerun()

    # Full-width editable table
    edited_tasks = st.data_editor(
        st.session_state["tasks"],
        num_rows="dynamic",
        use_container_width=True,
        key="task_editor",
        column_config={
            "task": st.column_config.TextColumn(
                "Task",
                required=True
            ),
            "category": st.column_config.SelectboxColumn(
                "Category",
                options=["Study", "Work", "Personal"],
                required=True
            ),
            "deadline": st.column_config.TextColumn(
                "Deadline",
                help="Leave empty if no deadline exists."
            )
        }
    )

    st.caption(
        "You can edit tasks, categories, and deadlines."
    )

    st.session_state["tasks"] = edited_tasks

    # Task Analysis
    st.divider()
    st.header("📊 Task Analysis")

    # Calculate statistics from the edited tasks
    summary = get_task_summary(edited_tasks)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Tasks", summary["total_tasks"])
    col2.metric("Study", summary["category_counts"]["Study"])
    col3.metric("Work", summary["category_counts"]["Work"])
    col4.metric("Personal", summary["category_counts"]["Personal"])
    col5.metric("Without Deadline", summary["without_deadline"])

    # Category Distribution Chart
    st.subheader("Task Distribution by Category")

    chart_data = get_category_chart_data(edited_tasks)

    st.bar_chart(chart_data)

    # CSV Export
    st.subheader("Export Tasks")

    st.download_button(
        label="📥 Download Tasks as CSV",
        data=export_tasks_to_csv(edited_tasks),
        file_name="organized_tasks.csv",
        mime="text/csv",
        key="download_tasks_button"
    )

