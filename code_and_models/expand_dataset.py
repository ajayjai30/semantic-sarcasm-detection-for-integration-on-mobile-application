#!/usr/bin/env python3
"""
Expand the base Tamil dataset to 50K+ entries with additional variants,
dialect-specific words, sentence-level entries, and more Tanglish forms.
"""

import json
import os
import random
import hashlib

OUTPUT_DIR = r"E:\tamil_slang_dataset"
SEED = 123
random.seed(SEED)

# ============================================================
# EXPANSION WORD BANKS - additional Tamil words by category
# ============================================================

EXPANSION_WORDS = {
    "body_extra": [
        ("மண்டைக்கால்", "முழங்கால்", "knee (colloquial)"),
        ("சூத்து", "பின்புறம்", "buttocks"),
        ("முலை", "மார்பகம்", "breast"),
        ("குண்டி", "பின்புறம்", "butt (colloquial)"),
        ("தொப்புள்", "தொப்புள்", "navel"),
        ("எலும்பு", "எலும்பு", "bone"),
        ("மூட்டு", "மூட்டு", "joint"),
        ("சதை", "சதை", "flesh"),
        ("தோல்", "தோல்", "skin"),
        ("நரம்பு", "நரம்பு", "nerve"),
        ("வியர்வை", "வியர்வை", "sweat"),
        ("உமிழ்நீர்", "உமிழ்நீர்", "saliva"),
        ("கண்ணீர்", "கண்ணீர்", "tears"),
        ("மூச்சு", "சுவாசம்", "breath"),
        ("இதயத் துடிப்பு", "இதயத் துடிப்பு", "heartbeat"),
    ],
    "food_extra": [
        ("பிரியாணி", "பிரியாணி", "biryani"),
        ("கருவாடு", "கருவாடு", "dried fish"),
        ("நெய்", "நெய்", "ghee"),
        ("பாயசம்", "பாயசம்", "payasam (dessert)"),
        ("சர்க்கரை பொங்கல்", "சர்க்கரை பொங்கல்", "sweet pongal"),
        ("வெண்பொங்கல்", "வெண்பொங்கல்", "white pongal"),
        ("காளை சாம்பார்", "சாம்பார்", "kadalai sambar"),
        ("மொச்சை கட்டி", "மொச்சை", "black-eyed peas curry"),
        ("ரவா தோசை", "ரவா தோசை", "rava dosa"),
        ("கல்லை தோசை", "கல்லை தோசை", "crispy dosa"),
        ("கோதுமை ரொட்டி", "கோதுமை ரொட்டி", "wheat roti"),
        ("சப்பாத்தி", "சப்பாத்தி", "chapati"),
        ("நாண்", "நாண்", "naan bread"),
        ("தயிர் சாதம்", "தயிர் சாதம்", "curd rice"),
        ("லெமன் ரைஸ்", "எலுமிச்சை சாதம்", "lemon rice"),
        ("தக்காளி சாதம்", "தக்காளி சாதம்", "tomato rice"),
        ("புளி சாதம்", "புளி சாதம்", "tamarind rice"),
        ("மிளகாய் பொடி", "மிளகாய் பொடி", "chili powder"),
        ("மசாலா", "மசாலா", "masala"),
        ("கருவேப்பிலை", "கருவேப்பிலை", "curry leaves"),
        ("வேப்பிலை", "வேப்பிலை", "neem leaves"),
        ("புதினா இலை", "புதினா இலை", "mint leaves"),
        ("சின்ன வெங்காயம்", "சின்ன வெங்காயம்", "small onion"),
        ("பெரிய வெங்காயம்", "பெரிய வெங்காயம்", "big onion"),
        ("காய்கறி", "காய்கறி", "vegetables"),
    ],
    "travel_extra": [
        ("ஃபாஸ்ட்", "விரைவு", "fast (bus)"),
        ("சூப்பர் ஃபாஸ்ட்", "மிக விரைவு", "super fast"),
        ("எக்ஸ்பிரஸ்", "விரைவு ரயில்", "express"),
        ("லோக்கல்", "உள்ளூர்", "local (train/bus)"),
        ("கம்யூட்டர்", "பயணிகள் ரயில்", "commuter train"),
        ("மெட்ரோ", "மெட்ரோ ரயில்", "metro"),
        ("மாநகர பேருந்து", "மாநகர பேருந்து", "city bus"),
        ("விரைவு பேருந்து", "விரைவு பேருந்து", "express bus"),
        ("டாக்ஸி", "காலி வண்டி", "taxi"),
        ("ஆட்டோ ரிக்‌ஷா", "ஆட்டோ", "auto rickshaw"),
        ("சைக்கிள் ரிக்‌ஷா", "மிதிவண்டி ஆட்டோ", "cycle rickshaw"),
        ("கப்பல்", "கப்பல்", "ship"),
        ("விமானம்", "விமானம்", "airplane"),
        ("ஹெலிகாப்டர்", "உலங்கு வானூர்தி", "helicopter"),
        ("சரக்கு வண்டி", "சரக்கு வண்டி", "truck"),
        ("கார்", "கார்", "car"),
        ("ஜீப்", "ஜீப்", "jeep"),
        ("வேன்", "வேன்", "van"),
    ],
    "emotion_extra": [
        ("ஏக்கம்", "ஏக்கம்", "longing"),
        ("தவிப்பு", "கவலை", "worry"),
        ("குழப்பம்", "குழப்பம்", "confusion"),
        ("திகில்", "அதிர்ச்சி", "shock / horror"),
        ("உசேர்", "கோபம்", "anger (Nellai)"),
        ("கலக்கம்", "கலக்கம்", "dejection"),
        ("மன அழுத்தம்", "மன அழுத்தம்", "depression"),
        ("மன உளைச்சல்", "மன உளைச்சல்", "mental stress"),
        ("உற்சாகம்", "உற்சாகம்", "enthusiasm"),
        ("உந்துசக்தி", "உந்துசக்தி", "motivation"),
        ("தன்னம்பிக்கை", "தன்னம்பிக்கை", "self-confidence"),
        ("பயம்", "அச்சம்", "fear"),
        ("அவமானம்", "அவமானம்", "humiliation"),
        ("பெருமை", "பெருமை", "pride"),
        ("கர்வம்", "கர்வம்", "arrogance"),
        ("திமிரு", "திமிரு", "attitude"),
        ("சிரிப்பு", "சிரிப்பு", "laughter"),
        ("அழுகை", "அழுகை", "crying"),
        ("கொண்டாட்டம்", "கொண்டாட்டம்", "celebration"),
        ("விருந்து", "விருந்து", "feast"),
    ],
    "shopping_extra": [
        ("தட்டு", "தட்டு", "plate"),
        ("கோப்பை", "கோப்பை", "cup"),
        ("ஜாடி", "குடுவை", "jar"),
        ("சீசா", "பாட்டில்", "bottle (Kongu)"),
        ("பிளாஸ்டிக்", "பிளாஸ்டிக்", "plastic"),
        ("காகிதம்", "காகிதம்", "paper"),
        ("பேப்பர்", "காகிதம்", "paper (Tanglish)"),
        ("ஸ்டிக்கர்", "ஒட்டு", "sticker"),
        ("பேனா", "எழுதுகோல்", "pen"),
        ("பென்சில்", "எழுதுகோல்", "pencil"),
        ("ரப்பர்", "அழிப்பான்", "eraser"),
        ("ஸ்கேல்", "அளவுகோல்", "scale"),
        ("நோட்டு", "நோட்டு", "notebook"),
        ("புத்தகம்", "நூல்", "book"),
        ("கைப்பை", "கைப்பை", "handbag"),
        ("ஷூ", "காலணி", "shoes"),
        ("சாக்ஸ்", "காலுறை", "socks"),
        ("தொப்பி", "தொப்பி", "hat"),
        ("குடை", "குடை", "umbrella"),
        ("கைக்கடிகாரம்", "கைக்கடிகாரம்", "wristwatch"),
    ],
    "rural_extra": [
        ("நெல்", "நெல்", "paddy"),
        ("கோதுமை", "கோதுமை", "wheat"),
        ("சோளம்", "சோளம்", "maize"),
        ("கம்பு", "கம்பு", "millet"),
        ("தினை", "தினை", "finger millet"),
        ("சிறுநீர்", "சிறுநீர்", "urine (clinical)"),
        ("பால்", "பால்", "milk"),
        ("மோர்", "மோர்", "buttermilk"),
        ("கட்டி", "கட்டி", "block / bundle"),
        ("மூட்டை", "பொதி", "bundle"),
        ("கலப்பை", "கலப்பை", "plough"),
        ("உழவு", "உழவு", "ploughing"),
        ("விதை", "விதை", "seed"),
        ("விளைச்சல்", "விளைச்சல்", "harvest yield"),
        ("பயிர்", "பயிர்", "crop"),
        ("களை", "களை", "weed"),
        ("நீர்ப்பாசனம்", "நீர்ப்பாசனம்", "irrigation"),
        ("ஆழ்துளை கிணறு", "ஆழ்துளை கிணறு", "bore well"),
        ("குளம்", "குளம்", "pond"),
        ("மேய்ச்சல்", "மேய்ச்சல்", "grazing"),
        ("கன்று", "கன்று", "calf"),
        ("கோழிக்குஞ்சம்", "கோழிக்குஞ்சம்", "chick"),
        ("முட்டை", "முட்டை", "egg"),
        ("தேன்", "தேன்", "honey"),
        ("மகரந்தம்", "மகரந்தம்", "pollen"),
    ],
    "urban_extra": [
        ("அலுவலகம்", "அலுவலகம்", "office"),
        ("மீட்டிங்", "கூட்டம்", "meeting"),
        ("ப்ரெசன்டேஷன்", "விளக்கக்காட்சி", "presentation"),
        ("டெஸ்க்", "மேசை", "desk"),
        ("சேர்", "நாற்காலி", "chair"),
        ("கம்ப்யூட்டர்", "கணினி", "computer"),
        ("பிரின்டர்", "அச்சுப்பொறி", "printer"),
        ("ஸ்கேனர்", "ஸ்கேனர்", "scanner"),
        ("ப்ராஜெக்டர்", "திரைக்காட்டி", "projector"),
        ("மைக்", "ஒலிவாங்கி", "microphone"),
        ("ஸ்பீக்கர்", "ஒலிப்பெருக்கி", "speaker"),
        ("ஹெட்போன்", "தலையணி", "headphone"),
        ("சார்ஜர்", "சார்ஜர்", "charger"),
        ("கேபிள்", "கம்பி", "cable"),
        ("சிம் கார்டு", "சிம் அட்டை", "SIM card"),
        ("நெட்", "இணையம்", "internet"),
        ("வைபை", "வயர்லெஸ்", "wifi"),
        ("ஹாட்ஸ்பாட்", "ஹாட்ஸ்பாட்", "hotspot"),
        ("ப்ளூடூத்", "ப்ளூடூத்", "bluetooth"),
        ("டேட்டா", "தரவு", "data"),
    ],
    "tanglish_extra": [
        ("ஸ்டைல்", "பாணி", "style"),
        ("மாஸ்", "பெருமை", "mass / swag"),
        ("பவர்", "சக்தி", "power"),
        ("எனர்ஜி", "ஆற்றல்", "energy"),
        ("ஸ்ட்ராங்", "வலுவான", "strong"),
        ("வீக்", "பலவீனமான", "weak"),
        ("ஹார்ட்", "கடினமான", "hard"),
        ("சாஃப்ட்", "மென்மையான", "soft"),
        ("ஃபாஸ்ட்", "விரைவான", "fast"),
        ("ஸ்லோ", "மெதுவான", "slow"),
        ("லார்ஜ்", "பெரிய", "large"),
        ("ஸ்மால்", "சின்ன", "small"),
        ("நைஸ்", "நல்ல", "nice"),
        ("கிரேட்", "சிறப்பான", "great"),
        ("பூர்", "ஏழை", "poor"),
        ("ரிச்", "பணக்காரன்", "rich"),
        ("ஹேப்பி", "மகிழ்ச்சி", "happy"),
        ("சாட்", "சோகம்", "sad"),
        ("ஏஞ்சல்", "தேவதை", "angel"),
        ("டெவில்", "பிசாசு", "devil"),
    ],
    "colloquial_extra": [
        ("என்ன மேட்டர்", "என்ன விசயம்", "what's the matter?"),
        ("ஒன்னும் இல்லையே", "ஒன்றும் இல்லை", "nothing, right?"),
        ("சரியா", "சரியா", "right?"),
        ("உண்மையா", "உண்மையா", "really?"),
        ("நிஜமா", "உண்மையா", "seriously?"),
        ("டேய் மச்சி", "ஏய் நண்பா", "hey bro"),
        ("என்ன லூசுத்தனம்", "என்ன பைத்தியக்காரத்தனம்", "what nonsense"),
        ("போடா போடி", "விலகு", "get out (casual)"),
        ("ம்ம் சரி", "சரி", "mm okay"),
        ("அப்படியா சார்", "அவ்வாறா", "is that so, sir?"),
        ("இல்ல இல்ல", "இல்லை இல்லை", "no no"),
        ("ஆமா ஆமா", "ஆம் ஆம்", "yes yes"),
        ("ஏன் டா", "ஏன்", "why dude?"),
        ("எப்ப டா", "எப்போது", "when dude?"),
        ("எங்க டா", "எங்கு", "where dude?"),
        ("யாரு டா", "யார்", "who dude?"),
        ("என்ன டா", "என்ன", "what dude?"),
        ("சொல்லு டா", "சொல்", "tell me dude"),
        ("நில்லு டா", "நில்", "wait dude"),
        ("போடா சாமி", "விலகு", "get lost (playful)"),
    ],
    "nature_extra": [
        ("மணல்", "மணல்", "sand"),
        ("சரளை", "சரளை", "gravel"),
        ("களிமண்", "களிமண்", "clay"),
        ("சேறு", "சேறு", "mud"),
        ("புழு", "புழு", "worm"),
        ("பூச்சி", "பூச்சி", "insect"),
        ("கொசு", "கொசு", "mosquito"),
        ("ஈ", "ஈ", "fly"),
        ("சிலந்தி", "சிலந்தி", "spider"),
        ("வண்டு", "வண்டு", "beetle"),
        ("தேனீ", "தேனீ", "bee"),
        ("சிட்டுக்குருவி", "சிட்டுக்குருவி", "sparrow"),
        ("கழுகு", "கழுகு", "eagle"),
        ("நாரை", "நாரை", "heron"),
        ("அரண்மனை வாத்து", "வாத்து", "duck"),
        ("முதலை", "முதலை", "crocodile"),
        ("ஆமை", "ஆமை", "turtle"),
        ("தவளை", "தவளை", "frog"),
        ("சுண்டல் பூச்சி", "சுண்டல் பூச்சி", "centipede"),
        ("தேரை", "தேரை", "toad"),
        ("மரவட்டி", "மரவட்டி", "tree spider"),
        ("நத்தை", "நத்தை", "snail"),
        ("சுருட்டுப் பூச்சி", "சுருட்டுப் பூச்சி", "snail"),
    ],
    "work_extra": [
        ("சம்பளம்", "ஊதியம்", "salary"),
        ("அதிகாரி", "அதிகாரி", "officer"),
        ("மேலாளர்", "மேலாளர்", "manager"),
        ("துணை மேலாளர்", "துணை மேலாளர்", "assistant manager"),
        ("பணியாளர்", "பணியாளர்", "employee"),
        ("தலைமை", "தலைமை", "leadership"),
        ("துறை", "துறை", "department"),
        ("அறிக்கை", "அறிக்கை", "report"),
        ("கூட்டம்", "கூட்டம்", "meeting"),
        ("நேர்காணல்", "நேர்காணல்", "interview"),
        ("விண்ணப்பம்", "விண்ணப்பம்", "application"),
        ("ஒப்பந்தம்", "ஒப்பந்தம்", "contract"),
        ("விலைப்பட்டியல்", "விலைப்பட்டியல்", "price list"),
        ("வரி", "வரி", "tax"),
        ("வருமானம்", "வருமானம்", "income"),
        ("செலவு", "செலவு", "expense"),
        ("லாபம்", "லாபம்", "profit"),
        ("நஷ்டம்", "நஷ்டம்", "loss"),
        ("வங்கி", "வங்கி", "bank"),
        ("கடன்", "கடன்", "loan"),
    ],
    "student_extra": [
        ("தேர்வு", "தேர்வு", "exam"),
        ("கல்வி", "கல்வி", "education"),
        ("படிப்பு", "படிப்பு", "studies"),
        ("பாடம்", "பாடம்", "lesson"),
        ("வகுப்பு", "வகுப்பு", "class"),
        ("ஆசிரியர்", "ஆசிரியர்", "teacher"),
        ("மாணவர்", "மாணவர்", "student"),
        ("மாணவி", "மாணவி", "female student"),
        ("கல்லூரி", "கல்லூரி", "college"),
        ("பல்கலைக்கழகம்", "பல்கலைக்கழகம்", "university"),
        ("பள்ளி", "பள்ளி", "school"),
        ("துறை", "துறை", "department"),
        ("பாடப்பிரிவு", "பாடப்பிரிவு", "subject"),
        ("மதிப்பெண்", "மதிப்பெண்", "marks"),
        ("தரவரிசை", "தரவரிசை", "ranking"),
        ("சான்றிதழ்", "சான்றிதழ்", "certificate"),
        ("கல்வி", "கல்வி", "education"),
        ("கற்றல்", "கற்றல்", "learning"),
        ("ஆய்வு", "ஆய்வு", "research"),
        ("திட்டம்", "திட்டம்", "project"),
    ],
    "family_extra": [
        ("மாமனார்", "மாமனார்", "father-in-law (wife's father)"),
        ("மாமியார்", "மாமியார்", "mother-in-law (wife's mother)"),
        ("மாப்பிள்ளை", "மாப்பிள்ளை", "son-in-law"),
        ("மருமகள்", "மருமகள்", "daughter-in-law"),
        ("குழந்தை", "குழந்தை", "child"),
        ("பேரன்", "பேரன்", "grandson"),
        ("பேத்தி", "பேத்தி", "granddaughter"),
        ("மருமகன்", "மருமகன்", "son-in-law"),
        ("நாத்தனார்", "நாத்தனார்", "husband's sister"),
        ("அண்ணாச்சி", "அண்ணாச்சி", "elder brother (Kanyakumari)"),
        ("தாத்தா", "தாத்தா", "grandfather"),
        ("பாட்டி", "பாட்டி", "grandmother"),
        ("மாமா", "மாமா", "maternal uncle"),
        ("மாமி", "மாமி", "aunt (maternal uncle's wife)"),
        ("கொழுந்தியாள்", "கொழுந்தியாள்", "husband's younger sister"),
    ],
    "greeting_extra": [
        ("வணக்கம்", "வணக்கம்", "greetings"),
        ("சபை நலமா", "நீங்கள் நலமா", "are you well, sir?"),
        ("சௌக்கியம்", "நலம்", "wellness"),
        ("சந்தோஷம்", "மகிழ்ச்சி", "happiness"),
        ("போய் வருகிறேன்", "சென்று வருகிறேன்", "I'm leaving"),
        ("நல்லது", "நல்லது", "good"),
        ("அருமை", "மிகச் சிறப்பு", "excellent"),
        ("சிறப்பு", "சிறப்பு", "special"),
        ("வாழ்த்துக்கள்", "வாழ்த்துக்கள்", "congratulations"),
        ("பிறந்த நாள் வாழ்த்துக்கள்", "பிறந்த நாள் வாழ்த்துக்கள்", "happy birthday"),
        ("புத்தாண்டு வாழ்த்துக்கள்", "புத்தாண்டு வாழ்த்துக்கள்", "happy new year"),
        ("தீபாவளி வாழ்த்துக்கள்", "தீபாவளி வாழ்த்துக்கள்", "happy diwali"),
        ("பொங்கல் வாழ்த்துக்கள்", "பொங்கல் வாழ்த்துக்கள்", "happy pongal"),
    ],
    "casual_extra": [
        ("ரொம்ப நல்லா இருக்கு", "மிக நன்றாக இருக்கிறது", "it's very good"),
        ("செம மாஸ்", "மிகச் சிறப்பு", "extremely stylish"),
        ("பக்கா கெத்து", "முழு ஆணவம்", "pure swagger"),
        ("தெறிக்க விடு", "அதிர வை", "make it awesome"),
        ("தூள் கிளப்பு", "சிறப்பாகச் செய்", "rock it"),
        ("கெத்தா இரு", "பெருமையாக இரு", "be proud"),
        ("செம ட்ரிப்", "மிகச் சிறப்பான அனுபவம்", "awesome trip"),
        ("செம ஃபன்", "மிகவும் மகிழ்ச்சி", "lots of fun"),
        ("மச்சி கெத்து", "நண்பனே பெருமை", "bro's pride"),
        ("செம கெத்து", "மிகப் பெருமை", "extremely proud"),
        ("பக்கா செம", "முற்றிலும் சிறப்பு", "totally awesome"),
        ("செம மாஸா", "மிக ஸ்டைலாக", "very stylishly"),
        ("கெத்தா", "பெருமையாக", "proudly"),
    ],
    "offensive_mild": [
        ("முட்டாள்", "முட்டாள்", "fool"),
        ("லூசு", "பைத்தியம்", "crazy"),
        ("பைத்தியம்", "பைத்தியம்", "mad"),
        ("சனியன்", "சனியன்", "wretched"),
        ("கேவலம்", "கேவலம்", "pathetic"),
        ("அறிவில்லாதவன்", "அறிவில்லாதவன்", "ignorant"),
        ("மூடன்", "மூடன்", "fool"),
        ("மக்கா", "முட்டாள்", "idiot"),
        ("தடிமன்", "தடிமன்", "stupid"),
        ("தடியன்", "தடியன்", "blockhead"),
        ("பொட்டச்சி", "பொட்டச்சி", "foolish girl"),
        ("மூர்க்கன்", "மூர்க்கன்", "madman"),
        ("பைத்தியக்காரன்", "பைத்தியக்காரன்", "lunatic"),
        ("கெட்டவன்", "கெட்டவன்", "bad person"),
        ("கெட்ட பையன்", "கெட்ட பையன்", "bad boy"),
    ],
}

