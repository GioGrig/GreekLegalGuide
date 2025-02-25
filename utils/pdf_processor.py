import PyPDF2
import re
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import os

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

def get_category_from_filename(filename: str) -> Tuple[str, str]:
    """
    Determine the main category and subcategory based on filename
    """
    filename = filename.lower()
    categories = {
        'ποινικοσ κωδικασ': ('ΠΟΙΝΙΚΟΣ ΚΩΔΙΚΑΣ', ''),
        'ναρκωτικων': ('ΝΑΡΚΩΤΙΚΑ', 'Διακίνηση και Κατοχή'),
        'οπλων': ('ΟΠΛΑ', 'Οπλοκατοχή'),
        'κατοικιδια': ('ΝΟΜΟΣ ΠΕΡΙ ΚΑΤΟΙΚΙΔΙΩΝ', 'Βασικές Διατάξεις'),
        'ενδοοικογενειακης': ('ΕΝΔΟΟΙΚΟΓΕΝΕΙΑΚΗ ΒΙΑ', 'Βασικές Διατάξεις'),
        'δικονομιασ': ('ΠΟΙΝΙΚΗ ΔΙΚΟΝΟΜΙΑ', 'Γενικές Διατάξεις'),
        'poinikoi_nomoi': ('ΕΙΔΙΚΟΙ ΠΟΙΝΙΚΟΙ ΝΟΜΟΙ', 'Γενικές Διατάξεις')
    }

    for key, (category, subcategory) in categories.items():
        if key in filename:
            return category, subcategory
    return '', 'Βασικές Διατάξεις'

def process_pdf_to_articles(file_path: str) -> List[Dict[str, str]]:
    """
    Process a PDF file and return structured articles with complete content
    """
    text = process_pdf(file_path)
    if not text:
        return []

    # Get the base category from filename
    filename = os.path.basename(file_path)
    main_category, default_subcategory = get_category_from_filename(filename)

    articles = []
    current_article = None
    current_subcategory = default_subcategory

    # Split text into sections
    sections = text.split('\n\n')

    # Patterns for article and category detection
    article_pattern = re.compile(r'(?:Άρθρο|ΑΡΘΡΟ)\s+(\d+[α-ω]?)\s*[-–]\s*(.+?)(?=\n|$)', re.IGNORECASE)
    category_pattern = re.compile(r'(?:ΚΕΦΑΛΑΙΟ|ΜΕΡΟΣ|ΤΜΗΜΑ|ΤΙΤΛΟΣ)\s+[ΑΒΓΔ\d]+\s*[-–]\s*(.+?)(?=\n|$)', re.IGNORECASE)

    for section in sections:
        if not section.strip():
            continue

        # Check for category headers
        category_match = category_pattern.search(section)
        if category_match:
            current_subcategory = category_match.group(1).strip()
            continue

        # Check for article headers
        article_match = article_pattern.search(section)
        if article_match:
            if current_article and current_article['content'].strip():
                articles.append(current_article)

            article_num = article_match.group(1)
            article_title = article_match.group(2).strip()

            current_article = {
                'title': f"Άρθρο {article_num} - {article_title}",
                'content': section.strip(),
                'category': main_category,
                'subcategory': current_subcategory,
                'law': f"{main_category} {article_num}",
                'penalty': ''
            }
        elif current_article:
            current_article['content'] += '\n' + section.strip()
            # Look for penalty information
            if any(word in section.lower() for word in ['τιμωρείται', 'ποινή', 'κύρωση', 'πρόστιμο']):
                current_article['penalty'] = section.strip()

    # Add the last article if it exists and has content
    if current_article and current_article['content'].strip():
        articles.append(current_article)

    return articles

def process_multiple_pdfs(pdf_directory: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Process all PDFs in a directory and organize articles by category
    """
    all_articles = {}
    pdf_dir = Path(pdf_directory)

    for pdf_file in pdf_dir.glob("*.pdf"):
        try:
            logger.info(f"Processing {pdf_file}")
            articles = process_pdf_to_articles(str(pdf_file))

            # Organize articles by their determined categories
            for article in articles:
                category = article["category"]
                if category not in all_articles:
                    all_articles[category] = {}

                subcategory = article["subcategory"]
                if subcategory not in all_articles[category]:
                    all_articles[category][subcategory] = []

                all_articles[category][subcategory].append(article)

        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {str(e)}")
            continue

    return all_articles