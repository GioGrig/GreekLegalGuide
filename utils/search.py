def search_content(query, categories):
    """
    Search through legal content with Greek language support
    """
    results = []
    query = query.lower()
    
    for category, subcategories in categories.items():
        for subcategory, articles in subcategories.items():
            for article in articles:
                if (query in article['title'].lower() or 
                    query in article['content'].lower()):
                    results.append({
                        'category': category,
                        'subcategory': subcategory,
                        'title': article['title'],
                        'content': article['content'],
                        'law': article['law']
                    })
    
    return results
