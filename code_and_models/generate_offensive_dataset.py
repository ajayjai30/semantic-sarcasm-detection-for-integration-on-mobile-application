"""
Tamil Nadu District-wise Offensive Slang Dataset Generator
For NLP Toxicity Detection Training

Severity Levels:
  - MILD: Everyday insults, teasing terms ( मामूலी அவமதிப்பு )
  - MODERATE: Stronger insults, vulgar language ( கடுமையான அவமதிப்பு )
  - SEVERE: Explicit, sexually charged, hate speech ( மிக கடுமையான வன்மொழி )

Categories:
  - insult: Personal attacks on character/intelligence
  - profanity: Sexual/vulgar content
  - slur: Caste/community/class-based slurs
  - body_shaming: Insults about appearance/physique
  - family_insult: Insults targeting family members
  - animal_comparison: Comparing someone to animals
  - death_wish: Wishing harm/death
  - gender_based: Gender-specific insults
  - class_based: Economic status insults
  - occupation_based: Work/profession insults
"""

import json
import os
import random
from datetime import datetime

DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
    "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
    "Vellore", "Viluppuram", "Virudhunagar"
]

# Base offensive words with Tamil script and transliteration
# Each entry: (tamil, transliteration, english_meaning, severity, category)
BASE_OFFENSIVE = {
    "general_insult": [
        # MILD
        ("பைத்தியம்", "paithiyam", "mad person/crazy", "mild", "insult"),
        ("முட்டாள்", "muttaal", "fool/stupid", "mild", "insult"),
        ("கெழு", "kezu", "idiot", "mild", "insult"),
        ("அறிவுக்கெட்டவன்", "arivukketavan", "uneducated/ignorant", "mild", "insult"),
        ("திமிரி", "timiri", "arrogant fool", "mild", "insult"),
        ("பேதை", "bèthai", "foolish person", "mild", "insult"),
        ("சுடுகாட்டு பிணம்", "sudukaattu pinam", "corpse-like person", "mild", "insult"),
        ("புண்ணாக்கு", "punnakku", "worthless/useless", "mild", "insult"),
        ("வேஸ்டு", "vèstu", "waste fellow", "mild", "insult"),
        ("லூசு", "loosu", "crazy/mad", "mild", "insult"),
        ("படிப்பு கிடையாது", "padippu kidaiyadhu", "uneducated", "mild", "insult"),
        ("தரம் கெட்டவன்", "taram ketavan", "low-class person", "mild", "insult"),
        # MODERATE
        ("தேவுடியா", "dèvudiya", "worthless fellow", "moderate", "insult"),
        ("பொறுக்கி", "porukki", "rascal/scoundrel", "moderate", "insult"),
        ("சனியன்", "saniyan", "wretched person", "moderate", "insult"),
        ("கழுதை", "kazhudhai", "donkey/ass", "moderate", "insult"),
        ("சூத்திரன்", "soothiran", "low-caste (slur)", "moderate", "slur"),
        ("தொழுகை", "thozhukai", "disgraceful person", "moderate", "insult"),
        ("நாய்", "naai", "dog", "moderate", "animal_comparison"),
        ("தேவ்டியா", "dèvdiya", "prostitute-like", "moderate", "insult"),
        ("கொலைகாரன்", "kolaikaran", "murderer (casual)", "moderate", "insult"),
        ("துரோகி", "thuroki", "traitor", "moderate", "insult"),
        ("நாசக்காரன்", "naasakkaaran", "destroyer/scoundrel", "moderate", "insult"),
        # SEVERE
        ("சவ்வாத்தி", "savvaathi", "promiscuous person", "severe", "profanity"),
        ("ஒழுக்கமில்லாதவன்", "ozhukkamillaatavan", "immoral person", "severe", "profanity"),
        ("கேவலமானவன்", "kèvalamaanavan", "disgusting person", "severe", "profanity"),
        ("கருமி", "karumi", "stingy miser", "severe", "insult"),
    ],
    "sexual_vulgar": [
        # MILD
        ("ஆம்பள ஏமாத்தி", "aambala yemaathi", "womanizer", "mild", "profanity"),
        ("லைலா", "laila", "flirty person", "mild", "profanity"),
        ("கிஸ்மத்", "kismat", "lustful", "mild", "profanity"),
        # MODERATE
        ("விலைமகள்", "vilaimagal", "prostitute", "moderate", "profanity"),
        ("தேவிடியா", "dèvidiya", "slut", "moderate", "profanity"),
        ("புரொஸ்டிடியூட்", "prostitute", "prostitute (English)", "moderate", "profanity"),
        ("விபசாரி", "vipasaari", "adulterer", "moderate", "profanity"),
        ("சூ\u200cத்தி மவன்", "soothi mavan", "bastard", "moderate", "profanity"),
        ("சூ\u200cத்தி பொம்பள", "soothi bombala", "female bastard", "moderate", "profanity"),
        ("தேவ்டியா பொம்பள", "dèvdiya bombala", "slut (female)", "moderate", "profanity"),
        ("கஞ்சா", "ganja", "druggie", "moderate", "profanity"),
        # SEVERE
        ("ஒழுக்கம் இல்லாத பொம்பள", "ozhukkam illaada bombala", "immoral woman", "severe", "profanity"),
        ("சூ\u200cத்தி புண்ட", "soothi pundu", "vulgar female slur", "severe", "profanity"),
        ("விலைமாது", "vilaimaathu", "call girl", "severe", "profanity"),
    ],
    "extreme_vulgar": [
        # Core Tamil extreme profanity words
        ("புண்டை", "pundai", "cunt/vagina", "severe", "profanity"),
        ("புண்டா", "pundaa", "cunt (variant)", "severe", "profanity"),
        ("சுன்னி", "sunni", "dick/penis", "severe", "profanity"),
        ("சுன்னா", "sunnnaa", "dick (variant)", "severe", "profanity"),
        ("தேவிடியா", "dhevidiyaa", "prostitute/whore", "severe", "profanity"),
        ("தேவ்டியா", "dhevdiyaa", "whore (variant)", "severe", "profanity"),
        ("தேவிடியா பைய", "dhevidiyaa paiya", "son of a whore", "severe", "profanity"),
        ("தேவிடியா புண்ட", "dhevidiyaa pund", "whore cunt", "severe", "profanity"),
        ("நாயே", "naaye", "dog (abusive)", "severe", "profanity"),
        ("நாய்க்கு பிறந்தவன்", "naaikku piranthavan", "born of a dog", "severe", "profanity"),
        ("சூத்து", "soothu", "asshole/butt", "severe", "profanity"),
        ("சூத்து ஓல்", "soothu ol", "ass fuck", "severe", "profanity"),
        ("ஓல்", "ol", "fuck (slang)", "severe", "profanity"),
        ("ஓக்கிற", "ookkira", "fucking", "severe", "profanity"),
        ("ஓத்தா", "ootha", "fucked", "severe", "profanity"),
        ("கூதி", "koothi", "cunt/pussy", "severe", "profanity"),
        ("கூத்தி", "kooththi", "cunt (variant)", "severe", "profanity"),
        ("மயிரு", "mayiru", "pubic hair/fuck all", "severe", "profanity"),
        ("மயிற்று", "mayirru", "pubic hair (variant)", "severe", "profanity"),
        ("மயிர் புண்டை", "mayiru pundai", "hairy cunt", "severe", "profanity"),
        ("மயிருக்கு கூட லாயக்கு இல்ல", "mayirukku kooda laayakku illa", "not even worth a hair", "severe", "profanity"),
        ("புண்டை மவன்", "pundai mavan", "son of a cunt", "severe", "profanity"),
        ("புண்டை பொண்ணு", "pundai ponnu", "cunt girl", "severe", "profanity"),
        ("புண்டை குண்டி", "pundai kundi", "cunt ass", "severe", "profanity"),
        ("சுன்னி தொங்க", "sunni thonga", "dick hanging", "severe", "profanity"),
        ("சுன்னி தலை", "sunni thalai", "dickhead", "severe", "profanity"),
        ("சுன்னி சப்பு", "sunni sappu", "suck dick", "severe", "profanity"),
        ("சுன்னிய சப்புற", "sunniya sappura", "sucking dick", "severe", "profanity"),
        ("தேவிடியா புண்டை", "dhevidiyaa pundai", "whore cunt", "severe", "profanity"),
        ("தேவிடியா மகனே", "dhevidiyaa magane", "son of a whore", "severe", "profanity"),
        ("தேவிடியா பொண்ணு", "dhevidiyaa ponnu", "whore girl", "severe", "profanity"),
        ("பொம்பள புண்டை", "bombala pundai", "woman cunt", "severe", "profanity"),
        ("ஆம்பிள புண்டை", "aambila pundai", "man cunt (insult)", "severe", "profanity"),
        ("சூ\u200cத்தி புண்ட", "soothi pund", "bastard cunt", "severe", "profanity"),
        ("சூ\u200cத்தி மவன்", "soothi mavan", "bastard son", "severe", "profanity"),
        ("சூ\u200cத்தி பொண்ணு", "soothi ponnu", "bastard girl", "severe", "profanity"),
        ("ஒழுக்கமில்லாத புண்டை", "ozhukkam illaadha pundai", "immoral cunt", "severe", "profanity"),
        ("ஒழுக்கமில்லாத சுன்னி", "ozhukkam illaadha sunni", "immoral dick", "severe", "profanity"),
        ("காத்த புண்டை", "kaaththa pundai", "burnt cunt", "severe", "profanity"),
        ("கருக்கிய புண்டை", "karukkiya pundai", "dried cunt", "severe", "profanity"),
        ("சுருக்கம் புண்டை", "surukkam pundai", "wrinkled cunt", "severe", "profanity"),
        ("தொங்கும் சுன்னி", "thonggum sunni", "hanging dick", "severe", "profanity"),
        ("சிறு\u200cத்தி சுன்னி", "siruththi sunni", "small dick", "severe", "profanity"),
        ("பெரிய சுன்னி", "periya sunni", "big dick", "severe", "profanity"),
        ("புண்டை மூடி", "pundai moodi", "cunt cover", "severe", "profanity"),
        ("சுன்னி மூடி", "sunni moodi", "dick cover", "severe", "profanity"),
        ("தேவிடியா ஓல்", "dhevidiyaa ol", "whore fuck", "severe", "profanity"),
        ("தேவிடியா ஓக்கிற", "dhevidiyaa ookkira", "whore fucking", "severe", "profanity"),
        ("புண்டை ஓக்கிற", "pundai ookkira", "cunt fucking", "severe", "profanity"),
        ("சுன்னி ஓக்கிற", "sunni ookkira", "dick fucking", "severe", "profanity"),
        ("நாய் புண்டை", "naai pundai", "dog cunt", "severe", "profanity"),
        ("நாய் சுன்னி", "naai sunni", "dog dick", "severe", "profanity"),
        ("பன்றி புண்டை", "panri pundai", "pig cunt", "severe", "profanity"),
        ("பன்றி சுன்னி", "panri sunni", "pig dick", "severe", "profanity"),
        ("கழுதை புண்டை", "kazhudhai pundai", "donkey cunt", "severe", "profanity"),
        ("கழுதை சுன்னி", "kazhudhai sunni", "donkey dick", "severe", "profanity"),
        ("ஏமாத்தி புண்டை", "yemaathi pundai", "cheating cunt", "severe", "profanity"),
        ("ஏமாத்தி சுன்னி", "yemaathi sunni", "cheating dick", "severe", "profanity"),
        ("விபசாரி புண்டை", "vipasaari pundai", "adulterer cunt", "severe", "profanity"),
        ("விபசாரி சுன்னி", "vipasaari sunni", "adulterer dick", "severe", "profanity"),
        ("கொலை புண்டை", "kolai pundai", "murder cunt", "severe", "profanity"),
        ("கொலை சுன்னி", "kolai sunni", "murder dick", "severe", "profanity"),
        ("கொள்ளை புண்டை", "kollai pundai", "thief cunt", "severe", "profanity"),
        ("கொள்ளை சுன்னி", "kollai sunni", "thief dick", "severe", "profanity"),
        ("கள்ள புண்டை", "kalla pundai", "illicit cunt", "severe", "profanity"),
        ("கள்ள சுன்னி", "kalla sunni", "illicit dick", "severe", "profanity"),
        ("சப்புற புண்டை", "sappura pundai", "sucking cunt", "severe", "profanity"),
        ("சப்புற சுன்னி", "sappura sunni", "sucking dick", "severe", "profanity"),
        ("கஞ்சா புண்டை", "ganja pundai", "druggie cunt", "severe", "profanity"),
        ("கஞ்சா சுன்னி", "ganja sunni", "druggie dick", "severe", "profanity"),
        ("சாராய புண்டை", "saaraaya pundai", "alcoholic cunt", "severe", "profanity"),
        ("சாராய சுன்னி", "saaraaya sunni", "alcoholic dick", "severe", "profanity"),
        ("துரோகி புண்டை", "thuroki pundai", "traitor cunt", "severe", "profanity"),
        ("துரோகி சுன்னி", "thuroki sunni", "traitor dick", "severe", "profanity"),
        ("நாச புண்டை", "naasa pundai", "destructive cunt", "severe", "profanity"),
        ("நாச சுன்னி", "naasa sunni", "destructive dick", "severe", "profanity"),
        ("கருமி புண்டை", "karumi pundai", "miser cunt", "severe", "profanity"),
        ("கருமி சுன்னி", "karumi sunni", "miser dick", "severe", "profanity"),
        ("பொறுக்கி புண்டை", "porukki pundai", "rascal cunt", "severe", "profanity"),
        ("பொறுக்கி சுன்னி", "porukki sunni", "rascal dick", "severe", "profanity"),
        ("சனியன் புண்டை", "saniyan pundai", "wretched cunt", "severe", "profanity"),
        ("சனியன் சுன்னி", "saniyan sunni", "wretched dick", "severe", "profanity"),
        ("முட்டாள் புண்டை", "muttaal pundai", "fool cunt", "severe", "profanity"),
        ("முட்டாள் சுன்னி", "muttaal sunni", "fool dick", "severe", "profanity"),
        ("லூசு புண்டை", "loosu pundai", "crazy cunt", "severe", "profanity"),
        ("லூசு சுன்னி", "loosu sunni", "crazy dick", "severe", "profanity"),
        ("கெழு புண்டை", "kezu pundai", "idiot cunt", "severe", "profanity"),
        ("கெழு சுன்னி", "kezu sunni", "idiot dick", "severe", "profanity"),
        ("வேஸ்டு புண்டை", "vèstu pundai", "waste cunt", "severe", "profanity"),
        ("வேஸ்டு சுன்னி", "vèstu sunni", "waste dick", "severe", "profanity"),
        ("ஏழை புண்டை", "èlazhai pundai", "poor cunt", "severe", "profanity"),
        ("ஏழை சுன்னி", "èlazhai sunni", "poor dick", "severe", "profanity"),
        ("கஞ்சி புண்டை", "kanji pundai", "gruel cunt", "severe", "profanity"),
        ("கஞ்சி சுன்னி", "kanji sunni", "gruel dick", "severe", "profanity"),
        ("கொடுப்பான் புண்டை", "koduppaan pundai", "giver cunt", "severe", "profanity"),
        ("கொடுப்பான் சுன்னி", "koduppaan sunni", "giver dick", "severe", "profanity"),
        ("கத்துற புண்டை", "kaththura pundai", "screaming cunt", "severe", "profanity"),
        ("கத்துற சுன்னி", "kaththura sunni", "screaming dick", "severe", "profanity"),
        ("அழுற புண்டை", "azhura pundai", "crying cunt", "severe", "profanity"),
        ("அழுற சுன்னி", "azhura sunni", "crying dick", "severe", "profanity"),
        ("சிரிக்குற புண்டை", "sirikkura pundai", "laughing cunt", "severe", "profanity"),
        ("சிரிக்குற சுன்னி", "sirikkura sunni", "laughing dick", "severe", "profanity"),
        ("நிக்குற புண்டை", "nikkura pundai", "standing cunt", "severe", "profanity"),
        ("நிக்குற சுன்னி", "nikkura sunni", "standing dick", "severe", "profanity"),
        ("உட்கார புண்டை", "udkaara pundai", "sitting cunt", "severe", "profanity"),
        ("உட்கார சுன்னி", "udkaara sunni", "sitting dick", "severe", "profanity"),
        ("படுக்க புண்டை", "padukka pundai", "sleeping cunt", "severe", "profanity"),
        ("படுக்க சுன்னி", "padukka sunni", "sleeping dick", "severe", "profanity"),
        ("ஓடுற புண்டை", "odura pundai", "running cunt", "severe", "profanity"),
        ("ஓடுற சுன்னி", "odura sunni", "running dick", "severe", "profanity"),
        ("நடக்குற புண்டை", "nadakkura pundai", "walking cunt", "severe", "profanity"),
        ("நடக்குற சுன்னி", "nadakkura sunni", "walking dick", "severe", "profanity"),
        ("தின்னுற புண்டை", "thinura pundai", "eating cunt", "severe", "profanity"),
        ("தின்னுற சுன்னி", "thinura sunni", "eating dick", "severe", "profanity"),
        ("குடிக்குற புண்டை", "kudikkura pundai", "drinking cunt", "severe", "profanity"),
        ("குடிக்குற சுன்னி", "kudikkura sunni", "drinking dick", "severe", "profanity"),
        ("பேசுற புண்டை", "pèsura pundai", "talking cunt", "severe", "profanity"),
        ("பேசுற சுன்னி", "pèsura sunni", "talking dick", "severe", "profanity"),
        ("கேக்குற புண்டை", "kèkkura pundai", "listening cunt", "severe", "profanity"),
        ("கேக்குற சுன்னி", "kèkkura sunni", "listening dick", "severe", "profanity"),
        ("பாக்குற புண்டை", "paakkura pundai", "watching cunt", "severe", "profanity"),
        ("பாக்குற சுன்னி", "paakkura sunni", "watching dick", "severe", "profanity"),
        ("தொடுற புண்டை", "thodura pundai", "touching cunt", "severe", "profanity"),
        ("தொடுற சுன்னி", "thodura sunni", "touching dick", "severe", "profanity"),
        ("முகந்த புண்டை", "mugandha pundai", "smelling cunt", "severe", "profanity"),
        ("முகந்த சுன்னி", "mugandha sunni", "smelling dick", "severe", "profanity"),
        ("சுவாசிக்குற புண்டை", "suvaa sikura pundai", "breathing cunt", "severe", "profanity"),
        ("சுவாசிக்குற சுன்னி", "suvaa sikura sunni", "breathing dick", "severe", "profanity"),
        ("வாழுற புண்டை", "vaazhura pundai", "living cunt", "severe", "profanity"),
        ("வாழுற சுன்னி", "vaazhura sunni", "living dick", "severe", "profanity"),
        ("செத்த புண்டை", "sèththa pundai", "dead cunt", "severe", "profanity"),
        ("செத்த சுன்னி", "sèththa sunni", "dead dick", "severe", "profanity"),
        ("பிறந்த புண்டை", "pirandha pundai", "born cunt", "severe", "profanity"),
        ("பிறந்த சுன்னி", "pirandha sunni", "born dick", "severe", "profanity"),
        ("வளர்ந்த புண்டை", "valarntha pundai", "grown cunt", "severe", "profanity"),
        ("வளர்ந்த சுன்னி", "valarntha sunni", "grown dick", "severe", "profanity"),
        ("முதிர்ந்த புண்டை", "muthirntha pundai", "matured cunt", "severe", "profanity"),
        ("முதிர்ந்த சுன்னி", "muthirntha sunni", "matured dick", "severe", "profanity"),
        ("கெட்ட புண்டை", "kèttha pundai", "spoiled cunt", "severe", "profanity"),
        ("கெட்ட சுன்னி", "kèttha sunni", "spoiled dick", "severe", "profanity"),
        ("சீரழிஞ்ச புண்டை", "seerazhinja pundai", "destroyed cunt", "severe", "profanity"),
        ("சீரழிஞ்ச சுன்னி", "seerazhinja sunni", "destroyed dick", "severe", "profanity"),
        ("முறிஞ்ச புண்டை", "murinja pundai", "broken cunt", "severe", "profanity"),
        ("முறிஞ்ச சுன்னி", "murinja sunni", "broken dick", "severe", "profanity"),
        ("உடைஞ்ச புண்டை", "udainja pundai", "smashed cunt", "severe", "profanity"),
        ("உடைஞ்ச சுன்னி", "udainja sunni", "smashed dick", "severe", "profanity"),
        ("நொறுங்குன புண்டை", "norungguna pundai", "crumbled cunt", "severe", "profanity"),
        ("நொறுங்குன சுன்னி", "norungguna sunni", "crumbled dick", "severe", "profanity"),
        ("காய்ஞ்ச புண்டை", "kaayinja pundai", "dried cunt", "severe", "profanity"),
        ("காய்ஞ்ச சுன்னி", "kaayinja sunni", "dried dick", "severe", "profanity"),
        ("சுண்ணி", "sunni", "dick (colloquial)", "severe", "profanity"),
        ("சுண்ணாம்பு", "sunnaambu", "lime (dick reference)", "severe", "profanity"),
        ("கொடு", "kodu", "give (sexual connotation)", "severe", "profanity"),
        ("கொடுக்கிற", "kodukkira", "giving (sexual)", "severe", "profanity"),
        ("வாங்குற", "vaanggura", "taking (sexual)", "severe", "profanity"),
        ("வாங்கு", "vaanggu", "take (sexual)", "severe", "profanity"),
        ("போடுற", "podura", "putting (sexual)", "severe", "profanity"),
        ("போடு", "podu", "put (sexual)", "severe", "profanity"),
        ("தள்ளுற", "thallura", "pushing (sexual)", "severe", "profanity"),
        ("தள்ளு", "thallu", "push (sexual)", "severe", "profanity"),
        ("இழுக்குற", "izhukura", "pulling (sexual)", "severe", "profanity"),
        ("இழு", "izhu", "pull (sexual)", "severe", "profanity"),
        ("திருப்புற", "thiruppura", "turning (sexual)", "severe", "profanity"),
        ("திருப்பு", "thiruppu", "turn (sexual)", "severe", "profanity"),
        ("சுத்துற", "suththura", "circling (sexual)", "severe", "profanity"),
        ("சுத்து", "suththu", "circle (sexual)", "severe", "profanity"),
        ("குத்துற", "kuththura", "stabbing (sexual)", "severe", "profanity"),
        ("குத்து", "kuththu", "stab (sexual)", "severe", "profanity"),
        ("அடிக்குற", "adikkura", "hitting (sexual)", "severe", "profanity"),
        ("அடி", "adi", "hit (sexual)", "severe", "profanity"),
        ("தாக்குற", "thaakkura", "attacking (sexual)", "severe", "profanity"),
        ("தாக்கு", "thaakku", "attack (sexual)", "severe", "profanity"),
        ("செய்யுற", "seyyura", "doing (sexual)", "severe", "profanity"),
        ("செய்", "sey", "do (sexual)", "severe", "profanity"),
        ("பண்ணுற", "pannura", "doing (sexual)", "severe", "profanity"),
        ("பண்ணு", "pannu", "do (sexual)", "severe", "profanity"),
    ],
    "family_insult": [
        # MILD
        ("உன் அம்மா", "un amma", "your mother (mild)", "mild", "family_insult"),
        ("உன் அப்பா", "un appa", "your father (mild)", "mild", "family_insult"),
        ("உன் வீட்டுக்காரி", "un veettukaari", "your wife (mild)", "mild", "family_insult"),
        # MODERATE
        ("உன் அம்மா பொண்ணு", "un amma ponnu", "your mother's daughter", "moderate", "family_insult"),
        ("உன் அப்பா மவன்", "un appa mavan", "your father's son", "moderate", "family_insult"),
        ("உன் தாயை", "un thaayai", "your mother (vulgar)", "moderate", "family_insult"),
        ("உன் பொண்ணு", "un ponnu", "your daughter (implied vulgar)", "moderate", "family_insult"),
        ("உன் சகோதரி", "un sahodari", "your sister (vulgar context)", "moderate", "family_insult"),
        # SEVERE
        ("உன் அம்மாவை கூத்த", "un ammaavai kooththa", "your mother (explicit)", "severe", "family_insult"),
        ("உன் அப்பாவை கூத்த", "un appaavai kooththa", "your father (explicit)", "severe", "family_insult"),
        ("உன் அம்மா புண்டை", "un amma pundai", "your mother's cunt", "severe", "family_insult"),
        ("உன் அப்பா சுன்னி", "un appa sunni", "your father's dick", "severe", "family_insult"),
        ("உன் அம்மா தேவிடியா", "un amma dhevidiyaa", "your mother is a whore", "severe", "family_insult"),
        ("உன் அப்பா புண்டை மவன்", "un appa pundai mavan", "your father's cunt son", "severe", "family_insult"),
        ("உன் சகோதரி புண்டை", "un sahodari pundai", "your sister's cunt", "severe", "family_insult"),
        ("உன் சகோதரி தேவிடியா", "un sahodari dhevidiyaa", "your sister is a whore", "severe", "family_insult"),
        ("உன் பொண்ணு புண்டை", "un ponnu pundai", "your daughter's cunt", "severe", "family_insult"),
        ("உன் பொண்ணு தேவிடியா", "un ponnu dhevidiyaa", "your daughter is a whore", "severe", "family_insult"),
        ("உன் வீட்டுக்காரி புண்டை", "un veettukaari pundai", "your wife's cunt", "severe", "family_insult"),
        ("உன் வீட்டுக்காரி தேவிடியா", "un veettukaari dhevidiyaa", "your wife is a whore", "severe", "family_insult"),
        ("உன் அம்மா சூத்து", "un amma soothu", "your mother's ass", "severe", "family_insult"),
        ("உன் அப்பா சூத்து", "un appa soothu", "your father's ass", "severe", "family_insult"),
        ("உன் அம்மா கூதி", "un amma koothi", "your mother's pussy", "severe", "family_insult"),
        ("உன் அப்பா கூதி", "un appa koothi", "your father's pussy", "severe", "family_insult"),
        ("உன் அம்மா ஓல்", "un amma ol", "your mother fuck", "severe", "family_insult"),
        ("உன் அப்பா ஓல்", "un appa ol", "your father fuck", "severe", "family_insult"),
        ("உன் அம்மா மயிரு", "un amma mayiru", "your mother's pubic hair", "severe", "family_insult"),
        ("உன் அப்பா மயிரு", "un appa mayiru", "your father's pubic hair", "severe", "family_insult"),
    ],
    "body_shaming": [
        # MILD
        ("கருப்பன்", "karuppan", "dark one", "mild", "body_shaming"),
        ("குள்ளன்", "kullan", "short person", "mild", "body_shaming"),
        ("உடம்பு சுத்தம் இல்ல", "udambu suttam illa", "unclean body", "mild", "body_shaming"),
        ("மூஞ்சி கெட்டவன்", "moonji ketavan", "ugly-faced", "mild", "body_shaming"),
        # MODERATE
        ("தடிமன்", "thadiman", "fat person", "moderate", "body_shaming"),
        ("ஒல்லி", "olli", "skinny person", "moderate", "body_shaming"),
        ("மூஞ்சி கிழி", "moonji kizhi", "torn face/ugly", "moderate", "body_shaming"),
        ("கண்ணாடி மூஞ்சி", "kannadi moonji", "glass face (ugly)", "moderate", "body_shaming"),
        ("உடம்பு இல்லாதவன்", "udambu illaavan", "body-less (very thin)", "moderate", "body_shaming"),
    ],
    "caste_slur": [
        # MILD (still offensive but less extreme)
        ("சூத்திரன்", "soothiran", "low caste (caste slur)", "mild", "slur"),
        ("பஞ்சமன்", "panchaman", "fifth caste (untouchable)", "mild", "slur"),
        ("தேவர் மகன்", "dèvar magan", "caste-based insult", "mild", "slur"),
        ("முதலியார் மகன்", "muthaliyaar magan", "caste insult", "mild", "slur"),
        # MODERATE
        ("நாயுடு", "naayudu", "caste slur (Yadav)", "moderate", "slur"),
        ("சக்கிலி", "sakkili", "untouchable (slur)", "moderate", "slur"),
        ("பள்ளன்", "pollan", "Pallar caste slur", "moderate", "slur"),
        ("நாடார்", "naadar", "caste slur (Nadar)", "moderate", "slur"),
        ("தேவர்", "dèvar", "caste slur (Thevar)", "moderate", "slur"),
        ("கவுண்டன்", "gavundan", "caste slur (Gounder)", "moderate", "slur"),
        ("முதலியார்", "muthaliyaar", "caste slur (Mudaliar)", "moderate", "slur"),
        ("நாயக்கர்", "naayakkar", "caste slur (Nair)", "moderate", "slur"),
        ("செட்டியார்", "chettiyaar", "caste slur (Chettiar)", "moderate", "slur"),
        ("கிருஷ்ணன் மகன்", "krishnan magan", "caste slur (Iyengar)", "moderate", "slur"),
    ],
    "animal_comparison": [
        # MILD
        ("நாய் மாதிரி", "naai maathiri", "like a dog", "mild", "animal_comparison"),
        ("பன்றி மாதிரி", "panri maathiri", "like a pig", "mild", "animal_comparison"),
        ("எலி மாதிரி", "eli maathiri", "like a rat", "mild", "animal_comparison"),
        ("பூனை மாதிரி", "poonai maathiri", "like a cat", "mild", "animal_comparison"),
        ("கழுதை மாதிரி", "kazhudhai maathiri", "like a donkey", "mild", "animal_comparison"),
        # MODERATE
        ("நாய் குட்டி", "naai kutti", "puppy (insult)", "moderate", "animal_comparison"),
        ("பன்றி மவன்", "panri mavan", "pig's son", "moderate", "animal_comparison"),
        ("கோழி", "kozhi", "chicken/coward", "moderate", "animal_comparison"),
        ("முயல்", "muyal", "rabbit (coward)", "moderate", "animal_comparison"),
        ("பாம்பு", "paambu", "snake (treacherous)", "moderate", "animal_comparison"),
        ("தேள்", "thèl", "scorpion (venomous)", "moderate", "animal_comparison"),
        ("நரி", "nari", "fox (cunning)", "moderate", "animal_comparison"),
        ("சிங்கம் மாதிரி நட", "singam maathiri nada", "walk like a lion (sarcastic)", "moderate", "animal_comparison"),
    ],
    "death_wish": [
        # MILD
        ("சாக மாட்டியா", "saaga maattiya", "won't you die?", "mild", "death_wish"),
        ("செத்துப் போ", "sèththu po", "go die", "mild", "death_wish"),
        # MODERATE
        ("உன் கதை முடிஞ்சது", "un kadhai mudinjathu", "your story is over", "moderate", "death_wish"),
        ("சுடுகாட்டுக்கு போ", "sudukaattukku po", "go to the cremation ground", "moderate", "death_wish"),
        ("மண்ணாந்தலை", "mannanthalai", "buried head (dead)", "moderate", "death_wish"),
    ],
    "gender_based": [
        # MILD
        ("பொம்பள வேலை", "bombala vèlai", "woman's job (derogatory)", "mild", "gender_based"),
        ("ஆம்பள மாதிரி நட", "aambala maathiri nada", "act like a man", "mild", "gender_based"),
        # MODERATE
        ("பொம்பளைய மதிக்க மாட்டான்", "bombalaiya mathikka maattaan", "doesn't respect women", "moderate", "gender_based"),
        ("சின்ன பொண்ணு", "chinn ponnu", "little girl (patronizing)", "moderate", "gender_based"),
        ("கல்யாணம் ஆகாதவன்", "kalyaanam aakaadavan", "unmarried person (insult)", "moderate", "gender_based"),
    ],
    "class_based": [
        # MILD
        ("ஏழை", "èlazhai", "poor person", "mild", "class_based"),
        ("வறுமை", "varumai", "poverty (used as insult)", "mild", "class_based"),
        ("கஞ்சி குடிக்கிறவன்", "kanji kudikkiravan", "gruel drinker (poor)", "mild", "class_based"),
        # MODERATE
        ("கூட்டுக்கு வராதவன்", "koottukku varaadavan", "doesn't fit in society", "moderate", "class_based"),
        ("தரம் இல்லாதவன்", "taram illaavan", "classless person", "moderate", "class_based"),
    ],
    "occupation_based": [
        # MILD
        ("தோட்ட வேலைக்காரன்", "thotta vèlaikkaaran", "garden worker (insult)", "mild", "occupation_based"),
        ("பஸ் டிரைவர்", "bus driver", "bus driver (insult)", "mild", "occupation_based"),
        ("கடைக்காரன்", "kadaikkaaran", "shopkeeper (insult)", "mild", "occupation_based"),
        # MODERATE
        ("சலவைத் தொழிலாளி", "salavai thozhilali", "washerman (caste slur)", "moderate", "occupation_based"),
        ("தேயிலைத் தோட்டக்காரன்", "thèyilai thottakkaaran", "tea estate worker (insult)", "moderate", "occupation_based"),
        ("விவசாயி", "vivasaayi", "farmer (when used as insult)", "moderate", "occupation_based"),
    ],
    "emotional_abuse": [
        # MILD
        ("உனக்கு ஒன்னும் தெரியாது", "unakku onnum theriyaadhu", "you know nothing", "mild", "insult"),
        ("படிச்சவன் மாதிரி நடி", "padichavan maathiri nadi", "act educated (sarcastic)", "mild", "insult"),
        ("உன்னால முடியாது", "unnala mudiyaadhu", "you can't do it", "mild", "insult"),
        # MODERATE
        ("உனக்கு மரியாதை கிடையாது", "unakku mariyaadhai kidaiyaadhu", "you have no respect", "moderate", "insult"),
        ("உன் பேச்சு கேக்க மாட்டேன்", "un pèchchu kèkka maatten", "won't listen to you", "moderate", "insult"),
    ],
    "random_abusive": [
        # MILD
        ("கோப்பு", "koppu", "anger person", "mild", "insult"),
        ("திமிர்", "timir", "arrogance", "mild", "insult"),
        ("அகம்படம்", "agambadham", "ego", "mild", "insult"),
        ("மதி கெட்டவன்", "mathi ketavan", "lost mind person", "mild", "insult"),
        ("புத்தி இல்லாதவன்", "putthi illaavan", "without sense", "mild", "insult"),
        ("திறமை இல்லாதவன்", "thiramai illaavan", "without talent", "mild", "insult"),
        ("சுரணை இல்லாதவன்", "suranai illaavan", "without conscience", "mild", "insult"),
        ("மனசாட்சி இல்லாதவன்", "manasaatchi illaavan", "without conscience", "mild", "insult"),
        ("கொள்ளையன்", "kollaiyan", "robber", "mild", "insult"),
        ("கள்ளன்", "kallan", "thief", "mild", "insult"),
        ("ஏமாற்றுக்காரன்", "yemaatrukkaaran", "cheater", "mild", "insult"),
        ("தகாதவன்", "thakaadhavan", "inappropriate person", "mild", "insult"),
        ("கீழ்த்தரமானவன்", "keezhtharamaanavan", "low-class person", "mild", "insult"),
        ("தாழ்ந்தவன்", "thaazhnthavan", "humbled/lowly", "mild", "insult"),
        ("ஏழைப்பாடு", "èlazhaippaadu", "poverty struggle", "mild", "insult"),
        ("கஞ்சக்காரன்", "kanjakkaaran", "miser", "mild", "insult"),
        ("கஞ்சி", "kanji", "gruel/miser", "mild", "insult"),
        ("வெள்ளைக்காரன்", "vellaikkaaran", "white person (insult context)", "mild", "insult"),
        ("கருப்பு", "karuppu", "black (insult context)", "mild", "insult"),
        ("சிவப்பு", "sivappu", "red (insult context)", "mild", "insult"),
        # MODERATE
        ("நாசம் பண்ணுற", "naasam panrura", "destroying", "moderate", "insult"),
        ("கெடுக்கிற", "kèdukkira", "ruining", "moderate", "insult"),
        ("சீரழிக்கிற", "seerazhikkira", "destroying completely", "moderate", "insult"),
        ("கொலை பண்ணுற", "kolaai panrura", "killing (casual)", "moderate", "insult"),
        ("கொல்லுற", "kollurura", "killing", "moderate", "insult"),
        ("அடிச்சு தள்ளுற", "adichu thallurura", "beating up", "moderate", "insult"),
        ("கத்தி காட்டுற", "kaththi kaatturura", "showing knife", "moderate", "insult"),
        ("கொடுஞ்செயல்", "kodunjeyal", "cruel act", "moderate", "insult"),
        ("கொடூரம்", "koodoorem", "cruelty", "moderate", "insult"),
        ("பாவம்", "paavam", "sin (when used as insult)", "moderate", "insult"),
        ("குற்றம்", "kutram", "fault (when used as insult)", "moderate", "insult"),
        ("தப்பு", "thappu", "wrong (when used as insult)", "moderate", "insult"),
        # SEVERE
        ("மிருகம்", "mirugam", "animal/beast", "severe", "insult"),
        ("மிருகத்தனம்", "mirugaththanam", "animalistic behavior", "severe", "insult"),
        ("காட்டுமிராண்டி", "kaattumirandi", "savage", "severe", "insult"),
        ("மிரண்டவன்", "mirandhavan", "frightened person", "severe", "insult"),
        ("கொடியவன்", "kodiyavan", "cruel person", "severe", "insult"),
        ("கொலைகாரன்", "kolaikaran", "murderer", "severe", "insult"),
        ("கொலைவெறி", "kolaiveri", "murderous rage", "severe", "insult"),
        ("பயங்கரவாதி", "bayangara vaadhi", "terrorist", "severe", "insult"),
        ("வன்முறை", "vanmurai", "violence", "severe", "insult"),
    ],
}

