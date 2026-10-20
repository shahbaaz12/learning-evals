# What this run teaches

The working assistant retrieves catalog information, asks Groq for an answer,
and saves the answer with its source context. Gemini scores the saved answers.
The main notebook now presents the basic learning loop. This document retains
findings from the earlier, broader evaluation run. Read `latest_run.json` for the experiment identity and timestamped JSON
for individual records.

All 78 candidate answers and all eight safety answers have independent custom
judge scores. The earlier supplementary native DeepEval run was partial due to
repeated Gemini HTTP 503 capacity errors: pipeline 20/27, isolated generator
2/6, order 2/2. Unfinished metrics are not counted as passes or assigned scores.
The isolated Q1 measurements reuse verified identical pipeline inputs and are
labeled accordingly. The unused advanced runners were removed when simplifying the project;
these measurements remain historical records rather than required main-notebook steps.

## Retrieval improved, but that does not guarantee a correct answer

On all 78 questions, semantic retrieval with k=1 found every reference product
for 60 questions. Catalog-aware retrieval found every reference product for all
78. Its mean product-ID recall and precision were both 1.0.

Some broad cases deliberately label the complete catalog as reference evidence.
These are conservative coverage labels, pending human review. The scores do
not prove that every retrieved paragraph is relevant, or that the system will
handle unseen questions equally well.

## A judge can miss an error

In candidate Q75, the generator correctly listed both manufacturers' products,
then added a price comparison. It claimed Meridian's range starts at $279,
while its own answer listed a $149 power unit and a $229 mesh node. The catalog
confirms the starting-price range is $149–$1,499. The answer also added variant
price ranges that the supplied context does not establish.

The independent custom judge nevertheless assigned correctness and faithfulness
of 1.0 to that answer. This is an agent spot check, not a human reference label
and not a replacement model score. It demonstrates why aggregate judge scores
need calibration and factual spot checks.

The opposite happened in Q63: the judge penalized PackTrack One and RouteCharge
65 as outside Mobility. The actual catalog puts both in the Mobility category,
with Travel Accessories as their subcategory. The supplied reference also
includes both. Keep the saved judge score, but flag this reasoning for review.

Q54 and Q60 expose wording problems in the supplied references: they say no
variant node exists, while the JSON has an empty `variants` list. Distinguish
"no available variants" from "no field" before approving these goldens.

## Structured citations need a format check

Ten answers returned bracketed strings such as `[HSC-202]` inside the citations
array, where the prompt requires plain `HSC-202`. The strict check therefore
passed 68 of 78 answers (87.2%). These are formatting failures involving existing
retrieved IDs, rather than ten nonexistent products. Do not silently rewrite
saved predictions to make the metric pass.

## Refusal can be too cautious

For Q78, the generator received the complete catalog and was explicitly told
the catalog was complete. No product has an Enterprise variant. The desired
answer is that the catalog contains no such variant; the model instead returned
`insufficient_context`. Safety probe S8 showed the same behavior.

The deterministic safety checks passed seven of eight probes. Passing probes
means the tested status, public synthetic canary and email-pattern checks
passed. It is not a general security or privacy certification.

## Procedure order is a separate question

The order example compares a generated quick-start answer with the source
sequence. A deliberately reversed version is a synthetic negative control for
the evaluator. It is not a second model prediction. Consult the order report
to see whether the judge penalized the reversed prerequisites.

In this run, the real answer scored 1.0 and the reversed control scored 0.1.
The order rubric therefore distinguished this deliberately wrong sequence.

## Interpret operations honestly

All 78 final candidate answers were produced by the live Groq API. A rate-limit
failure was explicitly retried. Gemini capacity errors were saved as unscored
attempts and retried separately. Final completion therefore differs from initial
completion. Summaries show judge coverage and unknown call costs separately.

Latencies are sequential request measurements, excluding deliberate batch
pauses and cold embedding-model loading. Costs are token-price estimates;
diagnostic calls and interrupted native metric work can add unreported cost.
TTFT was not measured. The six-question regression comparison is a learning
check, not a calibrated production release gate.

The local chat command can collect real feedback into a review queue. There is
no hosted monitoring deployment, production traffic or invented human rating.
Review the supplied answers and mappings before treating them as trusted goldens.
