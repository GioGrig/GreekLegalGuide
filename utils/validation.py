import logging
from typing import Dict, List, Set, Tuple
import re

logger = logging.getLogger(__name__)

class ReferenceValidator:
    """
    Validates references between sections and articles in the legal database
    to prevent broken links when removing content.
    """
    
    def __init__(self, categories: Dict):
        self.categories = categories
        self.reference_map = {}
        self._build_reference_map()
    
    def _build_reference_map(self) -> None:
        """
        Builds a map of all references between articles and sections.
        """
        for category, subcategories in self.categories.items():
            for subcategory, articles in subcategories.items():
                for article in articles:
                    article_id = f"{category}:{subcategory}:{article['title']}"
                    self.reference_map[article_id] = self._find_references(article['content'])
    
    def _find_references(self, content: str) -> Set[str]:
        """
        Finds all article references in the given content.
        """
        references = set()
        # Match patterns like "Άρθρο 123", "άρθρο 456"
        article_pattern = re.compile(r'[Άά]ρθρο\s+(\d+[α-ω]?)', re.IGNORECASE)
        # Match law references like "Ν.4139/2013", "Π.Κ. 372"
        law_pattern = re.compile(r'(?:Ν\.|Π\.Κ\.|Π\.Δ\.|ΚΠΔ)\s*\d+(?:[α-ω])?(?:/\d{4})?', re.IGNORECASE)
        
        # Find article references
        for match in article_pattern.finditer(content):
            references.add(match.group())
        
        # Find law references
        for match in law_pattern.finditer(content):
            references.add(match.group())
        
        return references
    
    def validate_removal(self, category: str, subcategory: str, article_title: str) -> Tuple[bool, List[str]]:
        """
        Validates if removing an article would create broken references.
        Returns (is_safe, list_of_references)
        """
        target_id = f"{category}:{subcategory}:{article_title}"
        referencing_articles = []
        
        # Check for references to this article
        for article_id, references in self.reference_map.items():
            if any(ref in article_title for ref in references):
                referencing_articles.append(article_id)
        
        is_safe = len(referencing_articles) == 0
        return is_safe, referencing_articles
    
    def validate_section_removal(self, category: str, subcategory: str) -> Tuple[bool, List[str]]:
        """
        Validates if removing an entire section would create broken references.
        Returns (is_safe, list_of_references)
        """
        affected_references = []
        
        # Check all articles in the section
        if category in self.categories and subcategory in self.categories[category]:
            for article in self.categories[category][subcategory]:
                is_safe, references = self.validate_removal(category, subcategory, article['title'])
                if not is_safe:
                    affected_references.extend(references)
        
        return len(affected_references) == 0, list(set(affected_references))

    def get_article_references(self, category: str, subcategory: str, article_title: str) -> Set[str]:
        """
        Gets all references made by a specific article.
        """
        article_id = f"{category}:{subcategory}:{article_title}"
        return self.reference_map.get(article_id, set())

    def update_references(self) -> None:
        """
        Updates the reference map after changes to the categories.
        """
        self.reference_map.clear()
        self._build_reference_map()
