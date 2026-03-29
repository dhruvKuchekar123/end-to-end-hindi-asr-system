from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def add_styled_heading(doc, text, level, color=None):
    h = doc.add_heading(text, level=level)
    if color:
        h.runs[0].font.color.rgb = RGBColor(*color)
    return h

def add_bullet_point(doc, text):
    p = doc.add_paragraph(text, style='List Bullet')
    return p

def generate_professional_report():
    doc = Document()
    
    # Title Page Style
    title = doc.add_heading('Hindi ASR System: Performance Optimization & Evaluation', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # GitHub Link Section
    p_git = doc.add_paragraph()
    p_git.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_git.add_run('GitHub Repository: ')
    run.bold = True
    run_url = p_git.add_run('https://github.com/dhruvKuchekar123/end-to-end-hindi-asr-system.git')
    run_url.font.color.rgb = RGBColor(0, 0, 255)
    run_url.font.underline = True

    doc.add_paragraph('\n')

    # Executive Summary
    add_styled_heading(doc, '1. Executive Summary', 1)
    doc.add_paragraph(
        "This project delivers a robust pipeline for Hindi Automatic Speech Recognition (ASR). "
        "The core objectives were to fine-tune the OpenAI Whisper model, perform an in-depth error taxonomy, "
        "clean a large-scale conversational vocabulary (1.77L words), and develop a novel lattice-based "
        "evaluation framework that reduces unfair penalties for valid variations."
    )

    # Question 1: Data Preprocessing & Fine-Tuning
    add_styled_heading(doc, '2. Model Fine-Tuning & Preprocessing (Q1)', 1)
    doc.add_paragraph(
        "Fine-tuning `openai/whisper-small` required rigorous data standardization to align with the model's "
        "expected input distribution of 16kHz mono-audio and normalized Hindi text."
    )
    
    add_styled_heading(doc, 'Step-by-Step Preprocessing', 2)
    add_bullet_point(doc, "Audio Normalization: Resampling audio to 16,000 Hz and converting to mono to ensure spectral consistency.")
    add_bullet_point(doc, "Feature Engineering: Generating 80-channel Log-Mel Spectrograms from the time-domain signal.")
    add_bullet_point(doc, "Text Standardization: Removing non-Devanagari characters and standardizing Matra/Nuqta usage to reduce token vocabulary noise.")

    # Question 2: Error Analysis & Stability Fixes
    add_styled_heading(doc, '3. Systematic Error Analysis & Mitigation (Q2)', 1)
    doc.add_paragraph(
        "Baseline evaluation revealed significant failure modes, particularly 'Repetitive Hallucinations' "
        "where the decoder loops on common bigrams."
    )
    
    table_err = doc.add_table(rows=1, cols=3)
    table_err.style = 'Table Grid'
    hdr_cells = table_err.rows[0].cells
    hdr_cells[0].text = 'Error Type'
    hdr_cells[1].text = 'Observed Behavior'
    hdr_cells[2].text = 'Proposed/Implemented Fix'
    
    err_rows = [
        ('Repetitive Hallucination', 'Infinite loops of 1-3 tokens.', 'Implemented repetition_penalty=1.2 and no_repeat_ngram_size=3.'),
        ('Phonetic Misspelling', 'Substitutions of similar sounding characters.', 'SpecAugment during training to improve phonetic robustness.'),
        ('Word Omission', 'Skipping short filler words.', 'Adjusted beam size and lowered length_penalty.')
    ]
    for et, ob, fx in err_rows:
        row = table_err.add_row().cells
        row[0].text = et
        row[1].text = ob
        row[2].text = fx

    # Question 3: Large-Scale Vocabulary Cleaning
    add_styled_heading(doc, '4. Vocabulary Cleaning & Dataset Integrity (Q3)', 1)
    doc.add_paragraph(
        "The project processed 177,508 unique words from human transcriptions. We developed a classifier "
        "to separate high-accuracy spellings from potential errors."
    )
    
    add_styled_heading(doc, 'Classification Methodology', 2)
    doc.add_paragraph(
        "Our classifier employs a multi-stage validation logic:\n"
        "1. Frequency Verification: Words matching high-frequency lists are prioritized.\n"
        "2. Loanword Mapping: English words spoken in Hindi context are validated as correct.\n"
        "3. Phonotactic Heuristics: Detecting invalid Devanagari character sequences."
    )
    
    table_stats = doc.add_table(rows=1, cols=2)
    table_stats.style = 'Medium Shading 1 Accent 1'
    hdr_stats = table_stats.rows[0].cells
    hdr_stats[0].text = 'Category'
    hdr_stats[1].text = 'Count'
    
    stats_rows = [
        ('Unique Words Processed', '177,508'),
        ('Correct Spellings Identified', '170,565'),
        ('Incorrect Spellings (Errors)', '6,943')
    ]
    for cat, val in stats_rows:
        row = table_stats.add_row().cells
        row[0].text = cat
        row[1].text = val

    # Question 4: Lattice-Based ASR Evaluation
    add_styled_heading(doc, '5. Advanced Lattice-Based Evaluation (Q4)', 1)
    doc.add_paragraph(
        "The final phase replaced rigid string matching with a sequential 'Lattice' approach. "
        "This framework allows for multiple valid paths (synonyms, number formats, and consensus) "
        "to be considered 'correct' during scoring."
    )
    
    add_styled_heading(doc, 'Lattice Logic Features', 2)
    add_bullet_point(doc, "Positional Bins: Words are aligned relative to the reference backbone.")
    add_bullet_point(doc, "Consensus Rule: If 3+ models disagree with the reference but agree with each other, their choice is validated.")
    add_bullet_point(doc, "Lexical Flexibility: Automatic handling of '14' (number) vs 'चौदह' (word) variations.")

    add_styled_heading(doc, 'Final Performance metrics', 2)
    table_wer = doc.add_table(rows=1, cols=2)
    table_wer.style = 'Table Grid'
    hdr_wer = table_wer.rows[0].cells
    hdr_wer[0].text = 'ASR Model'
    hdr_wer[1].text = 'Lattice-Aware WER'
    
    wer_data = [('Model H', '1.47%'), ('Model i', '0.00%'), ('Model k', '3.35%'), 
                ('Model l', '2.93%'), ('Model m', '2.45%'), ('Model n', '2.68%')]
    for m, w in wer_data:
        row = table_wer.add_row().cells
        row[0].text = m
        row[1].text = w

    # Conclusion
    doc.add_paragraph('\n')
    doc.add_paragraph(
        "Conclusion: The combination of targeted model fine-tuning, robust vocabulary sanitization, "
        "and flexible lattice-based scoring provides a comprehensive solution for production-grade "
        "Hindi ASR systems."
    )

    # Save
    report_name = 'Comprehensive_Hindi_ASR_Project_Report.docx'
    doc.save(report_name)
    print(f"Professional report generated: {report_name}")

if __name__ == "__main__":
    generate_professional_report()
