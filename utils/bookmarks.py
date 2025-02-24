import json
from typing import List, Dict
import os
from datetime import datetime

class BookmarkManager:
    def __init__(self, storage_path: str = "data/bookmarks.json"):
        self.storage_path = storage_path
        self._ensure_storage_exists()
        
    def _ensure_storage_exists(self):
        """Ensure the storage directory and file exist"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save_bookmarks({})
            
    def _load_bookmarks(self) -> Dict:
        """Load bookmarks from storage"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _save_bookmarks(self, bookmarks: Dict) -> None:
        """Save bookmarks to storage"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, ensure_ascii=False, indent=2)
            
    def add_bookmark(self, article_id: str, article_data: Dict) -> bool:
        """Add a new bookmark"""
        bookmarks = self._load_bookmarks()
        if article_id not in bookmarks:
            article_data['bookmarked_at'] = datetime.now().isoformat()
            bookmarks[article_id] = article_data
            self._save_bookmarks(bookmarks)
            return True
        return False
        
    def remove_bookmark(self, article_id: str) -> bool:
        """Remove a bookmark"""
        bookmarks = self._load_bookmarks()
        if article_id in bookmarks:
            del bookmarks[article_id]
            self._save_bookmarks(bookmarks)
            return True
        return False
        
    def get_all_bookmarks(self) -> Dict:
        """Get all bookmarks"""
        return self._load_bookmarks()
        
    def is_bookmarked(self, article_id: str) -> bool:
        """Check if an article is bookmarked"""
        bookmarks = self._load_bookmarks()
        return article_id in bookmarks
