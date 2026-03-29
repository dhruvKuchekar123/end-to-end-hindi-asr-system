import re

HINDI_NUMBERS = {
    "शून्य": 0, "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "ग्यारह": 11, "बारह": 12, "तेरह": 13, "चौदह": 14, "पंद्रह": 15, "सोलह": 16, "सत्रह": 17, "अठारह": 18, "उन्नीस": 19, "बीस": 20,
    "इक्कीस": 21, "बाईस": 22, "तेईस": 23, "चौबीस": 24, "पच्चीस": 25, "छब्बीस": 26, "सत्ताईस": 27, "अठाईस": 28, "उनतीस": 29, "तीस": 30,
    "इकतीस": 31, "बत्तीस": 32, "तैंतीस": 33, "चौंतीस": 34, "पैंतीस": 35, "छत्तीस": 36, "सैंतीस": 37, "अड़तीस": 38, "उनतालीस": 39, "चालीस": 40,
    "इकतालीस": 41, "बयालीस": 42, "तैंतालीस": 43, "चवालीस": 44, "पैंतालीस": 45, "छियालीस": 46, "सैंतालीस": 47, "अड़तालीस": 48, "उनचास": 49, "पचास": 50,
    "इक्यावन": 51, "बावन": 52, "तिरपन": 53, "चौवन": 54, "पचपन": 55, "छप्पन": 56, "सत्तावन": 57, "अट्ठावन": 58, "उनसठ": 59, "साठ": 60,
    "इकसठ": 61, "बासठ": 62, "तिरसठ": 63, "चौंसठ": 64, "पैंसठ": 65, "छियासठ": 66, "सरसठ": 67, "अड़सठ": 68, "उनहत्तर": 69, "सत्तर": 70,
    "इकहत्तर": 71, "बहत्तर": 72, "तिहत्तर": 73, "चौहत्तर": 74, "पचहत्तर": 75, "छिहत्तर": 76, "सतहत्तर": 77, "अठहत्तर": 78, "उन्यासी": 79, "अस्सी": 80,
    "इक्यासी": 81, "बयासी": 82, "तिरासी": 83, "चौरासी": 84, "पचासी": 85, "छियासी": 86, "सतासी": 87, "अठासी": 88, "नवासी": 89, "नब्बे": 90,
    "इक्यानवे": 91, "बयानवे": 92, "तिरानवे": 93, "चौरानवे": 94, "पचानवे": 95, "छियानवे": 96, "सत्तानवे": 97, "अट्ठानवे": 98, "निन्यानवे": 99
}

HINDI_SCALES = {
    "सौ": 100,
    "हज़ार": 1000,
    "लाख": 100000,
    "करोड़": 10000000
}

# Idioms/Phrases to avoid conversion
IDIOMS = [
    r"दो-चार",
    r"एक-आध",
    r"नौ दो ग्यारह",
    r"छक्के छुड़ाना"
]

def hindi_words_to_number(text):
    """
    Converts a string of Hindi number words (e.g., 'तीन सौ चौवन') to an integer.
    """
    words = text.split()
    total = 0
    current = 0
    
    for word in words:
        if word in HINDI_NUMBERS:
            current += HINDI_NUMBERS[word]
        elif word in HINDI_SCALES:
            scale = HINDI_SCALES[word]
            if current == 0: # Handle cases like 'सौ' meaning '100'
                current = 1
            total += current * scale
            current = 0
        else:
            # Not a number word, skip or handle error
            pass
            
    return total + current

def normalize_numbers(text):
    """
    Detects and normalizes Hindi number words in a sentence, respecting idioms.
    """
    # 1. Protect idioms by masking
    masked_text = text
    for i, idiom in enumerate(IDIOMS):
        masked_text = re.sub(idiom, f"__IDIOM_{i}__", masked_text)
        
    # 2. Extract potential number sequences
    all_num_words = list(HINDI_NUMBERS.keys()) + list(HINDI_SCALES.keys())
    # Use a more flexible pattern for Devanagari word boundaries
    pattern = r'(?<![^\s])(?:' + '|'.join(all_num_words) + r')(?:\s+(?:' + '|'.join(all_num_words) + r'))*(?![^\s])'
    
    def replace_match(match):
        num_str = match.group(0)
        try:
            val = hindi_words_to_number(num_str)
            return str(val)
        except:
            return num_str

    normalized_text = re.sub(pattern, replace_match, masked_text)
    
    # 3. Restore idioms
    for i, idiom in enumerate(IDIOMS):
        # We need the original matched text, not the regex pattern
        # For simplicity, we'll just use a literal replacement if the pattern was simple
        # In a real app, we'd store the original string.
        # Here we'll just hardcode the restores for the common idioms above.
        original = ["दो-चार", "एक-आध", "नौ दो ग्यारह", "छक्के छुड़ाना"][i]
        normalized_text = normalized_text.replace(f"__IDIOM_{i}__", original)
        
    return normalized_text

if __name__ == "__main__":
    test_cases = [
        "दो",
        "दस",
        "सौ",
        "तीन सौ चौवन",
        "पच्चीस",
        "एक हज़ार",
        "मेरे पास दो-चार बातें हैं",
        "वह नौ दो ग्यारह हो गया",
        "उसने पच्चीस हजार तीन सौ अड़तालीस रुपये दिए"
    ]
    for t in test_cases:
        print(f"'{t}' -> '{normalize_numbers(t)}'")
