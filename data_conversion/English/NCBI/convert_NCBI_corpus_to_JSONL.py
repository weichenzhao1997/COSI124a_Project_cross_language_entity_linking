import re
import json
from collections import Counter
from pathlib import Path

TAG_RE = re.compile(r'<category="([^"]+)">(.*?)</category>')

BASE = Path(__file__).parent.parent.parent.parent
INPUT_DIR = BASE / "original_data" / "NCBI_corpus"
OUTPUT_DIR = BASE / "processed_corpus" / "English" / "NCBI"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SPLITS = {
    "train": "NCBI_corpus_training.txt",
    "dev":   "NCBI_corpus_development.txt",
    "test":  "NCBI_corpus_testing.txt",
}


def extract_entities_and_clean(raw_text, pmid, char_offset=0):
    """Strip inline tags from raw_text, return (clean_text, entities).
    char_offset is added to all positions (used when title precedes abstract)."""
    entities = []
    clean_parts = []
    cursor = 0   # position in clean text built so far
    last = 0     # position in raw_text

    for m in TAG_RE.finditer(raw_text):
        before = raw_text[last:m.start()]
        clean_parts.append(before)
        cursor += len(before)

        label = m.group(1)
        surface = m.group(2)
        char_start = char_offset + cursor
        char_end = char_start + len(surface)  # exclusive

        entities.append({
            "entity_id": f"ncbi_{pmid}_{char_start}_{char_end}",
            "surface_form": surface,
            "label": label,
            "original_label": label,
            "char_start": char_start,
            "char_end": char_end,
            "ontology_id": None,
            "ontology_label": None,
        })

        clean_parts.append(surface)
        cursor += len(surface)
        last = m.end()

    clean_parts.append(raw_text[last:])
    return "".join(clean_parts), entities


def parse_line(line):
    """Parse one PMID\\tTitle\\tAbstract line into a doc dict."""
    parts = line.rstrip("\n").split("\t")
    pmid, raw_title, raw_abstract = parts[0], parts[1], parts[2]

    title_clean, title_entities = extract_entities_and_clean(raw_title, pmid, char_offset=0)
    abstract_offset = len(title_clean) + 1  # +1 for the "\n" separator
    abstract_clean, abstract_entities = extract_entities_and_clean(raw_abstract, pmid, char_offset=abstract_offset)

    text = title_clean + "\n" + abstract_clean
    entities = title_entities + abstract_entities

    return {
        "doc_id": f"ncbi_{pmid}",
        "source_corpus": "english_ncbi",
        "text": text,
        "entities": entities,
    }


def process_split(split_name, filename):
    input_path = INPUT_DIR / filename
    output_path = OUTPUT_DIR / f"ncbi_{split_name}.jsonl"
    label_counter = Counter()

    with open(input_path, encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            doc = parse_line(line)
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
    all_counts = Counter()
    for split_name, filename in SPLITS.items():
        all_counts += process_split(split_name, filename)

    total = sum(all_counts.values())
    print(f"\n[combined] Label frequency (out of {total} entities):")
    for label, count in all_counts.most_common():
        print(f"  {label}: {count} ({count / total:.2%})")
