# Project 1: email categorization evaluation

## What we are trying to achieve

Check whether an LLM assigns the correct category to a customer email. Learn
how a golden dataset and a simple accuracy score form an evaluation.

## The idea

Give the model an email's subject and body. It returns one of three labels:
`complaint`, `feedback` or `general_query`. Python compares that label with the
reference label. Accuracy is correct predictions divided by evaluated emails.

An unresolved problem takes priority over feedback, which takes priority over a
general query. Use the same category rules when labeling and prompting.

## Setup

Complete the [parent setup](../README.md#setup). From the repository root:

```powershell
cd 1_email_categorization_eval
```

Select the shared root `.venv` kernel. New predictions need `GROQ_API_KEY` in
the root `.env`.

1. Review labels in `categorization/manual-categorization.ipynb`. Set its
   `project_root` to your local Project 1 folder before labeling.
2. Run `prompt/prompt_generator.ipynb` with `prompt/` as its working directory
   to save the classification prompt.
3. Run `email_eval.ipynb` with this project folder as its working directory.
   Generate predictions, score them, and inspect incorrect classifications.

To inspect existing predictions without model calls, import `json` and `Path`
from `pathlib`, then run the comparison and review cells in `email_eval.ipynb`.
Skip the model and batch-generation cells.

## Docs used

`docs/dataset/emails.json` contains 50 example food-delivery emails. Each has an
ID, subject and body. There is no external document retrieval in this project.
`prompt/saved_template.json` contains the classification instructions.

## Goldens

`docs/goldends/goldens.json` contains the expected category for each email ID.
`manual_labels.json` is separate labeling progress; its included partial record
does not prove that all 50 exported labels received human review.

The classifier receives email text and category instructions. Expected labels
are used only by the scorer. Saved predictions are in
`docs/evaluatedds/evaluated.json`; timestamped accuracy reports are in
`docs/evalresults/`.

## Folder structure

```text
1_email_categorization_eval/
  docs/
    dataset/                  # 50 source emails
    goldends/                 # Reference labels and labeling progress
    evaluatedds/              # Model predictions
    evalresults/              # Accuracy reports
  categorization/             # Manual-labeling notebook
  prompt/                     # Prompt notebook and saved template
  email_eval.ipynb             # Main evaluation notebook
  readme.md
```

Inspect a failed email, change one prompt instruction, and compare accuracy on
the same golden dataset. Review fresh examples separately before generalizing.
