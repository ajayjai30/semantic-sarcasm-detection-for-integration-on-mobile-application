import os
import time
import joblib
import ahocorasick
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression

STAGE1_TRIE_FILE = "stage1_trie.joblib"
STAGE2_MODEL_FILE = "stage2_classifier.joblib"

# ============================================================
# 1. WORD-BOUNDARY HELPER (PREVENTS 'romba' -> 'omba' COLLISION)
# ============================================================
def is_boundary_match(text: str, start_idx: int, end_idx: int) -> bool:
    """Ensures matched token is standalone, not inside a valid word."""
    if start_idx > 0 and text[start_idx - 1].isalnum():
        return False
    if end_idx + 1 < len(text) and text[end_idx + 1].isalnum():
        return False
    return True

# ============================================================
# 2. MODEL INITIALIZATION / FALLBACK LOADER
# ============================================================
def load_stage1_automaton():
    if os.path.exists(STAGE1_TRIE_FILE):
        print(f"[*] Loaded compiled Stage 1 Trie from '{STAGE1_TRIE_FILE}'")
        return joblib.load(STAGE1_TRIE_FILE)
    
    print("[!] 'stage1_trie.joblib' not found. Rebuilding fallback trie...")
    trie = ahocorasick.Automaton()
    fallback_words = ["punda", "koodhi", "thayoli", "soothiran", "omba", "சூத்திரன்"]
    for w in fallback_words:
        trie.add_word(w.lower(), w.lower())
    trie.make_automaton()
    return trie

def load_or_train_stage2_model():
    if os.path.exists(STAGE2_MODEL_FILE):
        print(f"[*] Loaded compiled Stage 2 Classifier from '{STAGE2_MODEL_FILE}'")
        return joblib.load(STAGE2_MODEL_FILE)

    print("[*] Training calibrated Stage 2 linear classifier...")
    train_texts = [
        # Class 1: Mock-praise & Sarcasm
        "Periya english professor 🤣😆",
        "Periya einstein moodu da imbecile",
        "Just the level of intelligence i need in my life",
        "Einstein vandhu vimarsanam panra ennam vera irukada incel kootame",
        "Tharkuri nu prove pannitey irukkanunga...",
        "aaha periya scientist ivaru",
        "Super logic bro unaku award tharanum",
        "wah kya dimaag hai bhai",
        # Class 0: Clean banter, Genuine praise, Daily peer talk
        'Use "hmmm mMmmmMmmm" before "pudichiruku romba pudichiruku" so they don’t find your message creepy.',
        "Which dept and batch bro?",
        "Hospital poiyacha",
        "Enna college konjam sollugala pls 🙏",
        "Nice bro. Dm panunga",
        "enaku unna romba pidichiruku bro",
        "Nee oru post podu bro, pesalaam",
        "call pannu bro free ah iruka",
        "Bacterial infection ku antibiotics vachu control pannirlam",
        "Good morning Beautiful People Have a good day ahead!"
    ]
    train_labels = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    pipeline = Pipeline([
        ("features", FeatureUnion([
            ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), analyzer="word", sublinear_tf=True)),
            ("char_tfidf", TfidfVectorizer(ngram_range=(3, 5), analyzer="char", sublinear_tf=True))
        ])),
        ("clf", LogisticRegression(C=2.0, class_weight="balanced", solver="liblinear", random_state=42))
    ])
    pipeline.fit(train_texts, train_labels)
    joblib.dump(pipeline, STAGE2_MODEL_FILE)
    return pipeline

# ============================================================
# 3. RUNTIME PIPELINE EVALUATOR
# ============================================================
def evaluate(text: str, trie, clf, threshold: float = 0.50):
    t0 = time.perf_counter()
    clean = text.strip().lower()

    # --- STAGE 1: SUB-20µs STRING SCAN ---
    matches = []
    for end_idx, matched_word in trie.iter(clean):
        start_idx = end_idx - len(matched_word) + 1
        if is_boundary_match(clean, start_idx, end_idx):
            matches.append(matched_word)

    t1 = time.perf_counter()
    stage1_latency = (t1 - t0) * 1_000_000

    if matches:
        return {
            "status": "STAGE 1 BLOCK",
            "stage_reached": 1,
            "details": f"Explicit Slur(s): {list(set(matches))}",
            "latency_us": round(stage1_latency, 2)
        }

    # --- STAGE 2: CONTEXTUAL N-GRAM CLASSIFIER ---
    t2 = time.perf_counter()
    prob = clf.predict_proba([text])[0][1]
    t3 = time.perf_counter()
    stage2_latency = (t3 - t2) * 1_000_000

    decision = "STAGE 2 BLOCK" if prob >= threshold else "STAGE 2 ALLOW"
    return {
        "status": decision,
        "stage_reached": 2,
        "details": f"Hostility/Sarcasm Probability: {prob:.4f} (Threshold: {threshold:.2f})",
        "stage1_latency_us": round(stage1_latency, 2),
        "stage2_latency_us": round(stage2_latency, 2),
        "total_latency_us": round(stage1_latency + stage2_latency, 2)
    }

# ============================================================
# 4. INTERACTIVE REPL LOOP
# ============================================================
def main():
    print("=" * 70)
    print("      TWO-STAGE NLP MODERATION ENGINE — RUNTIME TEST HARNESS")
    print("=" * 70)

    trie = load_stage1_automaton()
    clf = load_or_train_stage2_model()

    print("\nSystem ready! Type any sentence to inspect routing behavior.")
    print("Type 'exit' or 'q' to terminate the session.\n")

    while True:
        try:
            user_input = input("\n[Enter Message] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["q", "quit", "exit"]:
                print("Exiting session.")
                break

            result = evaluate(user_input, trie, clf)

            print("-" * 65)
            if result["stage_reached"] == 1:
                print(f"Decision     : \033[91m🚫 BLOCKED AT STAGE 1\033[0m")
                print(f"Trigger      : {result['details']}")
                print(f"Stage 2 Call : Skipped (Compute saved)")
                print(f"Latency      : {result['latency_us']} µs")
            else:
                print(f"Stage 1      : \033[92m✔ PASSED\033[0m ({result['stage1_latency_us']} µs)")
                if "BLOCK" in result["status"]:
                    print(f"Stage 2      : \033[91m🚫 BLOCKED (Sarcasm/Hostility)\033[0m")
                else:
                    print(f"Stage 2      : \033[92m✔ ALLOWED (Clean Conversation)\033[0m")
                print(f"Metrics      : {result['details']}")
                print(f"Total Latency: {result['total_latency_us']} µs")
            print("-" * 65)

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break

if __name__ == "__main__":
    main()