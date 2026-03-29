import pandas as pd
import re
from difflib import SequenceMatcher
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
import sys
import os

# Import the existing number translator from src
sys.path.append(os.path.abspath('src'))
try:
    from number_translator import normalize_numbers
except ImportError:
    def normalize_numbers(text): return text

# Normalize Hindi text
normalizer = DevanagariNormalizer()

# Common synonyms or lexical variations for Hindi ASR
SYNONYMS = {
    "किताबें": {"पुस्तकें", "किताबें"},
    "पुस्तकें": {"किताबें"},
    "खरीदीं": {"खरीदी"},
    "खरीदी": {"खरीदीं"},
    "करते": {"करतेहैं"},
    "हैं": {"है"},
    "है": {"हैं"},
    "डिश": {"डिशेस", "दिश", "डिशस"},
    "म्यूजिक": {"म्यूज़िक"},
}

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # 1. Standardize Hindi numbers (e.g., 'चौदह' -> '14')
    # Note: For lattice matching, it's better if we match the numeric representation
    # if both models agree on the value.
    text = normalize_numbers(text)
    # 2. Basic cleaning (punctuation)
    text = re.sub(r'[\u0964\u0965,.\-?!\(\)]', ' ', text)
    # 3. Unicode normalization
    return normalizer.normalize(text.strip())

def tokenize(text):
    return normalize_text(text).split()

def get_alternatives(word):
    """Returns a set of valid alternatives for a word."""
    alts = {word}
    if word in SYNONYMS:
        alts.update(SYNONYMS[word])
    return alts

def align_and_build_lattice(reference, model_outputs):
    """
    Constructs a lattice (positional bins) from reference and model outputs.
    reference: list of tokens
    model_outputs: list of lists of tokens (one per model)
    """
    # Initialize lattice with reference tokens and their known synonyms
    # "votes" tracks how many models (including ref) agree on a specific spelling
    lattice = []
    for w in reference:
        bin = {
            "ref": w, 
            "alternatives": get_alternatives(w), 
            "votes": {w: 1} # Human counts as 1 vote
        }
        lattice.append(bin)
    
    for model_tokens in model_outputs:
        matcher = SequenceMatcher(None, reference, model_tokens)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace' or tag == 'equal':
                # Models substitute or match words
                for offset in range(min(i2-i1, j2-j1)):
                    word = model_tokens[j1+offset]
                    lattice[i1+offset]["alternatives"].add(word)
                    lattice[i1+offset]["votes"][word] = lattice[i1+offset]["votes"].get(word, 0) + 1
            # Note: Insertions and Deletions are handled by the WER DP table later.
            # A 'delete' simply means the model doesn't provide a word for that bin.
            # An 'insert' is handled by the model having an extra word.

    # Model Consensus Rule: If 3+ models (majority) agree on a word, 
    # it is considered a valid transcription alternative even if not in the reference.
    for bin in lattice:
        for word, count in bin["votes"].items():
            if count >= 3:
                bin["alternatives"].add(word)
                
    return lattice

def calculate_lattice_wer(model_transcript, lattice):
    """
    Computes WER by checking if model words match ANY valid option (alternatives) 
    in the corresponding lattice bin.
    """
    model_tokens = tokenize(model_transcript)
    m = len(lattice)
    n = len(model_tokens)
    
    # DP table for edit distance (Levenshtein)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): dp[i][0] = i
    for j in range(m + 1): dp[0][j] = j
    
    for i in range(1, n + 1):
        model_word = model_tokens[i-1]
        model_alts = get_alternatives(model_word)
        
        for j in range(1, m + 1):
            # A 'match' is achieved if ANY alternative of the model word 
            # matches ANY valid alternative in the lattice bin.
            if any(alt in lattice[j-1]["alternatives"] for alt in model_alts):
                cost = 0
            else:
                cost = 1
            
            dp[i][j] = min(dp[i-1][j] + 1,      # Substitution/Cost-based
                           dp[i][j-1] + 1,      # Deletion/Insertion
                           dp[i-1][j-1] + cost) 
    
    edit_dist = dp[n][m]
    # WER = Edit Distance / Reference Length
    wer = edit_dist / m if m > 0 else 0
    return wer, edit_dist, m

def main():
    csv_path = "asr_transcripts.csv"
    print(f"Reading ASR transcripts from {csv_path}...")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Identify model columns (Model H, i, k, l, m, n)
    model_cols = [c for c in df.columns if c.lower().startswith('model')]
    results = []

    print(f"Processing {len(df)} utterances with {len(model_cols)} models...")
    for idx, row in df.iterrows():
        ref_text = row.get('Human', '')
        if not isinstance(ref_text, str) or not ref_text.strip(): continue
        
        ref_tokens = tokenize(ref_text)
        model_token_lists = []
        for col in model_cols:
            text = row.get(col, '')
            model_token_lists.append(tokenize(text) if isinstance(text, str) else [])
        
        # 1. Build the positional lattice
        lattice = align_and_build_lattice(ref_tokens, model_token_lists)
        
        # 2. Compute Lattice-Based WER for each model
        row_wer = {'ID': idx}
        for col in model_cols:
            wer, _, _ = calculate_lattice_wer(row[col], lattice)
            row_wer[f'{col}_WER'] = wer
            
        results.append(row_wer)
        
        if idx > 0 and idx % 20 == 0:
            print(f"Processed {idx} rows...")

    res_df = pd.DataFrame(results)
    res_df.to_csv("lattice_wer_results.csv", index=False)
    
    # Calculate column-wise mean for all WER columns
    wer_means = res_df.filter(like='_WER').mean()
    
    print("\nAverage Lattice-Based WER per Model:")
    print(wer_means)
    
    # Save a summary for reporting
    with open("wer_summary.txt", "w", encoding="utf-8") as f:
        f.write("Lattice-Based ASR Evaluation Results\n")
        f.write("====================================\n")
        f.write(wer_means.to_string())
        f.write(f"\n\nTotal Sentences Processed: {len(res_df)}")

if __name__ == "__main__":
    main()