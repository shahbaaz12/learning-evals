# Project 3: Human Evaluation of a Fables Chatbot

This project checks how helpful a chatbot's answers are.

The chatbot searches the fables for relevant passages and uses an LLM to answer
15 questions. This is a simple RAG: **retrieve text, then generate an answer**.

Jack, Jane, and Jill each give an answer a score from 1 to 5 and a short reason.
Python can then average their scores and show where they disagree.

## The flow

```text
Fables PDF -> chunks -> vector database -> question -> chatbot answer
           -> Jack / Jane / Jill ratings -> combined score
```

## What each folder is for

| Folder | What goes inside |
| --- | --- |
| `docs/dataset/` | The source PDF, complete fable texts, and extracted chunks |
| `docs/goldends/` | The 15 questions and the helpfulness rubric (scoring guide) |
| `docs/evaluatedds/` | Saved chatbot answers and the passages used to produce them |
| `docs/ratings/` | Jack, Jane, and Jill's rating files, grouped by response run |
| `docs/evalresults/` | Saved combined-score reports |
| `models/` | Shared settings, the embedding model, the vector store, and the answer model connection |
| `prompts/` | Instructions given to the chatbot |
| `tools/` | Helpers for generating answers, collecting ratings, saving files, and calculating scores |
| `tests/` | Checks that rating collection and score calculation work correctly |
| `chroma_store/` | The generated local vector database; ignored by Git |

## The main files

- **`create_vectordb.py`** reads the PDF, splits the ten fables into 43 chunks,
  and builds the vector database. Run it before generating new answers.
- **`human_eval.ipynb`** creates the simple RAG, generates or loads saved answers,
  and combines completed ratings.
- **`rate_answers.ipynb`** lets one reviewer read and rate five answers at a time.
  Rerun the rating cell for the next five; progress is saved.

## How to use it

Use the shared environment at the repository root. Open notebooks in VS Code
and select that root `.venv` as the kernel. Do not run `uv init` again.

**To generate new answers**, run these commands from the repository root:

```powershell
uv sync --locked
uv run python 3_fables_human_eval/create_vectordb.py
```

Put `GROQ_API_KEY` in the root `.env`, then run the preparation and generation
steps in `human_eval.ipynb`. The current answer model is
`openai/gpt-oss-120b`. Settings live in `models/config.py`; the default search
returns five chunks. Changing only that number does not require rebuilding the index.

**To use existing answers**, run the project-path cell in `human_eval.ipynb`
and skip to **Select a saved response run**. This needs no model calls or API key.

Then:

1. Confirm the response run you want to evaluate.
2. Open `rate_answers.ipynb` and set the reviewer name and matching response filename.
3. Read the rubric and give each answer a score and a brief reason.
4. Use a separate run-specific rating file for each reviewer.
5. Once all 45 ratings are filled, return to `human_eval.ipynb` and run
   **Combine completed ratings** when you want the report.

Run notebook cells individually. Their working directory can be the repository
root or this project folder. Restart the kernel after editing imported helpers
or switching between projects.

## How the scores work

The rubric defines every score from 1 (unhelpful) to 5 (fully helpful).

```text
Question score = (Jack + Jane + Jill) / 3
Overall score = average of the 15 question scores
```

A score is reported out of 5. The report also shows each reviewer's average and
questions where scores differ by 2 or more. All reviewers must rate the same
saved answers using the same rubric. Missing scores are not treated as zero.

Each new answer run gets its own file and rating folder, so earlier experiments
remain available. The root-level `docs/ratings/jack.json`, `jane.json`, and
`jill.json` files are blank templates; use the files inside the run's subfolder.

## Included practice ratings

The rating notebook currently selects `responses_20261014_215116_945329.json`.
Its three rating files contain 15 entries each. The first five existing ratings
per person were preserved; the remaining ten were filled as **simulated practice
data** at the user's request:

- Jack gives every remaining answer 5.
- Jill gives strict scores.
- Jane gives random scores from 1 to 5.

Those generated entries are marked `rating_origin: simulated`. They demonstrate
the workflow and do not establish actual human judgments about answer quality.
The earlier response run still has blank rating sheets. Questions and the rubric
also remain AI-prepared drafts for human review.

## Check the scoring code

From the repository root:

```powershell
uv run python -m pytest 3_fables_human_eval/tests -q --import-mode=importlib -o pythonpath=3_fables_human_eval
```

These checks use synthetic test data and do not change the project ratings.
