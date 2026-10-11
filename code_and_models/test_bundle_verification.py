"""
Runnable self-check verifying moderation_mobile_bundle.json integrity
and exact behavior of the mobile algorithm against test cases.
"""

import json
import math
import os
import re

BUNDLE_FILE = "moderation_mobile_bundle.json"


def run_checks():
    assert os.path.exists(BUNDLE_FILE), f"Missing {BUNDLE_FILE}"
    with open(BUNDLE_FILE, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    slurs = set(bundle["stage1_exact_slurs"])
    intercept = bundle["stage2_intercept"]
    weights = bundle["stage2_weights"]

    assert len(slurs) > 400, f"Expected >400 slurs, got {len(slurs)}"
    assert isinstance(intercept, float), "Intercept must be float"
    assert len(weights) > 1000, f"Expected >1000 weights, got {len(weights)}"

    def is_word_char(c):
        return c.isalnum() or ("\u0b80" <= c <= "\u0bff")

    def evaluate(text):
        clean = text.lower()
        n = len(clean)

        # Stage 1: Trie / Slur scan with boundary check
        for slur in slurs:
            if slur in clean:
                idx = 0
                while True:
                    pos = clean.find(slur, idx)
                    if pos == -1:
                        break
                    end = pos + len(slur) - 1
                    b_start = (pos == 0) or not is_word_char(clean[pos - 1])
                    b_end = (end + 1 >= n) or not is_word_char(clean[end + 1])
                    if b_start and b_end:
                        return {"blocked": True, "stage": 1, "reason": slur, "prob": 1.0}
                    idx = pos + 1

        # Stage 2: Feature evaluation
        tokens = [t for t in re.findall(r"\b\w\w+\b", clean, re.UNICODE)]
        w_ngrams = set(tokens)
        for i in range(len(tokens) - 1):
            w_ngrams.add(f"{tokens[i]} {tokens[i+1]}")

        c_ngrams = set()
        for length in (3, 4, 5):
            for i in range(len(clean) - length + 1):
                c_ngrams.add(clean[i : i + length])

        score = intercept
        for w in w_ngrams:
            score += weights.get(f"w:{w}", weights.get(w, 0.0))
        for c in c_ngrams:
            score += weights.get(f"c:{c}", weights.get(c, 0.0))

        prob = 1.0 / (1.0 + math.exp(-max(-50.0, min(50.0, score))))
        blocked = prob >= 0.50
        return {"blocked": blocked, "stage": 2, "prob": prob}

    # Test cases:
    # 1. Slur -> Block Stage 1
    res = evaluate("avan oru soothiran da")
    assert res["blocked"] and res["stage"] == 1, "Failed Stage 1 slur block"

    # 2. Boundary collision safe (romba vs omba, kundavai vs kundi) -> Pass Stage 1
    res = evaluate("romba nallavan da ivan")
    assert not res["blocked"] and res["stage"] == 2, "Failed boundary collision check"

    res = evaluate("kundavai is a character")
    assert not res["blocked"] and res["stage"] == 2, "Failed boundary collision check"

    # 3. Conversational phrases with auxiliary verbs -> Pass
    res = evaluate("call pannu bro free ah iruka")
    assert not res["blocked"], "Auxiliary verb falsely blocked"

    res = evaluate("enaku unna romba pidichiruku bro")
    assert not res["blocked"], "Friendly conversational banter falsely blocked"

    # 4. Sarcasm / Mock-praise -> Block Stage 2
    res = evaluate("Periya english professor")
    assert res["blocked"] and res["stage"] == 2, "Failed Stage 2 sarcasm block"

    res = evaluate("Super logic bro unaku award tharanum")
    assert res["blocked"] and res["stage"] == 2, "Failed Stage 2 mock-praise block"

    print("[+] All self-check test assertions passed successfully.")


if __name__ == "__main__":
    run_checks()