# Regional/Tanglish variants by dialect
DIALECT_VARIANTS = {
    "Northern_TamilNadu": {
        "region": "Chennai, Tiruvallur, Kancheepuram, Chengalpattu, Ranipet, Vellore",
        "districts": ["Chennai", "Tiruvallur", "Kancheepuram", "Chengalpattu", "Ranipet", "Vellore"],
        "tanglish_form": True,
        "dialect_note": "Chennai slang - heavy Tanglish influence",
        "variants": [
            ("poda", "go away/fellow", "mild", "insult"),
            ("podi", "girl (casual/insult)", "mild", "insult"),
            ("dei", "hey (aggressive)", "mild", "insult"),
            ("macha", "brother-in-law (casual)", "mild", "insult"),
            ("machan", "brother-in-law (aggressive)", "mild", "insult"),
            ("en da", "what fellow", "mild", "insult"),
            ("edhuku da", "why fellow", "mild", "insult"),
            ("enna da", "what fellow (aggressive)", "mild", "insult"),
            ("semma", "awesome (can be sarcastic)", "mild", "insult"),
            ("vera level", "another level (sarcastic)", "mild", "insult"),
            ("mokkai", "boring/flat joke", "mild", "insult"),
            ("mokka podu", "crack a flat joke", "mild", "insult"),
            ("chaplin", "chaplin (old man insult)", "mild", "insult"),
            ("yenda", "why fellow", "mild", "insult"),
            ("bayangaram", "terrific (can be sarcastic)", "mild", "insult"),
            ("sarakku", "alcohol/drunkard", "moderate", "insult"),
            ("kazhuthu", "neck/thick-headed", "moderate", "insult"),
            ("kai vittutan", "left him (dumped)", "moderate", "insult"),
            ("kai laam vittutaan", "completely let go", "moderate", "insult"),
            ("thooku pidi", "catch hold (insult)", "moderate", "insult"),
            ("pottu vachukko", "keep it (dismissive)", "moderate", "insult"),
            ("thee galatta", "fire disturbance", "moderate", "insult"),
            ("gaffa", "fool/loafer", "moderate", "insult"),
            ("thala ivan", "this fellow", "moderate", "insult"),
            ("nambikkai illa", "no hope", "moderate", "insult"),
            ("time pass", "timepass/worthless", "moderate", "insult"),
            ("junk", "junk/worthless", "moderate", "insult"),
            ("loafer", "loafer (English)", "moderate", "insult"),
            ("rowdy", "rowdy (English)", "moderate", "insult"),
            ("gunda", "gunda (English)", "moderate", "insult"),
            ("vandha padam", "terrible movie/person", "moderate", "insult"),
            ("koothu padam", "circus/movie (insult)", "moderate", "insult"),
            ("komban", "horns (insult)", "moderate", "insult"),
            ("kombu", "horn", "moderate", "insult"),
            ("pombala", "woman (mildly derogatory)", "mild", "insult"),
            ("aambala", "man (patronizing)", "mild", "insult"),
            ("kuttai", "small/borrowed", "moderate", "insult"),
            ("vechuru", "fried (insult)", "moderate", "insult"),
            ("kalaila kotta", "throw in stone", "moderate", "insult"),
        ]
    },
    "Central_TamilNadu": {
        "region": "Thanjavur, Tiruchirappalli, Perambalur, Ariyalur, Karur, Tiruvarur, Nagapattinam, Mayiladuthurai, Pudukkottai",
        "districts": ["Thanjavur", "Tiruchirappalli", "Perambalur", "Ariyalur", "Karur", "Tiruvarur", "Nagapattinam", "Mayiladuthurai", "Pudukkottai"],
        "tanglish_form": True,
        "dialect_note": "Central Tamil - Thanjavur dialect influence",
        "variants": [
            ("da", "fellow (aggressive)", "mild", "insult"),
            ("ye", "hey (casual)", "mild", "insult"),
            ("maapillai", "son-in-law (insult)", "mild", "insult"),
            ("maami", "auntie (patronizing)", "mild", "insult"),
            ("maama", "uncle (patronizing)", "mild", "insult"),
            ("thambi", "younger brother (patronizing)", "mild", "insult"),
            ("anna", "elder brother (when used as insult)", "mild", "insult"),
            ("akka", "elder sister (when used as insult)", "mild", "insult"),
            ("thala", "head/leader (sarcastic)", "mild", "insult"),
            ("kalai", "art/stone (insult)", "mild", "insult"),
            ("vaayku", "mouth (insult)", "mild", "insult"),
            ("kombu", "horn (insult)", "moderate", "insult"),
            ("maadi", "first floor/proud", "moderate", "insult"),
            ("vaayil poosu", "lipstick (insult)", "moderate", "insult"),
            ("kaluvi", "mixed/impure", "moderate", "insult"),
            ("thirumbu", "turn around (insult)", "moderate", "insult"),
            ("satta", "saree (insult)", "moderate", "insult"),
            ("pombala da", "woman (aggressive)", "moderate", "insult"),
            ("aambala da", "man (aggressive)", "moderate", "insult"),
            ("kaalai", "morning/cow (insult)", "moderate", "insult"),
            ("saan", "hanging (insult)", "moderate", "insult"),
            ("poottu kattu", "tie up (insult)", "moderate", "insult"),
            ("ketti vaaya", "big mouth", "moderate", "insult"),
            ("kal keta", "ask the stone", "moderate", "insult"),
            ("moodi", "cover/fool", "moderate", "insult"),
            ("koodhi", "bundle/fool", "moderate", "insult"),
            ("pombala sothu", "woman treasure (insult)", "moderate", "insult"),
            ("maami sothu", "auntie treasure (insult)", "moderate", "insult"),
            ("thirumbu po", "go back (insult)", "moderate", "insult"),
        ]
    },
    "Western_TamilNadu": {
        "region": "Coimbatore, Salem, Erode, Namakkal, Krishnagiri, Dharmapuri, Tiruppur, Nilgiris, Dindigul, Tirupathur",
        "districts": ["Coimbatore", "Salem", "Erode", "Namakkal", "Krishnagiri", "Dharmapuri", "Tiruppur", "Nilgiris", "Dindigul", "Tirupathur"],
        "tanglish_form": True,
        "dialect_note": "Kongu Tamil - Western dialect influence",
        "variants": [
            ("da", "fellow (aggressive)", "mild", "insult"),
            ("ye", "hey (casual)", "mild", "insult"),
            ("maama", "uncle (patronizing)", "mild", "insult"),
            ("maami", "auntie (patronizing)", "mild", "insult"),
            ("maapillai", "son-in-law (insult)", "mild", "insult"),
            ("kombu", "horn (insult)", "mild", "insult"),
            ("komban", "horns (insult)", "mild", "insult"),
            ("kaluvi", "mixed/impure", "moderate", "insult"),
            ("kaluviya", "mixed person", "moderate", "insult"),
            ("thirumbu", "turn around (insult)", "moderate", "insult"),
            ("vaayku", "mouth (insult)", "moderate", "insult"),
            ("ketti vaaya", "big mouth", "moderate", "insult"),
            ("moodi", "cover/fool", "moderate", "insult"),
            ("koodhi", "bundle/fool", "moderate", "insult"),
            ("pombala da", "woman (aggressive)", "moderate", "insult"),
            ("aambala da", "man (aggressive)", "moderate", "insult"),
            ("kaalai", "morning/cow (insult)", "moderate", "insult"),
            ("saan", "hanging (insult)", "moderate", "insult"),
            ("poottu kattu", "tie up (insult)", "moderate", "insult"),
            ("kal keta", "ask the stone", "moderate", "insult"),
            ("mokkai podu", "crack flat joke", "mild", "insult"),
            ("time pass", "timepass/worthless", "moderate", "insult"),
            ("sarakku", "alcohol/drunkard", "moderate", "insult"),
            ("gaffa", "fool/loafer", "moderate", "insult"),
            ("kazhuthu", "neck/thick-headed", "moderate", "insult"),
            ("vandha padam", "terrible movie/person", "moderate", "insult"),
            ("koothu padam", "circus/movie (insult)", "moderate", "insult"),
        ]
    },
    "Southern_TamilNadu": {
        "region": "Madurai, Tirunelveli, Thoothukudi, Theni, Virudhunagar, Sivaganga, Ramanathapuram, Tenkasi, Kanyakumari",
        "districts": ["Madurai", "Tirunelveli", "Thoothukudi", "Theni", "Virudhunagar", "Sivaganga", "Ramanathapuram", "Tenkasi", "Kanyakumari"],
        "tanglish_form": True,
        "dialect_note": "Southern Tamil - Madurai/Nellai dialect influence",
        "variants": [
            ("da", "fellow (aggressive)", "mild", "insult"),
            ("ye", "hey (casual)", "mild", "insult"),
            ("maama", "uncle (patronizing)", "mild", "insult"),
            ("maami", "auntie (patronizing)", "mild", "insult"),
            ("maapillai", "son-in-law (insult)", "mild", "insult"),
            ("kombu", "horn (insult)", "mild", "insult"),
            ("komban", "horns (insult)", "mild", "insult"),
            ("thirumbu", "turn around (insult)", "moderate", "insult"),
            ("vaayku", "mouth (insult)", "moderate", "insult"),
            ("ketti vaaya", "big mouth", "moderate", "insult"),
            ("moodi", "cover/fool", "moderate", "insult"),
            ("koodhi", "bundle/fool", "moderate", "insult"),
            ("pombala da", "woman (aggressive)", "moderate", "insult"),
            ("aambala da", "man (aggressive)", "moderate", "insult"),
            ("kaalai", "morning/cow (insult)", "moderate", "insult"),
            ("saan", "hanging (insult)", "moderate", "insult"),
            ("poottu kattu", "tie up (insult)", "moderate", "insult"),
            ("kal keta", "ask the stone", "moderate", "insult"),
            ("mokkai podu", "crack flat joke", "mild", "insult"),
            ("time pass", "timepass/worthless", "moderate", "insult"),
            ("sarakku", "alcohol/drunkard", "moderate", "insult"),
            ("gaffa", "fool/loafer", "moderate", "insult"),
            ("kazhuthu", "neck/thick-headed", "moderate", "insult"),
            ("vandha padam", "terrible movie/person", "moderate", "insult"),
            ("koothu padam", "circus/movie (insult)", "moderate", "insult"),
            ("nambikai illa", "no hope", "moderate", "insult"),
            ("kaluvanga", "mixed (insult)", "moderate", "insult"),
            ("pombala sothu", "woman treasure (insult)", "moderate", "insult"),
            ("maami sothu", "auntie treasure (insult)", "moderate", "insult"),
        ]
    },
}

