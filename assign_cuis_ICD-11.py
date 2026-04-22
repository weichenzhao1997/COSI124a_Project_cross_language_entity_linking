import time
import requests
import json
from config import CLIENT_ID, CLIENT_SECRET
from datetime import datetime, timedelta

input_path  = "processed_corpus/Combined/no_translation/test/combined_disease_corpus_test_cleaned.jsonl"
output_path = "processed_corpus/Combined/no_translation/test/combined_disease_corpus_test_with_cuis_icd11_cleaned.jsonl"
cache_path  = "processed_corpus/Combined/icd11_cache.json"




# --- Token management (unchanged) ---
token = None
token_expiry = datetime.now()

def get_token():
    global token, token_expiry
    if token and datetime.now() < token_expiry:
        return token
    r = requests.post(
        "https://icdaccessmanagement.who.int/connect/token",
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope":         "icdapi_access",
            "grant_type":    "client_credentials"
        }
    )
    data = r.json()
    token = data["access_token"]
    token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600) - 60)
    return token

def search_icd11(surface_form, lang="en"):
    headers = {
        "Authorization":   f"Bearer {get_token()}",
        "Accept":          "application/json",
        "Accept-Language": lang,
        "API-Version":     "v2"
    }
    try:
        r = requests.get(
            "https://id.who.int/icd/entity/search",
            params={"q": surface_form, "flatResults": True},
            headers=headers,
            timeout=10
        )
        if r.status_code != 200:
            return None, None

        results = r.json()
        if not results.get("destinationEntities"):
            return None, None

        top = results["destinationEntities"][0]

        # Use theCode if available, otherwise fall back to foundation URI
        code = top.get("theCode") or top.get("stemId") or top.get("id")

        # Strip HTML tags from title e.g. "<em class='found'>cancer</em>" → "cancer"
        import re
        raw_title = top.get("title", "")
        clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()

        return code, clean_title

    except Exception as e:
        print(f"  Warning: API error for '{surface_form}': {e}")
    return None, None

# --- Load existing cache if available ---
# This means if the script crashes, you don't lose progress
try:
    with open(cache_path) as f:
        cache = json.load(f)
    print(f"Loaded cache with {len(cache)} entries")
except FileNotFoundError:
    cache = {}
    print("No cache found, starting fresh")

def lookup_with_cache(surface_form, lang):
    """Check cache first; only call API if not cached."""
    key = f"{lang}::{surface_form}"
    if key in cache:
        return cache[key]["code"], cache[key]["label"]

    code, label = search_icd11(surface_form, lang)
    cache[key] = {"code": code, "label": label}
    time.sleep(0.05)   # only sleep when actually calling API
    return code, label

def save_cache():
    with open(cache_path, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

LANG_MAP = {
    "english_ncbi": "en",
    "simp_chinese":  "zh",
    "trad_chinese":  "zh-TW"
}

# # Run this as a standalone test BEFORE your main loop
# test_form = "cancer"
# headers = {
#     "Authorization":   f"Bearer {get_token()}",
#     "Accept":          "application/json",
#     "Accept-Language": "en",
#     "API-Version":     "v2"
# }
# r = requests.get(
#     "https://id.who.int/icd/entity/search",
#     params={"q": test_form, "flatResults": True},
#     headers=headers,
#     timeout=10
# )
# print("Status code:", r.status_code)
# print("Raw response:", json.dumps(r.json(), indent=2))


matched   = {"english_ncbi": 0, "simp_chinese": 0, "trad_chinese": 0}
unmatched = {"english_ncbi": 0, "simp_chinese": 0, "trad_chinese": 0}
total_entities = 0

with open(input_path) as fin, \
     open(output_path, "w") as fout:

    for i, line in enumerate(fin):
        record = json.loads(line)
        corpus = record["source_corpus"]
        lang   = LANG_MAP.get(corpus, "en")

        for entity in record.get("entities", []):
            code, label = lookup_with_cache(entity["surface_form"], lang)

            if code:
                entity["ontology_id"]    = code
                entity["ontology_label"] = label
                matched[corpus] += 1
            else:
                unmatched[corpus] += 1

            total_entities += 1

        fout.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Save cache every 100 documents
        if (i + 1) % 100 == 0:
            save_cache()
            print(f"Processed {i + 1} docs | {total_entities} entities | "
                  f"matched: {matched} | unmatched: {unmatched} | "
                  f"cache size: {len(cache)}")

# Final cache save
save_cache()
print("\nFinished.")
print("Matched:  ", matched)
print("Unmatched:", unmatched)
print("Total entities:", total_entities)


# # Quick test before proceeding
# test_cases = [
#     ("阿茲海默症", "zh-TW"), 
#     ("憂鬱症",       "zh-TW"),  
#     ("肝癌", "zh-TW"),
#     ("中風", "zh-TW"),

#     ("糖尿病",     "zh-TW"),   # diabetes — should match in any Chinese
#     ("糖尿病",     "zh"),      # same term in Simplified — compare coverage
# ]

# for term, lang in test_cases:
#     code, label = search_icd11(term, lang)
#     print(f"[{lang}] {term:15s} → {code} | {label}")