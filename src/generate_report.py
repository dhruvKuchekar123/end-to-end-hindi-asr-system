from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def add_header(doc, text, level=1):
    doc.add_heading(text, level=level)

def add_paragraph(doc, text, bold=False):
    p = doc.add_paragraph(text)
    if bold:
        p.runs[0].bold = True

def generate_report():
    doc = Document()
    
    # Title
    title = doc.add_heading('Hindi ASR Performance Improvement Project', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Introduction
    add_header(doc, 'Project Overview', 1)
    doc.add_paragraph(
        "This report summarizes the end-to-end effort to improve Hindi Automatic Speech Recognition (ASR). "
        "The project scope includes fine-tuning the Whisper model, performing systematic error analysis, "
        "cleaning the training vocabulary, and implementing an advanced lattice-based evaluation framework."
    )

    # Question 1 & 2: Fine-Tuning and Baseline
    add_header(doc, '1. Fine-Tuning and Baseline Evaluation (Q1 & Q2)', 1)
    
    add_header(doc, 'Preprocessing Strategy', 2)
    doc.add_paragraph(
        "- Audio standardization to 16kHz mono.\n"
        "- Metadata alignment and text normalization (removal of punctuation).\n"
        "- Feature extraction using Mel-spectrograms."
    )
    
    add_header(doc, 'WER Results', 2)
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Model'
    hdr_cells[1].text = 'WER'
    hdr_cells[2].text = 'Status'
    
    rows = [
        ('Whisper-Small (Pretrained)', '1.15*', 'Catastrophic hallucinations'),
        ('Whisper-Small (Stability Fix)', '0.8377', 'Stable, phonetic errors'),
        ('Fine-Tuned (checkpoint-5)', '0.8312', 'Stable improvement')
    ]
    for m, w, s in rows:
        row_cells = table.add_row().cells
        row_cells[0].text = m
        row_cells[1].text = w
        row_cells[2].text = s
    
    add_header(doc, 'Error Taxonomy and Fixes', 2)
    doc.add_paragraph(
        "Key errors identified: Repetitive hallucinations, phonetic misspellings, and word omissions. "
        "The primary fix implemented was an Inference-time Repetition Penalty (1.2), which reduced WER by ~27%."
    )

    # Question 3: Hindi Vocabulary Cleaning
    add_header(doc, '2. Hindi Vocabulary Cleaning (Q3)', 1)
    doc.add_paragraph(
        "Objective: Identify correct vs. incorrect spellings in a list of ~1.77L unique words to prioritize re-transcription."
    )
    
    add_header(doc, 'Methodology', 2)
    doc.add_paragraph(
        "A multi-layered classification approach was used:\n"
        "- Frequency Analysis: Validating common words using 'wordfreq'.\n"
        "- Loanword Detection: Verifying English words in Devanagari (e.g., 'कंप्यूटर').\n"
        "- Unicode Normalization & Linguistic Heuristics."
    )
    
    add_header(doc, 'Results', 2)
    doc.add_paragraph("Total Unique Words Processed: 177,508")
    doc.add_paragraph("- Correct Spellings: 170,565")
    doc.add_paragraph("- Incorrect Spellings: 6,943")
    doc.add_paragraph("Accuracy on Low Confidence Bucket: ~92%")
    
    add_paragraph(doc, "Data Link: https://docs.google.com/spreadsheets/d/17DwCAx6Tym5Nt7eOni848np9meR-TIj7uULMtYcgQaw/edit?gid=0#gid=0", bold=True)

    # Question 4: Advanced Lattice-Based Evaluation
    add_header(doc, '3. Lattice-Based ASR Evaluation (Q4)', 1)
    doc.add_paragraph(
        "Standard WER unfairly penalizes valid spelling and lexical variations. We implemented a lattice-based "
        "evaluation that groups synonyms and variations into positional bins."
    )
    
    add_header(doc, 'Key Features', 2)
    doc.add_paragraph(
        "- Choice of Unit: Word (for semantic and numeric mapping).\n"
        "- Number Normalization: Mapping '14' to 'चौदह' validly.\n"
        "- Model Consensus Logic: Trusting 3+ models over a potentially erroneous reference."
    )
    
    add_header(doc, 'Final Lattice-WER Results', 2)
    table2 = doc.add_table(rows=1, cols=2)
    hdr2 = table2.rows[0].cells
    hdr2[0].text = 'Model'
    hdr2[1].text = 'Lattice-Based WER'
    
    wer_data = [
        ('Model H', '1.47%'),
        ('Model i', '0.00%'),
        ('Model k', '3.35%'),
        ('Model l', '2.93%'),
        ('Model m', '2.45%'),
        ('Model n', '2.68%')
    ]
    for m, w in wer_data:
        row_cells = table2.add_row().cells
        row_cells[0].text = m
        row_cells[1].text = w

    add_paragraph(doc, "Data Link: https://docs.google.com/spreadsheets/d/1J_I0raoRNbe29HiAPD5FROTr0jC93YtSkjOrIglKEjU/edit?gid=1432279672#gid=1432279672", bold=True)

    # Save
    report_name = 'Comprehensive_Hindi_ASR_Report.docx'
    doc.save(report_name)
    print(f"Report generated successfully: {report_name}")

if __name__ == "__main__":
    generate_report()
