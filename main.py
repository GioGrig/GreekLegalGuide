import streamlit as st
import pandas as pd
from utils.pdf_processor import process_pdf, process_pdf_to_articles
from utils.search import search_content
from utils.law_updater import LawUpdater, update_categories_from_database
from data.categories import CATEGORIES
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def main():
    try:
        # Initialize session state
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

        # Category selection
        selected_category = st.sidebar.selectbox(
            "Επιλέξτε Κατηγορία:",
            list(st.session_state.cached_categories.keys())
        )

        # Welcome message in sidebar (permanent fixture) - moved below categories
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