# Project 2: Fables Retriever Evaluation

Learn programmatic evaluation by checking whether a retriever finds the fable
passages needed to answer a question. The source is `Classic_Fables_Collection.pdf`:
a cover followed by ten fables, each on its own page.

## Folder structure

```text
2_fables_retriever_eval/
├── docs/
│   ├── dataset/       # Source PDF and extracted chunks.json
│   ├── goldends/      # Questions with human-reviewed relevant chunk IDs
│   ├── evaluatedds/   # Retrieved chunk IDs for each question
│   └── evalresults/   # Per-question scores and overall results
├── models/            # Retrieval model configuration, as needed
├── prompts/           # Reserved for any prompts needed later
├── tools/             # Simple extraction and evaluation helpers, as needed
├── create_vectordb.py # PDF loading, chunking, and Chroma indexing
├── readme.md
└── retriever_eval.ipynb
```

Place the fables PDF in `docs/dataset/`. Keep its original filename.
Use the shared Python environment at the `eval-genius` root; do not run
`uv init` again inside this folder. Open the notebook in VS Code and select
the root `.venv` kernel.

## Approach

1. Inspect the PDF, skip the cover, and load each fable page as a LangChain Document.
2. Split pages with `RecursiveCharacterTextSplitter`: chunk size 600 characters,
   overlap 100 characters. Assign chunk IDs and export `docs/dataset/chunks.json`.
3. Embed the chunks with the local `BAAI/bge-small-en-v1.5` model and add them
   to a LangChain Chroma vector store using cosine distance.
4. Create questions, manually identify all relevant chunk IDs, and retrieve the
   top k chunks for each question.
5. Use Python to compare retrieved chunk IDs with the human-reviewed reference IDs.
6. Calculate Recall@k for each question and average across questions.
7. Inspect missed documents, change one retrieval setting, and compare results.

```text
Recall@k = relevant chunks retrieved in the top k / total relevant chunks
```

Humans prepare the relevance labels. Python produces the evaluation score.
An embedding model may support retrieval, but an LLM judge is not needed.
Answer generation is outside this project's scope.

## Create the vector database

From the repository root, run:

```powershell
uv run python 2_fables_retriever_eval/create_vectordb.py
```

`create_vectordb.py` reads the PDF, excludes the cover, splits its ten fable
pages into 43 chunks, exports `docs/dataset/chunks.json`, and indexes the chunks
in Chroma. It uses the same chunk text, metadata, and IDs as the original
notebook, so the current golden labels still refer to the same passages.
Its paths are relative to the script location; no absolute checkout path is needed.

`models/vector_store.py` holds the chunk settings, embedding-model name, and
collection name. Both the build script and evaluation notebook use these settings.

## Run and compare evaluations

Open `retriever_eval.ipynb` in VS Code and select the root `.venv` kernel.
Restart the kernel after the refactor, then run the cells from top to bottom.
The working directory may be the repository root or the Project 2 folder.

1. Open the existing vector database and load the 24 golden questions.
2. Set `baseline_k`, run the baseline, and save its report.
3. Set `candidate_k`, run the candidate, and save its report.
4. Compare per-question recall and the average recall and precision.

Changing only k does not require rebuilding the vector database. After editing
a helper module, restart the notebook kernel so Python loads the changed code.

The [AI-prepared golden dataset](docs/goldends/readme.md) contains question inputs,
reference chunk IDs, and supporting evidence for human review. Only the questions
are sent to the retriever. Recall and precision are calculated by comparing IDs.

## Reusable helpers

| File | Responsibility |
| --- | --- |
| `models/vector_store.py` | Shared settings and `load_vector_store()` |
| `tools/evaluation.py` | `evaluate_retriever(vector_store, goldens, k)` returns per-question scores and averages |
| `tools/results.py` | `save_results`, `print_results`, `print_comparison`, and optional `print_misses` |

Every call to `save_results` creates a new timestamped JSON report under
`docs/evalresults/`, including k, chunk settings, embedding model, question count,
average recall and precision, and per-question retrieval details. Existing
baseline and candidate reports are preserved.

The earlier experiment measured 80.56% recall / 44.44% precision at k=3 and
95.14% recall / 34.17% precision at k=5. These are results for this question set,
not an estimate of performance on unseen questions.

The embedding model downloads on the first run. Chroma saves the index under
`chroma_store/`, which is ignored by Git. The collection is named
`classic_fables_600_100_cosine` to distinguish these chunks from the earlier
whole-fable collection.

`chunks.json` records each chunk's text, source filename, PDF page, and chunk ID.
Keep the PDF and chunking settings fixed when comparing retrieval runs. Changing
document boundaries requires reviewing the golden chunk IDs. The recursive
splitter preserves text boundaries where possible, so chunk lengths and actual
overlap can vary.

The earlier `fables.json` export is retained as a reference; the updated workflow
uses LangChain Documents and `chunks.json` instead.
