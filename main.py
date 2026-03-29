from src.data_loader import load_dataset
from src.preprocess import preprocess_dataset
from src.train_whisper import train_model
from src.evaluate import evaluate
from src.cleanup_pipeline import cleanup
from src.word_analysis import analyze_words
from src.lattice_eval import lattice_wer

# Step 1: Load data
df = load_dataset("data/raw/FT Data - data.csv", "data/raw")

# Step 2: Preprocess
processed = preprocess_dataset(df, "data/processed")

# Step 3: Train
model, processor = train_model(processed)

# Step 4: Evaluate
wer_score, predictions = evaluate(model, processor, processed)

# Save predictions
with open("outputs/predictions/preds.txt", "w") as f:
    for p in predictions:
        f.write(p + "\n")

# Step 5: Cleanup example
cleaned = [cleanup(p) for p in predictions]

# Step 6: Word analysis
analyze_words(processed)

# Step 7: Lattice WER
refs = [d["text"] for d in processed]
lattice_score = lattice_wer(refs, predictions)

print("WER:", wer_score)
print("Lattice WER:", lattice_score)