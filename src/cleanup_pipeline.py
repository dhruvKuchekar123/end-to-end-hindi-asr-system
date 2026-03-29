from number_translator import normalize_numbers
from english_detector import tag_english_words
import pandas as pd
import os

def cleanup_asr_output(text):
    """
    Applies the full cleanup pipeline to a raw ASR transcription.
    """
    if not text or not isinstance(text, str):
        return text
        
    # 1. Number Normalization
    text = normalize_numbers(text)
    
    # 2. English Word Tagging
    text = tag_english_words(text)
    
    return text

def process_results(input_csv, output_csv):
    """
    Processes a results CSV, applying cleanup to the 'prediction' column.
    """
    if not os.path.exists(input_csv):
        print(f"File not found: {input_csv}")
        return
        
    df = pd.read_csv(input_csv)
    
    # Keep original for reference in report later
    df['raw_prediction'] = df['prediction']
    
    # Apply cleanup
    df['prediction'] = df['prediction'].apply(cleanup_asr_output)
    
    df.to_csv(output_csv, index=False)
    print(f"Cleaned results saved to {output_csv}")

if __name__ == "__main__":
    # Process real ASR results
    input_file = "outputs/predictions/results_whisper-small.csv"
    output_file = "outputs/predictions/results_whisper-small_cleaned.csv"
    process_results(input_file, output_file)
    
    # Quick sanity check on some generated samples
    print("\nSample Cleanup Results:")
    df_cleaned = pd.read_csv(output_file)
    for i, row in df_cleaned.head(20).iterrows():
        if row['prediction'] != row['raw_prediction']:
            print(f"Row {i}:")
            print(f"  Raw: {row['raw_prediction']}")
            print(f"  Clean: {row['prediction']}")
            print("-" * 10)