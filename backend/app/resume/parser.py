import re
from pathlib import Path
from typing import Dict, Any, List
import pypdf
import docx

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

def extract_text_from_pdf(file_path: Path) -> str:
    """Extract plain text from a PDF file using pypdf."""
    text_content = []
    try:
        reader = pypdf.PdfReader(str(file_path))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    return "\n\n".join(text_content).strip()

def extract_text_from_docx(file_path: Path) -> str:
    """Extract plain text from a Word document (.docx) using python-docx."""
    text_content = []
    try:
        doc = docx.Document(str(file_path))
        for para in doc.paragraphs:
            if para.text.strip():
                text_content.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_content.append(" | ".join(row_text))
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    return "\n".join(text_content).strip()

def parse_resume_document(file_path: Path, file_type: str) -> Dict[str, Any]:
    """Parse resume document and extract text and preliminary metadata."""
    file_type = file_type.lower().strip(".")
    if file_type == "pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported resume file type: {file_type}. Supported types: pdf, docx")

    # Extract basic metadata
    emails = list(set(re.findall(EMAIL_REGEX, raw_text)))
    phones = list(set(re.findall(PHONE_REGEX, raw_text)))

    return {
        "raw_text": raw_text,
        "word_count": len(raw_text.split()),
        "character_count": len(raw_text),
        "detected_emails": emails,
        "detected_phones": phones,
    }
