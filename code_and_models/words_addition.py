import os
import json
import joblib
import ahocorasick

STAGE1_TRIE_FILE = "stage1_trie.joblib"
STAGE1_HARVESTED_SLURS = "stage1_harvested_slurs.json"
STAGE1_LEXICON = "stage1_slur_lexicon.json"

# Put your new target words here (Tamil script, Tanglish, or slang)
NEW_WORDS_TO_ADD = ["thevudiya","thevudiyalae"
]

# Safeguard: Never let generic auxiliary verbs become exact triggers
FALSE_POSITIVE_GUARDS = {
    "adi", "sey", "pannu", "podu", "kodu", "vaanggu", 
    "thallu", "izhu", "suththu", "thiruppu", "ganja", "mirugam"
}

def load_existing_words() -> set:
    existing = set()

    # 1. Pull from existing compiled trie if available
    if os.path.exists(STAGE1_TRIE_FILE):
        try:
            trie = joblib.load(STAGE1_TRIE_FILE)
            existing.update(trie.keys())
        except Exception:
            pass

    # 2. Pull from stage1_harvested_slurs.json
    if os.path.exists(STAGE1_HARVESTED_SLURS):
        with open(STAGE1_HARVESTED_SLURS, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                existing.update([w.strip().lower() for w in data if w.strip()])

    # 3. Pull from stage1_slur_lexicon.json
    if os.path.exists(STAGE1_LEXICON):
        with open(STAGE1_LEXICON, "r", encoding="utf-8") as f:
            lex = json.load(f)
            for k, meta in lex.items():
                cat = meta.get("category", "")
                sev = meta.get("severity", "")
                if cat == "slur" or sev == "severe" or cat == "family_insult":
                    existing.add(k.strip().lower())

    return existing

def recompile():
    words = load_existing_words()
    initial_count = len(words)

    # Ingest new targets
    added_count = 0
    for raw in NEW_WORDS_TO_ADD:
        cleaned = raw.strip().lower()
        if not cleaned:
            continue
        if cleaned in FALSE_POSITIVE_GUARDS:
            print(f"[Skipped] '{cleaned}' is in false-positive stopword list.")
            continue
        if cleaned not in words:
            words.add(cleaned)
            added_count += 1

    # Build fresh automaton
    trie = ahocorasick.Automaton()
    for word in sorted(words):
        trie.add_word(word, word)
    trie.make_automaton()

    # Save compiled trie
    joblib.dump(trie, STAGE1_TRIE_FILE)

    # Sync back to stage1_harvested_slurs.json
    with open(STAGE1_HARVESTED_SLURS, "w", encoding="utf-8") as f:
        json.dump(sorted(list(words)), f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("STAGE 1 TRIE RECOMPILED")
    print(f" • Previous words : {initial_count:,}")
    print(f" • New words added: {added_count:,}")
    print(f" • Total targets  : {len(words):,}")
    print(f" • Exported to    : {STAGE1_TRIE_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    recompile()