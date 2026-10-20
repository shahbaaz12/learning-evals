# Project 6: simple product RAG evaluation

## What we are trying to achieve

Check whether a product assistant retrieves useful evidence and gives complete,
supported answers. Understand one failure, change one retrieval setting, and
compare the same question again.

## The idea

A local embedding model helps retrieve product documents. Groq generates an
answer from the selected text. One Gemini judge scores it against the source
and reference answer.

The main notebook introduces retrieval and answer quality through Step 6.
Steps 7–10 inspect Q61, identify missing evidence, switch from semantic retrieval
to category retrieval, and compare results. In the saved example, the answer
goes from one of six requested products to all six; completeness rises from
0.17 to 1.0. Read the answers alongside the judge's scores.

## Setup

Complete the [parent setup](../README.md#setup). From the repository root:

```powershell
cd 6_product_rag_eval
```

Open `rag_eval.ipynb` with the shared root `.venv` kernel. It supports this
folder or the repository root and displays saved real results by default.
Run cells in order. Keep `RUN_EXAMPLE = False` to study without new API calls.

To prepare/rebuild the local vector store and reference mappings deliberately:

```powershell
uv run python -m services.prepare_documents
uv run python -m services.prepare_goldens
```

Changing only retrieval mode or k does not require rebuilding embeddings.
For a fresh run of just the one-question comparison, set `RUN_EXAMPLE = True`
in the notebook, or use:

```powershell
uv run python -m services.learning
```

That command runs Q61 in two versions, judges each answer, and saves a separate
`learning_<timestamp>.json` report. It needs `GROQ_API_KEY` and `GOOGLE_API_KEY`
in the root `.env`. The notebook's optional cell uses fresh results immediately;
the terminal command saves its report without replacing the notebook example.

## Docs used

The catalog was copied from `C:\a\pproj\AI\doc\products2` and has 20 products.
`docs/dataset/Hierarchical_Product_Catalog.json` is the indexed source. PDF and
TXT copies are alternate formats. One complete product, including variants,
is one stored document. `chunks.json` and the manifests record prepared inputs
and source/index identity.

Embeddings use `nomic-ai/modernbert-embed-base` locally on CPU. Answers use
`openai/gpt-oss-120b` through Groq; judging uses `gemini-3.5-flash-lite` through
Google. Embedding model files download on first use; fresh answers and judging
use the provider APIs.

## Goldens

`docs/goldends/Hierarchical_RAG_Validation_Questions.json` contains 78 supplied
questions and reference answers. `retrieval_cases.json` adds expected product
IDs for retrieval scoring. Variants map to their parent product; broad questions
can require several products or the whole catalog. Human review is pending.

The answering model receives only the question and source text. The judge also
receives the expected answer. The main notebook reads saved answers and scores
from `docs/evaluatedds/` and `docs/evalresults/`. Earlier experiment reports are
retained as history. [Recorded findings](docs/evalresults/findings.md) show why
reference wording and judge reasoning still need review.

## Folder structure

```text
6_product_rag_eval/
  docs/
    dataset/                 # Catalog, prepared documents and manifests
    goldends/                # Questions, expected answers and product IDs
    evaluatedds/             # Saved answers and the context they received
    evalresults/             # Saved scores and comparisons
  models/                    # Settings, embeddings, vector store and API calls
  prompts/                   # Answer and judge instructions
  services/                  # Preparation, retrieval, RAG and one-example runner
  tools/                     # Retrieval/answer scoring and saved-report helpers
  verify_project.py          # Offline data and routing checks
  rag_eval.ipynb             # Main ten-step learning notebook
  readme.md
```

The generated `chroma_store/` is local and ignored by Git. The project is
complete when you can explain the failure, the one changed setting, and the
before/after result for the same question.
