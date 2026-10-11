#!/usr/bin/env python3
"""
Tamil Nadu District-wise Tamil/Tanglish Language Dataset Generator
Generates ~50K-150K total entries across 38 districts with regional variations.
"""

import json
import os
import random
import hashlib
from typing import List, Dict, Any

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = r"E:\tamil_slang_dataset"
SEED = 42
random.seed(SEED)

# ============================================================
# DISTRICT METADATA - All 38 districts of Tamil Nadu
# ============================================================

DISTRICTS = {
    "Chennai": {
        "dialect_region": "Northern",
        "sub_dialect": "Madras Bashai",
        "languages_influenced": ["English", "Telugu", "Hindi", "Urdu"],
        "word_count_target": 5000,
    },
    "Coimbatore": {
        "dialect_region": "Western",
        "sub_dialect": "Kongu Tamil",
        "languages_influenced": ["Kannada", "Telugu", "English"],
        "word_count_target": 4000,
    },
    "Madurai": {
        "dialect_region": "Southern",
        "sub_dialect": "Madurai Bashai",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 4000,
    },
    "Tirunelveli": {
        "dialect_region": "Southern",
        "sub_dialect": "Nellai Tamil / ThenPaandi Tamil",
        "languages_influenced": ["Malayalam", "Standard Tamil"],
        "word_count_target": 3500,
    },
    "Thanjavur": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil / Chola Tamil",
        "languages_influenced": ["Standard Tamil", "Sanskrit"],
        "word_count_target": 3500,
    },
    "Tiruchirappalli": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 3500,
    },
    "Salem": {
        "dialect_region": "Western",
        "sub_dialect": "Kongu Tamil (North)",
        "languages_influenced": ["Kannada", "Telugu"],
        "word_count_target": 3000,
    },
    "Erode": {
        "dialect_region": "Western",
        "sub_dialect": "Kongu Tamil",
        "languages_influenced": ["Kannada", "Telugu"],
        "word_count_target": 3000,
    },
    "Tiruppur": {
        "dialect_region": "Western",
        "sub_dialect": "Kongu Tamil",
        "languages_influenced": ["Kannada", "Telugu", "English"],
        "word_count_target": 3000,
    },
    "Thoothukudi": {
        "dialect_region": "Southern",
        "sub_dialect": "Nellai Tamil variant",
        "languages_influenced": ["English", "Standard Tamil"],
        "word_count_target": 3000,
    },
    "Kanyakumari": {
        "dialect_region": "Southern",
        "sub_dialect": "Nanjil Tamil",
        "languages_influenced": ["Malayalam", "English"],
        "word_count_target": 3000,
    },
    "Dindigul": {
        "dialect_region": "Western",
        "sub_dialect": "Western Tamil",
        "languages_influenced": ["Kannada", "Telugu"],
        "word_count_target": 2500,
    },
    "Vellore": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu", "Urdu"],
        "word_count_target": 2500,
    },
    "Tiruvallur": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu", "English"],
        "word_count_target": 2500,
    },
    "Kancheepuram": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu", "English"],
        "word_count_target": 2500,
    },
    "Tiruvannamalai": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu"],
        "word_count_target": 2500,
    },
    "Cuddalore": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Krishnagiri": {
        "dialect_region": "Northern",
        "sub_dialect": "North-Western Tamil",
        "languages_influenced": ["Kannada", "Telugu"],
        "word_count_target": 2500,
    },
    "Dharmapuri": {
        "dialect_region": "Western",
        "sub_dialect": "North-Western Tamil",
        "languages_influenced": ["Kannada"],
        "word_count_target": 2500,
    },
    "Namakkal": {
        "dialect_region": "Western",
        "sub_dialect": "Kongu Tamil",
        "languages_influenced": ["Kannada"],
        "word_count_target": 2500,
    },
    "Karur": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil variant",
        "languages_influenced": ["Kongu Tamil"],
        "word_count_target": 2500,
    },
    "Pudukkottai": {
        "dialect_region": "Central",
        "sub_dialect": "Chola Nadu Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Ramanathapuram": {
        "dialect_region": "Southern",
        "sub_dialect": "Ramnad Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Virudhunagar": {
        "dialect_region": "Southern",
        "sub_dialect": "Southern Tamil variant",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Sivaganga": {
        "dialect_region": "Southern",
        "sub_dialect": "Southern Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Theni": {
        "dialect_region": "Southern",
        "sub_dialect": "Western Tamil variant",
        "languages_influenced": ["Kannada"],
        "word_count_target": 2500,
    },
    "Tiruvarur": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil / Chola Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Nagapattinam": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2500,
    },
    "Viluppuram": {
        "dialect_region": "Central",
        "sub_dialect": "South Arcot Tamil",
        "languages_influenced": ["Telugu"],
        "word_count_target": 2500,
    },
    "Nilgiris": {
        "dialect_region": "Western",
        "sub_dialect": "Badaga Tamil / Kota Tamil",
        "languages_influenced": ["Kannada", "Malayalam", "English"],
        "word_count_target": 2500,
    },
    "Perambalur": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2000,
    },
    "Ariyalur": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2000,
    },
    "Chengalpattu": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu", "English"],
        "word_count_target": 2500,
    },
    "Kallakurichi": {
        "dialect_region": "Central",
        "sub_dialect": "South Arcot Tamil",
        "languages_influenced": ["Telugu"],
        "word_count_target": 2000,
    },
    "Ranipet": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu"],
        "word_count_target": 2500,
    },
    "Tirupathur": {
        "dialect_region": "Northern",
        "sub_dialect": "Northern Tamil",
        "languages_influenced": ["Telugu", "Kannada"],
        "word_count_target": 2000,
    },
    "Tenkasi": {
        "dialect_region": "Southern",
        "sub_dialect": "Nellai Tamil variant",
        "languages_influenced": ["Malayalam"],
        "word_count_target": 2500,
    },
    "Mayiladuthurai": {
        "dialect_region": "Central",
        "sub_dialect": "Central Tamil",
        "languages_influenced": ["Standard Tamil"],
        "word_count_target": 2000,
    },
}

# ============================================================
# WORD DATABASE - Core Tamil words by category
# ============================================================

# Each entry: (tamil_word, standard_tamil, meaning, category)
# Categories: address, family, greeting, casual, daily_life, food,
#             travel, friendship, conversation, student, shopping,
#             rural, urban, offensive, romantic, work, nature, body, emotion, time

