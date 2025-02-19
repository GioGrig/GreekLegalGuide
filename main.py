import streamlit as st
import pandas as pd
from utils.pdf_processor import process_pdf
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

# Custom CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("Νομικός Βοηθός για Αστυνομικούς")

    # Add update button in sidebar
    st.sidebar.title("Διαχείριση")
    if st.sidebar.button("🔄 Ενημέρωση Νομικής Βάσης"):
        with st.spinner("Έλεγχος για ενημερώσεις..."):
            updater = LawUpdater()
            if updater.update_laws():
                st.sidebar.success("Η βάση δεδομένων ενημερώθηκε επιτυχώς!")
            else:
                st.sidebar.info("Δεν βρέθηκαν νέες ενημερώσεις.")

    # Show last update time
    try:
        with open("data/law_database.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            last_update = data.get('last_update', {})
            if last_update:
                last_update_time = max(datetime.fromisoformat(date) for date in last_update.values())
                st.sidebar.text(f"Τελευταία ενημέρωση:\n{last_update_time.strftime('%d/%m/%Y %H:%M')}")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        pass

    # Sidebar for main navigation
    st.sidebar.title("Κατηγορίες")
    category = st.sidebar.selectbox(
        "Επιλέξτε Κατηγορία:",
        list(CATEGORIES.keys())
    )

    # Search functionality
    search_query = st.text_input("🔍 Αναζήτηση νομικών διατάξεων...", "")

    # Main content area
    st.header(category)

    # Display subcategories and articles
    if category in CATEGORIES:
        for subcategory, articles in CATEGORIES[category].items():
            with st.expander(f"📚 {subcategory}"):
                for article in articles:
                    st.markdown(f"""
                    ### {article['title']}
                    **Νόμος:** {article['law']}

                    {article['content']}

                    **Ποινή:** {article['penalty']}
                    """)

    # Search results
    if search_query:
        results = search_content(search_query, CATEGORIES)
        st.subheader("Αποτελέσματα Αναζήτησης")
        for result in results:
            st.markdown(f"""
            #### {result['title']}
            {result['content']}
            """)

if __name__ == "__main__":
    main()