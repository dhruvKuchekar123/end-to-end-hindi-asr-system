from collections import Counter
import pandas as pd

def analyze_words(data):
    words = []

    for sample in data:
        words.extend(sample["text"].split())

    freq = Counter(words)

    results = []

    for word, count in freq.items():
        confidence = count / sum(freq.values())

        status = "correct" if confidence > 0.0001 else "incorrect"

        results.append({
            "word": word,
            "count": count,
            "confidence": confidence,
            "status": status
        })

    df = pd.DataFrame(results)
    df.to_csv("outputs/reports/word_analysis.csv", index=False)

    return df