CORE_WORDS = {
    "address": [
        ("அண்ணா", "அண்ணா", "elder brother / respectful address", "address"),
        ("அண்ணே", "அண்ணா", "elder brother (respectful, Madurai variant)", "address"),
        ("அண்ணாச்சி", "அண்ணா", "elder brother (Nellai respectful)", "address"),
        ("அக்கா", "அக்கா", "elder sister", "address"),
        ("எக்கா", "அக்கா", "elder sister (Madurai variant)", "address"),
        ("அத்தை", "அத்தை", "aunt (father's sister)", "address"),
        ("மாமா", "மாமா", "maternal uncle", "address"),
        ("மச்சான்", "மச்சான்", "bro / buddy (brother-in-law)", "address"),
        ("மச்சி", "மச்சான்", "buddy (shortened)", "address"),
        ("டா", "டா", "informal suffix for male friends", "address"),
        ("டி", "டி", "informal suffix for female friends", "address"),
        ("தம்பி", "தம்பி", "younger brother", "address"),
        ("தங்கச்சி", "தங்கச்சி", "younger sister", "address"),
        ("மாமி", "மாமி", "aunt (maternal uncle's wife)", "address"),
        ("பெரியப்பா", "பெரியப்பா", "elder uncle (father's elder brother)", "address"),
        ("பெரியம்மா", "பெரியம்மா", "elder aunt (father's elder brother's wife)", "address"),
        ("சித்தப்பா", "சித்தப்பா", "younger uncle (father's younger brother)", "address"),
        ("சித்தி", "சித்தி", "aunt (father's younger brother's wife)", "address"),
        ("அப்பா", "அப்பா", "father", "address"),
        ("அம்மா", "அம்மா", "mother", "address"),
        ("தாத்தா", "தாத்தா", "grandfather", "address"),
        ("பாட்டி", "பாட்டி", "grandmother", "address"),
        ("மச்சன்", "மச்சான்", "brother-in-law", "address"),
        ("மருமகன்", "மருமகன்", "son-in-law", "address"),
        ("மாப்பிள்ளை", "மாப்பிள்ளை", "groom / son-in-law", "address"),
        ("புருஷன்", "புருஷன்", "husband (casual)", "address"),
        ("கணவன்", "கணவன்", "husband", "address"),
        ("மனைவி", "மனைவி", "wife", "address"),
        ("சொக்காரன்", "சகோதரன்", "brother (Nellai variant)", "address"),
        ("சொக்காரி", "சகோதரி", "sister (Nellai variant)", "address"),
    ],
    "family": [
        ("குடும்பம்", "குடும்பம்", "family", "family"),
        ("பொண்ணு", "பெண்", "girl / daughter", "family"),
        ("பையன்", "ஆண்", "boy / son", "family"),
        ("குழந்தை", "குழந்தை", "child", "family"),
        ("பசங்க", "குழந்தைகள்", "kids / children", "family"),
        ("ஆம்பிளை", "ஆண்", "man / male", "family"),
        ("பொம்பள", "பெண்", "woman / female", "family"),
        ("கல்யாணம்", "திருமணம்", "marriage", "family"),
        ("காதல்", "காதல்", "love", "family"),
        ("குடும்பத்தலைவி", "குடும்பத் தலைவி", "head of household (female)", "family"),
        ("சொந்தம்", "உறவினர்", "relatives", "family"),
        ("உறவினர்", "உறவினர்", "relatives", "family"),
        ("கோடி", "உறவினர்", "relative (Tanglish)", "family"),
        ("நண்பன்", "நண்பன்", "friend", "family"),
        ("தோழி", "தோழி", "female friend", "family"),
        ("பக்கா", "நண்பன்", "best friend / close buddy", "family"),
        ("சொக்காரன்", "சகோதரன்", "brother (Kanyakumari)", "family"),
        ("அம்மச்சி", "பாட்டி", "grandmother (Kongu variant)", "family"),
        ("அப்பச்சி", "தாத்தா", "grandfather (Kongu variant)", "family"),
        ("அம்மாயி", "பாட்டி", "grandmother (Kongu variant)", "family"),
        ("பண்ணாடி", "கணவர்", "husband (Kongu variant)", "family"),
        ("கொலுந்தியா", "நாத்தனார்", "sister-in-law (Nellai)", "family"),
        ("மைனி", "மச்சினி", "sister-in-law (Nellai)", "family"),
    ],
    "greeting": [
        ("வணக்கம்", "வணக்கம்", "hello / greetings", "greeting"),
        ("வாங்க", "வாங்க", "come / welcome", "greeting"),
        ("எப்படி இருக்கீங்க", "எப்படி இருக்கிறீர்கள்", "how are you (respectful)", "greeting"),
        ("எப்படி இருக்க", "எப்படி இருக்கிறாய்", "how are you (informal)", "greeting"),
        ("சௌக்கியமா", "நலமா", "are you well?", "greeting"),
        ("சுவமா இருக்கியாலா", "நலமா இருக்கிறாயா", "are you well (Nellai)", "greeting"),
        ("சுவம்", "சுகம்", "wellness (Nellai)", "greeting"),
        ("சூப்பரா", "நன்றாக", "are you super?", "greeting"),
        ("நல்லா இருக்கியா", "நல்லா இருக்கிறாயா", "are you fine?", "greeting"),
        ("நல்லா இருக்கேன்", "நல்லா இருக்கிறேன்", "I am fine", "greeting"),
        ("போயிட்டு வரேன்", "சென்று வருகிறேன்", "I will come back", "greeting"),
        ("சரி", "சரி", "okay / alright", "greeting"),
        ("நலம்", "நலம்", "wellness (formal)", "greeting"),
        ("சந்தோஷம்", "சந்தோஷம்", "happiness / glad", "greeting"),
        ("உங்கள பாக்கணும்", "உங்களைப் பார்க்க வேண்டும்", "nice to see you", "greeting"),
        ("கோமா", "எப்படி", "how? (casual)", "greeting"),
        ("கோமா இருக்க", "எப்படி இருக்க", "how are you (casual)", "greeting"),
        ("கோமா போகுது", "எப்படி போகுது", "how is it going?", "greeting"),
        ("தூரமா போறியா", "தூரம் போகிறாயா", "going far? (Nellai)", "greeting"),
        ("போறீங்களா", "போகிறீர்களா", "are you going?", "greeting"),
        ("வர்றீங்களா", "வருகிறீர்களா", "are you coming?", "greeting"),
        ("எங்க போற", "எங்கு போகிறாய்", "where are you going?", "greeting"),
        ("என்ன சமாச்சாரம்", "என்ன விசயம்", "what's up?", "greeting"),
    ],
    "casual": [
        ("செம்ம", "அற்புதம்", "awesome / superb", "casual"),
        ("செம மாஸ்", "மிகச் சிறப்பு", "very stylish", "casual"),
        ("மாஸ்", "பெருமை", "style / swag", "casual"),
        ("செம சூப்பர்", "மிக நன்றாக", "very super", "casual"),
        ("மொக்க", "மொக்கை", "lousy / boring", "casual"),
        ("மொக்கை", "மோசம்", "bad / terrible", "casual"),
        ("செட்டை", "கலாட்டா", "mischief / fun", "casual"),
        ("கலாட்டா", "கலவரம்", "commotion / fun chaos", "casual"),
        ("கலாய்", "கிண்டல்", "tease / make fun", "casual"),
        ("கலாய்க்கிற", "கிண்டல் செய்யும்", "teasing", "casual"),
        ("மெர்சல்", "அச்சம்", "fear (Madras Bashai)", "casual"),
        ("கெத்து", "ஆணவம்", "swagger / pride", "casual"),
        ("தரம்", "தரம்", "quality / standard", "casual"),
        ("தீப்பற", "சொல்", "tell me", "casual"),
        ("சொல்லு", "சொல்", "tell", "casual"),
        ("சும்மா", "வீணாக", "for free / casually", "casual"),
        ("ஜாலியா", "மகிழ்ச்சியாக", "happily / joyfully", "casual"),
        ("கொள்ளை", "மிகவும்", "very much (Nellai)", "casual"),
        ("செம கொள்ளை", "மிக மிகச் சிறப்பு", "extremely awesome (Nellai)", "casual"),
        ("கோலா", "நல்லா", "well / good (Nellai)", "casual"),
        ("ஷோக்கா", "நன்றாக", "looking sharp (Madras Bashai)", "casual"),
        ("ஜம்புனு", "சுகமாக", "comfortably (Madras Bashai)", "casual"),
        ("உஷாரா", "எச்சரிக்கையாக", "be alert (Madras Bashai)", "casual"),
        ("கேத்து", "ஆணவம்", "swagger (Madras Bashai)", "casual"),
        ("சோலி", "வேலை", "work (Kongu)", "casual"),
        ("வெடுக்குனு", "விரைவாக", "quickly (Kongu)", "casual"),
        ("பொசுக்குனு", "சடக்கென்று", "suddenly (Kongu)", "casual"),
        ("விசுக்குனு", "திடீரென்று", "suddenly (Kongu)", "casual"),
        ("மடார்", "உடனடியாக", "immediately (Kongu)", "casual"),
        ("வெருசா", "சீக்கிரமாய்", "quickly (Kongu)", "casual"),
    ],
    "daily_life": [
        ("வீடு", "வீடு", "house / home", "daily_life"),
        ("தெரு", "தெரு", "street", "daily_life"),
        ("வேலை", "வேலை", "work", "daily_life"),
        ("சாப்பாடு", "உணவு", "food / meal", "daily_life"),
        ("தண்ணி", "நீர்", "water", "daily_life"),
        ("படு", "உறங்கு", "sleep", "daily_life"),
        ("எழு", "எழுந்திரு", "wake up", "daily_life"),
        ("சாப்பிடு", "உண்", "eat", "daily_life"),
        ("குளி", "நீராடு", "bathe", "daily_life"),
        ("போ", "செல்", "go", "daily_life"),
        ("வா", "வா", "come", "daily_life"),
        ("உட்கார்", "அமர்", "sit", "daily_life"),
        ("நில்", "நில்", "stand", "daily_life"),
        ("ஓடு", "ஓடு", "run", "daily_life"),
        ("நட", "நட", "walk", "daily_life"),
        ("தூங்கு", "தூங்கு", "sleep", "daily_life"),
        ("முக்கு", "சந்து", "street corner (Madurai)", "daily_life"),
        ("துணி", "ஆடை", "clothes", "daily_life"),
        ("பாத்திரம்", "பாத்திரம்", "vessels / dishes", "daily_life"),
        ("சோப்பு", "சோப்பு", "soap", "daily_life"),
        ("துடைப்பம்", "துடைப்பம்", "broom", "daily_life"),
        ("விளக்கு", "விளக்கு", "lamp", "daily_life"),
        ("சேலை", "புடவை", "saree", "daily_life"),
        ("பனியன்", "உடை", "vest / undershirt", "daily_life"),
        ("சட்டை", "சட்டை", "shirt", "daily_life"),
        ("பேண்ட்", "கால்சட்டை", "pants", "daily_life"),
        ("தொப்பி", "தொப்பி", "cap", "daily_life"),
        ("மேச்சல்", "கைமேசை", "dining mat", "daily_life"),
        ("குப்பை", "குப்பை", "garbage", "daily_life"),
        ("மேட்டு", "மாடி", "upper floor", "daily_life"),
    ],
    "food": [
        ("சாப்பாடு", "உணவு", "food", "food"),
        ("சமையல்", "சமையல்", "cooking", "food"),
        ("ரசம்", "ரசம்", "rasam (soup)", "food"),
        ("மொளகு சாறு", "ரசம்", "rasam (Kongu variant)", "food"),
        ("சாம்பார்", "சாம்பார்", "sambar", "food"),
        ("துவையல்", "துவையல்", "chutney", "food"),
        ("குழம்பு", "குழம்பு", "gravy / curry", "food"),
        ("ஆணம்", "குழம்பு", "gravy (Madurai)", "food"),
        ("பொரியல்", "பொரியல்", "stir-fry", "food"),
        ("கீரை", "கீரை", "greens / spinach", "food"),
        ("ரக்கரி", "கீரை", "greens (Kongu variant)", "food"),
        ("மோர்", "மோர்", "buttermilk", "food"),
        ("தயிர்", "தயிர்", "curd / yogurt", "food"),
        ("புட்டு", "புட்டு", "steamed rice cake", "food"),
        ("சந்தக்கை", "இடியாப்பம்", "string hoppers (Kongu)", "food"),
        ("தோசை", "தோசை", "dosa", "food"),
        ("இட்லி", "இட்லி", "idli", "food"),
        ("புத்து", "புட்டு", "rice cake (Kongu variant)", "food"),
        ("உப்பு", "உப்பு", "salt", "food"),
        ("மிளகாய்", "மிளகாய்", "chili", "food"),
        ("மஞ்சள்", "மஞ்சள்", "turmeric", "food"),
        ("கடுகு", "கடுகு", "mustard seeds", "food"),
        ("வெந்தயம்", "வெந்தயம்", "fenugreek", "food"),
        ("சீரகம்", "சீரகம்", "cumin", "food"),
        ("மல்லி", "மல்லி", "coriander", "food"),
        ("புதினா", "புதினா", "mint", "food"),
        ("இஞ்சி", "இஞ்சி", "ginger", "food"),
        ("பூண்டு", "பூண்டு", "garlic", "food"),
        ("வெங்காயம்", "வெங்காயம்", "onion", "food"),
        ("தக்காளி", "தக்காளி", "tomato", "food"),
        ("உருளைக்கிழங்கு", "உருளைக்கிழங்கு", "potato", "food"),
        ("பீன்ஸ்", "பீன்ஸ்", "beans", "food"),
        ("கேரட்", "கேரட்", "carrot", "food"),
        ("கத்திரிக்காய்", "கத்திரிக்காய்", "brinjal", "food"),
        ("புடலங்காய்", "புடலங்காய்", "snake gourd", "food"),
        ("சுரைக்காய்", "சுரைக்காய்", "bottle gourd", "food"),
        ("வாழைப்பழம்", "வாழைப்பழம்", "banana", "food"),
        ("மாம்பழம்", "மாம்பழம்", "mango", "food"),
        ("தேங்காய்", "தேங்காய்", "coconut", "food"),
        ("நெய்", "நெய்", "ghee", "food"),
        ("எண்ணெய்", "எண்ணெய்", "oil", "food"),
        ("சீனி", "சர்க்கரை", "sugar (Madurai)", "food"),
        ("பொங்கல்", "பொங்கல்", "pongal (rice dish)", "food"),
        ("இட்லி", "இட்லி", "steamed rice cake", "food"),
        ("வடை", "வடை", "vada", "food"),
        ("பஜ்ஜி", "பஜ்ஜி", "bajji (fritter)", "food"),
        ("சோறு", "சாதம்", "rice", "food"),
        ("கூழ்", "கஞ்சி", "porridge / gruel", "food"),
    ],
    "travel": [
        ("பேருந்து", "பேருந்து", "bus", "travel"),
        ("ரயில்", "ரயில்", "train", "travel"),
        ("ஆட்டோ", "ஆட்டோ", "auto-rickshaw", "travel"),
        ("கார்", "கார்", "car", "travel"),
        ("பைக்", "மோட்டார் சைக்கிள்", "bike", "travel"),
        ("சைக்கிள்", "மிதிவண்டி", "bicycle", "travel"),
        ("நடை", "நடை", "walk", "travel"),
        ("ஏர்போர்ட்", "விமான நிலையம்", "airport", "travel"),
        ("ஸ்டேஷன்", "நிலையம்", "station", "travel"),
        ("ஸ்டாப்", "நிறுத்தம்", "stop (bus stop)", "travel"),
        ("கன்டக்டர்", "கண்டக்டர்", "bus conductor", "travel"),
        ("டிக்கெட்", "நுழைவுச் சீட்டு", "ticket", "travel"),
        ("சீட்டு", "இருக்கை", "seat", "travel"),
        ("வண்டி", "வாகனம்", "vehicle", "travel"),
        ("பெட்ரோல்", "நிலக்கரி எரிபொருள்", "petrol", "travel"),
        ("டீசல்", "டீசல்", "diesel", "travel"),
        ("பாதை", "சாலை", "road", "travel"),
        ("சாலை", "சாலை", "road", "travel"),
        ("சந்தை", "சந்தை", "market / junction", "travel"),
        ("குறுக்குச் சாலை", "குறுக்குச் சாலை", "cross road", "travel"),
        ("சிக்னல்", "சிக்னல்", "traffic signal", "travel"),
        ("கிராஸ்", "குறுக்கு", "crossing", "travel"),
        ("ஏணி மரம்", "ஏணி", "ladder (Madurai)", "travel"),
        ("சைக்கிள்", "மிதிவண்டி", "bicycle", "travel"),
        ("மோட்டார்", "இயந்திரம்", "motor", "travel"),
        ("கப்பல்", "கப்பல்", "ship", "travel"),
        ("விமானம்", "விமானம்", "airplane", "travel"),
        ("நடைபாதை", "நடைபாதை", "footpath", "travel"),
    ],
    "friendship": [
        ("நண்பன்", "நண்பன்", "friend", "friendship"),
        ("தோழன்", "தோழன்", "companion", "friendship"),
        ("பக்கா", "நெருங்கிய நண்பன்", "close buddy", "friendship"),
        ("மச்சான்", "மச்சான்", "bro / dude", "friendship"),
        ("மச்சி", "மச்சான்", "buddy (short)", "friendship"),
        ("சகோ", "சகோதரன்", "bro", "friendship"),
        ("டா", "டா", "mate (informal)", "friendship"),
        ("டி", "டி", "mate (female, informal)", "friendship"),
        ("கூட்டாளி", "கூட்டாளி", "partner / buddy", "friendship"),
        ("சேரி", "கூட்டம்", "group of friends", "friendship"),
        ("கேங்", "கூட்டம்", "gang / group", "friendship"),
        ("சைட்", "பக்கம்", "side / area", "friendship"),
        ("மாப்பு", "நண்பன்", "mate / buddy", "friendship"),
        ("கோழி", "நண்பன்", "friend (casual)", "friendship"),
        ("தோழி", "தோழி", "female friend", "friendship"),
        ("கல்யாணி", "தோழி", "female buddy", "friendship"),
        ("பேர்", "பெயர்", "name / reputation", "friendship"),
        ("டல்லா", "தோழன்", "dude / pal", "friendship"),
        ("மச்சான் பச்சை", "நண்பர் குழு", "friend circle", "friendship"),
        ("கேங் மெம்பர்", "குழு உறுப்பினர்", "gang member", "friendship"),
    ],
    "emotion": [
        ("சந்தோஷம்", "மகிழ்ச்சி", "happiness", "emotion"),
        ("துக்கம்", "துக்கம்", "sadness", "emotion"),
        ("கோபம்", "கோபம்", "anger", "emotion"),
        ("பயம்", "பயம்", "fear", "emotion"),
        ("ஆச்சரியம்", "வியப்பு", "surprise", "emotion"),
        ("வெறுப்பு", "வெறுப்பு", "hatred", "emotion"),
        ("பாசம்", "பாசம்", "affection", "emotion"),
        ("பொறாமை", "பொறாமை", "jealousy", "emotion"),
        ("காதல்", "காதல்", "love", "emotion"),
        ("திமிர்", "திமிர்", "arrogance", "emotion"),
        ("திமிரு", "திமிரு", "pride / arrogance", "emotion"),
        ("தயக்கம்", "தயக்கம்", "hesitation", "emotion"),
        ("உற்சாகம்", "உற்சாகம்", "excitement", "emotion"),
        ("சோம்பல்", "சோம்பல்", "laziness", "emotion"),
        ("வெசனம்", "வருத்தம்", "sadness (Kongu)", "emotion"),
        ("விரக்தி", "விரக்தி", "frustration", "emotion"),
        ("ஆத்திரம்", "ஆத்திரம்", "impatience", "emotion"),
        ("கலக்கம்", "கலக்கம்", "confusion", "emotion"),
        ("பதற்றம்", "பதற்றம்", "anxiety", "emotion"),
        ("அமைதி", "அமைதி", "peace", "emotion"),
    ],
    "nature": [
        ("மழை", "மழை", "rain", "nature"),
        ("காற்று", "காற்று", "wind", "nature"),
        ("வெயில்", "வெயில்", "sun / heat", "nature"),
        ("குளிர்", "குளிர்", "cold", "nature"),
        ("நீர்", "நீர்", "water", "nature"),
        ("மரம்", "மரம்", "tree", "nature"),
        ("பூ", "மலர்", "flower", "nature"),
        ("கடல்", "கடல்", "sea", "nature"),
        ("ஆறு", "ஆறு", "river", "nature"),
        ("குளம்", "குளம்", "pond", "nature"),
        ("மலை", "மலை", "mountain", "nature"),
        ("காடு", "காடு", "forest", "nature"),
        ("வயல்", "வயல்", "field", "nature"),
        ("தோட்டம்", "தோட்டம்", "garden", "nature"),
        ("சோலை", "சோலை", "grove", "nature"),
        ("காய்க்காய்", "காய்", "vegetable", "nature"),
        ("பழம்", "பழம்", "fruit", "nature"),
        ("மண்", "மண்", "soil", "nature"),
        ("கல்", "கல்", "stone", "nature"),
        ("மேகம்", "மேகம்", "cloud", "nature"),
        ("இடி", "இடி", "thunder", "nature"),
        ("மின்னல்", "மின்னல்", "lightning", "nature"),
        ("வானம்", "வானம்", "sky", "nature"),
        ("நிலம்", "நிலம்", "earth / land", "nature"),
        ("சூரியன்", "சூரியன்", "sun", "nature"),
        ("நிலவு", "நிலவு", "moon", "nature"),
        ("நட்சத்திரம்", "நட்சத்திரம்", "star", "nature"),
    ],
    "body": [
        ("தலை", "தலை", "head", "body"),
        ("கண்", "கண்", "eye", "body"),
        ("காது", "காது", "ear", "body"),
        ("மூக்கு", "மூக்கு", "nose", "body"),
        ("வாய்", "வாய்", "mouth", "body"),
        ("முகம்", "முகம்", "face", "body"),
        ("கை", "கை", "hand", "body"),
        ("கால்", "கால்", "leg", "body"),
        ("விரல்", "விரல்", "finger", "body"),
        ("நகம்", "நகம்", "nail", "body"),
        ("தோள்", "தோள்", "shoulder", "body"),
        ("மார்பு", "மார்பு", "chest", "body"),
        ("வயிறு", "வயிறு", "stomach", "body"),
        ("முதுகு", "முதுகு", "back", "body"),
        ("தொடை", "தொடை", "thigh", "body"),
        ("முழங்கால்", "முழங்கால்", "knee", "body"),
        ("கழுத்து", "கழுத்து", "neck", "body"),
        ("முடி", "முடி", "hair", "body"),
        ("எலும்பு", "எலும்பு", "bone", "body"),
        ("இரத்தம்", "இரத்தம்", "blood", "body"),
        ("மண்டை", "மண்டை", "skull (casual)", "body"),
        ("மூளை", "மூளை", "brain", "body"),
        ("இதயம்", "இதயம்", "heart", "body"),
        ("நுரையீரல்", "நுரையீரல்", "lungs", "body"),
        ("மோஷை", "முகம்", "face (Nellai variant)", "body"),
    ],
    "time": [
        ("இன்று", "இன்று", "today", "time"),
        ("நேற்று", "நேற்று", "yesterday", "time"),
        ("நாளை", "நாளை", "tomorrow", "time"),
        ("காலை", "காலை", "morning", "time"),
        ("மாலை", "மாலை", "evening", "time"),
        ("நள்ளிரவு", "நள்ளிரவு", "midnight", "time"),
        ("நண்பகல்", "நண்பகல்", "noon", "time"),
        ("நேரம்", "நேரம்", "time", "time"),
        ("சத்தியம்", "சத்தியம்", "moment (colloquial)", "time"),
        ("வெள்ளனே", "சீக்கிரம்", "early morning (Madurai)", "time"),
        ("கருக்கல்", "சாயங்காலம்", "evening (Madurai)", "time"),
        ("செத்த நேரம்", "சிறிது நேரம்", "a little while (Madurai)", "time"),
        ("எட்டு", "வாரம்", "week (Kongu)", "time"),
        ("நேத்து", "நேற்று", "yesterday (colloquial)", "time"),
        ("பொந்து", "காலை", "morning (dialect)", "time"),
        ("காலையிலே", "காலையில்", "in the morning", "time"),
        ("மதியம்", "மதியம்", "afternoon", "time"),
        ("இரவு", "இரவு", "night", "time"),
        ("பகல்", "பகல்", "daytime", "time"),
        ("மாசம்", "மாதம்", "month", "time"),
        ("வருஷம்", "ஆண்டு", "year", "time"),
        ("செத்த நேரம்", "கொஞ்ச நேரம்", "short while (Madurai)", "time"),
    ],
    "work": [
        ("வேலை", "வேலை", "work", "work"),
        ("உத்தியோகம்", "வேலை", "job (formal)", "work"),
        ("சம்பளம்", "சம்பளம்", "salary", "work"),
        ("அலுவலகம்", "அலுவலகம்", "office", "work"),
        ("தொழிற்சாலை", "தொழிற்சாலை", "factory", "work"),
        ("கடை", "கடை", "shop", "work"),
        ("வியாபாரம்", "வியாபாரம்", "business", "work"),
        ("தொழில்", "தொழில்", "trade / profession", "work"),
        ("விவசாயம்", "விவசாயம்", "agriculture", "work"),
        ("பணம்", "பணம்", "money", "work"),
        ("துட்டு", "பணம்", "money (Madras Bashai from Kannada)", "work"),
        ("டப்பு", "பணம்", "money (Madras Bashai from Telugu)", "work"),
        ("காசு", "பணம்", "money (casual)", "work"),
        ("லாபம்", "லாபம்", "profit", "work"),
        ("நஷ்டம்", "நஷ்டம்", "loss", "work"),
        ("விலை", "விலை", "price", "work"),
        ("சந்தை", "சந்தை", "market", "work"),
        ("விவசாயி", "விவசாயி", "farmer", "work"),
        ("தொழிலாளி", "தொழிலாளி", "worker", "work"),
        ("முதலாளி", "முதலாளி", "boss / owner", "work"),
        ("சோலி", "வேலை", "work (Kongu)", "work"),
        ("நாள்", "நாள்", "day", "work"),
        ("ஊதியம்", "சம்பளம்", "wage", "work"),
        ("ஆள்", "மனிதன்", "person / man", "work"),
    ],
    "student": [
        ("பாடம்", "பாடம்", "lesson", "student"),
        ("புத்தகம்", "நூல்", "book", "student"),
        ("ஸ்கூல்", "பள்ளி", "school", "student"),
        ("காலேஜ்", "கல்லூரி", "college", "student"),
        ("டீச்சர்", "ஆசிரியர்", "teacher", "student"),
        ("ப்ரொபஸர்", "பேராசிரியர்", "professor", "student"),
        ("எக்ஸாம்", "தேர்வு", "exam", "student"),
        ("மார்க்", "மதிப்பெண்", "marks", "student"),
        ("கிளாஸ்", "வகுப்பு", "class", "student"),
        ("கேள்வி", "கேள்வி", "question", "student"),
        ("பதில்", "பதில்", "answer", "student"),
        ("காப்பி", "நகல்", "copy / cheat", "student"),
        ("புக்", "நூல்", "book (Tanglish)", "student"),
        ("ஹோம் வொர்க்", "வீட்டுப்பாடம்", "homework", "student"),
        ("அசைன்மென்ட்", "பணிக்குறிப்பு", "assignment", "student"),
        ("லேப்", "ஆய்வகம்", "laboratory", "student"),
        ("லைப்ரரி", "நூலகம்", "library", "student"),
        ("லெக்ச்சர்", "விரிவுரை", "lecture", "student"),
        ("செமஸ்டர்", "பருவம்", "semester", "student"),
        ("ப்ராஜெக்ட்", "திட்டப்பணி", "project", "student"),
        ("விடுதி", "விடுதி", "hostel", "student"),
        ("மெஸ்", "உணவகம்", "mess (canteen)", "student"),
    ],
    "shopping": [
        ("கடை", "கடை", "shop", "shopping"),
        ("விலை", "விலை", "price", "shopping"),
        ("சலுகை", "தள்ளுபடி", "discount", "shopping"),
        ("பேரம்", "பேரம்", "bargaining", "shopping"),
        ("மார்க்கெட்", "சந்தை", "market", "shopping"),
        ("மால்", "சந்தை", "mall", "shopping"),
        ("சூப்பர் மார்க்கெட்", "மளிகைக்கடை", "supermarket", "shopping"),
        ("துணிக்கடை", "ஆடைக்கடை", "cloth shop", "shopping"),
        ("நகைக்கடை", "நகைக்கடை", "jewellery shop", "shopping"),
        ("மளிகை", "மளிகை", "grocery", "shopping"),
        ("மூட்டை", "பொதி", "bundle / bag", "shopping"),
        ("பை", "பை", "bag", "shopping"),
        ("காசு", "பணம்", "cash", "shopping"),
        ("சில்லறை", "சில்லறை", "change (coins)", "shopping"),
        ("நோட்டு", "நோட்டு", "currency note", "shopping"),
        ("பில்", "கணக்கு", "bill", "shopping"),
        ("ரசீது", "ரசீது", "receipt", "shopping"),
        ("கணக்கு", "கணக்கு", "account", "shopping"),
        ("கட்டணம்", "கட்டணம்", "payment", "shopping"),
        ("ஆர்டர்", "ஆணை", "order", "shopping"),
        ("டெலிவரி", "விநியோகம்", "delivery", "shopping"),
    ],
    "rural": [
        ("கிராமம்", "கிராமம்", "village", "rural"),
        ("ஊர்", "ஊர்", "village / hometown", "rural"),
        ("தெரு", "தெரு", "street", "rural"),
        ("மாடு", "காளை", "cow / ox", "rural"),
        ("பசு", "பசு", "cow", "rural"),
        ("கோழி", "கோழி", "chicken", "rural"),
        ("நாய்", "நாய்", "dog", "rural"),
        ("பூனை", "பூனை", "cat", "rural"),
        ("ஆடு", "ஆடு", "goat", "rural"),
        ("குதிரை", "குதிரை", "horse", "rural"),
        ("கிணறு", "கிணறு", "well", "rural"),
        ("மச்சாணி", "குளம்", "pond (rural)", "rural"),
        ("களம்", "களம்", "threshing floor", "rural"),
        ("கொல்லை", "கொல்லை", "backyard", "rural"),
        ("தோப்பு", "தோப்பு", "grove", "rural"),
        ("வேலி", "வேலி", "fence", "rural"),
        ("கத்தி", "கத்தி", "knife / machete", "rural"),
        ("அரிவாள்", "அரிவாள்", "sickle", "rural"),
        ("கலப்பை", "கலப்பை", "plough", "rural"),
        ("முக்கு", "சந்து", "corner / alley", "rural"),
        ("கோடி", "கோடி", "corner", "rural"),
        ("கொட்டகை", "கொட்டகை", "shed", "rural"),
        ("சாளை", "பண்ணை", "farmhouse (Kongu)", "rural"),
        ("பொறவு", "அப்புறம்", "afterwards (Kongu)", "rural"),
        ("ஊரணி", "குளம்", "pond (Madurai)", "rural"),
        ("வெஞ்சனம்", "தொட்டுக்கொள்ளும் உணவு", "side dish (Madurai)", "rural"),
        ("சொளகு", "முறம்", "winnow (Madurai)", "rural"),
    ],
    "urban": [
        ("அப்பார்ட்மென்ட்", "குடியிருப்பு", "apartment", "urban"),
        ("சொசைட்டி", "குடியிருப்பு", "housing society", "urban"),
        ("மால்", "வணிக வளாகம்", "mall", "urban"),
        ("சினிமா", "திரைப்படம்", "cinema", "urban"),
        ("மால்", "வணிக வளாகம்", "shopping complex", "urban"),
        ("பூம்", "குப்புற படுத்தல்", "boom (urban)", "urban"),
        ("நைட் லைஃப்", "இரவு வாழ்க்கை", "nightlife", "urban"),
        ("பார்", "மதுக்கடை", "bar", "urban"),
        ("ரெஸ்டாரண்ட்", "உணவகம்", "restaurant", "urban"),
        ("கஃபே", "கடை", "cafe", "urban"),
        ("கிளப்", "கழகம்", "club", "urban"),
        ("ஜிம்", "உடற்பயிற்சி கூடம்", "gym", "urban"),
        ("ஸ்பா", "அழகு நிலையம்", "spa", "urban"),
        ("சலூன்", "தலைமுடிக் கடை", "saloon", "urban"),
        ("வைஃபை", "இணைய இணைப்பு", "wifi", "urban"),
        ("மொபைல்", "கைப்பேசி", "mobile phone", "urban"),
        ("லேப்டாப்", "மடிக்கணினி", "laptop", "urban"),
        ("ஆப்", "பயன்பாடு", "app", "urban"),
        ("ப்ளாக்", "வலைப்பதிவு", "blog", "urban"),
        ("ட்விட்டர்", "சமூக ஊடகம்", "twitter", "urban"),
        ("பேஸ்புக்", "சமூக ஊடகம்", "facebook", "urban"),
        ("இன்ஸ்டா", "இன்ஸ்டாகிராம்", "instagram", "urban"),
    ],
    "offensive": [
        ("தேவுடியா", "தேவடியா", "prostitute / offensive", "offensive"),
        ("தேவுடியா பைய", "தேவடியா பையன்", "son of a prostitute", "offensive"),
        ("பன்னி", "பன்றி", "pig (offensive)", "offensive"),
        ("நாய்", "நாய்", "dog (used as slur)", "offensive"),
        ("நாய் மகன்", "நாய் மகன்", "son of a dog", "offensive"),
        ("பைத்தியம்", "பைத்தியம்", "crazy person", "offensive"),
        ("லூசு", "பைத்தியம்", "crazy / mad (casual)", "offensive"),
        ("முட்டாள்", "முட்டாள்", "fool", "offensive"),
        ("கேவலம்", "கேவலம்", "pathetic", "offensive"),
        ("அறிவுகெட்டவன்", "அறிவில்லாதவன்", "foolish person", "offensive"),
        ("சனியன்", "சனியன்", "wretched person", "offensive"),
        ("பாவி", "பாவி", "sinner / bad person", "offensive"),
        ("நாசக்காரன்", "நாசக்காரன்", "destroyer / rascal", "offensive"),
        ("கூறு கெட்டவன்", "கெட்டவன்", "worthless person (Madurai)", "offensive"),
        ("பொசகட்ட பய", "உபயோகமில்லாதவன்", "useless fellow (Madurai)", "offensive"),
        ("காவாளி", "வீணர்", "waste fellow (Madurai)", "offensive"),
        ("கொங்கா பய", "அறிவில்லாதவன்", "ignorant person (Madurai)", "offensive"),
        ("கோழி", "பயந்தவன்", "coward", "offensive"),
        ("புடுங்கன்", "திருடன்", "thief", "offensive"),
        ("களவாணி", "திருடன்", "thief (Madurai)", "offensive"),
        ("களவாணிப்பய", "திருடன்", "thief (Madurai)", "offensive"),
        ("கலீஜு", "அசுத்தம்", "dirty (Madras Bashai from Urdu)", "offensive"),
        ("கஸ்மாலம்", "அசுத்தம்", "dirty (Madras Bashai from Sanskrit)", "offensive"),
        ("பேமானி", "கேவலம்", "shameless (Madras Bashai from Urdu)", "offensive"),
        ("கொல்லைல போவான்", "நாசமாகப் போவான்", "hell with him (Kanyakumari)", "offensive"),
        ("துக்க", "அறிவுகெட்டவன்", "idiot (Kanyakumari)", "offensive"),
        ("கீசாரி பய", "அயோக்கியன்", "rogue (Kanyakumari)", "offensive"),
        ("தட்டு", "லூசு", "mental (Kanyakumari)", "offensive"),
        ("சொன்னா புரியாதவன்", "அறிவில்லாதவன்", "doesn't understand anything", "offensive"),
    ],
    "romantic": [
        ("காதல்", "காதல்", "love", "romantic"),
        ("காதலி", "காதலி", "girlfriend", "romantic"),
        ("காதலன்", "காதலன்", "boyfriend", "romantic"),
        ("சீரியஸ்", "தீவிரமான", "serious (relationship)", "romantic"),
        ("லவ்", "காதல்", "love (Tanglish)", "romantic"),
        ("ப்ரப்போஸ்", "காதல் கோரிக்கை", "propose", "romantic"),
        ("ரிஜெக்ட்", "நிராகரி", "reject", "romantic"),
        ("சைட்", "பார்வை", "side / glance", "romantic"),
        ("கன்னா பின்னா", "மிகவும்", "intensely", "romantic"),
        ("சீன்", "நிலை", "scene / situation", "romantic"),
        ("மாப்பு", "நண்பன்", "mate / buddy", "romantic"),
        ("மாயா", "மாயம்", "illusion / magic", "romantic"),
        ("ராசி", "அதிர்ஷ்டம்", "luck", "romantic"),
        ("பார்வை", "பார்வை", "glance", "romantic"),
        ("தோற்றம்", "தோற்றம்", "appearance", "romantic"),
        ("அழகு", "அழகு", "beauty", "romantic"),
        ("ஏக்கம்", "ஏக்கம்", "longing", "romantic"),
        ("தவிப்பு", "தவிப்பு", "yearning", "romantic"),
        ("சிரிப்பு", "சிரிப்பு", "smile", "romantic"),
        ("கண்ணாலம்", "காதல்", "love (literary)", "romantic"),
        ("இதயம்", "இதயம்", "heart", "romantic"),
        ("நெஞ்சம்", "நெஞ்சம்", "heart (colloquial)", "romantic"),
    ],
    "tanglish_common": [
        ("ஒகே", "சரி", "okay", "tanglish"),
        ("ப்ளீஸ்", "தயவுசெய்து", "please", "tanglish"),
        ("தேங்க்ஸ்", "நன்றி", "thanks", "tanglish"),
        ("சாரி", "மன்னிக்கவும்", "sorry", "tanglish"),
        ("கியாரக்டர்", "பாத்திரம்", "character", "tanglish"),
        ("சிச்சுவேஷன்", "நிலைமை", "situation", "tanglish"),
        ("கமிட்மென்ட்", "உறுதிப்பாடு", "commitment", "tanglish"),
        ("ரிலேஷன்ஷிப்", "உறவு", "relationship", "tanglish"),
        ("அப்ரோச்", "அணுகுமுறை", "approach", "tanglish"),
        ("பிராப்ளம்", "பிரச்சனை", "problem", "tanglish"),
        ("சொல்யூஷன்", "தீர்வு", "solution", "tanglish"),
        ("ஆப்ஷன்", "விருப்பம்", "option", "tanglish"),
        ("செகண்ட்", "இரண்டாவது", "second", "tanglish"),
        ("மினிட்", "நிமிடம்", "minute", "tanglish"),
        ("ஆன்ஸர்", "பதில்", "answer", "tanglish"),
        ("க்வஸ்டியன்", "கேள்வி", "question", "tanglish",
         ),
        ("எக்ஸ்பிரஸ்", "வெளிப்பாடு", "expression", "tanglish"),
        ("டென்ஷன்", "பதற்றம்", "tension", "tanglish"),
        ("டிப்ஸ்", "குறிப்புகள்", "tips", "tanglish"),
        ("ட்ரிக்", "உத்தி", "trick", "tanglish"),
        ("சீன்", "காட்சி", "scene", "tanglish"),
        ("சோங்", "பாடல்", "song", "tanglish"),
        ("மூவி", "திரைப்படம்", "movie", "tanglish"),
        ("பேன்", "ரசிகர்", "fan", "tanglish"),
        ("ஸ்டார்", "நட்சத்திரம்", "star", "tanglish"),
        ("க்ளாஸ்", "வகுப்பு", "class", "tanglish"),
        ("பஸ்", "பேருந்து", "bus", "tanglish"),
        ("டிக்கெட்", "நுழைவுச்சீட்டு", "ticket", "tanglish"),
        ("போன்", "தொலைபேசி", "phone", "tanglish"),
        ("மெசேஜ்", "செய்தி", "message", "tanglish"),
    ],
    "colloquial_phrases": [
        ("என்ன சமாச்சாரம்", "என்ன விசயம்", "what's the matter?", "colloquial"),
        ("ஏண்டா ஏண்டி", "ஏன்", "hey man / hey girl", "colloquial"),
        ("அட போடா", "விலகு", "get out (casual)", "colloquial"),
        ("நீ தான்", "நீதான்", "it's you only", "colloquial"),
        ("அப்படியா", "அவ்வாறா", "is that so?", "colloquial"),
        ("சும்மா இரு", "வம்பு செய்யாதே", "just stay quiet", "colloquial"),
        ("விடு டா", "விட்டுவிடு", "leave it, dude", "colloquial"),
        ("சரி டா", "சரி", "alright, dude", "colloquial"),
        ("நீ சொல்றது சரிதான்", "நீ சொல்வது சரி", "you're right", "colloquial"),
        ("அது சரிதான்", "அது சரி", "that's correct", "colloquial"),
        ("நான் சொன்னது புரியுதா", "புரிகிறதா", "do you understand what I said?", "colloquial"),
        ("புரியுதா", "புரிகிறதா", "understand?", "colloquial"),
        ("வேணாம் டா", "வேண்டாம்", "no need, dude", "colloquial"),
        ("விடுங்க", "விட்டுவிடுங்கள்", "leave it (respectful)", "colloquial"),
        ("சொல்லு", "சொல்", "tell me", "colloquial"),
        ("சொல்லிட்டே இரு", "தொடர்ந்து சொல்", "keep telling", "colloquial"),
        ("அப்புறம் என்ன", "பிறகு என்ன", "then what?", "colloquial"),
        ("இப்ப என்ன", "இப்போது என்ன", "now what?", "colloquial"),
        ("ஏன் கேக்குற", "ஏன் கேட்கிறாய்", "why are you asking?", "colloquial"),
        ("ஒன்னும் இல்ல", "ஒன்றும் இல்லை", "nothing", "colloquial"),
        ("ஒண்ணும் இல்ல", "ஒன்றும் இல்லை", "nothing (colloquial)", "colloquial"),
        ("போங்க", "போங்கள்", "go (respectful)", "colloquial"),
        ("வாங்க", "வாங்கள்", "come (respectful)", "colloquial"),
        ("நில்லு", "நில்", "stop / wait", "colloquial"),
        ("உட்காரு", "அமர்", "sit down", "colloquial"),
        ("எழுந்திரு", "எழு", "get up", "colloquial"),
        ("தூங்கு", "உறங்கு", "sleep", "colloquial"),
        ("சாப்பிடு", "உண்", "eat", "colloquial"),
        ("குடி", "அருந்து", "drink", "colloquial"),
    ],
}


