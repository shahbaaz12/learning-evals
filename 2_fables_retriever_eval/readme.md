# Project 2: fables retriever evaluation

## What we are trying to achieve

Check whether a retriever finds the passages needed to answer a question.
Learn retrieval evaluation before adding answer generation.

## The idea

Split the fables into chunks, embed them locally, and store them in Chroma.
For each question, compare the retrieved chunk IDs with reference IDs.

- Recall@k: relevant chunks retrieved / all reference-relevant chunks.
- Precision@k: relevant chunks retrieved / retrieved chunks.

Compare k=3 with k=5 using the same questions. Python calculates the scores;
this project does not use an LLM judge.

## Setup

Complete the [parent setup](../README.md#setup). From the repository root,
build the local index if it does not exist:

```powershell
uv run python 2_fables_retriever_eval/create_vectordb.py
```

Open `retriever_eval.ipynb` with the shared root `.venv` kernel. Its working
directory can be the repository root or this project folder. Run the baseline,
candidate and comparison cells. No API key is needed; the embedding model
downloads on first use.

## Docs used

`docs/dataset/Classic_Fables_Collection.pdf` contains a cover and ten fables.
Preparation skips the cover and creates 43 chunks using a 600-character chunk
size and 100-character overlap. `chunks.json` records the text, pages and IDs.
The earlier `fables.json` export is kept as a source reference.

`models/vector_store.py` holds shared settings for the local
`BAAI/bge-small-en-v1.5` embeddings and Chroma collection. Changing only k does
not require rebuilding the index.

## Goldens

`docs/goldends/goldens.json` contains 24 AI-prepared questions: two per fable
and four combining evidence from multiple fables. Human review is pending.

Each record has a question, `relevant_chunk_ids`, a reference answer and evidence
excerpts. The retriever receives only the question. The answer and excerpts help
reviewers check the labels; the scorer compares chunk IDs.

A relevant chunk directly supports a factual part of the reference answer.
Include all supporting chunks, including overlapping ones. Shared names alone
are insufficient. Review the entire chunk collection for missing evidence.
`goldens_metadata.json` records the chunk settings and fingerprint. If source
text or chunk boundaries change, review the reference IDs again.

## Folder structure

```text
2_fables_retriever_eval/
  docs/
    dataset/             # Fables PDF and prepared text
    goldends/            # Questions, relevant IDs and reference metadata
    evaluatedds/         # Reserved for separate retrieved outputs
    evalresults/         # Timestamped recall and precision reports
  models/                # Embeddings and vector-store settings
  prompts/               # Reserved; no answering prompt is needed
  tools/                 # Scoring and report helpers
  create_vectordb.py     # PDF loading, chunking and indexing
  retriever_eval.ipynb   # Main evaluation notebook
  readme.md
```

The generated `chroma_store/` is local and ignored by Git. Reports retain the
retrieved IDs and scores for each question, so inspect misses before changing k.
