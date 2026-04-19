"""
Convert TwiMed corpus (brat standoff format) to human-readable text output.

Each document is rendered as:
  - The sentence text
  - Annotated entities with their type, span text, attributes, and concept reference
  - Relations between entities
"""

import os
import re
from collections import defaultdict


CORPUS_DIR = os.path.join(os.path.dirname(__file__), "TwiMed-master", "gold", "pubmed")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "twimed_pubmed_readable.txt")


def parse_ann(ann_path):
    entities = {}    # T-id -> {type, start, end, text}
    attributes = defaultdict(dict)  # T-id -> {attr_name: value}
    references = {}  # T-id -> concept string
    relations = []   # list of {rel_type, arg1_id, arg2_id}

    with open(ann_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            tag = parts[0]

            if tag.startswith("T"):
                # T1  Drug 37 46  tamoxifen
                mid = parts[1]
                m = re.match(r"(\w+)\s+(\d+)\s+(\d+)", mid)
                if m:
                    entities[tag] = {
                        "type": m.group(1),
                        "start": int(m.group(2)),
                        "end": int(m.group(3)),
                        "text": parts[2] if len(parts) > 2 else "",
                    }

            elif tag.startswith("A"):
                # A1  Modality T1 Generic
                mid = parts[1]
                m = re.match(r"(\w+)\s+(T\d+)\s+(.*)", mid)
                if m:
                    attr_name, entity_id, value = m.group(1), m.group(2), m.group(3)
                    attributes[entity_id][attr_name] = value

            elif tag.startswith("N"):
                # N1  Reference T1 Concepts:5376  Tamoxifen
                mid = parts[1]
                m = re.match(r"Reference\s+(T\d+)\s+(\S+)", mid)
                if m:
                    references[m.group(1)] = m.group(2)

            elif tag.startswith("R"):
                # R1  Reason-to-use Arg1:T2 Arg2:T1
                mid = parts[1]
                m = re.match(r"(\S+)\s+Arg1:(T\d+)\s+Arg2:(T\d+)", mid)
                if m:
                    relations.append({
                        "type": m.group(1),
                        "arg1": m.group(2),
                        "arg2": m.group(3),
                    })

    return entities, attributes, references, relations


def format_document(doc_id, text, entities, attributes, references, relations):
    lines = []
    lines.append(f"=== {doc_id} ===")
    lines.append(f"TEXT: {text}")
    lines.append("")

    if entities:
        lines.append("ENTITIES:")
        for eid, ent in sorted(entities.items(), key=lambda x: x[1]["start"]):
            attrs = attributes.get(eid, {})
            ref = references.get(eid, "")
            attr_str = ""
            if attrs:
                attr_str = "  [" + ", ".join(f"{k}={v}" for k, v in attrs.items()) + "]"
            ref_str = f"  <{ref}>" if ref else ""
            lines.append(f"  {eid} {ent['type']:10s} [{ent['start']}:{ent['end']}]  \"{ent['text']}\"{attr_str}{ref_str}")

    if relations:
        lines.append("")
        lines.append("RELATIONS:")
        for rel in relations:
            a1 = entities.get(rel["arg1"], {})
            a2 = entities.get(rel["arg2"], {})
            a1_label = f"{a1.get('type','?')}(\"{a1.get('text','?')}\")"
            a2_label = f"{a2.get('type','?')}(\"{a2.get('text','?')}\")"
            lines.append(f"  {a1_label}  --[{rel['type']}]-->  {a2_label}")

    lines.append("")
    return "\n".join(lines)


def collect_doc_ids(corpus_dir):
    ids = set()
    for fname in os.listdir(corpus_dir):
        base, ext = os.path.splitext(fname)
        if ext in (".txt", ".ann"):
            ids.add(base)
    return sorted(ids)


def main():
    doc_ids = collect_doc_ids(CORPUS_DIR)
    print(f"Found {len(doc_ids)} documents in {CORPUS_DIR}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for doc_id in doc_ids:
            txt_path = os.path.join(CORPUS_DIR, doc_id + ".txt")
            ann_path = os.path.join(CORPUS_DIR, doc_id + ".ann")

            if not os.path.exists(txt_path) or not os.path.exists(ann_path):
                continue

            with open(txt_path, encoding="utf-8") as f:
                text = f.read().strip()

            entities, attributes, references, relations = parse_ann(ann_path)
            block = format_document(doc_id, text, entities, attributes, references, relations)
            out.write(block + "\n")

    print(f"Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