# ============================================================
# PHONETIC VARIATIONS - Generate Tanglish and dialect variants
# ============================================================

# Common Tamil-to-Tanglish transliteration patterns
TAMIL_TO_TANGLISH = {
    "ஆ": "aa", "ஆ": "aa",
    "ஈ": "ee", "ஈ": "ee",
    "ஊ": "oo", "ஊ": "oo",
    "ஏ": "ae", "ஏ": "ae",
    "ஐ": "ai", "ஐ": "ai",
    "ஒ": "o", "ஒ": "o",
    "ஔ": "au", "ஔ": "au",
    "கா": "kaa", "கி": "ki", "கீ": "kee",
    "கு": "ku", "கூ": "koo", "கெ": "ke",
    "கே": "kae", "கோ": "koo",
    "சா": "saa", "சி": "si", "சீ": "see",
    "சு": "su", "சூ": "soo",
    "தா": "thaa", "தி": "thi", "தீ": "thee",
    "து": "thu", "தூ": "thoo",
    "நா": "naa", "நி": "ni", "நீ": "nee",
    "பா": "paa", "பி": "pi", "பீ": "pee",
    "பு": "pu", "பூ": "poo",
    "மா": "maa", "மி": "mi", "மீ": "mee",
    "மு": "mu", "மூ": "moo",
    "யா": "yaa", "ரா": "raa",
    "லா": "laa", "வா": "vaa",
    "ழா": "zhaa", "ளா": "laa",
}

