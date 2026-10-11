"""
Exports Stage 1 Aho-Corasick vocabulary and Stage 2 folded IDF weights
into a lightweight static JSON bundle for mobile deployment.
"""

import json
import os
import joblib

STAGE1_TRIE_FILE = "stage1_trie.joblib"
STAGE2_MODEL_FILE = "stage2_classifier.joblib"
OUTPUT_BUNDLE_FILE = "moderation_mobile_bundle.json"

# Common conversational auxiliary verbs/words protected against false positives
FALSE_POSITIVE_STOPWORDS = {
    "adi", "\u0b85\u0b9f\u0bbf",
    "sey", "\u0b9a\u0bc6\u0baf\u0bcd", "seyyura", "\u0b9a\u0bc6\u0baf\u0bcd\u0baf\u0bc1\u0bb1",
    "pannu", "\u0baa\u0ba3\u0bcd\u0ba3\u0bc1", "pannura", "\u0baa\u0ba3\u0bcd\u0ba3\u0bc1\u0bb1",
    "podu", "\u0baa\u0bcb\u0b9f\u0bc1", "podura", "\u0baa\u0bcb\u0b9f\u0bc1\u0bb1",
    "kodu", "\u0b95\u0bca\u0b9f\u0bc1", "kodukkira", "\u0b95\u0bca\u0b9f\u0bc1\u0b95\u0bcd\u0b95\u0bbf\u0bb1",
    "vaanggu", "\u0bb5\u0bbe\u0b99\u0bcd\u0b95\u0bc1", "vaanggura", "\u0bb5\u0bbe\u0b99\u0bcd\u0b95\u0bc1\u0bb1",
    "thallu", "\u0ba4\u0bb3\u0bcd\u0bb3\u0bc1", "thallura", "\u0ba4\u0bb3\u0bcd\u0bb3\u0bc1\u0bb1",
    "izhu", "\u0b87\u0bb4\u0bc1", "izhukura", "\u0b87\u0bb4\u0bc1\u0b95\u0bcd\u0b95\u0bc1\u0bb1",
    "suththu", "\u0b9a\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1", "suththura", "\u0b9a\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1\u0bb1",
    "thiruppu", "\u0ba4\u0bbf\u0bb0\u0bc1\u0baa\u0bcd\u0baa\u0bc1", "thiruppura", "\u0ba4\u0bbf\u0bb0\u0bc1\u0baa\u0bcd\u0baa\u0bc1\u0bb1",
    "kuththu", "\u0b95\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1", "kuththura", "\u0b95\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1\u0bb1",
    "ganja", "\u0b95\u0b9e\u0bcd\u0b9a\u0bbe",
    "mirugam", "\u0bae\u0bbf\u0bb0\u0bc1\u0b95\u0bae\u0bcd"
}


def export_bundle():
    print("[*] Loading trained model artifacts...")
    trie = joblib.load(STAGE1_TRIE_FILE)
    clf_pipeline = joblib.load(STAGE2_MODEL_FILE)

    # 1. Extract Stage 1 clean slurs (filtered from conversational auxiliary verbs)
    stage1_slurs = sorted([
        w.lower().strip() for w in trie.keys()
        if w.lower().strip() and w.lower().strip() not in FALSE_POSITIVE_STOPWORDS
    ])
    print(f"[*] Extracted {len(stage1_slurs)} clean Stage 1 exact slur targets.")

    # 2. Extract Stage 2 folded weights
    fu = clf_pipeline.named_steps["features"]
    clf = clf_pipeline.named_steps["clf"]

    word_vec = fu.transformer_list[0][1]
    char_vec = fu.transformer_list[1][1]

    word_names = word_vec.get_feature_names_out()
    word_idfs = word_vec.idf_
    n_word = len(word_names)

    char_names = char_vec.get_feature_names_out()
    char_idfs = char_vec.idf_

    coefs = clf.coef_[0]
    intercept = float(clf.intercept_[0])

    weights = {}

    # Weight folding: w'_{folded} = w_i * idf_i
    for i, name in enumerate(word_names):
        w_val = round(float(coefs[i] * word_idfs[i]), 6)
        weights[f"w:{name}"] = w_val
        if name not in weights:
            weights[name] = w_val

    for j, name in enumerate(char_names):
        c_val = round(float(coefs[n_word + j] * char_idfs[j]), 6)
        weights[f"c:{name}"] = c_val
        if name not in weights:
            weights[name] = c_val
        else:
            weights[name] = round(weights[name] + c_val, 6)

    bundle = {
        "stage1_exact_slurs": stage1_slurs,
        "stage2_intercept": round(intercept, 6),
        "stage2_weights": weights,
    }

    with open(OUTPUT_BUNDLE_FILE, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    size_kb = os.path.getsize(OUTPUT_BUNDLE_FILE) / 1024.0
    print(f"[+] Bundle written to '{OUTPUT_BUNDLE_FILE}' ({size_kb:.1f} KB).")
    print(f"    • Stage 1 targets: {len(stage1_slurs)}")
    print(f"    • Stage 2 intercept: {bundle['stage2_intercept']}")
    print(f"    • Stage 2 weight entries: {len(weights)}")


if __name__ == "__main__":
    export_bundle()
