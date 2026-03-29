import soundfile as sf
import os
import re
import json
import pandas as pd
from tqdm import tqdm
import numpy as np
import librosa

def clean_text(text):
    if not text:
        return ""
    # Keep Hindi characters, numbers, and basic punctuation, but normalize whitespace
    text = re.sub(r'[^\u0900-\u097F0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_segments(audio_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    metadata = []
    
    files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    
    for audio_file in tqdm(files, desc="Preprocessing audio"):
        file_id = audio_file.replace('.wav', '')
        audio_path = os.path.join(audio_dir, audio_file)
        json_path = os.path.join(audio_dir, f"{file_id}.txt")
        
        if not os.path.exists(json_path):
            continue
            
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                segments = json.load(f)
            except json.JSONDecodeError:
                continue
        
        try:
            with sf.SoundFile(audio_path) as f:
                orig_sr = f.samplerate
                for idx, seg in enumerate(segments):
                    start_sec = seg.get('start', 0)
                    end_sec = seg.get('end', 0)
                    text = clean_text(seg.get('text', ''))
                    
                    if not text or (end_sec - start_sec) < 0.5:
                        continue
                    
                    start_frame = int(start_sec * orig_sr)
                    end_frame = int(end_sec * orig_sr)
                    
                    f.seek(start_frame)
                    data = f.read(end_frame - start_frame)
                    
                    # Convert to mono if stereo
                    if len(data.shape) > 1:
                        data = data.mean(axis=1)
                    
                    # Resample to 16000Hz
                    if orig_sr != 16000:
                        data = librosa.resample(data, orig_sr=orig_sr, target_sr=16000)
                    
                    output_filename = f"{file_id}_seg_{idx}.wav"
                    output_path = os.path.join(output_dir, output_filename)
                    sf.write(output_path, data, 16000) 
                    
                    # Use absolute path for metadata to avoid ambiguity
                    abs_output_path = os.path.abspath(output_path)
                    metadata.append({"audio": abs_output_path, "text": text})
        except Exception as e:
            print(f"Error processing {file_id}: {e}")

    return pd.DataFrame(metadata)

if __name__ == "__main__":
    raw_dir = r"d:\hindi_asr_project\data\raw"
    processed_dir = r"d:\hindi_asr_project\data\processed"
    
    df_meta = process_segments(raw_dir, processed_dir)
    df_meta.to_csv(os.path.join(processed_dir, "metadata.csv"), index=False)
    print(f"Preprocessing complete. Total segments: {len(df_meta)}")