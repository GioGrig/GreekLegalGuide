import streamlit as st
import pandas as pd
from utils.pdf_processor import process_pdf, process_pdf_to_articles
from utils.search import search_content
from utils.law_updater import LawUpdater, update_categories_from_database
from data.categories import CATEGORIES
import json
from datetime import datetime

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

# Initialize session state for caching
if 'cache_timestamp' not in st.session_state:
    st.session_state.cache_timestamp = datetime.now()
if 'cached_categories' not in st.session_state:
    st.session_state.cached_categories = CATEGORIES

def get_app_version():
    """Get current version of the law database"""
    try:
        with open("data/law_database.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            last_update = data.get('last_update', {})
            if last_update:
                return max(datetime.fromisoformat(date) for date in last_update.values())
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return datetime.now()
    return datetime.now()

def show_help():
    """Display help and documentation"""
    st.markdown("""
    ### 📖 Οδηγίες Χρήσης

    1. **Πλοήγηση**
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
    # Display version badge
    version_date = get_app_version()
    st.markdown(f"""
    <div style="text-align: right;">
        <span class="version-badge">v.{version_date.strftime('%Y.%m.%d')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Main title and welcome message
    st.title("🏛️ Νομικός Βοηθός για Αστυνομικούς")
    st.markdown("""
    ### Καλώς ήρθατε στον Νομικό Βοηθό!
    Αυτή η εφαρμογή παρέχει πρόσβαση στο πλήρες περιεχόμενο των νομικών διατάξεων και άρθρων.
    """)

    # Help button in sidebar
    st.sidebar.title("Πλοήγηση")
    if st.sidebar.button("ℹ️ Βοήθεια"):
        show_help()

    # Category selection with error handling
    try:
        category = st.sidebar.selectbox(
            "Επιλέξτε Κατηγορία:",
            list(st.session_state.cached_categories.keys())
        )
    except Exception as e:
        st.error("Σφάλμα στη φόρτωση κατηγοριών. Παρακαλώ ανανεώστε τη σελίδα.")
        st.stop()

    # Search with loading state
    search_query = st.text_input(
        "🔍 Αναζήτηση νομικών διατάξεων...",
        placeholder="π.χ. κατοικίδια, ποινές, πρόστιμα, άδειες..."
    )

    # Main content area with error handling
    try:
        st.header(f"📖 {category}")

        if category in st.session_state.cached_categories:
            for subcategory, articles in st.session_state.cached_categories[category].items():
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

        # Search results with loading state
        if search_query:
            with st.spinner("Αναζήτηση..."):
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
        st.error("Παρουσιάστηκε σφάλμα κατά την προβολή του περιεχομένου. Παρακαλώ δοκιμάστε ξανά.")
        st.exception(e)

    # Footer with version info
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        Τελευταία ενημέρωση: {version_date.strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()