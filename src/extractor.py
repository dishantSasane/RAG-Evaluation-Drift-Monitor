import nltk
from pypdf import PdfReader

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

def extract_and_tokenize(pdf_path: str) -> list[str]:
    """
    Parses a PDF file from a storage boundary, strips white spaces, 
    and transforms the block stream into decoupled sentence arrays.
    """
    reader = PdfReader(pdf_path)
    full_text = ""
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    if not full_text.strip():
        raise ValueError(f"PDF extraction yielded zero character items from data path: {pdf_path}")
        
    sentences = nltk.sent_tokenize(full_text)
    return sentences

def group_chunks(sentences: list[str], group_size: int = 4, overlap: int = 1) -> list[str]:
    """
    Groups sentence streams into discrete overlapping arrays to preserve structural boundaries.
    """
    chunked_sentences = []
    for i in range(0, len(sentences), group_size - overlap):
        batch = sentences[i : i + group_size]
        if batch:
            chunked_sentences.append(" ".join(batch))
        if i + group_size >= len(sentences):
            break
    return chunked_sentences