import streamlit as st
import pandas as pd
from utils.pdf_processor import process_pdf
from utils.search import search_content
from data.categories import CATEGORIES

# Set page config
st.set_page_config(
    page_title="Νομική Αναφορά",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("Νομική Αναφορά για Αστυνομικούς")
    
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
