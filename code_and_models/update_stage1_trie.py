"""
Incremental update script to add new slur targets to Stage 1 Aho-Corasick trie
without retraining Stage 2 classifier.
"""

import sys
import joblib
import ahocorasick
from export_for_mobile import export_bundle

STAGE1_TRIE_FILE = "stage1_trie.joblib"


def add_slurs(new_words):
    try:
        trie = joblib.load(STAGE1_TRIE_FILE)
        existing_words = set(trie.keys())
    except Exception:
        print("[!] No existing trie found. Creating fresh automaton.")
        existing_words = set()

    added = 0
    for w in new_words:
        clean = w.strip().lower()
        if clean and clean not in existing_words:
            existing_words.add(clean)
            added += 1

    # Recompile automaton
    new_trie = ahocorasick.Automaton()
    for w in existing_words:
        new_trie.add_word(w, w)
    new_trie.make_automaton()

    joblib.dump(new_trie, STAGE1_TRIE_FILE)
    print(f"[+] Added {added} new slur targets. Total targets in Stage 1: {len(existing_words):,}")

    # Synchronize mobile bundle
    print("[*] Re-exporting mobile bundle...")
    export_bundle()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
        add_slurs(targets)
    else:
        print("Usage: python update_stage1_trie.py <word1> <word2> ...")