# Common Tamil sentence templates for sentence-level entries
SENTENCE_TEMPLATES = [
    ("அவன் வர மாட்டான்", "அவன் வர மாட்டான்", "He won't come"),
    ("அவள் போயிட்டா", "அவள் போய்விட்டாள்", "She left"),
    ("நாளை மழை வரும்", "நாளை மழை வரும்", "Tomorrow it will rain"),
    ("இன்று வேலை அதிகம்", "இன்று வேலை அதிகம்", "Today there's too much work"),
    ("அவன் நல்லா படிக்கிறான்", "அவன் நன்றாகப் படிக்கிறான்", "He studies well"),
    ("அம்மா சாப்பாடு பண்ணிட்டாங்க", "அம்மா சமைத்துவிட்டார்", "Mom finished cooking"),
    ("அப்பா வேலைக்கு போயிட்டார்", "அப்பா வேலைக்குச் சென்றுவிட்டார்", "Dad went to work"),
    ("குழந்தை தூங்கிடிச்சு", "குழந்தை தூங்கிவிட்டது", "The child slept"),
    ("மழை அதிகமா பெய்யுது", "மழை அதிகமாகப் பெய்கிறது", "It's raining heavily"),
    ("வெயில் ரொம்ப கொடுமை", "வெயில் மிகக் கொடுமை", "The sun is very harsh"),
    ("காற்று சுள்ளுனு அடிக்குது", "காற்று குளிர்ச்சியாக அடிக்கிறது", "The wind is blowing cold"),
    ("அவன் ரொம்ப கெத்து", "அவன் மிகவும் பெருமையாக இருக்கிறான்", "He's very proud"),
    ("இந்த படம் செம மாஸ்", "இந்தத் திரைப்படம் மிகச் சிறப்பு", "This movie is awesome"),
    ("அவள் அழகா இருக்கா", "அவள் அழகாக இருக்கிறாள்", "She is beautiful"),
    ("மழைக்கு குடை எடுத்துட்டு வா", "மழைக்குக் குடை எடுத்துக்கொண்டு வா", "Bring an umbrella for rain"),
    ("அவன் மிகவும் நல்லவன்", "அவன் மிகவும் நல்லவன்", "He is very good"),
    ("இன்று பண்டிகை", "இன்று பண்டிகை", "Today is a festival"),
    ("சாப்பிட்டுயிட்டியா", "உண்டுமுடிந்ததா", "Have you eaten?"),
    ("எங்க போற இப்போ", "எங்கு போகிறாய் இப்போது", "Where are you going now?"),
    ("வீட்டுக்கு போகணும்", "வீட்டுக்குச் செல்ல வேண்டும்", "Need to go home"),
    ("காலைல சீக்கிரம் எழுந்திரு", "காலையில் விரைவாக எழுந்திரு", "Wake up early in the morning"),
    ("ராத்திரி நல்லா தூங்கு", "இரவில் நன்றாகத் தூங்கு", "Sleep well at night"),
    ("அவன் வந்தானா", "அவன் வந்தானா", "Did he come?"),
    ("அவள் பேச மாட்டாள்", "அவள் பேச மாட்டாள்", "She won't speak"),
    ("ரொம்ப நன்றி", "மிக நன்றி", "Thank you very much"),
    ("மன்னிச்சிடுங்க", "மன்னிக்கவும்", "Please forgive"),
    ("சரி வாங்க", "சரி வாங்கள்", "Okay, come"),
    ("போயிட்டு வரேன்", "சென்று வருகிறேன்", "I'll be back"),
    ("எப்ப வருவ நீ", "நீ எப்போது வருவாய்", "When will you come?"),
    ("இப்ப தான் வரேன்", "இப்போதுதான் வருகிறேன்", "I'm just coming now"),
]

