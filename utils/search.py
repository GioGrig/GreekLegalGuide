def normalize_greek_text(text):
    """Normalize Greek text for search by removing accents and converting to lowercase"""
    import unicodedata
    text = text.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def search_content(query, categories):
    """
    Search through legal content with enhanced Greek language support
    """
    try:
        results = []
        if not query or not isinstance(query, str):
            return results

        normalized_query = normalize_greek_text(query)

        for category, subcategories in categories.items():
            for subcategory, articles in subcategories.items():
                for article in articles:
                    # Normalize the searchable text
                    normalized_title = normalize_greek_text(article['title'])
                    normalized_content = normalize_greek_text(article['content'])
                    normalized_law = normalize_greek_text(article.get('law', ''))

                    # Check if query exists in any of the normalized fields
                    if (normalized_query in normalized_title or 
                        normalized_query in normalized_content or
                        normalized_query in normalized_law):

                        results.append({
                            'category': category,
                            'subcategory': subcategory,
                            'title': article['title'],
                            'content': article['content'],
                            'law': article.get('law', ''),
                            'penalty': article.get('penalty', '')
                        })

        return results
    except Exception as e:
        import logging
        logging.error(f"Search error: {str(e)}")
        return []