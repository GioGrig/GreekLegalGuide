import json
import os
from typing import Dict, Optional

def load_welcome_messages() -> Dict[str, str]:
    """Load welcome messages from JSON file."""
    try:
        with open('data/welcome_messages.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {
            "default": "Καλωσήρθατε στον Νομικό Βοηθό",
            "departments": {}
        }

def save_welcome_messages(messages: Dict) -> None:
    """Save welcome messages to JSON file."""
    with open('data/welcome_messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def get_welcome_message(department: Optional[str] = None) -> str:
    """Get welcome message for specific department or default message."""
    messages = load_welcome_messages()
    if department and department in messages['departments']:
        return messages['departments'][department]
    return messages['default']

def update_department_message(department: str, message: str) -> None:
    """Update welcome message for a specific department."""
    messages = load_welcome_messages()
    messages['departments'][department] = message
    save_welcome_messages(messages)

def update_default_message(message: str) -> None:
    """Update the default welcome message."""
    messages = load_welcome_messages()
    messages['default'] = message
    save_welcome_messages(messages)

def get_departments() -> list:
    """Get list of all departments."""
    messages = load_welcome_messages()
    return list(messages['departments'].keys())
