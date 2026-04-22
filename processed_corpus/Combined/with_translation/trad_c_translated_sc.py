import json
from opencc import OpenCC

def convert_traditional_to_simplified(input_file, output_file):

    cc = OpenCC('t2s')  # traditional to simplified
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            try:
                data = json.loads(line.strip())
                
                if data.get('source_corpus') == 'trad_chinese':
                    if 'text' in data:
                        data['text'] = cc.convert(data['text'])
                    if 'entities' in data:
                        for entity in data['entities']:
                            if 'surface_form' in entity:
                                entity['surface_form'] = cc.convert(entity['surface_form'])
                            if 'ontology_label' in entity and entity['ontology_label']:
                                entity['ontology_label'] = cc.convert(entity['ontology_label'])

                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"line {line_num} get error: {e}")
                continue
            except Exception as e:
                print(f"line {line_num} get error: {e}")
                continue

input_path = "processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned.jsonl"
output_path = "processed_corpus/Combined/with_translation/train/combined_disease_corpus_train_with_cuis_icd11_cleaned_simplified.jsonl"

convert_traditional_to_simplified(input_path, output_path)

print(f"translation completed {output_path}")