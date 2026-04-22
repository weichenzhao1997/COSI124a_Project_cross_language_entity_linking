import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import re

class Analyse:
    def __init__(self, path: Path):
        self.documents = []
        project_root = Path(__file__).parent.parent.parent
        #self.path1 = [project_root / "processed_corpus" / "English" / "NCBI" / "ncbi_train_disease_only.jsonl"]
        #self.path2 = [project_root / "processed_corpus" / "Simplified_Chinese" / "cmeee_disease_only_train"]
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                self.documents.append(json.loads(line))

        self.english_docs = [d for d in self.documents if d['source_corpus'] == 'english_ncbi']
        self.chinese_docs = [d for d in self.documents if d['source_corpus'] == 'simp_chinese']
        self.traditional_docs = [d for d in self.documents if d['source_corpus'] == 'trad_chinese']
    
    def compute_stats(self, docs):
        disease_count = 0
        total_entities = 0
        lengths = []

        for doc in docs:
            entities = doc.get("entities", [])
            total_entities += len(entities)

            for ent in entities:
                if ent["label"] == "DISEASE":
                    disease_count += 1
                    lengths.append(ent["char_end"] - ent["char_start"])

        avg_length = sum(lengths) / len(lengths) if lengths else 0
        density = total_entities / len(docs) if docs else 0

        return {
            "disease_count": disease_count,
            "avg_entity_length": avg_length,
            "entity_density": density,
            "num_sentences": len(docs)
        }
    
    def compare(self):
        results = {
            "english": self.compute_stats(self.english_docs),
            "simplified_chinese": self.compute_stats(self.chinese_docs),
            "traditional_chinese": self.compute_stats(self.traditional_docs)
        }
        return results
    def clean(self, text: str):
        return text.lower().strip()

    def tokenize(self, text: str):
        return re.findall(r"[a-zA-Z]+", text.lower())

    def is_valid_entity(self, text: str):
        text = text.strip()
        if len(text) < 3:
            return False
        if re.fullmatch(r"(?:[a-zA-Z]\s+)+[a-zA-Z]", text):
            return False

        return True
    def collect_entities(self):
        entity_map = {}  # normalized_text -> {corpus: set(surface_forms)}

        for doc in self.documents:
            corpus = doc["source_corpus"]

            for ent in doc.get("entities", []):
                if ent["label"] != "DISEASE":
                    continue

                surface = ent["surface_form"]
                norm = self.normalize(surface)

                if norm not in entity_map:
                    entity_map[norm] = {}

                if corpus not in entity_map[norm]:
                    entity_map[norm][corpus] = set()

                entity_map[norm][corpus].add(surface)

        return entity_map

    '''
    def span_boundary_analysis(self):
        entity_map = {} 
        for doc in self.documents:
            corpus = doc["source_corpus"]

            for ent in doc.get("entities", []):
                if ent["label"] != "DISEASE":
                    continue

                surface = ent["surface_form"].lower()

                if corpus not in entity_map:
                    entity_map[corpus] = []

                entity_map[corpus].append(surface)

        inconsistencies = []

        corpora = list(entity_map.keys())

        for i in range(len(corpora)):
            for j in range(i + 1, len(corpora)):
                c1, c2 = corpora[i], corpora[j]

                for s1 in entity_map[c1]:
                    for s2 in entity_map[c2]:

                        if s1 == s2:
                            continue

                        if s1 in s2 or s2 in s1:
                            inconsistencies.append({
                                "corpus_pair": (c1, c2),
                                "shorter": s1 if len(s1) < len(s2) else s2,
                                "longer": s2 if len(s1) < len(s2) else s1
                            })

        return inconsistencies
    '''
    def analyze_single_corpus(self, docs, corpus_name):
        entities = []
        for doc in docs:
            for ent in doc.get("entities", []):
                if ent["label"] != "DISEASE":
                    continue
                surface = ent["surface_form"].lower()
                entities.append(surface)

        inconsistencies = []
        seen_pairs = set()
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                s1 = entities[i]
                s2 = entities[j]

                if s1 == s2:
                    continue

                shorter = s1 if len(s1) < len(s2) else s2
                longer = s2 if len(s1) < len(s2) else s1
                
                pair_key = (shorter, longer)
                
                if pair_key in seen_pairs:
                    continue
                    
                if s1 in s2 or s2 in s1:
                    seen_pairs.add(pair_key)
                    inconsistencies.append({
                        "corpus_pair": (corpus_name, corpus_name),
                        "shorter": shorter,
                        "longer": longer
                    })

        return inconsistencies

    def span_boundary_analysis(self):
        all_inconsistencies = {}

        english_inconsistencies = self.analyze_single_corpus(self.english_docs, "english_ncbi")
        all_inconsistencies["english_ncbi"] = english_inconsistencies
        
        chinese_inconsistencies = self.analyze_single_corpus(self.chinese_docs, "simp_chinese")
        all_inconsistencies["simp_chinese"] = chinese_inconsistencies
        
        traditional_inconsistencies = self.analyze_single_corpus(self.traditional_docs, "trad_chinese")
        all_inconsistencies["trad_chinese"] = traditional_inconsistencies
        
        return all_inconsistencies

    def save_all_span_analyses(self, output_dir: Path):
        
        all_results = self.span_boundary_analysis()
        
        for corpus_name, inconsistencies in all_results.items():
            output_file = output_dir / f"{corpus_name}_boundary_analysis.txt"
            
            with open(output_file, "w", encoding="utf-8") as f:
                header = f"Boundary analysis for {corpus_name}: Total inconsistencies: {len(inconsistencies)}\n"
                f.write(header)
                f.write("="*80 + "\n\n")

                for i, item in enumerate(inconsistencies):
                    text = (
                        f"Inconsistency #{i+1}:\n"
                        f"Corpus Pair: {item['corpus_pair']}\n"
                        f"Shorter Span: {item['shorter']}\n"
                        f"Longer Span: {item['longer']}\n"
                        f"{'-'*50}\n"
                    )
                    f.write(text)
                
                if len(inconsistencies) == 0:
                    f.write("No boundary inconsistencies found.\n")
                    
            print(f"Saved boundary analysis for {corpus_name} to {output_file}")
    def normalize(self, text: str):
        return re.sub(r"\s+", "", text.lower())

    def clean(self, text):
        return text.lower().replace(" ", "").replace("-", "")

    def print_and_save_comparison(self, output_path: Path):
        results = self.compare()

        with open(output_path, "w", encoding="utf-8") as f:
            for corpus, stats in results.items():
                text = (
                    f"\n=== {corpus.upper()} ===\n"
                    f"Sentences: {stats['num_sentences']}\n"
                    f"DISEASE count: {stats['disease_count']}\n"
                    f"Avg entity length: {stats['avg_entity_length']:.2f}\n"
                    f"Entity density: {stats['entity_density']:.2f}\n"
                )

                print(text)
                f.write(text)
    def print_and_save_span_analysis(self, output_path: Path):
        results = self.span_boundary_analysis()
        unique = set()
        filtered_results = []

        for r in results:
            key = (r["shorter"], r["longer"], r["corpus_pair"])
            if key not in unique:
                unique.add(key)
                filtered_results.append(r)

        with open(output_path, "w", encoding="utf-8") as f:
            header = f"Total boundary inconsistencies: {len(filtered_results)}\n"
            #print(header)
            f.write(header)

            for item in filtered_results:
                text = (
                    f"Corpus Pair: {item['corpus_pair']}\n"
                    f"Shorter Span: {item['shorter']}\n"
                    f"Longer Span:  {item['longer']}\n"
                    f"{'-'*50}\n"
                )

                #print(text)
                f.write(text)