# Regional pronunciation shifts
REGIONAL_SHIFTS = {
    "Chennai": {"zh": "y", "ḷ": "l"},  # zh → y in North Chennai
    "Madurai": {"final_n": "ng", "ai": "ae"},
    "Tirunelveli": {"c": "ch"},  # c as palatal affricate
    "Coimbatore": {"nga": "ng", "ka": "k"},
    "Thanjavur": {"ai": "e", "au": "o"},
}

# ============================================================
# GENERATION FUNCTIONS
# ============================================================

def generate_tanglish(word: str) -> str:
    """Generate a Tanglish (Tamil-English) transliteration."""
    tanglish = word
    for ta, en in TAMIL_TO_TANGLISH.items():
        tanglish = tanglish.replace(ta, en)
    # If no replacements made, create a simple hash-based variant
    if tanglish == word:
        h = hashlib.md5(word.encode()).hexdigest()[:4]
        tanglish = word[:2] + h[:2]
    return tanglish


def generate_dialect_variants(word: str, district: str, meta: dict) -> List[str]:
    """Generate dialect-specific variants of a word."""
    variants = []
    region = meta["dialect_region"]

    # Northern dialect variants
    if region == "Northern" and district == "Chennai":
        if word.endswith("ம்"):
            variants.append(word[:-1] + "ன்")  # ம் → ன்
        if "ழ" in word:
            variants.append(word.replace("ழ", "ய"))  # ழ → ய

    # Madurai dialect
    if district == "Madurai":
        if word.endswith("கிறான்"):
            variants.append(word.replace("கிறான்", "றான்"))
        if word.endswith("கிறார்கள்"):
            variants.append(word.replace("கிறார்கள்", "றாங்க"))

    # Kongu dialect
    if meta["sub_dialect"] == "Kongu Tamil":
        if word.endswith("கிறீர்கள்"):
            variants.append(word.replace("கிறீர்கள்", "ரீங்க"))

    # Nellai dialect
    if "Nellai" in meta.get("sub_dialect", ""):
        if "சு" in word:
            variants.append(word.replace("சு", "சூ"))

    return variants[:2]  # Return max 2 variants


