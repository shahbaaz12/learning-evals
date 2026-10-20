# Learning LLM Evals

An evaluation checks whether an AI application does the task we expect. We give
it known examples, compare its outputs with reference answers or a rubric, and
inspect the mistakes. A golden dataset is that set of reference examples.

These small projects follow one loop:

**Define the task → prepare goldens → run the application → score → inspect a failure → improve and compare.**

## Projects

| Project | What we are learning |
| --- | --- |
| [1. Email categorization](1_email_categorization_eval/readme.md) | Compare predicted email categories with reference labels using accuracy |
| [2. Fables retriever](2_fables_retriever_eval/readme.md) | Check whether retrieval finds the right passages using recall and precision |
| [3. Human evaluation](3_fables_human_eval/readme.md) | Rate chatbot helpfulness and combine Jack, Jane and Jill's scores |
| [4. SSC history grader](4_ssc_history_exam_grader/readme.md) | Grade World War I answers with an LLM and compare marks with reference grades |
| [5. HR text-to-SQL](5_hr_text_to_sql/readme.md) | Compare models by the answer tables their SQL produces, latency and cost |
| [6. Product RAG](6_product_rag_eval/readme.md) | Evaluate answers from a product catalog, inspect one failure and improve retrieval |

Each numbered folder has one README explaining its idea, setup, source
material, goldens and folder structure. Work through one project at a time.

## Setup

Install Python 3.12 or later, uv, and VS Code with the Python and Jupyter
extensions. Then:

```powershell
git clone https://github.com/shahbaaz12/learning-evals.git
cd learning-evals
uv sync --locked
code .
```

For this existing checkout, open `eval-genius` and run `uv sync --locked` there.
All six projects share this root environment. Do not run `uv init` inside each
numbered folder.

For new model calls, create a `.env` at the repository root:

```dotenv
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key
```

Projects 1, 3 and 4 use Groq. Projects 5 and 6 use Groq and Google. Project 2
uses local embeddings; its first model download needs internet. Saved outputs
and scores can be inspected without new model calls; follow each README's
notebook instructions.

Open a project's notebook in VS Code and select the Python interpreter in the
root `.venv` as its kernel. Run cells individually. Restart the kernel when
switching projects or editing imported helper files.

## Repository structure

```text
learning-evals/                 # This checkout is named eval-genius
  1_email_categorization_eval/
  2_fables_retriever_eval/
  3_fables_human_eval/
  4_ssc_history_exam_grader/
  5_hr_text_to_sql/
  6_product_rag_eval/
  README.md
  pyproject.toml                # Shared dependencies
  uv.lock                       # Locked package versions
  requirements.txt              # Dependency list for reference
  .env                          # Local keys; ignored by Git
  .venv/                        # Shared environment; ignored by Git
```

Inside each project, `docs/dataset` holds inputs, `docs/goldends` holds
references, `docs/evaluatedds` holds model outputs, and `docs/evalresults` holds
scores. Models, prompts and tools stay separate from the learning notebook.
Project 1 keeps its original `prompt/` and `categorization/` arrangement.

AI-prepared labels and simulated ratings are identified in the project READMEs.
Review them before treating the results as agreement with real human judgments.