# Common Tanglish forms for all regions
TANGLISH_OFFENSIVE = [
    ("vesadi", "useless fellow", "mild", "insult"),
    ("loosu manda", "crazy head", "mild", "insult"),
    ("loosu payya", "crazy boy", "mild", "insult"),
    ("loosu ponnu", "crazy girl", "mild", "insult"),
    ("loosu mappilla", "crazy husband", "mild", "insult"),
    ("loosu mami", "crazy auntie", "mild", "insult"),
    ("loosu maama", "crazy uncle", "mild", "insult"),
    ("vesadi payya", "useless boy", "mild", "insult"),
    ("vesadi ponnu", "useless girl", "mild", "insult"),
    ("vesadi mappilla", "useless husband", "mild", "insult"),
    ("vesadi mami", "useless auntie", "mild", "insult"),
    ("vesadi maama", "useless uncle", "mild", "insult"),
    ("loosu mappillai", "crazy son-in-law", "mild", "insult"),
    ("vesadi mappillai", "useless son-in-law", "mild", "insult"),
    ("loosu thantha", "crazy grandfather", "mild", "insult"),
    ("vesadi thantha", "useless grandfather", "mild", "insult"),
    ("loosu paati", "crazy grandmother", "mild", "insult"),
    ("vesadi paati", "useless grandmother", "mild", "insult"),
    ("loosu kuttikku", "crazy child", "mild", "insult"),
    ("vesadi kuttikku", "useless child", "mild", "insult"),
    ("loosu ayya", "crazy sir", "mild", "insult"),
    ("vesadi ayya", "useless sir", "mild", "insult"),
    ("loosu akka", "crazy elder sister", "mild", "insult"),
    ("vesadi akka", "useless elder sister", "mild", "insult"),
    ("loosu anna", "crazy elder brother", "mild", "insult"),
    ("vesadi anna", "useless elder brother", "mild", "insult"),
    ("loosu thambi", "crazy younger brother", "mild", "insult"),
    ("vesadi thambi", "useless younger brother", "mild", "insult"),
    ("loosu thangai", "crazy younger sister", "mild", "insult"),
    ("vesadi thangai", "useless younger sister", "mild", "insult"),
    ("loosu peran", "crazy grandson", "mild", "insult"),
    ("vesadi peran", "useless grandson", "mild", "insult"),
    ("loosu peththi", "crazy granddaughter", "mild", "insult"),
    ("vesadi peththi", "useless granddaughter", "mild", "insult"),
    ("loosu mappillamaar", "crazy husbands", "mild", "insult"),
    ("vesadi mappillamaar", "useless husbands", "mild", "insult"),
    ("loosu maamilar", "crazy uncles", "mild", "insult"),
    ("vesadi maamilar", "useless uncles", "mild", "insult"),
    ("loosu mamiyar", "crazy aunties", "mild", "insult"),
    ("vesadi mamiyar", "useless aunties", "mild", "insult"),
    ("loosu kuttigal", "crazy children", "mild", "insult"),
    ("vesadi kuttigal", "useless children", "mild", "insult"),
    ("loosu ayyar", "crazy sirs", "mild", "insult"),
    ("vesadi ayyar", "useless sirs", "mild", "insult"),
    ("loosu akkaar", "crazy elder sisters", "mild", "insult"),
    ("vesadi akkaar", "useless elder sisters", "mild", "insult"),
    ("loosu annaarParams", "crazy elder brothers", "mild", "insult"),
    ("vesadi annaarParams", "useless elder brothers", "mild", "insult"),
    ("loosu thambaarParams", "crazy younger brothers", "mild", "insult"),
    ("vesadi thambaarParams", "useless younger brothers", "mild", "insult"),
    ("loosu thangaikals", "crazy younger sisters", "mild", "insult"),
    ("vesadi thangaikals", "useless younger sisters", "mild", "insult"),
    ("loosu peranakkals", "crazy grandsons", "mild", "insult"),
    ("vesadi peranakkals", "useless grandsons", "mild", "insult"),
    ("loosu peththaikals", "crazy granddaughters", "mild", "insult"),
    ("vesadi peththaikals", "useless granddaughters", "mild", "insult"),
]