def generate_usage_example(word: str, meaning: str, district: str) -> str:
    """Generate a usage example sentence."""
    templates = [
        f"அவன் {word} பேசினான்",
        f"அவள் {word} சொன்னாள்",
        f"{word} நல்லா இருக்கு",
        f"{word} பண்ணாதே",
        f"நீ {word} தானே",
        f"{word} ன்னு சொல்லு",
        f"அது {word} மாதிரி இருக்கு",
        f"{word} என்ன அர்த்தம்",
    ]
    return random.choice(templates)


def generate_entry_id(district: str, idx: int) -> str:
    """Generate a unique entry ID."""
    prefix = district[:3].upper()
    return f"{prefix}_{idx:06d}"


def create_entry(
    word_data: tuple,
    district: str,
    meta: dict,
    idx: int,
    entry_type: str = "base",
) -> dict:
    """Create a single dataset entry."""
    tamil_word, standard_tamil, meaning, category = word_data

    entry = {
        "id": generate_entry_id(district, idx),
        "tamil_word": tamil_word,
        "tanglish": generate_tanglish(tamil_word),
        "standard_tamil": standard_tamil,
        "meaning": meaning,
        "region": district,
        "dialect_region": meta["dialect_region"],
        "sub_dialect": meta["sub_dialect"],
        "category": category,
        "entry_type": entry_type,
        "usage_example": generate_usage_example(tamil_word, meaning, district),
        "languages_influenced": meta["languages_influenced"],
    }

    # Add regional variants
    variants = generate_dialect_variants(tamil_word, district, meta)
    if variants:
        entry["regional_variants"] = variants

    return entry


