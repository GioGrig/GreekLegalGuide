import streamlit as st
import pandas as pd
from utils.pdf_processor import process_pdf_to_articles, process_multiple_pdfs
from utils.search import search_content
from utils.law_updater import LawUpdater, update_categories_from_database
from data.categories import CATEGORIES
import json
from datetime import datetime
import logging
import tempfile
import os
from pathlib import Path
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_binary_file_downloader_html(bin_file_path, file_label='File'):
    """Generate a download link for binary files"""
    try:
        with open(bin_file_path, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<a href="data:application/pdf;base64,{b64}" download="{os.path.basename(bin_file_path)}">{file_label}</a>'
    except Exception as e:
        logger.error(f"Error creating download link for {bin_file_path}: {str(e)}")
        return None

def get_source_url(category: str, subcategory: str = None) -> tuple:
    """Get the official source URL or PDF path for a given category and optional subcategory"""
    law_updater = LawUpdater()
    source = law_updater.sources.get(category, "#")

    # Handle nested sources (e.g., ΑΣΤΥΝΟΜΙΚΟ ΠΡΟΣΩΠΙΚΟ category)
    if isinstance(source, dict) and subcategory:
        source = source.get(subcategory, "#")

    # Handle local PDF files
    if source and isinstance(source, str) and source.startswith("/"):
        pdf_path = source[1:]  # Remove leading slash
        if os.path.exists(pdf_path):
            return (pdf_path, True)  # Return path and flag indicating it's a local file
    return (source, False)  # Return URL and flag indicating it's an external link

def display_pdf_download(source_path: str, custom_label: str = None, subcategory: str = None) -> None:
    """Display PDF download button with custom label"""
    st.markdown("### 📄 Πλήρες Κείμενο Νόμου")
    try:
        # Ensure the path exists and is readable
        if not os.path.exists(source_path):
            logger.error(f"PDF file not found: {source_path}")
            st.error("Το αρχείο PDF δεν είναι διαθέσιμο.")
            return

        # Generate a unique key for each download button based on the filename, custom label, and subcategory
        key_parts = [
            os.path.basename(source_path).replace(' ', '_'),
            custom_label.replace(' ', '_') if custom_label else '',
            subcategory.replace(' ', '_') if subcategory else ''
        ]
        button_key = f"download_btn_{'_'.join(filter(None, key_parts))}"

        with open(source_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
            st.download_button(
                label=custom_label or "Κατέβασμα PDF",
                data=PDFbyte,
                file_name=os.path.basename(source_path),
                mime='application/pdf',
                key=button_key
            )
    except Exception as e:
        logger.error(f"Error reading PDF {source_path}: {str(e)}")
        st.error("Το αρχείο PDF δεν είναι διαθέσιμο.")

# Set page config
st.set_page_config(
    page_title="Νομικός Βοηθός",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for better readability and mobile responsiveness
st.markdown("""
<style>
    .law-article {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .article-title {
        color: #1f4e79;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    .article-content {
        font-size: 1em;
        line-height: 1.6;
        margin: 15px 0;
        white-space: pre-wrap;  # Add this to preserve formatting
    }
    .article-penalty {
        color: #721c24;
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .sidebar-welcome {
        background-color: #1f4e79;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
        font-size: 0.9em;
        line-height: 1.5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .feedback-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
    }
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .law-article {
            padding: 10px;
        }
        .article-title {
            font-size: 1.1em;
        }
        .article-content {
            font-size: 0.9em;
        }
        .sidebar-welcome {
            font-size: 0.8em;
            padding: 10px;
        }
    }
    /* Version badge */
    .version-badge {
        background-color: #1f4e79;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

def show_help():
    """Display help and documentation"""
    st.markdown("""
    ### 📖 Οδηγίες Χρήσης

    1. **Πλοήγηση**
       - Χρησιμοποιήστε το κουμπί 🏠 Αρχική για να επιστρέψετε στην αρχική σελίδα
       - Χρησιμοποιήστε το μενού στα αριστερά για να επιλέξετε κατηγορία
       - Κάθε κατηγορία περιέχει υποκατηγορίες με σχετικά άρθρα

    2. **Αναζήτηση**
       - Πληκτρολογήστε λέξεις-κλειδιά στο πεδίο αναζήτησης
       - Τα αποτελέσματα θα εμφανιστούν αυτόματα

    3. **Ενημερώσεις**
       - Το σύστημα ενημερώνεται αυτόματα με νέες νομικές διατάξεις
       - Δείτε την ημερομηνία τελευταίας ενημέρωσης στο κάτω μέρος

    4. **Προβολή Άρθρων**
       - Κάντε κλικ στα βέλη ▼ για να δείτε το πλήρες περιεχόμενο
       - Οι ποινές εμφανίζονται με κόκκινο φόντο
    """)

def process_uploaded_files(uploaded_files):
    """Process uploaded PDF files and update categories"""
    temp_dir = Path("temp_pdfs")
    temp_dir.mkdir(exist_ok=True)

    try:
        # Save uploaded files temporarily
        for uploaded_file in uploaded_files:
            temp_path = temp_dir / uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        # Process all PDFs in the temp directory
        all_articles = process_multiple_pdfs(str(temp_dir))

        # Update session state with new articles
        for category, subcategories in all_articles.items():
            if category not in st.session_state.cached_categories:
                st.session_state.cached_categories[category] = {}

            for subcategory, articles in subcategories.items():
                if subcategory not in st.session_state.cached_categories[category]:
                    st.session_state.cached_categories[category][subcategory] = []
                st.session_state.cached_categories[category][subcategory].extend(articles)

        return True
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}")
        return False
    finally:
        # Cleanup temp files
        for file in temp_dir.glob("*.pdf"):
            file.unlink()
        temp_dir.rmdir()


def main():
    try:
        # Initialize session state for categories if not exists
        if 'cached_categories' not in st.session_state:
            st.session_state.cached_categories = CATEGORIES

        # Display version badge
        version_date = datetime.now()
        st.markdown(f"""
        <div style="text-align: right;">
            <span class="version-badge">v.{version_date.strftime('%Y.%m.%d')}</span>
        </div>
        """, unsafe_allow_html=True)

        # Main title
        st.title("🏛️ Νομικός Βοηθός για Αστυνομικούς")

        # Sidebar navigation
        st.sidebar.title("Πλοήγηση")

        # Help button
        if st.sidebar.button("ℹ️ Βοήθεια"):
            st.session_state.show_help = True
            show_help()

        # Admin section for PDF uploads
        with st.sidebar.expander("🔒 Διαχείριση Περιεχομένου"):
            st.write("Ανέβασμα νέων νομικών κειμένων:")
            uploaded_files = st.file_uploader(
                "Επιλέξτε PDF αρχεία",
                type=['pdf'],
                accept_multiple_files=True,
                key="pdf_uploader"
            )

            if uploaded_files:
                if st.button("Ενημέρωση Περιεχομένου"):
                    with st.spinner("Επεξεργασία αρχείων..."):
                        success = process_uploaded_files(uploaded_files)
                        if success:
                            st.success("Το περιεχόμενο ενημερώθηκε επιτυχώς!")
                        else:
                            st.error("Παρουσιάστηκε σφάλμα κατά την επεξεργασία των αρχείων.")


        # Category selection
        selected_category = st.sidebar.selectbox(
            "Επιλέξτε Κατηγορία:",
            list(st.session_state.cached_categories.keys())
        )

        # Welcome message in sidebar (permanent fixture)
        st.sidebar.markdown("""
        <div class="sidebar-welcome">
        Αυτή η διαδικτυακή εφαρμογή δημιουργήθηκε με τη βοήθεια τεχνητής νοημοσύνης από μάχιμους αστυνομικούς για μάχιμους αστυνομικούς. Είθε η χρήση της τεχνολογίας να μας βοηθήσει στην εκπλήρωση του δύσκολου και πολλές φορές επικίνδυνου έργο μας, παρέχοντας τις καλύτερες δυνατές υπηρεσίες προς τον πολίτη όπως έχουμε ορκιστεί. Καλές υπηρεσίες, να προσέχετε ο ένας τον άλλον, και πάντα το σχόλασμα να σας βρίσκει γέρους και με τις οικογένειές σας.
        </div>
        """, unsafe_allow_html=True)

        # Search with loading state
        search_query = st.text_input(
            "🔍 Αναζήτηση νομικών διατάξεων...",
            placeholder="π.χ. κατοικίδια, ποινές, πρόστιμα..."
        )

        if selected_category:
            with st.spinner("Φόρτωση περιεχομένου..."):
                st.header(f"📖 {selected_category}")

                # Display category content
                if selected_category in st.session_state.cached_categories:
                    for subcategory, articles in st.session_state.cached_categories[selected_category].items():
                        with st.expander(f"📚 {subcategory}", expanded=True):
                            # Get source for category/subcategory combination
                            source_path, is_local = get_source_url(selected_category, subcategory)

                            if source_path != "#":
                                if is_local:
                                    if selected_category == "ΕΝΔΟΟΙΚΟΓΕΝΕΙΑΚΗ ΒΙΑ (Ν.3500/2006)":
                                        if subcategory in ["Ορισμοί", "Σωματική Βία"]:
                                            display_pdf_download(source_path, "Κατέβασμα Νόμου 3500/2006 (PDF)", subcategory)
                                        elif subcategory == "Οδηγός Αντιμετώπισης":
                                            display_pdf_download(source_path, "Κατέβασμα Οδηγού Αντιμετώπισης (PDF)", subcategory)
                                    else:
                                        display_pdf_download(source_path, None, subcategory)
                                else:
                                    st.markdown(f"""
                                    <div style="text-align: right; margin-bottom: 20px;">
                                        <a href="{source_path}" target="_blank" style="color: #1f4e79;">
                                            📄 Πλήρες Κείμενο Νόμου
                                        </a>
                                    </div>
                                    """, unsafe_allow_html=True)

                            # Display articles
                            for article in articles:
                                st.markdown(f"""
                                <div class="law-article">
                                    <div class="article-title">{article['title']}</div>
                                    <strong>Νόμος:</strong> {article['law']}
                                    <div class="article-content">{article['content']}</div>
                                    <div class="article-penalty">
                                        <strong>Ποινή:</strong> {article['penalty']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

        # Search results
        if search_query:
            with st.spinner("Αναζήτηση..."):
                try:
                    results = search_content(search_query, st.session_state.cached_categories)
                    if results:
                        st.subheader("🔍 Αποτελέσματα Αναζήτησης")
                        for result in results:
                            with st.expander(f"📑 {result['title']}", expanded=True):
                                st.markdown(f"""
                                <div class="law-article">
                                    <strong>Κατηγορία:</strong> {result['category']}
                                    <br>
                                    <strong>Υποκατηγορία:</strong> {result['subcategory']}
                                    <div class="article-content">{result['content']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Δεν βρέθηκαν αποτελέσματα για την αναζήτησή σας.")
                except Exception as e:
                    logger.error(f"Search error: {str(e)}")
                    st.error("Παρουσιάστηκε σφάλμα κατά την αναζήτηση. Παρακαλώ δοκιμάστε ξανά.")

        # Feedback section
        st.markdown("---")
        with st.expander("📝 Αναφορά Προβλήματος"):
            st.markdown("""
            <div class="feedback-box">
            Εάν εντοπίσατε κάποιο πρόβλημα ή έχετε προτάσεις βελτίωσης, παρακαλούμε επικοινωνήστε μαζί μας:

            📧 Email: support@nomikos-voithos.gr
            </div>
            """, unsafe_allow_html=True)

        # Footer
        st.markdown(f"""
        <div style="text-align: center; color: #666;">
            Τελευταία ενημέρωση: {version_date.strftime('%d/%m/%Y %H:%M')}
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("Παρουσιάστηκε σφάλμα. Παρακαλώ ανανεώστε τη σελίδα ή επικοινωνήστε με την υποστήριξη.")

if __name__ == "__main__":
    main()