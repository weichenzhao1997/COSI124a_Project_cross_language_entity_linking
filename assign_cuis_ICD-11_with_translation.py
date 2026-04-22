import time
import requests
import json
from config import CLIENT_ID, CLIENT_SECRET
from datetime import datetime, timedelta
import opencc

input_path  = "processed_corpus/Traditional_Chinese/tc_test_disease_only.jsonl"
output_path = "processed_corpus/Traditional_Chinese/assign_CUIs_translated/tc_test_translated_with_CUIs.jsonl"
cache_path  = "processed_corpus/Combined/icd11_cache.json"

# ADD: initialize converter once at the top level
converter = opencc.OpenCC('t2s')

# Add tracking for how TC entities were matched
tc_match_stats = {
    "matched_zh_TW":        0,   # matched directly via zh-TW
    "matched_opencc_zh":    0,   # only matched after OpenCC conversion
    "unmatched":            0,   # unmatched even after OpenCC fallback
}

MEDICAL_OVERRIDES = {
    "憂鬱症":  "抑郁症",   
    "躁鬱症":  "双相情感障碍", 
    "失智症":  "痴呆",     
    "過動症": "多动症",
    "巴金森氏症": "帕金森病",
    "愛滋病": "艾滋病",
    "思覺失調症": "精神分裂症",
    "阿茲海默症": "阿尔茨海默病",
}

def tc_to_sc_medical(surface_form):
    """
    Convert Traditional Chinese medical term to Simplified Chinese.
    Use manual override table first, then fall back to OpenCC.
    """
    if surface_form in MEDICAL_OVERRIDES:
        return MEDICAL_OVERRIDES[surface_form]
    return converter.convert(surface_form)

def lookup_trad_chinese(surface_form):
    """
    For Traditional Chinese:
    1. Try zh-TW directly first
    2. If no match, convert to Simplified via OpenCC and try zh
    3. Track which path succeeded for analysis
    """
    # Step 1: try zh-TW directly (reuses cache)
    code, label = lookup_with_cache(surface_form, "zh-TW")
    if code:
        tc_match_stats["matched_zh_TW"] += 1
        return code, label

    # Step 2: medical-aware conversion + zh fallback
    simplified = tc_to_sc_medical(surface_form)
    if simplified != surface_form:
        code, label = lookup_with_cache(simplified, "zh")
        if code:
            tc_match_stats["matched_opencc_zh"] += 1
            return code, label

    # Step 3: nothing worked
    tc_match_stats["unmatched"] += 1
    return None, None


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

def search_icd11(surface_form, lang="en", min_score=0.5):
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

        # Reject low-confidence matches
        score = top.get("score", 0)
        if score < min_score:
            return None, None


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

            # Route Traditional Chinese through the new fallback function
            if corpus == "trad_chinese":
                code, label = lookup_trad_chinese(entity["surface_form"])
            else:
                code, label = lookup_with_cache(entity["surface_form"], lang)

            if code:
                entity["ontology_id"]    = code
                entity["ontology_label"] = label
                matched[corpus] += 1
            else:
                unmatched[corpus] += 1

            total_entities += 1

        fout.write(json.dumps(record, ensure_ascii=False) + "\n")

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
print("\n=== Traditional Chinese Match Path Breakdown ===")
print(f"  Matched via zh-TW directly:   {tc_match_stats['matched_zh_TW']}")
print(f"  Matched via OpenCC + zh:       {tc_match_stats['matched_opencc_zh']}")
print(f"  Unmatched after both attempts: {tc_match_stats['unmatched']}")


