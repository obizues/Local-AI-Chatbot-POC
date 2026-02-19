import os
import re
import glob
import pandas as pd
from typing import List, Dict

# For PDF and DOCX
import fitz  # PyMuPDF
import docx

# Chunking
from textwrap import wrap

# Metadata extraction helpers
def extract_metadata_from_text(text: str) -> Dict[str, str]:
    meta = {}
    # YAML frontmatter
    yaml_match = re.match(r"---\n(.*?)---", text, re.DOTALL)
    if yaml_match:
        for line in yaml_match.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
    # Simple key: value
    for line in text.splitlines()[:5]:
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip().lower()] = v.strip()
    return meta

def read_txt_md(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text

def read_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    # Preprocess: merge headings with following paragraph (robust)
    lines = text.splitlines()
    merged_blocks = []
    buffer = ""
    in_heading = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # Heading if markdown (#) or short line ending with :
        if stripped.startswith("#") or (stripped.endswith(":") and len(stripped.split()) < 6):
            if buffer:
                merged_blocks.append(buffer.strip())
                buffer = ""
            buffer += stripped + " "
            in_heading = True
        elif in_heading:
            buffer += stripped + " "
            in_heading = False
        else:
            buffer += stripped + " "
    if buffer:
        merged_blocks.append(buffer.strip())

    # Now chunk as before, but on merged_blocks
    words = " ".join(merged_blocks).split()
    chunk_size = 1500
    overlap = 100
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_documents(data_dir: str) -> pd.DataFrame:
    records = []
    for ext in ['txt', 'md', 'pdf', 'docx']:
        for file_path in glob.glob(os.path.join(data_dir, '**', f'*.{ext}'), recursive=True):
            if ext in ['txt', 'md']:
                text = read_txt_md(file_path)
            elif ext == 'pdf':
                text = read_pdf(file_path)
            elif ext == 'docx':
                text = read_docx(file_path)
            else:
                continue
            meta = extract_metadata_from_text(text)
            chunks = chunk_text(text)
            for idx, chunk in enumerate(chunks):
                records.append({
                    'file': file_path,
                    'chunk_id': idx,
                    'text': chunk,
                    **meta
                })
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = ingest_documents(os.path.join(os.path.dirname(__file__), '../mock_data'))
    df.to_csv(os.path.join(os.path.dirname(__file__), 'document_chunks.csv'), index=False)
    print(f"Ingested and chunked {len(df)} chunks. Saved to document_chunks.csv.")