# Example sentences for context
EXAMPLE_SENTENCES = [
    "அவன் ஒரு முட்டாள்",
    "நீ ஒரு லூசு",
    "போடா போடி",
    "உனக்கு ஒன்னும் தெரியாது",
    "நீ ஒரு நாய்",
    "செத்துப் போ",
    "உன் அம்மா",
    "நீ ஒரு பைத்தியம்",
    "வேஸ்டு பேர்",
    "சனியன்",
    "பொறுக்கி",
    "தேவுடியா",
    "கழுதை",
    "நாசக்காரன்",
    "துரோகி",
    "புண்ணாக்கு",
    "லூசு மாதிரி நட",
    "முட்டாள் மாதிரி பேசாத",
    "உனக்கு புத்தி இல்ல",
    "நீ ஒரு கெழு",
    "வேஸ்டு பேர்",
    "சுடுகாட்டு பிணம்",
    "திமிரி",
    "பேதை",
    "நாய் மாதிரி நட",
    "பன்றி மாதிரி சாப்பிடு",
    "கோழி மாதிரி பயப்படாத",
    "பாம்பு மாதிரி கடிக்காத",
    "நரி மாதிரி ஏமாத்தாத",
    "தேள் மாதிரி கொட்டாத",
    "முயல் மாதிரி ஓடாத",
]

