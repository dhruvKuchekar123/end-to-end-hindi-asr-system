import pandas as pd
import re
from wordfreq import word_frequency, top_n_list
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Normalize Hindi text
normalizer = DevanagariNormalizer()

# Common English loanwords in Hindi (Devanagari)
# In a real system, we'd use a larger list or a reverse-transliteration model
COMMON_LOANWORDS = {
    "कंप्यूटर", "इंटरनेट", "मोबाइल", "स्क्रीन", "कीबोर्ड", "माउस", "सॉफ्टवेयर", "हार्डवेयर",
    "ऑफिस", "मीटिंग", "प्रोजेक्ट", "मैनेजर", "रिपोर्ट", "डाटा", "डेटा", "वीडियो", "ऑडियो",
    "अकाउंट", "पासवर्ड", "लॉगिन", "साइनअप", "पेमेंट", "बैंक", "कार्ड", "चेक", "लिस्ट",
    "ग्रुप", "लिंक", "फाइल", "फोल्डर", "फोटो", "इमेज", "म्यूजिक", "गेम", "प्ले", "स्टॉप",
    "पॉज", "नेक्स्ट", "प्रीवियस", "कैंसिल", "ओके", "यस", "नो", "थैंक्यू", "सॉरी", "प्लीज"
}

def is_valid_hindi_char(char):
    """Check if character is within Devanagari Unicode range."""
    cp = ord(char)
    return (0x0900 <= cp <= 0x097F) or (cp == 0x200D) or (cp == 0x200C)

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    return normalizer.normalize(text.strip())

def check_word_validity(word):
    """
    Classifies a word as 'correct spelling' or 'incorrect spelling'.
    Returns (classification, confidence, reason)
    """
    if not word or len(word) < 1:
        return "incorrect spelling", "low", "Empty or invalid string"

    # Step 1: Normalization
    normalized_word = normalize_text(word)
    
    # Step 2: Basic Frequency Check (Hindi)
    # word_frequency returns values between 0 and 1
    freq = word_frequency(normalized_word, 'hi')
    if freq > 1e-6:
        return "correct spelling", "high", "Common Hindi word (Freq: {:.2e})".format(freq)

    # Step 3: English Loanword Check
    if normalized_word in COMMON_LOANWORDS:
        return "correct spelling", "high", "Common English loanword"

    # Step 4: Transliteration Heuristic
    # If the word transliterates to a common English word
    eng_translit = transliterate(normalized_word, sanscript.DEVANAGARI, sanscript.ITRANS).lower()
    # Simple check for English sounding words (this is a heuristic)
    # Better would be to use a dictionary lookup for eng_translit
    if len(eng_translit) > 3 and freq == 0:
        # Check if it contains 'aa', 'ee', 'oo' etc which are common in English transliterations
        # This is medium confidence
        if any(v in eng_translit for v in ['sh', 'th', 'ph', 'ch']):
             # If it's a medium frequency word in English (approximate)
             # we could check word_frequency(eng_translit, 'en')
             eng_freq = word_frequency(eng_translit, 'en')
             if eng_freq > 1e-6:
                 return "correct spelling", "medium", "Plausible English transliteration ({})".format(eng_translit)

    # Step 5: Low frequency Hindi words
    if freq > 0:
        return "correct spelling", "medium", "Low frequency Hindi word"

    # Step 6: Heuristics for errors (e.g., character repetition, invalid sequences)
    if re.search(r'(.)\1\1', normalized_word):
        return "incorrect spelling", "medium", "Suspected character repetition"
    
    # Step 7: Final Bucket - Low confidence
    # Most unique words in a 1.77L dataset might be proper nouns, slang, or typos
    # We mark them as correct if they look linguistically valid, but with low confidence
    if all(is_valid_hindi_char(c) for c in normalized_word):
        return "correct spelling", "low", "Linguistically valid but unknown"
    
    return "incorrect spelling", "low", "Contains non-Devanagari characters or invalid sequence"

def main():
    print("Reading unique words...")
    try:
        df = pd.read_csv("unique_words.csv", encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv("unique_words.csv", encoding='latin1') # fallback
    
    # Ensure words are strings
    df['word'] = df['word'].astype(str)
    
    print(f"Processing {len(df)} words...")
    results = []
    
    for i, word in enumerate(df['word']):
        if i % 10000 == 0:
            print(f"Processed {i} words...")
        
        classification, confidence, reason = check_word_validity(word)
        results.append({
            'word': word,
            'classification': classification,
            'confidence': confidence,
            'reason': reason
        })
    
    res_df = pd.DataFrame(results)
    res_df.to_csv("hindi_word_classification_results.csv", index=False, encoding='utf-8-sig')
    
    # Summary stats
    correct_count = len(res_df[res_df['classification'] == 'correct spelling'])
    incorrect_count = len(res_df[res_df['classification'] == 'incorrect spelling'])
    print(f"\nFinal Summary:")
    print(f"Unique words processed: {len(df)}")
    print(f"Correct Spellings: {correct_count}")
    print(f"Incorrect Spellings: {incorrect_count}")
    
    # Bucket counts
    print("\nConfidence Buckets:")
    print(res_df.groupby(['classification', 'confidence']).size())

if __name__ == "__main__":
    main()
