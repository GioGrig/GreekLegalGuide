import PyPDF2
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def process_pdf(file_path: str) -> Optional[str]:
    """
    Process PDF files and extract complete text with enhanced Greek character support
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {str(e)}")
        return None

    # Clean and normalize text
    text = clean_text(text)
    return text

def clean_text(text: str) -> str:
    """
    Enhanced text cleaning with better Greek support and formatting
    """
    # Remove extra whitespace while preserving paragraph breaks
    text = re.sub(r'\s*\n\s*\n\s*', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    # Enhanced Greek character normalization
    greek_chars = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ώ': 'Ω',
        'ϊ': 'ι', 'ϋ': 'υ', 'ΐ': 'ι', 'ΰ': 'υ'
    }

    for accent, base in greek_chars.items():
        text = text.replace(accent, base)

    return text.strip()

def extract_law_sections(text: str) -> List[Dict[str, str]]:
    """
    Enhanced extraction of law sections with better article and category detection
    """
    articles = []
    current_article = {"title": "", "content": "", "law": "", "penalty": "", "category": ""}

    # Improved pattern matching for article numbers and categories
    article_pattern = re.compile(r'Άρθρο\s+(\d+[α-ω]?)\s*[-–]\s*(.+?)(?=\n|$)', re.IGNORECASE)
    category_pattern = re.compile(r'ΚΕΦΑΛΑΙΟ|ΜΕΡΟΣ|ΤΜΗΜΑ|ΤΙΤΛΟΣ\s+[ΑΒΓΔ\d]+\s*[-–]\s*(.+?)(?=\n|$)', re.IGNORECASE)
    penalty_pattern = re.compile(r'(?:τιμωρείται|επιβάλλεται).+?(?:φυλάκιση|κάθειρξη|πρόστιμο|ποινή).+?\.', re.IGNORECASE)

    current_category = ""
    lines = text.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()

        # Detect category changes
        category_match = category_pattern.search(line)
        if category_match:
            current_category = category_match.group(1).strip()
            continue

        # Detect new articles
        article_match = article_pattern.search(line)
        if article_match:
            if current_article["content"]:
                articles.append(current_article.copy())

            article_num = article_match.group(1)
            article_title = article_match.group(2).strip()

            current_article = {
                "title": f"Άρθρο {article_num} - {article_title}",
                "content": line + "\n",
                "law": "Π.Κ. " + article_num,
                "penalty": "",
                "category": current_category
            }
            continue

        # Add content to current article
        if current_article["content"]:
            current_article["content"] += line + "\n"

            # Look for penalty information if not already found
            if not current_article["penalty"]:
                penalty_match = penalty_pattern.search(line)
                if penalty_match:
                    current_article["penalty"] = penalty_match.group(0)

    # Add the last article
    if current_article["content"]:
        articles.append(current_article)

    return articles

def process_pdf_to_articles(file_path: str, law_category: str) -> List[Dict[str, str]]:
    """
    Process a PDF file and return structured articles with complete content
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