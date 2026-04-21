import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
INPUT_DIR = BASE / "processed_corpus/Traditional_Chinese"
OUTPUT_DIR = BASE / "processed_corpus/Traditional_Chinese"


def process_split(split_name):
    input_path = INPUT_DIR / f"tc_{split_name}.jsonl"
    output_path = OUTPUT_DIR / f"tc_{split_name}_disease_only.jsonl"

    total_docs = 0
    retained_docs = 0
    label_counter = Counter()

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            doc = json.loads(line)
            total_docs += 1
            for e in doc["entities"]:
                label_counter[e["label"]] += 1

            disease_entities = [e for e in doc["entities"] if e["label"] == "DISEASE"]
            if disease_entities:
                retained_docs += 1
                fout.write(json.dumps({**doc, "entities": disease_entities}, ensure_ascii=False) + "\n")

    total_entities = sum(label_counter.values())
    disease_count = label_counter.get("DISEASE", 0)
    print(f"\n[{split_name}] All label frequencies (out of {total_entities} entities):")
    for label, count in label_counter.most_common():
        print(f"  {label}: {count} ({count / total_entities:.2%})")
    print(f"DISEASE ratio: {disease_count} / {total_entities} = {disease_count / total_entities:.2%}")
    print(f"Documents retained: {retained_docs} / {total_docs}")
    print(f"Saved → {output_path}")


if __name__ == "__main__":
    process_split("train")
    process_split("test")
