import torch
from transformers import (
    WhisperProcessor, 
    WhisperForConditionalGeneration, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer,
    WhisperTokenizer,
    WhisperFeatureExtractor
)
from datasets import Dataset, Audio
import pandas as pd
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        import soundfile as sf
        input_features = []
        label_features = []
        
        for feature in features:
            # Load audio from path
            audio_path = feature["audio"]
            audio_array, _ = sf.read(audio_path)
            
            # Extract features
            f = self.processor.feature_extractor(audio_array, sampling_rate=16000).input_features[0]
            input_features.append({"input_features": f})
            
            # Tokenize text
            l = self.processor.tokenizer(feature["text"]).input_ids
            label_features.append({"input_ids": l})

        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        batch["labels"] = labels
        return batch

def train_model():
    model_id = "openai/whisper-small"
    processor = WhisperProcessor.from_pretrained(model_id, language="Hindi", task="transcribe")
    model = WhisperForConditionalGeneration.from_pretrained(model_id)
    
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []

    # Load preprocessed metadata
    metadata_path = r"d:\hindi_asr_project\data\processed\metadata.csv"
    if not os.path.exists(metadata_path):
        print(f"Metadata not found at {metadata_path}")
        return
        
    df = pd.read_csv(metadata_path)
    
    # Use a dataset with just paths and text
    dataset = Dataset.from_dict({
        "audio": df["audio"].values.tolist(),
        "text": df["text"].values.tolist()
    })

    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

    training_args = Seq2SeqTrainingArguments(
        output_dir="./outputs/models",
        per_device_train_batch_size=4, # Smaller for CPU
        gradient_accumulation_steps=2,
        learning_rate=1e-5,
        warmup_steps=10,
        max_steps=5, # Fast-track for CPU
        gradient_checkpointing=False,
        fp16=False, # CPU doesn't support fp16 well
        eval_strategy="no",
        save_steps=5,
        logging_steps=5,
        report_to=["none"], 
        predict_with_generate=False,
        generation_max_length=225,
        push_to_hub=False,
        save_total_limit=2,
        remove_unused_columns=False,
    )

    trainer = Seq2SeqTrainer(
        args=training_args,
        model=model,
        train_dataset=dataset,
        data_collator=data_collator,
        processing_class=processor.feature_extractor,
    )

    # Set generation config to avoid ValueError on save
    model.generation_config.alignment_heads = None
    model.config.suppress_tokens = None
    
    print("Starting training...")
    trainer.train()
    
    trainer.save_model("./outputs/models/final")
    processor.save_pretrained("./outputs/models/final")
    print("Training complete and model saved.")

if __name__ == "__main__":
    train_model()