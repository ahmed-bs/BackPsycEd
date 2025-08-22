#!/usr/bin/env python
"""
Test script to verify ProfileItem translation functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ProfileItem.translation_utils import translation_service

def test_translation():
    """Test the translation functionality"""
    print("Testing ProfileItem translation functionality...")
    
    # Test data
    test_data = {
        'name': 'Test Item',
        'name_ar': '',
        'description': 'This is a test description',
        'description_ar': '',
        'comentaire': 'Test comment',
        'commentaire_ar': '',
    }
    
    print("Original data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Apply translation
    fields_to_translate = ['name', 'description', 'comentaire']
    translated_data = translation_service.auto_translate_fields(test_data, fields_to_translate)
    
    print("\nTranslated data:")
    for key, value in translated_data.items():
        print(f"  {key}: {value}")
    
    # Test Arabic to French translation
    print("\nTesting Arabic to French translation...")
    arabic_data = {
        'name': '',
        'name_ar': 'عنصر اختبار',
        'description': '',
        'description_ar': 'هذا وصف اختبار',
        'comentaire': '',
        'commentaire_ar': 'تعليق اختبار',
    }
    
    print("Original Arabic data:")
    for key, value in arabic_data.items():
        print(f"  {key}: {value}")
    
    translated_arabic_data = translation_service.auto_translate_fields(arabic_data, fields_to_translate)
    
    print("\nTranslated Arabic data:")
    for key, value in translated_arabic_data.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_translation()
