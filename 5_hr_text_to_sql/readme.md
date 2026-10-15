# Project 5: choose a model for HR text-to-SQL

HR asks a question in plain English. An LLM writes SQL. SQLite runs the SQL and
returns a table. We compare that table with a saved correct answer to decide
which model works best for this small application.

This follows `Docs/Six.md`: requirements → cost estimate → shortlist → custom
evaluation → model decision. Different SQL can produce the same correct answer.
There is no LLM judge here: the returned values determine correctness.

## Start here

Use the existing shared environment. From the repository root:

```powershell
uv sync --locked
uv run python 5_hr_text_to_sql/create_database.py
uv run python 5_hr_text_to_sql/create_goldens.py
```

The first command rebuilds only the six fixture tables and saves `seed.json`.
The second saves six reference queries and their executed answer tables.
Expected output: 24 employees, five departments, and six validated goldens.
No API key is needed for these commands.

To repeat the offline evaluator and budget checks:

```powershell
uv run python 5_hr_text_to_sql/verify_project.py
```

Open [hr_model_eval.ipynb](hr_model_eval.ipynb) in VS Code and select the root
`.venv` Python kernel. Run cells one at a time. Start from the repository root
or this project folder. Restart the kernel when switching between projects
because their `models` and `tools` folders use the same import names.

## What the data contains

