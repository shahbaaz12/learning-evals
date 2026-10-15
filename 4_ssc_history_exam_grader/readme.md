# Project 4: SSC History — World War I Grader

This project teaches **LLM-as-a-judge evaluation**. An LLM grades written
answers using a rubric. Python checks the returned marks and measures how
closely they match the reference grades.

These are SSC-level history practice exercises, not official SSC questions
or an official marking scheme.

## What is included

Five questions cover:

1. Long-term causes and the escalation of war in 1914.
2. Opposing camps and countries that joined later.
3. Trench warfare and stalemate on the Western Front.
4. US entry in 1917 and the distinction between armistice and peace.
5. The Treaty of Versailles and its significance.

Each question has five marking dimensions worth 0, 1, or 2 marks.
That makes **10 marks per question and 50 marks per student**.

| Fictional student | Writing profile | Simulated reference total |
| --- | --- | ---: |
| Jack | Casual but informed | 43 / 50 |
| Jill | Perfectionist | 50 / 50 |
| Jane | Not well prepared | 16 / 50 |
| John | Average preparation | 33 / 50 |
| Jake | Unprepared | 0 / 50 |

All five students answer all five questions: **25 answers**.

The reference marks were prepared by an AI assistant through a separate reading
of the answers against the rubric. They include dimension-level reasons and are
labelled **simulated, pending human review**. They are not judgments collected
from real human examiners. Review them before using them as genuine human
reference data.

## The flow

```text
Question + rubric + anonymous student answer
                -> LLM dimension marks
                -> Python calculates the total
                -> compare with reference marks
                -> MAE and grading disagreements
```

The judge sees the question, an ideal factual reference answer, its rubric, and
the student's answer text. It never sees names, personas, or the marks already
assigned in the separate reference-grade file. Marks should follow demonstrated
knowledge, not answer length or writing style.

## Folder roles

| Folder | Contents |
| --- | --- |
| `docs/dataset/` | Student profiles, 25 answers, WWI study notes, and historical source links |
| `docs/goldends/` | Five questions, ideal answers, anchored rubrics, simulated reference grades, and reference metadata |
| `docs/evaluatedds/` | Saved LLM grading runs, created when the notebook grades all answers |
| `docs/evalresults/` | Timestamped MAE reports and per-answer comparisons |
| `models/` | Shared model settings and connection code |
| `prompts/` | The grading instructions |
| `tools/` | JSON handling, model grading, validation, and score calculation |
| `tests/` | Small checks using synthetic test cases |

The main notebook is `wwi_eval.ipynb`. It loads the data, runs the judge,
and compares results. No RAG or vector database is needed.

## How to use it

From the repository root:

```powershell
uv sync --locked
```

Use the existing root `.env` with `GROQ_API_KEY` and the shared `.venv` kernel
in VS Code. Do not run `uv init` again. The current grading model is
`openai/gpt-oss-120b`, configured in `models/config.py`.

Open `wwi_eval.ipynb` and run cells individually:

1. Set the project path and load the dataset.
2. Read the questions, rubric, and one worked reference.
3. Connect the model and optionally grade one answer.
4. Grade all 25 answers and save the model run.
5. Select that run and calculate the comparison report.
6. Inspect the largest grading errors and their dimension-level reasons.

The working directory can be the repository root or Project 4 folder. Restart
the kernel after changing helper files or switching from another project's
`models` or `tools` packages.

The full grading cell makes 25 API calls. If a call fails, the cell stops;
no new complete grading run is saved. Successful reruns create separate files
and preserve earlier runs. A lower provider request limit may require spacing
calls or trying again later.

Once a complete run exists, you can inspect it offline: run the notebook's
path and data-loading cells, skip the model cells, and select the saved run.
The student/reference data can also be inspected without any API calls.

## How the evaluation works

```text
Absolute error = abs(LLM marks - reference marks)
MAE = sum of absolute errors / 25 answers
```

If the reference is 8 and the model awards 6, the error is 2 marks.
Lower MAE means closer agreement. The notebook also shows each student's
reference total, model total, and MAE.

The initial learning target is **MAE <= 1 mark per answer**. This is a practice
threshold, not a production acceptance claim. With simulated references, it
measures agreement with these examples rather than validated human grading.

The code checks complete IDs, legal marks, correct totals, and matching data
fingerprints. If you edit the rubric, answers, or references, create a deliberate
new version and rerun the experiment. Model grades are saved with the prompt and
model settings; comparison reports retain the simulated-reference status.

## Review the history

Read `docs/dataset/wwi_notes.md` and `sources.json` for museum, government,
and archive references. Some student answers intentionally contain historical
errors so the grader has something meaningful to assess; they are examples of
student mistakes, not study notes.

## Verification

From the repository root:

```powershell
uv run python -m pytest 4_ssc_wwi_grader/tests -q --import-mode=importlib -o pythonpath=4_ssc_wwi_grader
```

The checks use synthetic fixtures and do not create fake model runs or change
the reference grades.
