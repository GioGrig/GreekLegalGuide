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

# Custom CSS for better readability of full articles
st.markdown("""
<style>
    .law-article {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
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
</style>
""", unsafe_allow_html=True)

def main():
    # Add a welcome message with user instructions
    st.title("🏛️ Νομικός Βοηθός για Αστυνομικούς")
    st.markdown("""
    ### Καλώς ήρθατε στον Νομικό Βοηθό!
    Αυτή η εφαρμογή παρέχει πρόσβαση στο πλήρες περιεχόμενο των νομικών διατάξεων και άρθρων.

    - 📚 Αναζητήστε νομικές διατάξεις
    - 📋 Δείτε το πλήρες κείμενο κάθε άρθρου
    - 🔍 Εξερευνήστε όλες τις λεπτομέρειες των νόμων
    """)

    # Sidebar navigation
    st.sidebar.title("Πλοήγηση")
    category = st.sidebar.selectbox(
        "Επιλέξτε Κατηγορία:",
        list(CATEGORIES.keys())
    )

    # Search functionality with improved placeholder
    search_query = st.text_input(
        "🔍 Αναζήτηση νομικών διατάξεων...",
        placeholder="π.χ. κατοικίδια, ποινές, πρόστιμα, άδειες..."
    )

    # Main content area
    st.header(f"📖 {category}")

    # Display full content of subcategories and articles
    if category in CATEGORIES:
        for subcategory, articles in CATEGORIES[category].items():
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

    # Enhanced search results
    if search_query:
        results = search_content(search_query, CATEGORIES)
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

if __name__ == "__main__":
    main()