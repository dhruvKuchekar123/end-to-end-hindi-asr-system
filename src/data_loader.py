import os
import requests
import pandas as pd
from tqdm import tqdm

def download_file(url, save_path):
    r = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(r.content)

def load_dataset(csv_path, save_dir):
    df = pd.read_csv(csv_path)
    os.makedirs(save_dir, exist_ok=True)

    data = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        audio_path = os.path.join(save_dir, f"{row['recording_id']}.wav")
        text_path = os.path.join(save_dir, f"{row['recording_id']}.txt")

        download_file(row['rec_url_gcp'], audio_path)
        download_file(row['transcription_url_gcp'], text_path)

        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        data.append({"audio": audio_path, "text": text})

    return pd.DataFrame(data)