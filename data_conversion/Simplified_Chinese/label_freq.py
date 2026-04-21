import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
INPUT_DIR = BASE / "original_data" / "CMeEE-V2"


def label_frequency(split_name):
    path = INPUT_DIR / f"CMeEE-V2_{split_name}.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    counter = Counter()
    for sentence in data:
        for entity in sentence.get("entities", []):
            counter[entity["type"]] += 1

    total = sum(counter.values())
    print(f"\n[{split_name}] Label frequency (out of {total} entities):")
    for label, count in counter.most_common():
        print(f"  {label}: {count} ({count / total:.2%})")
    return counter


if __name__ == "__main__":
    train_counts = label_frequency("train")
    dev_counts = label_frequency("dev")

    combined = train_counts + dev_counts
    total = sum(combined.values())
    print(f"\n[combined] Label frequency (out of {total} entities):")
    for label, count in combined.most_common():
        print(f"  {label}: {count} ({count / total:.2%})")
