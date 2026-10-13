# Learning LLM Evals

Small, notebook-based projects for learning how to evaluate LLM applications.
Each project follows the same cycle: define a task, prepare trusted examples,
generate predictions, measure results, inspect failures, and compare improvements.

## Projects

| Project | What it teaches |
| --- | --- |
| [1. Email categorization](1_email_categorization_eval/readme.md) | Golden datasets, LLM classification, exact-match accuracy, and failure analysis |
| [2. Fables retriever evaluation](2_fables_retriever_eval/readme.md) | PDF chunking, Chroma retrieval, programmatic recall and precision, and comparing values of k |

Planned projects cover human evaluation, LLM judges,
model selection, and a RAG evaluation suite. They will be built one at a time.

## Setup

Use Python 3.12+, [uv](https://docs.astral.sh/uv/), and VS Code with the Python
and Jupyter extensions.

```powershell
git clone https://github.com/shahbaaz12/learning-evals.git
cd learning-evals
uv sync --locked
code .
```

All numbered project folders share the root `.venv` and dependencies declared
in `pyproject.toml`. `uv.lock` records the resolved versions. `requirements.txt`
lists the direct dependencies; use `uv sync` for the locked project environment.

Create a `.env` file at the repository root for the current Groq-based classifier:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Open a project notebook and select the Python interpreter inside `.venv` as
its kernel. Work through cells individually. The [Project 1 README](1_email_categorization_eval/readme.md)
explains notebook order, paths, and how to evaluate the included saved predictions
without making model calls. New predictions require a working provider account
and may incur API costs.

The `.env` file, virtual environment, and local caches are ignored by Git.
The notebooks, example data, prompt templates, and evaluation results are tracked.