def get_district_region(district):
    """Determine which dialect region a district belongs to."""
    for region_name, region_data in DIALECT_VARIANTS.items():
        if district in region_data["districts"]:
            return region_name, region_data
    return None, None

def generate_offensive_dataset():
    """Generate the full offensive slang dataset."""
    
    all_entries = []
    district_stats = {}
    
    for district in DISTRICTS:
        district_entries = []
        region_name, region_data = get_district_region(district)
        
        # Add base offensive words
        for category_name, words in BASE_OFFENSIVE.items():
            for tamil, translit, english, severity, cat in words:
                # Add some randomness - not all words appear in all districts
                if random.random() < 0.7:  # 70% chance of inclusion
                    entry = {
                        "tamil": tamil,
                        "transliteration": translit,
                        "english": english,
                        "severity": severity,
                        "category": cat,
                        "district": district,
                        "region": region_name or "Unknown",
                        "source": "base_offensive",
                        "dialect_note": region_data["dialect_note"] if region_data else ""
                    }
                    district_entries.append(entry)
        
        # Add regional variants
        if region_data and region_name:
            for tamil, english, severity, cat in region_data["variants"]:
                entry = {
                    "tamil": tamil,
                    "transliteration": tamil,
                    "english": english,
                    "severity": severity,
                    "category": cat,
                    "district": district,
                    "region": region_name,
                    "source": "regional_variant",
                    "dialect_note": region_data["dialect_note"]
                }
                district_entries.append(entry)
        
        # Add Tanglish forms
        for tamil, english, severity, cat in TANGLISH_OFFENSIVE:
            if random.random() < 0.6:  # 60% chance
                entry = {
                    "tamil": tamil,
                    "transliteration": tamil,
                    "english": english,
                    "severity": severity,
                    "category": cat,
                    "district": district,
                    "region": region_name or "Unknown",
                    "source": "tanglish_offensive",
                    "dialect_note": region_data["dialect_note"] if region_data else ""
                }
                district_entries.append(entry)
        
        # Add example sentences
        for sentence in EXAMPLE_SENTENCES:
            if random.random() < 0.3:  # 30% chance
                entry = {
                    "tamil": sentence,
                    "transliteration": sentence,
                    "english": "example offensive sentence",
                    "severity": "moderate",
                    "category": "example_sentence",
                    "district": district,
                    "region": region_name or "Unknown",
                    "source": "example_sentence",
                    "dialect_note": region_data["dialect_note"] if region_data else ""
                }
                district_entries.append(entry)
        
        # Remove duplicates
        seen = set()
        unique_entries = []
        for entry in district_entries:
            key = (entry["tamil"], entry["severity"], entry["category"])
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)
        
        district_stats[district] = len(unique_entries)
        all_entries.extend(unique_entries)
        
        # Write district file
        district_dir = f"E:/tamil_slang_dataset/{district}"
        filepath = f"{district_dir}/{district}_offensive.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(unique_entries, f, ensure_ascii=False, indent=2)
        
        # Also write JSONL
        jsonl_path = f"{district_dir}/{district}_offensive.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for entry in unique_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # Summary
    severity_counts = {"mild": 0, "moderate": 0, "severe": 0}
    category_counts = {}
    region_counts = {}
    source_counts = {}
    
    for entry in all_entries:
        severity_counts[entry["severity"]] = severity_counts.get(entry["severity"], 0) + 1
        category_counts[entry["category"]] = category_counts.get(entry["category"], 0) + 1
        region_counts[entry["region"]] = region_counts.get(entry["region"], 0) + 1
        source_counts[entry["source"]] = source_counts.get(entry["source"], 0) + 1
    
    summary = {
        "total_entries": len(all_entries),
        "districts": len(DISTRICTS),
        "avg_per_district": round(len(all_entries) / len(DISTRICTS), 1),
        "severity_distribution": severity_counts,
        "category_distribution": category_counts,
        "region_distribution": region_counts,
        "source_distribution": source_counts,
        "district_stats": district_stats,
        "created_at": datetime.now().isoformat()
    }
    
    # Save summary
    with open("E:/tamil_slang_dataset/offensive_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("TAMIL OFFENSIVE SLANG DATASET GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nTotal entries: {len(all_entries):,}")
    print(f"Districts: {len(DISTRICTS)}")
    print(f"Average per district: {summary['avg_per_district']:,.1f}")
    print(f"\nSeverity Distribution:")
    for sev, count in severity_counts.items():
        print(f"  {sev.upper()}: {count:,} ({count*100/len(all_entries):.1f}%)")
    print(f"\nCategory Distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count:,}")
    print(f"\nRegion Distribution:")
    for reg, count in region_counts.items():
        print(f"  {reg}: {count:,}")
    print(f"\nSource Distribution:")
    for src, count in source_counts.items():
        print(f"  {src}: {count:,}")
    print(f"\nDistrict-wise distribution:")
    for dist, count in sorted(district_stats.items()):
        print(f"  {dist}: {count}")
    print(f"\nFiles saved to: E:/tamil_slang_dataset/")
    
    return summary

if __name__ == "__main__":
    random.seed(42)
    generate_offensive_dataset()
