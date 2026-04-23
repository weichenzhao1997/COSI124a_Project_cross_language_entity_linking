import json

TXT_PATH = "data_conversion/icd11/SimpleTabulation-ICD-11-MMS-zh.txt"
OUT_JSON = "data_conversion/icd11/icd11_map.jsonl"

def clean_title(text: str) -> str:
    text = text.strip().strip('"')
    text = text.lstrip("- ").lstrip("- ").lstrip("- ")
    return text.strip()

def main():
    result = {}
    with open(TXT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        cols = line.split("\t")
        if len(cols) < 6:
            continue

        code = cols[2].strip()
        title_en = cols[4].strip()
        title_zh = cols[5].strip()
        linear_uri = cols[1].strip()

        if not code:
            continue

        en_name = clean_title(title_en)
        zh_cn = clean_title(title_zh)

        result[code] = {
            "code": code,
            "en_name": en_name,
            "simpl_cn": zh_cn,
            "synonyms_en": [],
            "synonyms_sc": [],
            "synonyms_tc": [],
            "uri": linear_uri
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        for item in result.values():
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"converion completed！")
    print(f"line num: {len(result)}")
    print(f"outputfile: {OUT_JSON}")

if __name__ == "__main__":
    main()