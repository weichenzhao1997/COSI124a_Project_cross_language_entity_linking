# Cross-Language Medical Entity Linking

## Overview

This project investigates **medical entity linking (NEL)** across three languages — **English**, **Simplified Chinese**, and **Traditional Chinese** — using the [ICD-11](https://icd.who.int/en) ontology as the target knowledge base.

Given a disease mention extracted from clinical or biomedical text, the task is to map it to the correct ICD-11 concept URI. The core challenge is cross-lingual: English and Chinese corpora share overlapping concept invenctory, but their surface forms are written in entirely different scripts, and pre-trained biomedical encoders such as SapBERT were primarily trained on English UMLS synonyms.

A particular focus of this work is **Traditional Chinese**, a severely under-resourced language in biomedical NLP — existing ontologies such as UMLS provide no Traditional Chinese coverage, and ICD-11 only incidentally matches Traditional Chinese terms that overlap with Simplified Chinese characters. This project establishes an evaluation protocol for Traditional Chinese MEL and quantifies the performance gap between Traditional Chinese, Simplified Chinese, and English under identical retrieval conditions, providing a reproducible benchmark for future work on low-resource clinical NLP.

### Corpora

| Corpus | Language | Source |
|---|---|---|
| `english_ncbi` | English | NCBI Disease corpus |
| `simp_chinese` | Simplified Chinese | TwiMed-style biomedical corpus |
| `trad_chinese` | Traditional Chinese | TwiMed-style biomedical corpus |

### Ontology

We assign **ICD-11 Foundation URIs** as concept identifiers rather than UMLS CUIs, because UMLS does not provide Chinese-language coverage. Concept labels are matched against the ICD-11 API.

> **Important caveat on Traditional Chinese coverage:** The ICD-11 API does not formally support Traditional Chinese. It performs Simplified Chinese matching and incidentally accepts some Traditional Chinese input when characters overlap between the two scripts. As a result, the 33.2% ICD-11 match rate for Traditional Chinese reflects terms that share written forms with Simplified Chinese — not true Traditional Chinese linking. English and Simplified Chinese achieve 73.0% and 69.3% coverage respectively.

### Approach

Experiments use **SapBERT** (`cambridgeltl/SapBERT-from-PubMedBERT-fulltext`) as the mention encoder. Each disease mention and each concept label are encoded into a shared embedding space; retrieval is performed via FAISS nearest-neighbour search. Two index construction strategies are compared:

- **Unenriched index** — one vector per concept (canonical ICD-11 label only)
- **Enriched index** — one vector per concept representation: canonical label + all training-set surface forms mapped to that URI

A key preprocessing variable is whether Traditional Chinese surface forms are used as-is or first converted to Simplified Chinese via **OpenCC** (`t2s`), which substantially improves `trad_chinese` retrieval accuracy.

---

## Repository Structure

```
.
├── original_data/          # Raw, unprocessed source corpora
├── data_conversion/        # Scripts to convert corpora to unified JSONL format
├── processed_corpus/       # Processed corpora with ICD-11 labels
│   └── Combined/           # Train / dev / test splits across all three corpora
├── experiments/            # Jupyter notebooks for each experiment
├── results/                # Saved per-entity JSONL results and summary CSVs
├── analyses_output/        # Annotation analysis outputs
├── assign_cuis_ICD-11.py               # ICD-11 labeling (no translation)
├── assign_cuis_ICD-11_with_translation.py  # ICD-11 labeling (with OpenCC)
└── analyse.py              # Annotation analysis script
```

---

## Data

### Raw Corpora

Original, unprocessed source files: [original_data/](original_data/)

Processing scripts (convert to unified JSONL, retain disease labels): [data_conversion/](data_conversion/)

### Processed Splits

All splits are in JSONL format. Each line is one document with an `entities` list; each entity has `surface_form`, `ontology_id` (ICD-11 URI, or `null` if unmatched), and `ontology_label`.

#### Without Traditional Chinese → Simplified Chinese conversion

| Split | Path |
|---|---|
| Train | [no_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl](processed_corpus/Combined/no_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl) |
| Dev | [no_translation/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl](processed_corpus/Combined/no_translation/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl) |
| Test | [no_translation/test/combined_disease_corpus_test_with_cuis_icd11_cleaned.jsonl](processed_corpus/Combined/no_translation/test/combined_disease_corpus_test_with_cuis_icd11_cleaned.jsonl) |

#### With Traditional Chinese → Simplified Chinese conversion (OpenCC `t2s`)

| Split | Path |
|---|---|
| Train | [with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned_simplified.jsonl](processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned_simplified.jsonl) |
| Dev | [with_translation/dev/combined_disease_corpus_dev_with_cuis_icd11_cleaned_simplified.jsonl](processed_corpus/Combined/with_translation/dev/combined_disease_corpus_dev_with_cuis_icd11_cleaned_simplified.jsonl) |
| Test | [with_translation/test/combined_disease_corpus_test_with_cuis_icd11_cleaned_simplified.jsonl](processed_corpus/Combined/with_translation/test/combined_disease_corpus_test_with_cuis_icd11_cleaned_simplified.jsonl) |

> **Note:** An earlier translation strategy produced a lower-quality train split: [with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl](processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl). Prefer the `_simplified` version above.

---

## ICD-11 Labeling

ICD-11 URIs are assigned by querying the ICD-11 Foundation API with each entity's surface form.

| Script | Description |
|---|---|
| [`assign_cuis_ICD-11.py`](assign_cuis_ICD-11.py) | Labels entities using surface forms as-is (no script conversion) |
| [`assign_cuis_ICD-11_with_translation.py`](assign_cuis_ICD-11_with_translation.py) | Converts Traditional Chinese to Simplified Chinese via OpenCC before querying |

---

## Annotation Analysis

| Item | Description |
|---|---|
| [`analyse.py`](analyse.py) | Computes corpus-level statistics and label coverage |
| [`analyses_output/`](analyses_output) | Output files from annotation analysis |

---

## Experiments

All experiments use frozen SapBERT with a FAISS `IndexFlatIP` index (cosine similarity on L2-normalised embeddings). Evaluation metrics are Acc@1, Acc@5, and Acc@10 over entities with a non-null `ontology_id`.

> **Note:** All further experiments should use the **enriched index** with the **translated corpus** (OpenCC `t2s`): [`with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned_simplified.jsonl`](processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned_simplified.jsonl)

### Experiment 1 — Frozen SapBERT, Unenriched Index, No Translation

Baseline: one canonical ICD-11 label per concept URI in the index. Traditional Chinese surface forms encoded as-is.

| | Notebook | Results |
|---|---|---|
| Notebook | [frozen_sapbert_baseline_no_translation.ipynb](experiments/frozen_sapbert/frozen_sapbert_baseline_no_translation.ipynb) | [results/frozen_sapbert/v1-unenriched_index/](results/frozen_sapbert/v1-unenriched_index) |

### Experiment 1b — Frozen SapBERT, Enriched Index, No Translation

Same as Experiment 1, but the concept index is enriched with all training-set surface forms per URI in addition to the canonical label. Top-10 retrieval deduplicates by URI after fetching 100 raw vectors.

| | Notebook | Results |
|---|---|---|
| Notebook | [frozen_sapbert_baseline_enriched_index.ipynb](experiments/frozen_sapbert/frozen_sapbert_baseline_enriched_index.ipynb) | [results/frozen_sapbert/v2-enriched_index/](results/frozen_sapbert/v2-enriched_index) |

### Experiment 2v2 — Frozen SapBERT, Enriched Index, With Translation

Enriched index + Traditional Chinese surface forms converted to Simplified Chinese (OpenCC `t2s`) before encoding. This is the best-performing frozen baseline configuration.

| | Notebook | Results |
|---|---|---|
| Notebook | [frozen_sapbert_baseline_with_translation-v2.ipynb](experiments/frozen_sapbert_with_translation-v2/frozen_sapbert_baseline_with_translation-v2.ipynb) | [results/frozen_sapbert_with_translation/v2/](results/frozen_sapbert_with_translation/v2) |

---

## To Do

- [ ] **Experiment 3:** Fine-tuning SapBERT on the translated, enriched-index training split
