import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from datasets import load_dataset
from jiwer import wer
import pandas as pd
from tqdm import tqdm
import argparse
import os
import re

def clean_text(text):
    if not text:
        return ""
    # Simple cleaning for evaluation
    text = re.sub(r'[^\u0900-\u097F0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def evaluate(model_id_or_path, device="cuda" if torch.cuda.is_available() else "cpu"):
    print(f"Loading model from {model_id_or_path}...")
    processor = WhisperProcessor.from_pretrained("openai/whisper-small") # Always use base processor for tokenizer
    model = WhisperForConditionalGeneration.from_pretrained(model_id_or_path).to(device)
    
    print("Loading local processed dataset for evaluation (fallback)...")
    try:
        df = pd.read_csv("data/processed/metadata.csv")
        # Use the last 50 samples as a test set
        ds = df.tail(50).to_dict('records')
    except Exception as e:
        print(f"Failed to load local data: {e}")
        return 1.0
    
    all_results_for_csv = [] # This will store dicts for CSV
    all_references_for_wer = [] # This will store cleaned ref texts for WER
    all_predictions_for_wer = [] # This will store cleaned pred texts for WER
    
    print("Evaluating...")
    # Process the stream
    count = 0
    for sample in tqdm(ds):
        audio_path = sample["audio"]
        ref_text = sample["text"]
        
        # Load audio from file
        import soundfile as sf
        audio_array, sampling_rate = sf.read(audio_path)
        
        # Preprocess audio
        input_features = processor(audio_array, sampling_rate=sampling_rate, return_tensors="pt").input_features.to(device)
        
        # Generate transcription
        with torch.no_grad():
            generated_ids = model.generate(
                input_features, 
                max_length=225,
                no_repeat_ngram_size=3,
                repetition_penalty=1.2
            )
        
        prediction = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        cleaned_ref = clean_text(ref_text)
        cleaned_pred = clean_text(prediction)

        all_references_for_wer.append(cleaned_ref)
        all_predictions_for_wer.append(cleaned_pred)
        
        all_results_for_csv.append({
            "id": sample.get("id", "N/A"),
            "reference": cleaned_ref,
            "prediction": cleaned_pred
        })
        
        count += 1
        if count % 10 == 0:
            print(f"Processed {count} samples...")
        if count >= 10: # Reduced for speed on CPU
            break

    if not all_references_for_wer:
        print("No samples processed!")
        return 1.0

    error_rate = wer(all_references_for_wer, all_predictions_for_wer)
    print(f"\nWord Error Rate (WER) on {count} samples: {error_rate:.4f}")
    
    # Save results
    os.makedirs("outputs/predictions", exist_ok=True)
    model_name = os.path.basename(model_id_or_path.rstrip("/"))
    output_path = f"outputs/predictions/results_{model_name}.csv"
    pd.DataFrame(all_results_for_csv).to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    
    return error_rate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="openai/whisper-small")
    args = parser.parse_args()
    
    evaluate(args.model)