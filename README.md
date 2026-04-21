# Cross-Language Entity Linking

## Corpus

Combined train and dev splits are located in [processed_corpus/Combined/](processed_corpus/Combined/).

### Splits
1. The finalized train split with CUIs:  processed_corpus/Combined/train combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

2. The finalized dev split with CUIs: processed_corpus/Combined/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

## ICD-11 Labeling

We assign **ICD-11** labels instead of UMLS labels as originally planned — UMLS does not support Chinese.

> **Note:** The ICD-11 API does not perform true Traditional Chinese matching. It matches against Simplified Chinese and accepts some Traditional Chinese input incidentally when characters overlap.

## Scripts

| Script | Description |
|---|---|
| `assign_cuis_ICD-11.py` | Assigns ICD-11 labels (no translation) |
| `assign_cuis_ICD-11_with_translation.py` | Same as above — OpenCC translation step not yet added |

> **Warning:** When running `assign_cuis_ICD-11_with_translation.py`, **do not run it on the entire corpus** (it takes very long). Run it only on the Traditional Chinese data, then manually merge the results with the assigned English and Simplified Chinese data.

## To Do

1. Assign CUIs to the combined train set (currently missing the Simplified Chinese train split)
2. Complete Experiment 1 by combining the splits
3. **Experiment 2:** Add OpenCC translation to Traditional Chinese splits, assign CUIs to translated data, run frozen SapBERT on it
4. Fine-tuning experiments
