# Smart Task Organizer
AI for Personal Productivity — ARTI303 Final Project

## Project Overview
A Python application that uses AI to turn English notes into
organized tasks. The planned interface will be built with Streamlit.

## Problem
Tasks can get lost in unstructured notes. Manually organizing
them takes time and makes deadlines easy to overlook.

## Target Users
Students and individuals who want to organize their daily tasks.

## Planned Features
- Extract tasks from written notes.
- Classify tasks as Study, Work, or Personal.
- Extract deadlines when explicitly mentioned.
- Allow users to review and edit results.
- Display useful charts.
- Export tasks as a CSV file.

## Example
Input:
"Study Chapter 4 tomorrow. Buy groceries."

Expected output:

| Task | Category | Deadline |
|---|---|---|
| Study Chapter 4 | Study | Tomorrow |
| Buy groceries | Personal | Not specified |

## Project Status
Initial setup. The public dataset and AI model are being selected.

## Team

- Mada Abdulrahman Alghamdi
- Raghad Obaid Alhajri
- Saba Mubarak Alzahrani
- Mashael Nazih Alnasr
- Noran Deya Almohsin

## AI Model

The project uses the pretrained Qwen2.5 7B model through Ollama.

The AI module (`task_ai.py`) performs three functions:
- Extracts tasks from English notes.
- Classifies tasks as Study, Work, or Personal.
- Extracts deadlines when mentioned; otherwise, returns null.

### AI Setup
1. Install Ollama: https://ollama.com/download
2. Download the model:
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```
3. Make sure Ollama is running before using the application.
