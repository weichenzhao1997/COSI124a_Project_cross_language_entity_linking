import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).parent.parent.parent.parent
INPUT_DIR = BASE / "processed_corpus" / "English" / "NCBI"
OUTPUT_DIR = INPUT_DIR

SPLITS = ["train", "dev", "test"]


def process_split(split_name):
    input_path = INPUT_DIR / f"ncbi_{split_name}.jsonl"
    output_path = OUTPUT_DIR / f"ncbi_{split_name}_disease_only.jsonl"
    label_counter = Counter()
    total_docs = 0
    retained_docs = 0

    with open(input_path, encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            doc = json.loads(line)
            total_docs += 1
            for e in doc["entities"]:
                label_counter[e["label"]] += 1

            specific_disease = [
                {**e, "label": "DISEASE"}
                for e in doc["entities"]
                if e["label"] == "SpecificDisease"
            ]
            if specific_disease:
                retained_docs += 1
                fout.write(json.dumps({**doc, "entities": specific_disease}, ensure_ascii=False) + "\n")

    total_entities = sum(label_counter.values())
    sd_count = label_counter.get("SpecificDisease", 0)
    print(f"\n[{split_name}] All label frequencies (out of {total_entities} entities):")
    for label, count in label_counter.most_common():
        print(f"  {label}: {count} ({count / total_entities:.2%})")
    print(f"SpecificDisease ratio: {sd_count} / {total_entities} = {sd_count / total_entities:.2%}")
    print(f"Documents retained: {retained_docs} / {total_docs}")
    print(f"Saved → {output_path}")
    return label_counter


if __name__ == "__main__":
    all_counts = Counter()
    for split in SPLITS:
        all_counts += process_split(split)

    total = sum(all_counts.values())
    print(f"\n[combined] Label frequency (out of {total} entities):")
    for label, count in all_counts.most_common():
        print(f"  {label}: {count} ({count / total:.2%})")
