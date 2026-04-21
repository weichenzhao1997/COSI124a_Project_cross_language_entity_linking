import json
import random
from pathlib import Path

SEED = 42
TARGET_DISEASE_LABELS = 1000

BASE = Path(__file__).parent.parent.parent
INPUT_PATH = BASE / "processed_corpus" / "Traditional_Chinese" / "tc_train_disease_only.jsonl"
OUTPUT_TRAIN = BASE / "processed_corpus" / "Traditional_Chinese" / "tc_train_disease_only_split.jsonl"
OUTPUT_DEV = BASE / "processed_corpus" / "Traditional_Chinese" / "tc_dev_disease_only.jsonl"


def load_jsonl(path):
    docs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def write_jsonl(path, docs):
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def count_disease_labels(docs):
    return sum(len(doc["entities"]) for doc in docs)


if __name__ == "__main__":
    docs = load_jsonl(INPUT_PATH)
    print(f"Loaded {len(docs)} documents, {count_disease_labels(docs)} disease labels")

    random.seed(SEED)
    random.shuffle(docs)

    dev_docs = []
    dev_label_count = 0
    for doc in docs:
        if dev_label_count >= TARGET_DISEASE_LABELS:
            break
        dev_docs.append(doc)
        dev_label_count += len(doc["entities"])

    dev_set = set(id(d) for d in dev_docs)
    train_docs = [d for d in docs if id(d) not in dev_set]

    write_jsonl(OUTPUT_DEV, dev_docs)
    write_jsonl(OUTPUT_TRAIN, train_docs)

    print(f"\nDev  split: {len(dev_docs)} docs, {count_disease_labels(dev_docs)} disease labels")
    print(f"Train split: {len(train_docs)} docs, {count_disease_labels(train_docs)} disease labels")
    print(f"\nSaved dev   → {OUTPUT_DEV}")
    print(f"Saved train → {OUTPUT_TRAIN}")