# Regional dialect-specific phrases
REGIONAL_PHRASES = {
    "Chennai": [
        ("டா என்ன மாஸ் போடுற", "மாஸாக நட", "Walk with swag, dude"),
        ("செம செட்டை கொடுத்தான்", "நல்ல கலாட்டா பண்ணினான்", "He created a great scene"),
        ("நீ என்ன கேங் பண்ற", "நீ என்ன செய்கிறாய்", "What gang are you in?"),
        ("செம மொக்க பேசாதே", "மோசமாகப் பேசாதே", "Don't talk rubbish"),
        ("என்ன சீன் போடுற", "ஏன் ட்ராமா பண்ற", "Why are you creating drama?"),
        ("கலீஜு ஆகிடுச்சு", "அசுத்தமாகிவிட்டது", "It got dirty"),
        ("மச்சான் செம கெத்து", "நண்பனே மிகப் பெருமை", "Bro is very proud"),
        ("டுபாக்கூர் பண்ணாதே", "ஏமாற்றாதே", "Don't cheat"),
    ],
    "Madurai": [
        ("வாய்ங்க வாங்க", "வாருங்கள்", "Come (respectful, Madurai)"),
        ("குண்டக்க மண்டக்க பேசாதே", "தேவையில்லாமல் பேசாதே", "Don't talk nonsense"),
        ("சூதானமா இரு", "பத்திரமாக இரு", "Be careful"),
        ("பைய போ", "மெதுவாகச் செல்", "Go slowly"),
        ("சோலிய பாரு", "உன் வேலையைப் பார்", "Mind your business"),
        ("ராவுறான்", "சலிக்கிறான்", "He's boring"),
        ("எம்புட்டு", "எவ்வளவு", "How much?"),
        ("கொக்க மக்க", "உறவினர் குழு", "Relative group"),
    ],
    "Coimbatore": [
        ("நெங்கோ எப்படி இருக்கீங்க", "நீங்கள் எப்படி இருக்கிறீர்கள்", "How are you (Kongu respect)"),
        ("வாங்கோ உக்காருங்கோ", "வாருங்கள் அமருங்கள்", "Come, sit (Kongu)"),
        ("சாப்பிடுங்கோ", "உண்ணுங்கள்", "Eat (Kongu respect)"),
        ("நம்ம சோலி எப்படி போகுது", "நமது வேலை எப்படி போகிறது", "How is our work going?"),
        ("வெடுக்குனு முடி", "விரைவாக முடி", "Finish quickly"),
        ("பொறவு போறேன்", "பிறகு போகிறேன்", "I'll go later"),
        ("வெசனம் புடிச்சு இருக்கான்", "வருத்தத்தில் இருக்கிறான்", "He is upset"),
    ],
    "Tirunelveli": [
        ("எலேய் எப்படி இருக்கீய", "ஏய் எப்படி இருக்கிறாய்", "Hey, how are you?"),
        ("சுவமா இருக்கியாலா", "நலமா இருக்கிறாயா", "Are you well? (Nellai)"),
        ("அன்னாச்சி வாங்க", "அண்ணா வாருங்கள்", "Brother, come (Nellai)"),
        ("யேலா என்ன பண்ணுற", "ஏய் என்ன செய்கிறாய்", "Hey, what are you doing?"),
        ("சோலி இல்லாம சுத்துற", "வேலை இல்லாமல் சுற்றுகிறாய்", "You're roaming without work"),
        ("பையலுவா பசங்க", "பையன்கள்", "Boys (Nellai)"),
        ("கோலா போயிட்டு வா", "நல்லாப் போய்விட்டு வா", "Go well and come back"),
    ],
    "Thanjavur": [
        ("அங்க இருக்கான்", "அங்கே இருக்கிறான்", "He is there"),
        ("இங்க வா", "இங்கே வா", "Come here"),
        ("சரியா சொல்லு", "சரியாகச் சொல்", "Say it correctly"),
        ("நல்லா கவனி", "நன்றாகக் கவனி", "Watch carefully"),
        ("திருத்தமா பேசு", "திருத்தமாகப் பேசு", "Speak properly"),
    ],
}


