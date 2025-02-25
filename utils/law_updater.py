import trafilatura
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

class LawUpdater:
    def __init__(self, data_path: str = "data/law_database.json"):
        self.data_path = data_path
        self.sources = {
            "ΠΟΙΝΙΚΟΣ ΚΩΔΙΚΑΣ": "/attached_assets/Ποινικός-Κώδικας.pdf",
            "ΕΙΔΙΚΟΙ ΠΟΙΝΙΚΟΙ ΝΟΜΟΙ": "/attached_assets/eidikoi_poinikoi_nomoi-poinologi.pdf",
            "ΚΩΔΙΚΑΣ ΠΟΙΝΙΚΗΣ ΔΙΚΟΝΟΜΙΑΣ": "/attached_assets/Κώδικας-Ποινικής-Δικονομίας.pdf",
            "ΝΑΡΚΩΤΙΚΑ": "/attached_assets/nomos peri narkotikon.pdf",
            "ΟΠΛΑ": "/attached_assets/Ν.-2168.1993-ΠΕΡΙ-ΟΠΛΩΝ-ΕΠΙΚΑΙΡΟΠΟΙΗΜΕΝΟΣ.pdf",
            "ΕΝΔΟΟΙΚΟΓΕΝΕΙΑΚΗ ΒΙΑ (Ν.3500/2006)": {
                "Ορισμοί": "/attached_assets/νομος ενδοοικογενειακης βιας.pdf",
                "Σωματική Βία": "/attached_assets/νομος ενδοοικογενειακης βιας.pdf",
                "Οδηγός Αντιμετώπισης": "/attached_assets/Οδηγός αντιμετώπισης ενδοοικογενειακής βίας .pdf"
            },
            "ΝΟΜΙΜΕΣ ΔΙΑΔΙΚΑΣΙΕΣ - 141/1991": "/attached_assets/ΠΔ 141 1991 ΑΡΜΟΔΙΟΤΗΤΕΣ ΚΑΙ ΕΝΕΡΓΕΙΕΣ ΕΛΑΣ.pdf",
            "ΚΟΚ-ΤΡΟΧΟΝΟΜΙΚΑ": "/attached_assets/neoskok.pdf",
            "ΝΟΜΟΣ ΠΕΡΙ ΚΑΤΟΙΚΙΔΙΩΝ": "/attached_assets/ΦΕΚ κατοικιδια.pdf",
            "ΠΟΙΝΙΚΗ ΔΙΚΟΝΟΜΙΑ": "/attached_assets/Κώδικας-Ποινικής-Δικονομίας.pdf",
            "ΑΣΤΥΝΟΜΙΚΟ ΠΡΟΣΩΠΙΚΟ": {
                "Άδειες": "/attached_assets/adeies astynomikoy prosopikoy.pdf",
                "Μεταθέσεις": "/attached_assets/metaueseis astynomikoy prosopikoy.pdf",
                "Κώδικας Δεοντολογίας": "/attached_assets/kodikas deontologias.pdf",
                "Χρήση Οπλισμού": "/attached_assets/nomos peri xrhshs oplismoy.pdf",
                "Πειθαρχικό Δίκαιο": "/attached_assets/peitharxiko dikaio astynomikon.pdf",
                "Χρόνος Εργασίας": "/attached_assets/xronos ergasias astynomikon.pdf",
                "Παροχές και Αποζημιώσεις": "/attached_assets/Παροχές προς προσωπικό τραυματισμοί εν υπηρεσία κτλ.pdf"
            }
        }
        self.last_update = self._load_last_update()

    def _load_last_update(self) -> Dict:
        """Load the last update timestamp for each category"""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('last_update', {})
        return {}

    def _save_data(self, data: Dict) -> None:
        """Save updated data to JSON file"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def fetch_latest_content(self, url: str) -> Optional[str]:
        """Fetch and extract content from URL"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(downloaded)
            return None
        except Exception as e:
            print(f"Error fetching content from {url}: {str(e)}")
            return None

    def process_content(self, content: str) -> Dict:
        """Process raw content into structured data"""
        # This is a placeholder for more sophisticated processing
        # In a real implementation, this would use NLP to extract
        # article numbers, penalties, and categorize content
        sections = content.split('\n\n')
        processed_data = {
            'articles': []
        }

        for section in sections:
            if 'Άρθρο' in section:
                processed_data['articles'].append({
                    'title': section.split('\n')[0],
                    'content': section,
                    'last_updated': datetime.now().isoformat()
                })

        return processed_data

    def update_laws(self) -> bool:
        """Main method to check for updates and process new content"""
        updated = False
        current_data = {
            'categories': {},
            'last_update': {}
        }

        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

        for category, url in self.sources.items():
            print(f"Checking updates for {category}...")
            content = self.fetch_latest_content(url)

            if content:
                processed_data = self.process_content(content)
                if processed_data['articles']:
                    current_data['categories'][category] = processed_data
                    current_data['last_update'][category] = datetime.now().isoformat()
                    updated = True

        if updated:
            self._save_data(current_data)
            print("Law database updated successfully")

        return updated

def update_categories_from_database():
    """Update the CATEGORIES dictionary from the law database"""
    updater = LawUpdater()
    if os.path.exists(updater.data_path):
        with open(updater.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('categories', {})
    return {}