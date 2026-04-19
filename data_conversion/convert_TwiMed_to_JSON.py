import json
from pathlib import Path


def parse_ann_file(ann_path: str) -> dict:
    """Parse a .ann file and return entity spans with their normalizations."""
    entities = {}    # T-id -> {type, start, end, surface_form}
    norms = {}       # T-id -> {concept_id, concept_label}

    with open(ann_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            tag = parts[0]

            if tag.startswith("T") and len(parts) >= 3:
                # T1   Drug 90 103   carbamazepine
                span_info = parts[1].split()
                entity_type = span_info[0]
                # Handle discontinuous spans like "40;61 70" by taking overall min/max
                all_offsets = [int(x) for s in span_info[1:] for x in s.split(";")]
                start = min(all_offsets)
                end = max(all_offsets)
                surface_form = parts[2]
                entities[tag] = {
                    "type": entity_type,
                    "start": start,
                    "end": end,
                    "surface_form": surface_form,
                }

            elif tag.startswith("N") and len(parts) >= 2:
                # N1   Reference T1 Concepts:2554   Carbamazepine
                ref_parts = parts[1].split()
                t_ref = ref_parts[1]          # e.g. T1
                concept_raw = ref_parts[2] if len(ref_parts) > 2 else ""
                concept_id = concept_raw.split(":", 1)[1] if ":" in concept_raw else None
                concept_label = parts[2] if len(parts) >= 3 else None

                # Treat id "0" (Disagreement) as null
                if concept_id == "0":
                    concept_id = None
                if concept_label and concept_label.startswith("Disagreement"):
                    concept_label = None

                norms[t_ref] = {"ontology_id": concept_id, "ontology_label": concept_label}

    return entities, norms


def convert_pubmed_to_json(pubmed_dir: str, output_path: str) -> None:
    pubmed_dir = Path(pubmed_dir)
    docs = []

    # Collect all doc ids (base names without extension)
    txt_files = sorted(pubmed_dir.glob("*.txt"))
    for txt_file in txt_files:
        doc_id = txt_file.stem
        ann_file = pubmed_dir / (doc_id + ".ann")

        with open(txt_file, encoding="utf-8") as f:
            text = f.read().rstrip("\n")

        entities_raw, norms = {}, {}
        if ann_file.exists():
            entities_raw, norms = parse_ann_file(str(ann_file))

        entities = []
        for t_id, ent in sorted(entities_raw.items(), key=lambda x: int(x[0][1:])):
            norm = norms.get(t_id, {})
            entity_id = f"en_{doc_id}_{t_id}"
            original_label = ent["type"]
            label = original_label.upper()
            entities.append({
                "entity_id": entity_id,
                "surface_form": ent["surface_form"],
                "label": label,
                "original_label": original_label,
                "char_start": ent["start"],
                "char_end": ent["end"],
                "ontology_id": norm.get("ontology_id"),
                "ontology_label": norm.get("ontology_label"),
            })

        docs.append({
            "doc_id": doc_id,
            "source_corpus": "english",
            "text": text,
            "entities": entities,
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(docs)} documents -> {output_path}")


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    pubmed_dir = base / "TwiMed-master" / "gold" / "pubmed"
    output_path = base / "data_conversion" / "twimed_pubmed.json"
    convert_pubmed_to_json(str(pubmed_dir), str(output_path))