def generate_additional_words(district: str, meta: dict, base_count: int) -> List[dict]:
    """Generate additional entries by creating variations and compounds."""
    extra_entries = []
    categories = list(CORE_WORDS.keys())

    # Number-based entries
    numbers = [
        ("ஒன்று", "ஒன்று", "one"), ("இரண்டு", "இரண்டு", "two"),
        ("மூன்று", "மூன்று", "three"), ("நான்கு", "நந்கு", "four"),
        ("ஐந்து", "ஐந்து", "five"), ("ஆறு", "ஆறு", "six"),
        ("ஏழு", "ஏழு", "seven"), ("எட்டு", "எட்டு", "eight"),
        ("ஒன்பது", "ஒன்பது", "nine"), ("பத்து", "பத்து", "ten"),
    ]

    for i, (tn, std, en) in enumerate(numbers):
        extra_entries.append({
            "id": generate_entry_id(district, base_count + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (number)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "number",
            "entry_type": "base",
            "usage_example": f"{tn} பேர் வந்தாங்க",
            "languages_influenced": meta["languages_influenced"],
        })

    # Days of the week
    days = [
        ("திங்கள்", "திங்கள்", "Monday"),
        ("செவ்வாய்", "செவ்வாய்", "Tuesday"),
        ("புதன்", "புதன்", "Wednesday"),
        ("வியாழன்", "வியாழன்", "Thursday"),
        ("வெள்ளி", "வெள்ளி", "Friday"),
        ("சனி", "சனி", "Saturday"),
        ("ஞாயிறு", "ஞாயிறு", "Sunday"),
    ]

    offset = base_count + len(numbers)
    for i, (tn, std, en) in enumerate(days):
        extra_entries.append({
            "id": generate_entry_id(district, offset + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (day)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "time",
            "entry_type": "base",
            "usage_example": f"{tn} வந்தா சந்தோஷம்",
            "languages_influenced": meta["languages_influenced"],
        })

    # Body parts (extended)
    body_parts = [
        ("முகம்", "முகம்", "face"),
        ("கண்", "கண்", "eye"),
        ("காது", "காது", "ear"),
        ("மூக்கு", "மூக்கு", "nose"),
        ("வாய்", "வாய்", "mouth"),
        ("தலை", "தலை", "head"),
        ("முடி", "முடி", "hair"),
        ("கழுத்து", "கழுத்து", "neck"),
        ("தோள்", "தோள்", "shoulder"),
        ("மார்பு", "மார்பு", "chest"),
        ("கை", "கை", "hand"),
        ("விரல்", "விரல்", "finger"),
        ("நகம்", "நகம்", "nail"),
        ("முதுகு", "முதுகு", "back"),
        ("வயிறு", "வயிறு", "stomach"),
        ("இடுப்பு", "இடுப்பு", "waist"),
        ("தொடை", "தொடை", "thigh"),
        ("முழங்கால்", "முழங்கால்", "knee"),
        ("கால்", "கால்", "leg"),
        ("பாதம்", "பாதம்", "foot"),
        ("கணுக்கால்", "கணுக்கால்", "ankle"),
    ]

    offset2 = offset + len(days)
    for i, (tn, std, en) in enumerate(body_parts):
        extra_entries.append({
            "id": generate_entry_id(district, offset2 + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (body part)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "body",
            "entry_type": "base",
            "usage_example": f"{tn} வலிக்குது",
            "languages_influenced": meta["languages_influenced"],
        })

    # Animals
    animals = [
        ("நாய்", "நாய்", "dog"),
        ("பூனை", "பூனை", "cat"),
        ("மாடு", "மாடு", "cow"),
        ("பசு", "பசு", "cow"),
        ("கோழி", "கோழி", "chicken"),
        ("ஆடு", "ஆடு", "goat"),
        ("குதிரை", "குதிரை", "horse"),
        ("யானை", "யானை", "elephant"),
        ("புலி", "புலி", "tiger"),
        ("சிங்கம்", "சிங்கம்", "lion"),
        ("கரடி", "கரடி", "bear"),
        ("குரங்கு", "குரங்கு", "monkey"),
        ("மயில்", "மயில்", "peacock"),
        ("கிளி", "கிளி", "parrot"),
        ("காக்கை", "காக்கை", "crow"),
        ("புறா", "புறா", "pigeon"),
        ("அணில்", "அணில்", "squirrel"),
        ("பாம்பு", "பாம்பு", "snake"),
        ("மீன்", "மீன்", "fish"),
        ("நண்டு", "நண்டு", "crab"),
        ("இறால்", "இறால்", "prawn"),
        ("சிலந்தி", "சிலந்தி", "spider"),
        ("வண்டு", "வண்டு", "bee / beetle"),
        ("பூச்சி", "பூச்சி", "insect"),
        ("தேள்", "தேள்", "scorpion"),
    ]

    offset3 = offset2 + len(body_parts)
    for i, (tn, std, en) in enumerate(animals):
        extra_entries.append({
            "id": generate_entry_id(district, offset3 + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (animal)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "nature",
            "entry_type": "base",
            "usage_example": f"{tn} தெருவுல நடக்குது",
            "languages_influenced": meta["languages_influenced"],
        })

    # Colors
    colors = [
        ("சிவப்பு", "சிவப்பு", "red"),
        ("நீலம்", "நீலம்", "blue"),
        ("பச்சை", "பச்சை", "green"),
        ("மஞ்சள்", "மஞ்சள்", "yellow"),
        ("வெள்ளை", "வெள்ளை", "white"),
        ("கருப்பு", "கருப்பு", "black"),
        ("ஆரஞ்சு", "ஆரஞ்சு", "orange"),
        ("ஊதா", "ஊதா", "violet"),
        ("பிங்க்", "இளஞ்சிவப்பு", "pink"),
        ("பிரவுன்", "பழுப்பு", "brown"),
    ]

    offset4 = offset3 + len(animals)
    for i, (tn, std, en) in enumerate(colors):
        extra_entries.append({
            "id": generate_entry_id(district, offset4 + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (color)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "nature",
            "entry_type": "base",
            "usage_example": f"{tn} நிறம் அழகா இருக்கு",
            "languages_influenced": meta["languages_influenced"],
        })

    # Furniture / household items
    household = [
        ("மேசை", "மேசை", "table"),
        ("நாற்காலி", "நாற்காலி", "chair"),
        ("படுக்கை", "படுக்கை", "bed"),
        ("அலமாரி", "அலமாரி", "cupboard"),
        ("கதவு", "கதவு", "door"),
        ("ஜன்னல்", "ஜன்னல்", "window"),
        ("மின் விளக்கு", "மின் விளக்கு", "electric light"),
        ("பீரோ", "பீரோ", "wardrobe"),
        ("கடிகாரம்", "கடிகாரம்", "clock"),
        ("கண்ணாடி", "கண்ணாடி", "mirror / glasses"),
        ("தொலைக்காட்சி", "தொலைக்காட்சி", "television"),
        ("குளிர்சாதனம்", "குளிர்சாதனப் பெட்டி", "refrigerator"),
        ("மிக்ஸி", "மிக்ஸி", "mixer"),
        ("விசிறி", "விசிறி", "fan"),
    ]

    offset5 = offset4 + len(colors)
    for i, (tn, std, en) in enumerate(household):
        extra_entries.append({
            "id": generate_entry_id(district, offset5 + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (household)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "daily_life",
            "entry_type": "base",
            "usage_example": f"{tn} நல்லா இருக்கு",
            "languages_influenced": meta["languages_influenced"],
        })

    # Professions
    professions = [
        ("மருத்துவர்", "மருத்துவர்", "doctor"),
        ("வழக்கறிஞர்", "வழக்கறிஞர்", "lawyer"),
        ("ஆசிரியர்", "ஆசிரியர்", "teacher"),
        ("பொறியாளர்", "பொறியாளர்", "engineer"),
        ("விவசாயி", "விவசாயி", "farmer"),
        ("வியாபாரி", "வியாபாரி", "businessman"),
        ("ஓட்டுநர்", "ஓட்டுநர்", "driver"),
        ("தச்சு", "தச்சு", "carpenter"),
        ("தையல்காரர்", "தையல்காரர்", "tailor"),
        ("மேசன்", "மேசன்", "mason"),
        ("மீனவர்", "மீனவர்", "fisherman"),
        ("காவலர்", "காவலர்", "police"),
        ("ராணுவ வீரர்", "ராணுவ வீரர்", "soldier"),
        ("சமையல்காரர்", "சமையல்காரர்", "cook"),
        ("பால் விற்பவர்", "பால் விற்பவர்", "milkman"),
    ]

    offset6 = offset5 + len(household)
    for i, (tn, std, en) in enumerate(professions):
        extra_entries.append({
            "id": generate_entry_id(district, offset6 + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (profession)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "work",
            "entry_type": "base",
            "usage_example": f"அவர் {tn} வேலை பார்க்கிறார்",
            "languages_influenced": meta["languages_influenced"],
        })

    # Weather / seasons
    weather = [
        ("கோடை", "கோடை", "summer"),
        ("குளிர்", "குளிர்", "winter"),
        ("மழை", "மழை", "rain"),
        ("பனி", "பனி", "fog / mist"),
        ("வெயில்", "வெயில்", "sun / heat"),
        ("காற்று", "காற்று", "wind"),
        ("இடி", "இடி", "thunder"),
        ("மின்னல்", "மின்னல்", "lightning"),
        ("வெள்ளம்", "வெள்ளம்", "flood"),
        ("வறட்சி", "வறட்சி", "drought"),
    ]

    offset7 = offset6 + len(professions)
    for i, (tn, std, en) in enumerate(weather):
        extra_entries.append({
            "id": generate_entry_id(district, offset7 + i),
            "tamil_word": tn,
            "tanglish": generate_tanglish(tn),
            "standard_tamil": std,
            "meaning": f"{en} (weather)",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "nature",
            "entry_type": "base",
            "usage_example": f"இன்று {tn} அதிகமா இருக்கு",
            "languages_influenced": meta["languages_influenced"],
        })

    return extra_entries


def generate_compound_variants(entries: List[dict], district: str, meta: dict) -> List[dict]:
    """Generate compound and phrase variants from base entries."""
    compounds = []
    bases = random.sample(entries, min(len(entries), 50))

    prefixes = ["பெரிய", "சின்ன", "நல்ல", "கெட்ட", "புது", "பழைய", "அழகான", "சோகமான"]
    suffixes_verb = ["பண்ணு", "பண்ணிட்டு", "பண்ணாம", "பண்ணிட்டான்", "பண்ணிட்டாள்"]
    suffixes_adj = ["ஆக", "ஆகி", "ஆன", "ஆகவே"]

    for i, base in enumerate(bases[:30]):
        # Adjective + noun compounds
        prefix = random.choice(prefixes)
        compounds.append({
            "id": generate_entry_id(district, 10000 + i),
            "tamil_word": f"{prefix}{base['tamil_word']}",
            "tanglish": f"{generate_tanglish(prefix)}{base['tanglish']}",
            "standard_tamil": f"{prefix}{base['standard_tamil']}",
            "meaning": f"{prefix} {base['meaning']}",
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": base["category"],
            "entry_type": "compound",
            "usage_example": f"{prefix}{base['tamil_word']} ன்னு சொல்லு",
            "languages_influenced": meta["languages_influenced"],
        })

    return compounds


def generate_phonetic_variants(entries: List[dict], district: str, meta: dict) -> List[dict]:
    """Generate phonetic/spelling variants."""
    variants = []
    bases = random.sample(entries, min(len(entries), 40))

    vowel_swaps = {
        "அ": "ஆ", "ஆ": "அ",
        "இ": "ஈ", "ஈ": "இ",
        "உ": "ஊ", "ஊ": "உ",
    }

    consonant_swaps = {
        "க": "க",
        "ச": "ச",
        "த": "த",
        "ப": "ப",
    }

    for i, base in enumerate(bases[:20]):
        word = base["tamil_word"]
        if len(word) >= 3:
            # Swap a vowel
            for orig, replacement in vowel_swaps.items():
                if orig in word:
                    new_word = word.replace(orig, replacement, 1)
                    variants.append({
                        "id": generate_entry_id(district, 20000 + i),
                        "tamil_word": new_word,
                        "tanglish": generate_tanglish(new_word),
                        "standard_tamil": base["standard_tamil"],
                        "meaning": f"{base['meaning']} (phonetic variant)",
                        "region": district,
                        "dialect_region": meta["dialect_region"],
                        "sub_dialect": meta["sub_dialect"],
                        "category": base["category"],
                        "entry_type": "phonetic_variant",
                        "usage_example": base["usage_example"],
                        "languages_influenced": meta["languages_influenced"],
                    })
                    break

    return variants


def generate_misspellings(entries: List[dict], district: str, meta: dict) -> List[dict]:
    """Generate common misspelling variants."""
    misspellings = []
    bases = random.sample(entries, min(len(entries), 30))

    for i, base in enumerate(bases[:15]):
        word = base["tamil_word"]
        if len(word) >= 3:
            # Duplicate a character
            pos = random.randint(0, len(word) - 1)
            new_word = word[:pos] + word[pos] + word[pos:]
            misspellings.append({
                "id": generate_entry_id(district, 30000 + i),
                "tamil_word": new_word,
                "tanglish": generate_tanglish(new_word),
                "standard_tamil": base["standard_tamil"],
                "meaning": f"{base['meaning']} (misspelling)",
                "region": district,
                "dialect_region": meta["dialect_region"],
                "sub_dialect": meta["sub_dialect"],
                "category": base["category"],
                "entry_type": "misspelling",
                "usage_example": base["usage_example"],
                "languages_influenced": meta["languages_influenced"],
            })

    return misspellings


def generate_district_dataset(district: str, meta: dict) -> List[dict]:
    """Generate complete dataset for a single district."""
    entries = []
    idx = 0

    # Add all core words
    for category, words in CORE_WORDS.items():
        for word_data in words:
            entry = create_entry(word_data, district, meta, idx)
            idx += 1
            entries.append(entry)

    # Generate additional standard entries
    extra = generate_additional_words(district, meta, idx)
    entries.extend(extra)
    idx += len(extra)

    # Generate compound variants
    compounds = generate_compound_variants(entries, district, meta)
    entries.extend(compounds)

    # Generate phonetic variants
    phonetics = generate_phonetic_variants(entries, district, meta)
    entries.extend(phonetics)

    # Generate misspellings
    misspellings = generate_misspellings(entries, district, meta)
    entries.extend(misspellings)

    return entries


# ============================================================
# MAIN GENERATION
# ============================================================

def main():
    print("=" * 60)
    print("Tamil Nadu District-wise Tamil/Tanglish Dataset Generator")
    print("=" * 60)

    total_entries = 0
    district_stats = {}

    for district, meta in DISTRICTS.items():
        district_dir = os.path.join(OUTPUT_DIR, district)
        os.makedirs(district_dir, exist_ok=True)

        print(f"\nGenerating dataset for: {district} ({meta['sub_dialect']})")

        entries = generate_district_dataset(district, meta)

        # Save as JSON
        output_file = os.path.join(district_dir, f"{district.lower()}_dataset.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        # Save as JSONL for large datasets
        jsonl_file = os.path.join(district_dir, f"{district.lower()}_dataset.jsonl")
        with open(jsonl_file, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        count = len(entries)
        total_entries += count
        district_stats[district] = {
            "count": count,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
        }
        print(f"  -> {count:,} entries generated")

    # Generate summary statistics
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nTotal entries: {total_entries:,}")
    print(f"Districts covered: {len(DISTRICTS)}")

    # Save summary
    summary = {
        "total_entries": total_entries,
        "districts": len(DISTRICTS),
        "district_stats": district_stats,
        "schema": {
            "id": "Unique entry identifier",
            "tamil_word": "Word in Tamil script",
            "tanglish": "Tanglish transliteration",
            "standard_tamil": "Standard Tamil equivalent",
            "meaning": "English meaning",
            "region": "District name",
            "dialect_region": "Major dialect region",
            "sub_dialect": "Specific dialect variety",
            "category": "Word category",
            "entry_type": "base/compound/phonetic_variant/misspelling",
            "usage_example": "Example usage sentence",
            "languages_influenced": "Languages that influenced the dialect",
            "regional_variants": "Regional pronunciation variants (optional)",
        },
        "categories": list(CORE_WORDS.keys()),
        "dialect_regions": ["Northern", "Central", "Western", "Southern"],
    }

    summary_file = os.path.join(OUTPUT_DIR, "dataset_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nSummary saved to: {summary_file}")

    # Print top 10 districts by count
    print("\nTop 10 districts by entry count:")
    sorted_stats = sorted(district_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    for district, stats in sorted_stats[:10]:
        print(f"  {district:25s} -> {stats['count']:>6,} entries ({stats['sub_dialect']})")


if __name__ == "__main__":
    main()
