# Project 1: Email Categorization Evaluation

This project evaluates an LLM that categorizes customer emails for a
food-delivery application. It teaches the basic evaluation loop using a small,
inspectable dataset and a deterministic Python scorer.

The LLM predicts a category. Human reference labels define the expected
category. Python compares the two; no LLM judge is used to calculate accuracy.

## Task and category rules

Input: an email's subject and body. Output: exactly one category label.

| Label | Meaning |
| --- | --- |
| `complaint` | Reports an unresolved problem or requests a remedy, such as a refund or replacement |
| `feedback` | Gives praise, appreciation, or a suggestion; includes thanks after an issue is resolved |
| `general_query` | Asks for information without reporting an unresolved problem |

For mixed intents, prioritize `complaint`, then `feedback`, then
`general_query`. Apply the same definitions when labeling data and writing
the classifier prompt.

## Folder structure

```text
1_email_categorization_eval/
├── categorization/
│   └── manual-categorization.ipynb
├── docs/
│   ├── dataset/
│   │   └── emails.json
│   ├── goldends/
│   │   ├── manual_labels.json
│   │   └── goldens.json
│   ├── evaluatedds/
│   │   └── evaluated.json
│   └── evalresults/
│       └── result_<timestamp>.json
├── prompt/
│   ├── prompt_generator.ipynb
│   └── saved_template.json
├── email_eval.ipynb
└── readme.md
```

## How the data works

| File | Purpose | Record fields |
| --- | --- | --- |
| `docs/dataset/emails.json` | Source inputs: 50 example emails | `id`, `subject`, `body` |
| `docs/goldends/manual_labels.json` | Saved progress while a person labels emails | Source fields plus `expected_output` |
| `docs/goldends/goldens.json` | Reference labels used by the scorer | Source fields plus `expected_output` |
| `docs/evaluatedds/evaluated.json` | Saved LLM predictions | Source fields plus `predicted_output` |
| `docs/evalresults/result_<timestamp>.json` | A timestamped scoring report | `summary` and per-email `details` |

Stable email IDs connect the files. The included golden dataset has 20
`feedback`, 15 `complaint`, and 15 `general_query` labels. Label by meaning;
these counts are not quotas to force during manual review.

The committed labeling-progress file currently contains one record, while
the golden export contains 50. They are separate artifacts. To create your own
human-reviewed reference, complete the labeling notebook and review all labels
before exporting. Do not assume the progress file documents review of the
entire included export.

Expected labels are used only by the scorer. The classifier receives the
email subject, body, and prompt instructions.

## Setup and notebook paths

Complete the [root setup](../README.md#setup), then select the shared root
`.venv` kernel in VS Code. Keep `.env` at the repository root.

Notebook working directories matter because the code uses relative paths:

| Notebook | Path requirement |
| --- | --- |
| `categorization/manual-categorization.ipynb` | Update `project_root` in its first code cell to your local Project 1 folder; the supplied path points to the original Windows checkout |
| `prompt/prompt_generator.ipynb` | Run with `prompt/` as the working directory so `saved_template.json` is saved there |
| `email_eval.ipynb` | Run with `1_email_categorization_eval/` as the working directory so `docs/`, `prompt/`, and `../.env` resolve correctly |

Check the working directory with `Path.cwd()` after importing `Path` from
`pathlib`. If necessary, use the notebook's `%cd` command with the full path
to the appropriate directory before running its existing cells.

## Workflow

1. **Review or create golden labels.** Open
   `categorization/manual-categorization.ipynb`. Read and label emails in batches
   of five. Each valid label is saved to the progress file. Review labels,
   optionally correct them, and export the final golden dataset. Export checks
   coverage, unique IDs, category validity, and unchanged source text. Run cells
   individually because labeling requires input and the correction step is optional.

2. **Prepare the prompt.** Run `prompt/prompt_generator.ipynb` to save a
   LangChain `ChatPromptTemplate` in `prompt/saved_template.json`. It contains
   category rules and placeholders for the subject and body. No model call is
   made in this notebook.

3. **Try one prediction.** In `email_eval.ipynb`, load the prompt and source
   emails, format the first email, and invoke the model. The current code uses
   LangChain's Groq integration with `qwen/qwen3.8-27b` and `temperature=0`.
   If that model is unavailable to your account, set an available model ID in
   the model-creation cell.

4. **Generate the prediction dataset.** Run the batch classification cell.
   It predicts one label per email and writes `docs/evaluatedds/evaluated.json`
   after the whole loop completes. A successful rerun replaces that file.

5. **Score and inspect.** Run the comparison cell to match predictions with
   golden labels by ID. It saves a new timestamped report, then the review cell
   displays the email text and labels for incorrect predictions.

6. **Improve and compare.** Inspect failures, change one prompt instruction,
   regenerate its saved template, reload it, and generate new predictions.
   Score the same golden dataset again and compare results. Keep the dataset
   fixed during this comparison; later, try fresh examples as a separate check.

## Accuracy and saved results

```text
Accuracy (%) = correct predictions / evaluated emails × 100
```

The scorer compares `predicted_output` with `expected_output` using exact
string equality after the model output has been stripped of surrounding
whitespace. Extra explanations or different label spellings count as errors.

Reports contain the scoring time, total evaluated, correct and incorrect
counts, accuracy percentage, and the expected/predicted labels for each email.
The two included reports each record 50 correct predictions out of 50 (100%).
That describes these examples; it does not establish accuracy on unseen emails.

## Scoring without model calls

You can inspect the existing prediction file and score it without an API key.
In `email_eval.ipynb`, run the comparison cell, then the incorrect-prediction
review cell. If starting from a fresh kernel, first import `json` and
`Path` from `pathlib`. Set the working directory as described above.

The batch loop saves only when every model call succeeds. If a generation run
fails, an older prediction file can remain. Scoring that file evaluates the
older predictions; a new report timestamp records scoring time, not proof of
a successful new generation run. Confirm which predictions you are scoring.
The current reports do not record a model ID or prompt version.
