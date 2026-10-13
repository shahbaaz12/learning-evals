# Retriever golden dataset

`goldens.json` contains 24 AI-prepared questions and relevance labels:
two questions for each of the ten fables, plus four questions that combine
evidence from different fables. Labels were selected by reading the source
chunks, without using retrieval results. They are pending human review.

## Fields

| Field | Purpose |
| --- | --- |
| `id` | Stable question ID |
| `question` | Input to the retriever |
| `relevant_chunk_ids` | Relevant chunks against which Python calculates Recall@k |
| `reference_answer` | Short source-grounded answer to clarify the intended facts |
| `evidence` | A supporting excerpt for each listed chunk ID, to help review labels |

The reference answer and excerpts are for reviewing the labels. The retriever
receives only the question. The scorer compares chunk IDs; no LLM judge is used.

## Relevance rule

A relevant chunk directly supports at least one factual part of the reference
answer. Include all such chunks, including overlapping passages that each contain
support. Shared names, setting, or keywords alone are insufficient.

For example, `q001` asks why the villagers ignored the real wolf warning.
`Classic_Fables_Collection:2:3` directly states that they remembered the boy's
two tricks. Other chunks that merely mention the boy or wolf are not labelled
relevant to that question.

Each question currently has one to three relevant chunks. For a question with
three relevant chunks, retrieving two of them gives Recall@k = 2/3. Finding any
one supporting passage is a different metric; it does not mean full chunk recall.

## Before evaluation

Review the questions and labels against `../dataset/chunks.json`. Read the entire
collection when checking whether any relevant chunk has been missed; excerpts
only demonstrate support for the listed chunks.

`goldens_metadata.json` records the authoring status, chunk settings, and a
SHA-256 fingerprint of the chunk file. These labels belong to the current
600-character / 100-character-overlap collection. If the PDF, extraction, chunk
settings, or chunk file changes, recheck the labels before using this dataset.

Keep these goldens fixed while comparing retrieval settings. Fresh questions
can be added as a separate set to check behavior beyond the examples used for tuning.
