import PyPDF2
import re

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

def extract_law_sections(text):
    """
    Extract law sections from the processed text
    """
    sections = []
    current_section = ""

    for line in text.split('\n'):
        if line.strip().startswith('Άρθρο'):
            if current_section:
                sections.append(current_section)
            current_section = line
        else:
            current_section += '\n' + line

    if current_section:
        sections.append(current_section)

    return sections