def generate_sentence_entries(district, meta, base_idx):
    """Generate sentence-level entries."""
    entries = []
    for i, (tamil, std, eng) in enumerate(SENTENCE_TEMPLATES):
        entries.append({
            "id": f"{district[:3].upper()}_{base_idx + i:06d}",
            "tamil_word": tamil,
            "tanglish": "",
            "standard_tamil": std,
            "meaning": eng,
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "sentence",
            "entry_type": "sentence",
            "usage_example": tamil,
            "languages_influenced": meta["languages_influenced"],
        })
    return entries


def generate_regional_phrase_entries(district, meta, base_idx):
    """Generate dialect-specific phrase entries."""
    entries = []
    phrases = REGIONAL_PHRASES.get(district, [])
    for i, (tamil, std, eng) in enumerate(phrases):
        entries.append({
            "id": f"{district[:3].upper()}_{base_idx + i:06d}",
            "tamil_word": tamil,
            "tanglish": "",
            "standard_tamil": std,
            "meaning": eng,
            "region": district,
            "dialect_region": meta["dialect_region"],
            "sub_dialect": meta["sub_dialect"],
            "category": "regional_phrase",
            "entry_type": "regional_phrase",
            "usage_example": tamil,
            "languages_influenced": meta["languages_influenced"],
        })
    return entries


