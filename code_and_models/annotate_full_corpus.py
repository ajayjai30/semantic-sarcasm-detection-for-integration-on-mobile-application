import os
import json
import time
from itertools import cycle
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ============================================================
# 1. API KEYS POOL
# ============================================================
GEMINI_API_KEYS = [] # fill up one or more gemini api keys or u can change other ai models, for that change the api structure
# Initialize clients across keys
CLIENT_POOL = [genai.Client(api_key=key.strip()) for key in GEMINI_API_KEYS if key.strip()]
client_rotator = cycle(CLIENT_POOL)

# Configured lightweight model for fast throughput and higher rate limits
MODEL_NAME = "gemini-3.5-flash-lite"

INPUT_FILE = "unified_reddit_chat_corpus.json"
CHECKPOINT_FILE = "stage2_labeled_checkpoint.json"
FINAL_STAGE2_OUTPUT = "stage2_annotated_training_corpus.json"
FINAL_STAGE1_SLURS = "stage1_harvested_slurs.json"

BATCH_SIZE = 30  # Flash-Lite easily handles 30 short lines per call

# ============================================================
# 2. STRUCTURED RESPONSE SCHEMA
# ============================================================
class ItemAnnotation(BaseModel):
    id: int
    is_toxic_or_sarcastic: bool = Field(
        description="True for sarcasm, mock-praise ('பாராட்டுற மாதிரி கலாய்க்கிறது'), passive-aggressive ridicule, direct hostility, or toxic trolling. False for genuine conversation, questions, greetings, everyday small talk, or harmless slang."
    )
    extracted_severe_slurs: list[str] = Field(
        default=[],
        description="Explicit, zero-tolerance vulgar slurs or severe cuss words present in the text to add to the Stage 1 trie filter. Return [] if none exist."
    )

class BatchAnnotationEnvelope(BaseModel):
    results: list[ItemAnnotation]

# ============================================================
# 3. FAST INFERENCE WITH ROUND-ROBIN CLIENT
# ============================================================
def annotate_batch_chunk(client_instance: genai.Client, batch: list[tuple[int, str]]) -> list[ItemAnnotation]:
    formatted_lines = "\n".join([f"[{idx}] {text}" for idx, text in batch])
    
    prompt = f"""
You are an expert NLP data annotator evaluating Indian multilingual chat data (Tamil, Tanglish, Hindi, Hinglish, English).

Evaluate each message:
1. `is_toxic_or_sarcastic`:
   - Set to TRUE (1) if the message contains sarcasm, mock-compliments ('பாராட்டுற மாதிரி கலாய்க்கிறது'), passive-aggressive trolling, insults, or hostility.
   - Set to FALSE (0) if the message is genuine small talk, neutral discussion, ordinary peer chatter, greetings, or benign banter.
2. `extracted_severe_slurs`:
   - Extract raw zero-tolerance vulgar profanities and severe slurs (e.g., variations of punda, thayoli, koodhi, chutiya, bhosdiwale) for an exact-match blocklist. Return an empty list if none exist.

Messages to annotate:
{formatted_lines}
"""

    response = client_instance.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BatchAnnotationEnvelope,
            temperature=0.0,
        ),
    )
    
    parsed = json.loads(response.text)
    return parsed.get("results", [])

# ============================================================
# 4. CHECKPOINT LOGIC
# ============================================================
def load_or_init_progress():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("labeled_items", []), set(data.get("slurs", [])), data.get("processed_index", 0)
    return [], set(), 0

def save_checkpoint(labeled_items, slurs, current_idx):
    payload = {
        "processed_index": current_idx,
        "labeled_items": labeled_items,
        "slurs": sorted(list(slurs))
    }
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

# ============================================================
# 5. EXECUTION PIPELINE
# ============================================================
def main():
    if not CLIENT_POOL:
        print("Error: Add at least one valid key to GEMINI_API_KEYS.")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not locate '{INPUT_FILE}'.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_corpus = json.load(f)

    cleaned_corpus = list(dict.fromkeys([line.strip() for line in raw_corpus if line.strip()]))
    total_samples = len(cleaned_corpus)
    print(f"Running '{MODEL_NAME}' across {len(CLIENT_POOL)} pooled key(s) on {total_samples:,} messages.")

    labeled_items, discovered_slurs, start_idx = load_or_init_progress()
    if start_idx > 0:
        print(f"Resuming from index {start_idx:,}...")

    for i in range(start_idx, total_samples, BATCH_SIZE):
        chunk = cleaned_corpus[i:i + BATCH_SIZE]
        indexed_chunk = [(idx, text) for idx, text in enumerate(chunk)]

        success = False
        max_attempts = len(CLIENT_POOL) * 2

        for attempt in range(max_attempts):
            active_client = next(client_rotator)
            try:
                batch_results = annotate_batch_chunk(active_client, indexed_chunk)
                
                result_map = {res["id"]: res for res in batch_results}
                for idx, text in indexed_chunk:
                    item_data = result_map.get(idx)
                    is_toxic = item_data["is_toxic_or_sarcastic"] if item_data else False
                    labeled_items.append({
                        "text": text,
                        "label": 1 if is_toxic else 0
                    })
                    
                    if item_data:
                        for slur in item_data.get("extracted_severe_slurs", []):
                            clean_slur = slur.strip().lower()
                            if clean_slur:
                                discovered_slurs.add(clean_slur)

                success = True
                break

            except Exception as e:
                err_msg = str(e).lower()
                if any(kw in err_msg for kw in ["429", "resource_exhausted", "quota"]):
                    print(f"[Quota Limit] Rotating key immediately... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(0.5)
                else:
                    print(f"[Warning] Error: {e}. Switching key...")
                    time.sleep(1.0)

        if not success:
            print(f"[Fallback] Defaulting batch {i} to label 0.")
            for _, text in indexed_chunk:
                labeled_items.append({"text": text, "label": 0})

        current_processed = min(i + BATCH_SIZE, total_samples)
        print(f"Progress: {current_processed:,} / {total_samples:,}")
        save_checkpoint(labeled_items, discovered_slurs, current_processed)
        
        # Flash-Lite latency is low; 0.2s pause is sufficient
        time.sleep(0.2)

    with open(FINAL_STAGE2_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(labeled_items, f, ensure_ascii=False, indent=2)

    with open(FINAL_STAGE1_SLURS, "w", encoding="utf-8") as f:
        json.dump(sorted(list(discovered_slurs)), f, ensure_ascii=False, indent=2)

    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

    print("\nPipeline Complete!")
    print(f" • Stage 2 Labeled Corpus : {len(labeled_items):,} saved to {FINAL_STAGE2_OUTPUT}")
    print(f" • Stage 1 Extracted Slurs: {len(discovered_slurs):,} saved to {FINAL_STAGE1_SLURS}")

if __name__ == "__main__":
    main()