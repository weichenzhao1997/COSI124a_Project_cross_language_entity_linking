import json
from data_conversion.Simplified_Chinese.label_freq import label_frequency
from data_conversion.Simplified_Chinese.sc_parse import JSON_Parser
from pathlib import Path
from typing import List
from data_conversion.Simplified_Chinese.label_freq import label_frequency
from data_conversion.Simplified_Chinese.sc_parse import JSON_Parser
from analyse import Analyse

def merge_jsonl(paths: List[str]):
    #files = ["file1.jsonl", "file2.jsonl", "file3.jsonl"]
    with open("all_corpora.jsonl", "w", encoding="utf-8") as out:
        for path in paths:
            with open(Path(path), encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    out.write(json.dumps(data, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    path1 = "processed_corpus/English/NCBI/ncbi_train_disease_only.jsonl"
    path2 = "processed_corpus/Simplified_Chinese/cmeee_disease_only_train.jsonl"
    path3 = "processed_corpus/Traditional_Chinese/tc_train_disease_only.jsonl"
    #merge_jsonl([path1, path2, path3])

    analyser = Analyse("all_corpora.jsonl")
    analyser.print_and_save_comparison("comparison.txt")
    analyser.print_and_save_span_analysis("span_analysis.txt")