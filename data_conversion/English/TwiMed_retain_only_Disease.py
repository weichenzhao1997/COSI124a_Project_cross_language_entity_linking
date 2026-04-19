import json
from collections import Counter
from pathlib import Path

INPUT_PATH = Path(__file__).parent.parent.parent / "processed_corpus/English/twimed_pubmed.json"
OUTPUT_PATH = Path(__file__).parent.parent.parent / "processed_corpus/English/twimed_pubmed_disease_only.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    corpus = json.load(f)

label_counter = Counter()
for doc in corpus:
    for entity in doc.get("entities", []):
        label_counter[entity["label"]] += 1

total_entities = sum(label_counter.values())
disease_count = label_counter.get("DISEASE", 0)

print("Label frequency:")
for label, count in label_counter.most_common():
    print(f"  {label}: {count} ({count / total_entities:.2%})")
print(f"\nDISEASE ratio: {disease_count} / {total_entities} = {disease_count / total_entities:.2%}")

filtered = []
for doc in corpus:
    disease_entities = [e for e in doc.get("entities", []) if e["label"] == "DISEASE"]
    if disease_entities:
        filtered.append({**doc, "entities": disease_entities})

print(f"\nDocuments retained: {len(filtered)} / {len(corpus)}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

print(f"Saved to {OUTPUT_PATH}")
