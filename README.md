# End-to-End Hindi ASR System

This repository implements a comprehensive framework for Improving and Evaluating Hindi Automatic Speech Recognition (ASR) performance. It addresses common challenges like transcription variations, model hallucinations, and vocabulary noise.

## 🚀 Key Features
- **Fine-Tuning**: Optimized `openai/whisper-small` for Hindi conversational data.
- **Vocabulary Cleaning**: Automated classification of ~1.77L unique words into correct/incorrect spellings using `indic-nlp` and frequency analysis.
- **Lattice-Based Evaluation**: A flexible evaluation system that accounts for lexical synonyms and number-to-text variations (e.g., "14" vs "चौदह").
- **Model Consensus Logic**: Trusting majority model agreement to identify reference errors and valid alternatives.

## 📁 Repository Structure
- `src/word_classifier.py`: Logic for Hindi vocabulary cleaning.
- `src/lattice_eval.py`: Lattice-based WER computation engine.
- `src/number_translator.py`: Devanagari number normalization.
- `Comprehensive_Hindi_ASR_Report.docx`: Summary report of all project phases (Q1-Q4).

## 📊 Summary of Results
| Model | Lattice-Based WER |
| :--- | :--- |
| **Model H** | 1.47% |
| **Model i** | 0.00% |
| **Model k** | 3.35% |
| **Model l** | 2.93% |
| **Model m** | 2.45% |
| **Model n** | 2.68% |

## 🛠 Setup & Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run evaluation:
   ```bash
   python src/lattice_eval.py
   ```

## 📄 Final Report
For detailed analysis, error taxonomies, and implementation details, see [Comprehensive_Hindi_ASR_Report.docx](./Comprehensive_Hindi_ASR_Report.docx).
