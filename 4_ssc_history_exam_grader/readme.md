# Project 4: SSC history exam grader

## What we are trying to achieve

Use an LLM to grade World War I answers against a rubric, then measure how
closely its marks agree with reference grades.

## The idea

Five fictional students—Jack, Jill, Jane, John and Jake—answer five questions.
Each question has five marking dimensions worth 0, 1 or 2 marks: 10 marks per
question and 50 per student.

The judge sees the question, rubric, ideal answer and anonymous student answer.
Student names, personas and separate reference marks are kept out of its input.
Python compares the 25 model grades with the reference grades using mean
absolute error: average `abs(model marks - reference marks)`. Lower is better.

## Setup

Complete the [parent setup](../README.md#setup). Open `wwi_eval.ipynb` in VS Code
and select the shared root `.venv` kernel. Its working directory can be the
repository root or this project folder.

New grading calls need `GROQ_API_KEY` in the root `.env`. Run cells individually:
load the data, read one question and rubric, grade the answers, and compare the
saved grades. To inspect existing results offline, run the path/data cells,
skip model calls, and select a saved grading run.

## Docs used

`docs/dataset/wwi_notes.md` summarizes the history; `sources.json` records its
museum, government and archive sources. The five questions cover causes and
escalation, opposing camps, trench warfare, US entry and armistice, and Versailles.

`students.json` describes the fictional students, and `student_answers.json`
contains their 25 answers. Some answers intentionally contain mistakes; use the
study notes as the factual source. These are practice exercises, not official
SSC questions or an official marking scheme.

## Goldens

`docs/goldends/questions.json` contains the questions, ideal answers and rubrics.
`reference_grades.json` contains marks and reasons for each answer;
`reference_metadata.json` records their origin and data fingerprints.

These reference marks are AI-authored simulations, pending human review. They
are not marks collected from real examiners. The evaluation therefore measures
agreement with these teaching references until a knowledgeable human reviews them.

## Folder structure

```text
4_ssc_history_exam_grader/
  docs/
    dataset/             # WWI notes, sources, students and their answers
    goldends/            # Questions, rubrics and reference grades
    evaluatedds/         # Saved model grading runs
    evalresults/         # MAE and per-answer comparisons
  models/                # Grading-model settings and connection
  prompts/               # Grading instructions
  tools/                 # Grading, validation and score helpers
  tests/                 # Offline grading checks
  wwi_eval.ipynb         # Main evaluation notebook
  readme.md
```

Inspect the largest marking disagreements and their rubric dimensions. Keep the
same questions, answers and references when comparing a prompt improvement.
