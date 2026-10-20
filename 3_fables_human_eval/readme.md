# Project 3: human evaluation of a fables chatbot

## What we are trying to achieve

Judge how helpful a chatbot's answers are, combine reviewers' scores, and
understand where reviewers disagree.

## The idea

A simple RAG retrieves fable passages and generates an answer. Jack, Jane and
Jill each rate helpfulness from 1 to 5 using the same rubric. Python averages
the three scores per question, then averages across questions.

Reviewers must rate the same saved answers. Missing ratings are not zeroes.

## Setup

Complete the [parent setup](../README.md#setup). To prepare the local index,
run this from the repository root:

```powershell
uv run python 3_fables_human_eval/create_vectordb.py
```

Select the shared root `.venv` kernel in VS Code. New answers need
`GROQ_API_KEY` in the root `.env`.

1. Open `human_eval.ipynb` to generate answers or select a saved response run.
2. Open `rate_answers.ipynb`; choose a reviewer and that same response filename.
   Rate five answers at a time and repeat for the three reviewers.
3. Return to `human_eval.ipynb` to combine the 45 completed ratings.

Both notebooks support the repository root or this project folder. For offline
study, run the path setup and saved-run selection cells, skipping generation.

## Docs used

`docs/dataset/Classic_Fables_Collection.pdf` contains the ten source fables.
`chunks.json` holds the 43 retrieval chunks; `fables.json` holds complete fable
texts so reviewers can read the source. The chatbot sees retrieved passages,
while reviewers can inspect the complete relevant fables.

## Goldens

`docs/goldends/questions.json` contains 15 questions.
`rubric.json` defines helpfulness scores from 1 to 5. This project uses a rubric
rather than one exact reference answer. Questions and the rubric are AI-prepared
and pending human review.

`docs/ratings/` stores separate Jack, Jane and Jill sheets for each response run.
Some included ratings were filled as simulated practice data at your request:
Jack gives 5, Jill is strict, and Jane is random. Those entries are marked
`rating_origin: simulated`; they are not collected human judgments.

## Folder structure

```text
3_fables_human_eval/
  docs/
    dataset/             # PDF, full fables and chunks
    goldends/            # Questions and helpfulness rubric
    evaluatedds/         # Saved answers and retrieved context
    ratings/             # Reviewer sheets grouped by response run
    evalresults/         # Combined scores and disagreements
  models/                # Embeddings, vector store and answer model
  prompts/               # Answering instructions
  tools/                 # Response, rating and score helpers
  tests/                 # Offline scoring checks
  create_vectordb.py     # Source preparation and indexing
  human_eval.ipynb       # Generate/load answers and combine scores
  rate_answers.ipynb     # Collect reviewer scores
  readme.md
```

The local `chroma_store/` is ignored by Git. Inspect disagreements alongside the
answers and reasons; an average alone can hide different reviewer standards.
