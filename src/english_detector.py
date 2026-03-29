import re

# A common lexicon of English words frequently used in Hindi, transcribed in Devanagari.
# In a production system, this could be a much larger dictionary or a classifier.
ENGLISH_LOANWORDS_DEVANAGARI = [
    "इंटरव्यू", "जॉब", "प्रॉब्लम", "सॉल्व", "कंप्यूटर", "ऑफिस", "मीटिंग", "फोन", "मैसेज", 
    "कॉल", "टीम", "प्रोजेक्ट", "मैनेजर", "सॉफ्टवेयर", "इंजीनियर", "डेटा", "इंटरनेट", 
    "वेबसाइट", "एप", "एप्लीकेशन", "वीडियो", "ऑडियो", "स्क्रीन", "कीबोर्ड", "माउस", 
    "लैपटॉप", "डेस्कटॉप", "सर्वर", "नेटवर्क", "पासवर्ड", "लॉगिन", "साइनअप", "अकाउंट",
    "पेमेंट", "बैंक", "कार्ड", "टिकेट", "बुकिंग", "होटल", "रेस्टोरेंट", "कार", "बस", 
    "ट्रेन", "फ्लाइट", "एयरपोर्ट", "स्टेशन", "मार्केट", "मॉल", "शॉपिंग", "डिस्काउंट",
    "ऑफर", "सेल", "कस्टमर", "सर्विस", "क्वालिटी", "ब्रांड", "प्रोडक्ट", "आइटम", 
    "लिस्ट", "चेक", "सेंड", "रिसीव", "अपडेट", "डिलीट", "कॉपी", "पेस्ट", "शेयर", 
    "लाइक", "कमेंट", "सब्सक्राइब", "फॉलो", "ब्लॉक", "रिपोर्ट", "हेल्प", "सपोर्ट",
    "प्लान", "आइडिया", "चांस", "टाइम", "डेट", "नंबर", "एड्रेस", "ईमेल", "चैट", 
    "ग्रुप", "लिंक", "फाइल", "फोल्डर", "फोटो", "इमेज", "म्यूजिक", "गेम", "प्ले", 
    "स्टॉप", "पॉज", "नेक्स्ट", "प्रीवियस", "कैंसिल", "ओके", "यस", "नो", "वेरी", 
    "गुड", "बैड", "बेस्ट", "कूल", "नाइस", "सॉरी", "थैंक", "थैंक्यू", "वेलकम", 
    "बाय", "हेलो", "हाए", "प्लीज", "एक्सक्यूज", "किलियर", "परफैक्ट", "एडजेस्ट", "सिफ्ट"
]

def tag_english_words(text):
    """
    Identifies and tags English loanwords in Devanagari.
    Example: 'मेरा इंटरव्यू अच्छा रहा' -> 'मेरा [EN]इंटरव्यू[/EN] अच्छा रहा'
    """
    # Sort by length descending to match longer phrases first
    sorted_words = sorted(ENGLISH_LOANWORDS_DEVANAGARI, key=len, reverse=True)
    
    # Use capturing groups to handle boundaries without look-behind
    # Punctuation and whitespace characters to consider as boundaries
    bounds = r'[\s\u0964\u0965,.\-?!\(\)]'
    pattern = r'(^|' + bounds + r')(' + '|'.join(sorted_words) + r')(?=' + bounds + r'|$)'
    
    # Replacement uses the first group to restore the boundary
    tagged_text = re.sub(pattern, r'\1[EN]\2[/EN]', text)
    return tagged_text

if __name__ == "__main__":
    test_cases = [
        "मेरा इंटरव्यू बहुत अच्छा गया और मुझे जॉब मिल गई",
        "ये प्रॉब्लम सॉल्व नहीं हो रहा",
        "मैंने कल लैपटॉप खरीदा",
        "क्या आपने मैसेज देखा?",
        "आपका आवाज थोड़ा किलियर नहीं आ रहा है",
        "अब परफैक्ट है",
        "कपड़े को एडजेस्ट करना",
        "मकान में सिफ्ट हुए हैं"
    ]
    for t in test_cases:
        print(f"'{t}' -> '{tag_english_words(t)}'")
