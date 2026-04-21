Combined train and dev split: processed_corpus/Combined

We are assigning ICD-11 labels as opposed to UMLS labels as originally planned as UMLS does not support Chinese at all
That being said, the ICD-11 API is not doing true Traditional Chinese matching — it is doing Simplified Chinese matching and accepting some Traditional Chinese input by accident when characters overlap.

assign_cuis_ICD-11.py: this script assigns ICD-11 labels (no translation)
assign_cuis_ICD-11_with_translation.py: this script is currently the same as assign_cuis_ICD-11.py, need to add OpenCC translation step
    <b>when running assign_cuis_ICD-11_with_translation.py, DO NOT run it on the entire corpus (it takes forever); run it only on the traditional chinese data and add it manually to the assigned English and Simplified Chinese data </b>


To do: 
1 - assign CUIs to the combined train set (currently missing the simplified chinese train set)
2 - complete experiment 1 by combining 
3 - experiment 2: add OpenCC translation to the traditional chinese splits, assign CUIs to the translated data, run frozen SapBERT on it
4 - fine-tuning experiments