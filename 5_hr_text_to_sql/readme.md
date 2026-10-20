# Project 5: HR text-to-SQL model evaluation

## What we are trying to achieve

Choose a model that answers HR questions correctly within a pilot budget.
Evaluate the returned answer table, rather than the wording of generated SQL.

## The idea

HR asks a question in plain English. A model writes SQL, SQLite executes it,
and Python compares the rows with a saved correct result. Different SQL can
pass if it produces the same requested values and ordering. There is no LLM judge.

Compare six questions—two simple, two intermediate and two difficult—across the
Gemini/Groq candidates. Check answer accuracy first, then latency and estimated
cost. The planning budget is INR 10,000/month at 1,000 requests/day.

## Setup

Complete the [parent setup](../README.md#setup). From the repository root,
prepare the fictional fixture and reference results if rebuilding them:

```powershell
uv run python 5_hr_text_to_sql/create_database.py
uv run python 5_hr_text_to_sql/create_goldens.py
```

Open `hr_model_eval.ipynb` with the shared root `.venv` kernel. It supports the
repository root or this project folder. Saved comparisons are displayed with
`RUN_STEP6 = False`. The single-question demonstration has a separate `RUN_LIVE`
flag. Enable them only when you want fresh model calls using `GROQ_API_KEY` and
`GOOGLE_API_KEY` in the root `.env`.

## Docs used

The schema follows the [MySQL Employees guide](https://dev.mysql.com/doc/employee/en/employees-installation.html),
adapted to SQLite. It has six tables: employees, departments, department
assignments, managers, titles and salaries. The 24 employees and five departments
are fictional; this is not a subset of the official employee records.

- `docs/dataset/schema.sql` and `seed.json`: structure and fictional data.
- `employees.sqlite`: the local database; no MySQL server is required.
- `business_rules.md`: reporting date, active rows, salaries, ties and ordering.
- `provenance.md`: source attribution, adaptation notes and schema license.
- `questions.json`: the six HR questions.
- `budget.json` and `active_models.json`: planning assumptions and model settings.

The reporting date is fixed at 2026-10-01 and salaries are annual INR amounts.
Follow the business rules rather than substituting today's date.

## Goldens

`docs/goldends/goldens.json` holds each question, reference SQL, expected columns
and expected result rows. Each reference query and result also has its own file.
The six topics are departments, 2024 hires, department headcount/average salary,
above-average earners, top salary ranks with ties, and raises of at least 10%.

The references are AI-prepared, execution-validated and checked against
independently calculated values. Human review is pending. Reference SQL and
expected results never enter the model prompt.

A matching answer table scores 1; an incorrect table or SQL error scores 0.
Accuracy is correct results divided by six. Historical measured comparisons
are in `docs/evalresults/live_comparison.json`; they are not current price or
availability guarantees.

## Folder structure

```text
5_hr_text_to_sql/
  docs/
    dataset/             # Schema, fixture, database, questions and model budget
    goldends/            # Reference SQL and correct result tables
    evaluatedds/         # Model SQL, actual rows and token usage
    evalresults/         # Accuracy, latency, cost and model comparisons
  models/                # Settings, candidate selection and provider requests
  prompts/               # Text-to-SQL instructions
  tools/                 # SQL execution, scoring, budgeting and reports
  create_database.py     # Build the fictional SQLite fixture
  create_goldens.py      # Execute and save reference answers
  refresh_models.py      # Optional model-shortlist refresh
  verify_project.py      # Offline fixture/evaluator checks
  hr_model_eval.ipynb    # Main evaluation notebook
  readme.md
```

Inspect expected and actual rows for a failed question, change one prompt
instruction, and compare the same six questions again.
