# Multilingual Content Moderation Engine — System Spec & Agent Directives

## 1. AGENT CONTEXT GUARDRAIL (STRICT RULE)

> **DO NOT OPEN, READ, OR INDEX ANY OF THE FOLLOWING RAW JSON DATA FILES:**
>
> - `unified_reddit_chat_corpus*.json`
> - `stage1_slur_lexicon.json`
> - `stage2_annotated_training_corpus*.json`
>
> These files contain thousands of lines of raw text, conversational data, and glossary terms. Reading them will saturate your context window and degrade reasoning performance. All structural schemas, token rules, and mathematical mappings are already defined in this document.

---

## 2. SYSTEM ARCHITECTURE & MATHEMATICAL SPECIFICATION

This engine is a low-latency, two-stage on-device content moderation pipeline designed to filter Tamil and Tanglish text natively on mobile devices in $< 300\ \mu\text{s}$ with zero ML runtime dependencies (no PyTorch, ONNX, or TensorFlow).

### Stage 1: Deterministic Aho-Corasick Automaton ($< 25\ \mu\text{s}$)

- **Purpose:** Immediate hard-blocking of severe slurs, caste abuse, and explicit vulgarity in both Tamil Unicode script and Romanized Tanglish.
- **Critical Invariant — Word Boundary Check:** Substring matches must be verified with boundary validation (`isalnum` checks on index `start - 1` and `end + 1`). This prevents false-positive collisions where innocent words contain slur roots (e.g., ensuring `"romba"` does not trigger on `"omba"`, and `"kundavai"` does not trigger on `"kundi"`).
- **Behavior:** If a slur is matched, execution terminates immediately with `BLOCK` (Stage 1). Downstream compute is completely bypassed.

### Stage 2: Sub-Word Linear Sarcasm & Mock-Praise Classifier ($< 250\ \mu\text{s}$)

- **Purpose:** Identifies contextual toxicity, sarcasm, ridicule, and mock-praise (e.g., _"Periya english professor 🤣"_, _"super logic bro unaku award tharanum"_) while safely allowing everyday colloquial discourse (_"enaku unna romba pidichiruku"_, _"call pannu bro"_).
- **Feature Space:** A Feature Union of word $n$-grams $(1, 2)$ and character $n$-grams $(3, 5)$ to handle spelling variations in unstandardized Tanglish transliteration.
- **Weight Folding Equation:** To execute on mobile without a TF-IDF matrix vectorizer, IDF values are pre-multiplied into the Logistic Regression coefficients at export time:
  $$w'_{\text{folded}} = w_i \cdot \text{idf}_i$$
- **Inference Evaluation:** Mobile inference requires only a hash map lookup over input $n$-grams, summing folded weights with the bias term $b$, and passing through the standard Sigmoid function:
  $$P(\text{Hostile/Sarcastic}) = \frac{1}{1 + e^{-(\sum w'_{\text{folded}} + b)}}$$
  The decision threshold is calibrated to $0.50$ (or $0.55$).

---

## 3. FILE MANIFEST & WORKSPACE ROLES

| File                                             | Type                | Role & Description                                                                                                                   |
| :----------------------------------------------- | :------------------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| `stage1_slur_lexicon.json`                       | Data (DO NOT READ)  | Seed dictionary of Tamil script and Tanglish profanities and identity slurs.                                                         |
| `unified_reddit_chat_corpus*.json`               | Data (DO NOT READ)  | Scraped authentic Reddit chat comments reflecting real Tanglish discourse and banter.                                                |
| `stage1_trie.joblib`                             | Binary Artifact     | Compiled Aho-Corasick automaton trie storing clean Stage 1 targets.                                                                  |
| `stage2_classifier.joblib`                       | Binary Artifact     | Trained Scikit-Learn pipeline (FeatureUnion TF-IDF + LogisticRegression).                                                            |
| `moderation_mobile_bundle.json`                  | Deployment Artifact | Lightweight static JSON bundle containing: `stage1_exact_slurs` (list), `stage2_intercept` (float), and `stage2_weights` (hash map). |
| `interactive_test_moderation.py`                 | Python Script       | Interactive CLI REPL for live evaluation, latency profiling, and edge-case testing.                                                  |
| `update_stage1_trie.py`                          | Python Script       | Incremental update script to add new slur targets to Stage 1 without retraining Stage 2.                                             |
| `train_stage2_expanded.py` / `train_stage2_*.py` | Python Script       | Model training scripts utilizing sub-word feature extractors and contrastive seeds.                                                  |
| `export_for_mobile.py`                           | Python Script       | Computes folded weights ($w' = w \cdot \text{idf}$) and generates `moderation_mobile_bundle.json`.                                   |

---

## 4. AGENT DELIVERABLES REQUIRED

You are tasked with generating the following production deliverables for this workspace:

### Deliverable A: Embedded Mobile Client API & Service

Create a self-contained, production-ready embedded API class for mobile (Android/Kotlin) that can be imported directly into any mobile app.

- **Requirements:**
  1. Zero external ML libraries (use only standard collections and native JSON parsing).
  2. Implement an in-memory `MobileModerationClient` (or `MobileModerationService`) exposing clean asynchronous and synchronous methods:
     - `fun evaluate(text: String): ModerationResult`
     - `suspend fun evaluateAsync(text: String): ModerationResult`
  3. Strict word boundary checks for Stage 1.
  4. Generation of word $(1, 2)$-grams and character $(3, 5)$-grams for Stage 2 weight aggregation.
  5. Detailed response structure returning: `isBlocked: Boolean`, `stage: Int`, `reason: String`, `probability: Float`, and `latencyUs: Long`.

### Deliverable B: Production `README.md`

Write a comprehensive project `README.md` containing:

1. Executive architecture overview and stage sequence diagram/flow.
2. Latency and resource benchmarks ($< 300\ \mu\text{s}$ execution, $< 500\text{ KB}$ asset footprint).
3. Local Python setup and CLI testing guide.
4. Model updating and retraining instructions.
5. Android/Mobile integration instructions.

### Deliverable C: Architecture & Integration Spec (`AGENT.md`)

Write an `AGENT.md` developer guide documenting:

1. Mathematical justification and proof for IDF weight folding.
2. The boundary check algorithm and edge-case protection rules.
3. Step-by-step pipeline workflow connecting Python training to native mobile consumption.
4. Maintenance and update runbooks for adding new vocabulary or recalibrating decision boundaries.
