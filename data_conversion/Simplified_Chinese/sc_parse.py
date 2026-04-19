import gzip
import json
from pathlib import Path

class JSON_Parser:
    @staticmethod
    def load_json_file(path: Path) -> dict:
        if path.name.endswith(".gz"):
            with gzip.open(path, "rb") as f:
                return json.load(f)
        else:
            with open(path, encoding="utf-8") as f:
                return json.load(f)

    @staticmethod
    def parse(original:dict) -> list:
        i = 0
        output = []
        for sentence in original:
            new_sentence = {}
            new_sentence["doc_id"] = "sc_" + str(i)
            new_sentence["source_corpus"] = "simp_chinese"
            new_sentence["text"] = sentence["text"]
            dis_entities = []
            for entity in sentence["entities"]:
                if entity["type"] == "dis":
                    dis_entities.append({"entity_id":"sc_"+ new_sentence["doc_id"]+"_"+ str(entity["start_idx"]) +"_"+ str(entity["end_idx"]),
                                         "surface_form": entity["entity"],
                                         "label": "DISEASE",
                                         "original_label": "dis",
                                         "char_start": entity["start_idx"],
                                         "char_end": entity["end_idx"],
                                         "ontology_id": None,
                                         "ontology_label": None
                                         })
            i += 1
            if len(dis_entities) > 0:
                new_sentence["entities"] = dis_entities
            output.append(new_sentence)
        return output

    @staticmethod
    def save_json_file(path: Path, outlist:list) ->None:
        with open(path, "w", encoding="utf-8") as f:
            #for item in outlist:
                #f.write(json.dumps(item, ensure_ascii=False) + "\n")
            json.dump(outlist, f, ensure_ascii=False, indent=2)
    @staticmethod
    def process(input_path: Path, output_path: Path) -> None:
        data = JSON_Parser.load_json_file(input_path)
        parsed = JSON_Parser.parse(data)
        JSON_Parser.save_json_file(output_path, parsed)