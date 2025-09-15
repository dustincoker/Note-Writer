import spacy
import re

# Load the spaCy NER model
nlp = spacy.load("en_core_web_trf")

# Function to anonymize text
def anonymize_text(text):
    doc = nlp(text)
    anonymized_text = text
    
    # Replace detected entities with placeholders
    for ent in doc.ents:
        replacement = f"[{ent.label_}]"
        anonymized_text = anonymized_text.replace(ent.text, replacement)

    # Additional regex-based anonymization for emails and phone numbers
    anonymized_text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", anonymized_text)
    anonymized_text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", anonymized_text)

    return anonymized_text

# Function to process a text file and anonymize its contents
def anonymize_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        case_notes = f.readlines()

    anonymized_notes = [anonymize_text(note) for note in case_notes]

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(anonymized_notes)

    print(f"✅ Anonymization complete! Anonymized notes saved to {output_file}")

# Specify file paths
input_file = "case_notes_final.txt"  # Replace with your actual file
output_file = "anonymized_notes.txt"

# Run the anonymization process
anonymize_file(input_file, output_file)