def generate_tanglish_form(word_entry):
    """Create a Tanglish variant of a word entry."""
    return {
        "id": word_entry["id"].replace("_", "_TL_"),
        "tamil_word": word_entry["tanglish"] if word_entry["tanglish"] else word_entry["tamil_word"],
        "tanglish": word_entry["tanglish"],
        "standard_tamil": word_entry["standard_tamil"],
        "meaning": word_entry["meaning"],
        "region": word_entry["region"],
        "dialect_region": word_entry["dialect_region"],
        "sub_dialect": word_entry["sub_dialect"],
        "category": word_entry["category"],
        "entry_type": "tanglish_form",
        "usage_example": word_entry.get("usage_example", ""),
        "languages_influenced": word_entry["languages_influenced"],
    }


def main():
    print("=" * 60)
    print("Tamil Dataset Expansion Script")
    print("=" * 60)

    # Load district metadata
    districts_meta = {}
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(OUTPUT_DIR, "generate_dataset.py")
    )
    gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen_module)
    DISTRICTS = gen_module.DISTRICTS

    total_added = 0

    for district, meta in DISTRICTS.items():
        district_dir = os.path.join(OUTPUT_DIR, district)
        base_file = os.path.join(district_dir, f"{district.lower()}_dataset.json")

        if not os.path.exists(base_file):
            print(f"Skipping {district}: base file not found")
            continue

        with open(base_file, "r", encoding="utf-8") as f:
            existing = json.load(f)

        new_entries = list(existing)
        base_idx = len(existing) + 5000

        # 1. Add expansion words
        for cat_name, words in EXPANSION_WORDS.items():
            for i, (tn, std, meaning) in enumerate(words):
                new_entries.append({
                    "id": f"{district[:3].upper()}_{base_idx:06d}",
                    "tamil_word": tn,
                    "tanglish": gen_module.generate_tanglish(tn),
                    "standard_tamil": std,
                    "meaning": meaning,
                    "region": district,
                    "dialect_region": meta["dialect_region"],
                    "sub_dialect": meta["sub_dialect"],
                    "category": cat_name.replace("_extra", ""),
                    "entry_type": "base",
                    "usage_example": gen_module.generate_usage_example(tn, meaning, district),
                    "languages_influenced": meta["languages_influenced"],
                })
                base_idx += 1

        # 2. Add sentence entries
        sentences = generate_sentence_entries(district, meta, base_idx)
        new_entries.extend(sentences)
        base_idx += len(sentences)

        # 3. Add regional phrases
        phrases = generate_regional_phrase_entries(district, meta, base_idx)
        new_entries.extend(phrases)
        base_idx += len(phrases)

        # 4. Generate Tanglish forms for existing base words
        tanglish_entries = []
        for entry in existing:
            if entry["entry_type"] == "base" and entry["tanglish"]:
                tl = generate_tanglish_form(entry)
                tl["id"] = f"{district[:3].upper()}_{base_idx:06d}"
                tanglish_entries.append(tl)
                base_idx += 1
        new_entries.extend(tanglish_entries)

        # 5. Generate dialect variant entries (apply regional pronunciation rules)
        dialect_variants = []
        for entry in existing[:80]:
            if entry["entry_type"] == "base":
                variant_word = entry["tamil_word"]
                # Apply Northern dialect changes (Chennai-style)
                if meta["dialect_region"] == "Northern":
                    if variant_word.endswith("ம்"):
                        vw = variant_word[:-1] + "ன்"
                        dialect_variants.append({
                            "id": f"{district[:3].upper()}_{base_idx:06d}",
                            "tamil_word": vw,
                            "tanglish": gen_module.generate_tanglish(vw),
                            "standard_tamil": entry["standard_tamil"],
                            "meaning": f"{entry['meaning']} (Northern dialect variant)",
                            "region": district,
                            "dialect_region": meta["dialect_region"],
                            "sub_dialect": meta["sub_dialect"],
                            "category": entry["category"],
                            "entry_type": "dialect_variant",
                            "usage_example": entry.get("usage_example", ""),
                            "languages_influenced": meta["languages_influenced"],
                        })
                        base_idx += 1

                # Apply Kongu dialect changes
                if meta["sub_dialect"] == "Kongu Tamil":
                    if "கிறீர்கள்" in variant_word:
                        vw = variant_word.replace("கிறீர்கள்", "ரீங்க")
                        dialect_variants.append({
                            "id": f"{district[:3].upper()}_{base_idx:06d}",
                            "tamil_word": vw,
                            "tanglish": gen_module.generate_tanglish(vw),
                            "standard_tamil": entry["standard_tamil"],
                            "meaning": f"{entry['meaning']} (Kongu dialect variant)",
                            "region": district,
                            "dialect_region": meta["dialect_region"],
                            "sub_dialect": meta["sub_dialect"],
                            "category": entry["category"],
                            "entry_type": "dialect_variant",
                            "usage_example": entry.get("usage_example", ""),
                            "languages_influenced": meta["languages_influenced"],
                        })
                        base_idx += 1

                # Apply Madurai dialect changes
                if district == "Madurai":
                    if "கிறான்" in variant_word:
                        vw = variant_word.replace("கிறான்", "றான்")
                        dialect_variants.append({
                            "id": f"{district[:3].upper()}_{base_idx:06d}",
                            "tamil_word": vw,
                            "tanglish": gen_module.generate_tanglish(vw),
                            "standard_tamil": entry["standard_tamil"],
                            "meaning": f"{entry['meaning']} (Madurai dialect variant)",
                            "region": district,
                            "dialect_region": meta["dialect_region"],
                            "sub_dialect": meta["sub_dialect"],
                            "category": entry["category"],
                            "entry_type": "dialect_variant",
                            "usage_example": entry.get("usage_example", ""),
                            "languages_influenced": meta["languages_influenced"],
                        })
                        base_idx += 1

                # Apply Nellai dialect changes
                if "Nellai" in meta.get("sub_dialect", ""):
                    if "சுகம்" in variant_word:
                        vw = variant_word.replace("சுகம்", "சுவம்")
                        dialect_variants.append({
                            "id": f"{district[:3].upper()}_{base_idx:06d}",
                            "tamil_word": vw,
                            "tanglish": gen_module.generate_tanglish(vw),
                            "standard_tamil": entry["standard_tamil"],
                            "meaning": f"{entry['meaning']} (Nellai dialect variant)",
                            "region": district,
                            "dialect_region": meta["dialect_region"],
                            "sub_dialect": meta["sub_dialect"],
                            "category": entry["category"],
                            "entry_type": "dialect_variant",
                            "usage_example": entry.get("usage_example", ""),
                            "languages_influenced": meta["languages_influenced"],
                        })
                        base_idx += 1

        new_entries.extend(dialect_variants)

        added = len(new_entries) - len(existing)
        total_added += added

        # Save expanded dataset
        output_file = os.path.join(district_dir, f"{district.lower()}_dataset.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(new_entries, f, ensure_ascii=False, indent=2)

        # Save JSONL
        jsonl_file = os.path.join(district_dir, f"{district.lower()}_dataset.jsonl")
        with open(jsonl_file, "w", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"  {district:25s}: {len(existing):>5d} -> {len(new_entries):>5d} (+{added})")

    print(f"\nTotal entries added: {total_added:,}")

    # Update summary
    total_all = 0
    summary_stats = {}
    for district in DISTRICTS:
        district_dir = os.path.join(OUTPUT_DIR, district)
        base_file = os.path.join(district_dir, f"{district.lower()}_dataset.json")
        if os.path.exists(base_file):
            with open(base_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data)
            total_all += count
            summary_stats[district] = count

    print(f"\nGrand total: {total_all:,} entries across {len(DISTRICTS)} districts")

    summary = {
        "total_entries": total_all,
        "districts": len(DISTRICTS),
        "district_stats": {d: {"count": c} for d, c in summary_stats.items()},
        "schema": {
            "id": "Unique entry identifier",
            "tamil_word": "Word/phrase in Tamil script or Tanglish",
            "tanglish": "Tanglish transliteration",
            "standard_tamil": "Standard Tamil equivalent",
            "meaning": "English meaning",
            "region": "District name",
            "dialect_region": "Major dialect region (Northern/Central/Western/Southern)",
            "sub_dialect": "Specific dialect variety",
            "category": "Word category",
            "entry_type": "base/compound/phonetic_variant/misspelling/tanglish_form/dialect_variant/sentence/regional_phrase",
            "usage_example": "Example usage sentence in Tamil",
            "languages_influenced": "Languages that influenced the dialect",
        },
        "entry_types": {
            "base": "Core vocabulary entries",
            "tanglish_form": "Tanglish transliteration variants",
            "dialect_variant": "Region-specific pronunciation variants",
            "sentence": "Complete sentence entries",
            "regional_phrase": "Dialect-specific phrases",
            "compound": "Compound word entries",
            "phonetic_variant": "Spelling/phonetic variants",
            "misspelling": "Common misspelling variants",
        },
    }

    summary_file = os.path.join(OUTPUT_DIR, "dataset_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nSummary saved to: {summary_file}")


if __name__ == "__main__":
    main()
