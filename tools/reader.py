import os
import json
from PyPDF2 import PdfReader

def load_training_data(filepath):
    training_data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            training_data.append(json.loads(line))
    return training_data

def load_text_from_folder(folder="data/documentos"):
    text = ""
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text += f.read() + "\n"
        elif filename.endswith(".pdf"):
            try:
                reader = PdfReader(path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                print(f"⚠️ Error al leer {filename}: {e}")
    return text

