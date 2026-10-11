import json
import os
import time
import joblib
import ahocorasick
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression

STAGE1_OLD_LEXICON = "stage1_slur_lexicon.json" if os.path.exists("stage1_slur_lexicon.json") else os.path.join("..", "datasets", "stage1_slur_lexicon.json")
STAGE1_REDDIT_SLURS = "stage1_harvested_slurs.json" if os.path.exists("stage1_harvested_slurs.json") else os.path.join("..", "datasets", "stage1_harvested_slurs.json")
STAGE1_OUTPUT_TRIE = "stage1_trie.joblib"

# Common auxiliary verbs/words that must NEVER be standalone substring triggers
FALSE_POSITIVE_STOPWORDS = {
    "adi", "அடி",
    "sey", "செய்", "seyyura", "செய்யுற",
    "pannu", "பண்ணு", "pannura", "பண்ணுற",
    "podu", "போடு", "podura", "போடுற",
    "kodu", "கொடு", "kodukkira", "கொடுக்கிற",
    "vaanggu", "வாங்கு", "vaanggura", "வாங்குற",
    "thallu", "தள்ளு", "thallura", "தள்ளுற",
    "izhu", "இழு", "izhukura", "இழுக்குற",
    "suththu", "சுத்து", "suththura", "சுத்துற",
    "thiruppu", "திருப்பு", "thiruppura", "திருப்புற",
    "kuththu", "குத்து", "kuththura", "குத்துற",
    "ganja", "கஞ்சா",
    "mirugam", "மிருகம்"
}

def load_and_clean_stage1_lexicon():
    compiled_blocklist = set()

    # 1. Ingest stage1_slur_lexicon.json
    if os.path.exists(STAGE1_OLD_LEXICON):
        with open(STAGE1_OLD_LEXICON, "r", encoding="utf-8") as f:
            lexicon_data = json.load(f)

        for term, meta in lexicon_data.items():
            clean_term = term.strip().lower()
            if not clean_term:
                continue

            category = meta.get("category", "").lower()
            severity = meta.get("severity", "").lower()

            # Rule: Protect against single-word auxiliary verb collisions
            if clean_term in FALSE_POSITIVE_STOPWORDS:
                continue

            # Ingest all slurs (regardless of severity) and severe/family insults
            if category == "slur" or severity == "severe" or category == "family_insult":
                compiled_blocklist.add(clean_term)

        print(f"Loaded {len(compiled_blocklist):,} clean targets from '{STAGE1_OLD_LEXICON}'.")
    else:
        print(f"Warning: '{STAGE1_OLD_LEXICON}' not found.")

    # 2. Ingest stage1_harvested_slurs.json (from Reddit corpus)
    if os.path.exists(STAGE1_REDDIT_SLURS):
        with open(STAGE1_REDDIT_SLURS, "r", encoding="utf-8") as f:
            reddit_slurs = json.load(f)

        for slur in reddit_slurs:
            clean_slur = slur.strip().lower()
            if clean_slur and clean_slur not in FALSE_POSITIVE_STOPWORDS:
                compiled_blocklist.add(clean_slur)

        print(f"Total merged Stage 1 blocklist targets: {len(compiled_blocklist):,}")

    # 3. Build Aho-Corasick Automaton
    trie = ahocorasick.Automaton()
    for word in compiled_blocklist:
        trie.add_word(word, word)
    trie.make_automaton()

    joblib.dump(trie, STAGE1_OUTPUT_TRIE)
    print(f"Compiled Stage 1 Automaton successfully saved to '{STAGE1_OUTPUT_TRIE}'.\n")
    return trie

# ============================================================
# STAGE 2 MOCK RETRAINING & INFERENCE HARNESS
# ============================================================
def setup_stage2_model():
    # Anchors for contextual training
    train_texts = [
        "Periya english professor 🤣😆",
        "Periya einstein moodu da imbecile",
        "Just the level of intelligence i need in my life",
        "Einstein vandhu vimarsanam panra ennam vera irukada incel kootame",
        "Tharkuri nu prove pannitey irukkanunga...",
        "aaha periya scientist ivaru",
        "Super logic bro unaku award tharanum",
        'Use "hmmm mMmmmMmmm" before "pudichiruku romba pudichiruku" so they don’t find your message creepy.',
        "Which dept and batch bro?",
        "Hospital poiyacha",
        "Enna college konjam sollugala pls 🙏",
        "Nice bro. Dm panunga",
        "enaku unna romba pidichiruku bro",
        "post podu bro pesalam",
        "call pannu bro free ah iruka",
        "Bacterial infection ku antibiotics vachu control pannirlam"
    ]
    train_labels = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    pipeline = Pipeline([
        ("features", FeatureUnion([
            ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), analyzer="word", sublinear_tf=True)),
            ("char_tfidf", TfidfVectorizer(ngram_range=(3, 5), analyzer="char", sublinear_tf=True))
        ])),
        ("clf", LogisticRegression(C=2.0, class_weight="balanced", solver="liblinear", random_state=42))
    ])
    pipeline.fit(train_texts, train_labels)
    return pipeline

def test_pipeline(trie, stage2_model):
    test_cases = [
        # Must block in Stage 1 via old lexicon (Tamil Script)
        "நீ ஒரு சூத்திரன் டா",
        "அவன் ஒரு கேவலமானவன்",
        # Must block in Stage 1 via old lexicon (Tanglish Script)
        "avan oru soothiran da",
        "un amma pundai",
        # Must block in Stage 1 via Reddit-harvested slurs
        "Dai ungomma bundaila irukku da paithiyakaara koodhi",
        # Must NOT trigger Stage 1 despite containing words like 'podu' / 'pannu' / 'pidichiruku'
        "Nee oru post podu bro, pesalaam",
        "call pannu bro free ah iruka",
        "enaku unna romba pidichiruku",
        # Must pass Stage 1 and be BLOCKED by Stage 2 (Sarcasm/Mockery)
        "Periya english professor 🤣😆",
        "aaha periya scientist ivaru award tharalam"
    ]

    print(f"{'Input Message':<55} | {'Decision':<6} | {'Stage':<5} | {'Matched / Prob'}")
    print("-" * 95)

    for text in test_cases:
        t0 = time.perf_counter()
        clean = text.lower()
        matches = [m for _, m in trie.iter(clean)]

        if matches:
            t1 = time.perf_counter()
            print(f"{text[:53]:<55} | BLOCK  | 1     | {list(set(matches))[:2]}")
        else:
            prob = stage2_model.predict_proba([text])[0][1]
            t1 = time.perf_counter()
            decision = "BLOCK" if prob >= 0.50 else "ALLOW"
            print(f"{text[:53]:<55} | {decision:<6} | 2     | Prob: {prob:.4f}")

if __name__ == "__main__":
    trie = load_and_clean_stage1_lexicon()
    stage2_model = setup_stage2_model()
    test_pipeline(trie, stage2_model)