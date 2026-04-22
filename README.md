# Cross-Language Entity Linking

## Corpus

Combined train and dev splits are located in [processed_corpus/Combined/](processed_corpus/Combined/).

### Data Splits
#### no translation

1. The finalized train split with CUIs: processed_corpus/Combined/no_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

2. The finalized dev split with CUIs:  processed_corpus/Combined/no_translation/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

#### with translation
1. The finalized train split with CUIs:  processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

2. The finalized dev split with CUIs: processed_corpus/Combined/with_translation/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

## ICD-11 Labeling

We assign **ICD-11** labels instead of UMLS labels as originally planned — UMLS does not support Chinese.

> **Note:** The ICD-11 API does not perform true Traditional Chinese matching. It matches against Simplified Chinese and accepts some Traditional Chinese input incidentally when characters overlap.

## Scripts

| Script | Description |
|---|---|
| `assign_cuis_ICD-11.py` | Assigns ICD-11 labels (no translation) |
| `assign_cuis_ICD-11_with_translation.py` | Assigns ICD-11 labels (with translation) |


## To Do

1. Assign CUIs to the combined test set (currently missing the Simplified Chinese train split)
2. Complete Experiment 1 by evaluating on the combined test split
3. **Experiment 2:** run frozen SapBERT on corpus with translation
4. **Experiment 3:** Fine-tuning experiments