We use the six-table structure linked by the
[MySQL Employees guide](https://dev.mysql.com/doc/employee/en/employees-installation.html),
adapted to SQLite. All employee rows are fictional; this is not the official
full MySQL database. See [provenance](docs/dataset/provenance.md) for sources and
schema license attribution.

| Table | Meaning |
| --- | --- |
| `employees` | Names, birth dates, hire dates |
| `departments` | Department names |
| `dept_emp` | Department assignment history |
| `dept_manager` | Department managers |
| `titles` | Job titles |
| `salaries` | Annual salary history in INR |

The reporting date is fixed at **2026-10-01**. A record is active when its start
date is on or before that date and its end date is after it. There are 20 current
employees, three former employees, and one future hire. Research has no employees.
Salary ties and transfers help expose mistakes. The complete rules are in
[business_rules.md](docs/dataset/business_rules.md).

## Six questions and goldens

| ID | Level | HR question topic |
| --- | --- | --- |
| q001 | Simple | List departments |
| q002 | Simple | Find employees hired in 2024 |
| q003 | Intermediate | Current headcount and average salary for every department |
| q004 | Intermediate | Development employees earning above their department average |
| q005 | Difficult | Two highest distinct salary ranks per department, including ties |
| q006 | Difficult | Current employees with at least a 10% raise over their previous salary |

[questions.json](docs/dataset/questions.json) contains the exact questions.
[goldens.json](docs/goldends/goldens.json) contains questions, reference SQL,
column names, result rows, and fixture identity. Each query and answer table is
also saved separately. Goldens are AI-prepared, execution-validated, and checked
against independently calculated expected values. **Human review is pending.**
Reference SQL and golden answers never enter the model prompt.

## Active models: use your Gemini and Groq keys

The live comparison now uses only the existing root `GROQ_API_KEY` and
`GOOGLE_API_KEY`. No DeepSeek, Anthropic, or OpenAI API account is required.
GPT-OSS is served by Groq, so its key is the Groq key.

The original all-provider leaderboard shortlist remains in
`docs/evalresults/model_shortlist.json` as a planning reference. The active
key-constrained candidates and provider prices are in
[active_models.json](docs/dataset/active_models.json).

| Candidate | Provider | Input USD/M | Output USD/M | Planned monthly INR with reserve |
| --- | --- | ---: | ---: | ---: |
| GPT-OSS 120B | Groq | 0.15 | 0.60 | 1,641.60 |
| GPT-OSS 20B | Groq | 0.075 | 0.30 | 820.80 |
| Qwen 3.8 27B (preview) | Groq | 0.80 | 4.00 | 9,849.60 |
| Gemini 3.5 Flash-Lite | Google | 0.30 | 2.50 | 5,061.60 |

Price sources: [Groq supported models](https://console.groq.com/docs/models)
and [Google standard pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite).
Each row assumes that one model serves all requests; these are alternatives.
Qwen is a preview model whose availability can change.

Your budget is INR 10,000/month at 1,000 requests/day. Plan for 30 days,
1,600 input tokens and 400 output tokens per request, INR 95/USD, and 20% reserve.
The conversion is a planning assumption. Costs cover tokens only, excluding
infrastructure and taxes; no caching discounts are assumed.

```text
Monthly INR = (input tokens x input USD/M + output tokens x output USD/M)
              / 1,000,000 x 1,000 x 30 x 95 x 1.20
```

The Six.md leaderboard exercise is still available in `tools/budget.py` and
`refresh_models.py`. It normalizes coding quality and speed after filtering on
cost, with 90% quality and 10% speed. Refreshing the leaderboard does not change
our explicit Gemini/Groq candidate list.

## Step 6: actual live results

These are measured model outputs, not simulated answers or reference-query scores.
Each candidate answered the same six questions against the same fixture and prompt.

| Model | Correct | Accuracy | Mean request seconds | Projected monthly INR with reserve |
| --- | ---: | ---: | ---: | ---: |
| GPT-OSS 120B | 6/6 | 100% | 1.02 | 816.70 |
| Qwen 3.8 27B | 6/6 | 100% | 0.72 | 4,758.82 |
| Gemini 3.5 Flash-Lite | 6/6 | 100% | 3.09 | 2,706.53 |
| GPT-OSS 20B | 5/6 | 83.33% | 0.89 | 418.10 |

**GPT-OSS 120B is the preferred candidate for this pilot.** It answered all six
correctly, met the approximate three-second latency target, and had the lowest
projected cost among candidates scoring 6/6. Qwen was faster but more expensive.
Gemini's measured mean was slightly above three seconds. This result is specific
to these six examples, which still need human review; use a larger holdout before
making a production decision.

GPT-OSS 20B missed q006: its query calculated percentage raises but omitted the
`at least 10%` filter. It returned 19 employees rather than the correct nine.
This shows why executing valid SQL is not enough: the returned answer must match.

[Live comparison](docs/evalresults/live_comparison.json) references the four
individual timestamped reports. `docs/evaluatedds` contains generated SQL, exact
returned rows, expected rows, token counts, and correctness for every example.
The completed 24-call benchmark is estimated at **INR 1.45** using standard
uncached rates. This excludes diagnostic and interrupted requests and is not an invoice.
Free-tier allowances or provider caching may affect actual billing.

Monthly projections use the actual mean input/output token usage observed in the
six questions, not the larger planning allowance. Reported reasoning tokens are
included where the provider reports them.

## Run or inspect the notebook

Open [hr_model_eval.ipynb](hr_model_eval.ipynb) and run cells in order. Step 6
now defaults to `RUN_STEP6 = False` and displays the saved live results without
new API calls. Set `RUN_STEP6 = True` for a fresh comparison of all four models.
The optional single-question demonstration in Step 5 has its own `RUN_LIVE` flag.

The root `.env` needs only:

```dotenv
GROQ_API_KEY=your_existing_key
GOOGLE_API_KEY=your_existing_key
```

Both keys were verified against authenticated model listings. Listing a model does
not guarantee it can serve a generation request: Gemini 3.8 returned HTTP 503 high
demand, and 2.5 Flash returned HTTP 404. Gemini 3.5 Flash-Lite successfully completed
all six questions and was explicitly selected. These observations are recorded in
[provider_availability.json](docs/evalresults/provider_availability.json).

Groq initially rejected urllib requests; the small client now uses `httpx`.
Qwen hit a rate limit in the rapid batch; a later run with three-second spacing
completed. Fresh Step 6 runs use that pacing. Pauses happen before timing a request
and are not included in the reported latency. Provider errors stop visibly; there
are no automatic retries, silent fallbacks, or invented failure scores.

GPT-OSS uses low reasoning, Qwen uses none, and Gemini 3.5 Flash-Lite uses minimal
thinking. Each request allows 2,048 output tokens. The planning budget's 400 is
an estimate; measured usage determines the final projection. The fixture, prompt,
settings, and per-example results are saved for review.

## How scoring works

- Execute generated SQL against the same read-only database.
- Compare values and requested column positions; column aliases may differ.
- Respect requested row ordering and keep duplicate rows.
- Keep NULL distinct from zero and text distinct from numeric values.
- Round floating values to six decimals only to remove representation noise;
  the questions themselves request two-decimal salary averages and raises.
- A wrong table or SQL error scores 0. A matching table scores 1.

`accuracy = correct tables / 6`. One missed question changes the result by
16.7 percentage points. SQL runs in a tiny separate process so an invalid query
can be recorded as a failed example without `try`/`except`. It is read-only,
limited to 1,000 result rows, and has a five-second SQLite work limit.

Saved reports show overall and per-difficulty accuracy, SQL errors, mean
end-to-end latency, token usage, and cost. The timing includes a small local
process startup overhead. Provider speed rankings do not replace this measurement.

Aim for 6/6 on this pilot, projected monthly spend within budget, and mean latency
near three seconds. Among passing models prefer lower cost, then lower latency.
If none pass, record that outcome. The pilot preference above comes from the saved live results. Six questions need more reviewed examples and a holdout set
before supporting production decisions; manager and title queries are not yet covered.

## Folder roles

```text
5_hr_text_to_sql/
  docs/
    dataset/       # Schema, fictional seed, database, questions, budget, snapshot
    goldends/      # Reference SQL and saved correct result tables
    evaluatedds/   # Timestamped model SQL, returned rows, and token counts
    evalresults/   # Model shortlist and timestamped score/cost reports
  models/          # Paths, prompt assembly, and provider calls
  prompts/         # SQL-generation instructions
  tools/           # Budget, read-only execution, comparison, reporting
  create_database.py
  create_goldens.py
  refresh_models.py
  hr_model_eval.ipynb
  readme.md
```

To learn from a failure, inspect the saved expected and actual rows, change one
prompt setting, and rerun the same questions. Timestamped reports preserve the
previous experiment for comparison.
