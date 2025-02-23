import PyPDF2
import re
from typing import List, Dict

def process_pdf(file_path):
    """
    Process PDF files and extract text with enhanced Greek character support
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error processing PDF {file_path}: {str(e)}")
        return None

    # Clean and normalize text with enhanced Greek support
    text = clean_text(text)
    return text

def clean_text(text):
    """
    Clean and normalize extracted text with enhanced Greek character support
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Enhanced Greek character normalization
    greek_chars = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ώ': 'Ω',
        'ϊ': 'ι', 'ϋ': 'υ', 'ΐ': 'ι', 'ΰ': 'υ'
    }

    for accent, base in greek_chars.items():
        text = text.replace(accent, base)

    return text.strip()

def extract_law_sections(text) -> List[Dict[str, str]]:
    """
    Extract law sections from the processed text with improved article detection
    Returns a list of dictionaries containing article information
    """
    articles = []
    current_article = {"title": "", "content": "", "law": "", "penalty": ""}

    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()

        # Detect article starts
        if line.startswith('Άρθρο') or line.startswith('ΑΡΘΡΟ'):
            if current_article["content"]:  # Save previous article if exists
                articles.append(current_article.copy())

            # Start new article
            current_article = {
                "title": line,
                "content": line + "\n",
                "law": "",  # Will be set based on context
                "penalty": ""  # Will be extracted from content if available
            }

        # Detect law reference
        elif "Ν." in line or "Π.Δ." in line:
            current_article["law"] = line

        # Detect penalties (common penalty-related phrases in Greek)
        elif any(phrase in line.lower() for phrase in ["ποινή", "κύρωση", "πρόστιμο", "φυλάκιση"]):
            current_article["penalty"] = line

        # Add line to current article's content
        else:
            current_article["content"] += line + "\n"

    # Add the last article
    if current_article["content"]:
        articles.append(current_article)

    return articles

def process_pdf_to_articles(file_path, law_category) -> List[Dict[str, str]]:
    """
    Process a PDF file and return structured articles with full content
    """
    text = process_pdf(file_path)
    if text:
        articles = extract_law_sections(text)
        # Add category information to each article
        for article in articles:
            if not article["law"]:
                article["law"] = law_category
        return articles
    return []