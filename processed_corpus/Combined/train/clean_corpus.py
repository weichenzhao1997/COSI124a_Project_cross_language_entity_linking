import json

input_path  = "processed_corpus/Combined/intermediates/combined_disease_corpus_train.jsonl"
output_path = "processed_corpus/Combined/intermediates/combined_disease_corpus_train_cleaned.jsonl"

stats = {"kept": 0, "dropped": 0, "dropped_by_corpus": {}}

with open(input_path) as fin, \
     open(output_path, "w") as fout:
    for line in fin:
        record = json.loads(line)
        corpus = record["source_corpus"]

        if not record.get("entities"):
            stats["dropped"] += 1
            stats["dropped_by_corpus"][corpus] = \
                stats["dropped_by_corpus"].get(corpus, 0) + 1
        else:
            stats["kept"] += 1
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Kept:    {stats['kept']}")
print(f"Dropped: {stats['dropped']}")
print(f"Dropped by corpus: {stats['dropped_by_corpus']}")

# Kept:    13848
# Dropped: 6361
# Dropped by corpus: {'simp_chinese': 6361}