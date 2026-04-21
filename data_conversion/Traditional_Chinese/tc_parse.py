import json
from collections import Counter
from pathlib import Path

LABEL_MAP = {
    "DISE": "DISEASE",
    "SYMP": "SYMPTOM",
    "DRUG": "DRUG",
    "BODY": "BODY",
    "CHEM": "CHEMICAL",
    "EXAM": "EXAM",
    "INST": "INSTITUTION",
    "SUPP": "SUPPLEMENT",
    "TIME": "TIME",
    "TREAT": "TREATMENT",
}

BASE = Path(__file__).parent.parent.parent
INPUT_DIR = BASE / "original_data/Traditional Chinese Corpus"
OUTPUT_DIR = BASE / "processed_corpus/Traditional_Chinese"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_record(record):
    doc_id = record["id"]
    text = record["sentence"]
    characters = record["character"]
    char_labels = record["character_label"]

    entities = []
    i = 0
    while i < len(char_labels):
        lbl = char_labels[i]
        if lbl.startswith("B-"):
            entity_type = lbl[2:]
            start = i
            j = i + 1
            while j < len(char_labels) and char_labels[j] == f"I-{entity_type}":
                j += 1
            end = j - 1  # inclusive char index
            surface_form = "".join(characters[start:j])
            entity_id = f"tc_{doc_id}_{start}_{end}"
            entities.append({
                "entity_id": entity_id,
                "surface_form": surface_form,
                "label": LABEL_MAP.get(entity_type, entity_type),
                "original_label": entity_type,
                "char_start": start,
                "char_end": end,
                "ontology_id": None,
                "ontology_label": None,
            })
            i = j
        else:
            i += 1

    return {
        "doc_id": doc_id,
        "source_corpus": "trad_chinese",
        "text": text,
        "entities": entities,
    }


def process_split(split_name):
    input_path = INPUT_DIR / f"{split_name}.json"
    output_path = OUTPUT_DIR / f"tc_{split_name}.jsonl"
    label_counter = Counter()

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            doc = parse_record(json.loads(line))
            for e in doc["entities"]:
                label_counter[e["label"]] += 1
            fout.write(json.dumps(doc, ensure_ascii=False) + "\n")

    total = sum(label_counter.values())
    print(f"\n[{split_name}] Label frequency (out of {total} entities):")
    for label, count in label_counter.most_common():
        print(f"  {label}: {count} ({count / total:.2%})")
    print(f"Saved → {output_path}")
    return label_counter


if __name__ == "__main__":
    train_counts = process_split("train")
    test_counts = process_split("test")

    combined = train_counts + test_counts
    total = sum(combined.values())
    print(f"\n[combined] Label frequency (out of {total} entities):")
    for label, count in combined.most_common():
        print(f"  {label}: {count} ({count / total:.2%})")
