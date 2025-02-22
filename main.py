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
    # Add a welcome message with user instructions
    st.title("🏛️ Νομικός Βοηθός για Αστυνομικούς")
    st.markdown("""
    ### Καλώς ήρθατε στον Νομικό Βοηθό!
    Αυτή η εφαρμογή σας βοηθά να:
    - 📚 Αναζητήσετε νομικές διατάξεις
    - 📋 Δείτε πρόσφατες ενημερώσεις
    - 🔍 Βρείτε πληροφορίες για συγκεκριμένα άρθρα
    """)

    # Add a simple counter in the sidebar to demonstrate interactivity
    st.sidebar.title("Διαχείριση")
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    st.sidebar.subheader("Δοκιμαστικό Κουμπί")
    if st.sidebar.button("Πατήστε με! 🖱️"):
        st.session_state.counter += 1
    st.sidebar.write(f"Πατήσατε το κουμπί {st.session_state.counter} φορές")

    # Update button in sidebar
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

    # Search functionality with placeholder text
    search_query = st.text_input("🔍 Αναζήτηση νομικών διατάξεων...", 
                                placeholder="π.χ. κατοικίδια, ποινές, πρόστιμα...")

    # Main content area with category description
    st.header(f"📖 {category}")

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
                    ---
                    """)

    # Search results with improved formatting
    if search_query:
        results = search_content(search_query, CATEGORIES)
        if results:
            st.subheader("🔍 Αποτελέσματα Αναζήτησης")
            for result in results:
                with st.expander(f"📑 {result['title']}"):
                    st.markdown(f"""
                    **Κατηγορία:** {result['category']}
                    **Υποκατηγορία:** {result['subcategory']}

                    {result['content']}
                    """)
        else:
            st.info("Δεν βρέθηκαν αποτελέσματα για την αναζήτησή σας.")

if __name__ == "__main__":
    main()