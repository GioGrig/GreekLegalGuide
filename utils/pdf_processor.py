import PyPDF2
import re

def process_pdf(file_path):
    """
    Process PDF files and extract text with Greek character support
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
    
    # Clean and normalize text
    text = clean_text(text)
    return text

def clean_text(text):
    """
    Clean and normalize extracted text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Normalize Greek characters
    text = text.replace('ά', 'α').replace('έ', 'ε').replace('ή', 'η')
    text = text.replace('ί', 'ι').replace('ό', 'ο').replace('ύ', 'υ')
    text = text.replace('ώ', 'ω')
    
    return text.strip()
