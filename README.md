# Cross-Language Entity Linking

## Corpus

Combined train and dev splits are located in [processed_corpus/Combined/](processed_corpus/Combined/).

### Data Splits
#### no translation

1. The finalized train split with CUIs: processed_corpus/Combined/no_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

2. The finalized dev split with CUIs:  processed_corpus/Combined/no_translation/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

3. The finalized test split with CUIs:  processed_corpus/Combined/no_translation/test/combined_disease_corpus_test_with_cuis_icd11_cleaned.jsonl

#### with translation
1. The finalized train split with CUIs:  processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned_simplified.jsonl

> **Note:** There is another version translated with different strategy that yields worse performance: processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

2. The finalized dev split with CUIs: processed_corpus/Combined/with_translation/dev/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl

## ICD-11 Labeling

We assign **ICD-11** labels instead of UMLS labels as originally planned — UMLS does not support Chinese.

> **Note:** The ICD-11 API does not perform true Traditional Chinese matching. It matches against Simplified Chinese and accepts some Traditional Chinese input incidentally when characters overlap.

## Scripts

| Script | Description |
|---|---|
| `assign_cuis_ICD-11.py` | Assigns ICD-11 labels (no translation) |
| `assign_cuis_ICD-11_with_translation.py` | Assigns ICD-11 labels (with translation) |

## Experiments
Experiment 1 - fronzen baseline on untranslated corpus: experiments/frozen_sapbert/frozen_sapbert_baseline_no_translation.ipynb

Experiment 1b - fronzen baseline on untranslated corpus with enriched index: experiments/frozen_sapbert/frozen_sapbert_baseline_enriched_index.ipynb

Experiment 2-v2 - fronzen baseline on translated corpus with enriched index: experiments/frozen_sapbert_with_translation-v2/frozen_sapbert_baseline_with_translation-v2.ipynb
> **Note:** This experiment uses the translated corpus with better performance

## To Do

1. Assign CUIs to the combined test set with translation
3. **Experiment 2:** Finish it by evaluting on test set
4. **Experiment 3:** Fine-tuning experiments
