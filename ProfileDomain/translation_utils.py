import os
import re
from typing import Optional
from google.cloud import translate_v2 as translate
from django.conf import settings

class TranslationService:
    def __init__(self):
        # Initialize the Google Cloud Translate client
        # Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable
        # or use service account key file
        try:
            self.client = translate.Client()
        except Exception as e:
            print(f"Warning: Could not initialize Google Cloud Translate client: {e}")
            self.client = None

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text
        Returns language code (e.g., 'en', 'ar', 'fr')
        """
        if not self.client or not text:
            return None
        
        try:
            result = self.client.detect_language(text)
            return result['language']
        except Exception as e:
            print(f"Error detecting language: {e}")
            return None

    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> Optional[str]:
        """
        Translate text to target language
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'en', 'ar', 'fr')
            source_language: Source language code (optional, will auto-detect if not provided)
        Returns:
            Translated text or None if translation fails
        """
        if not self.client or not text:
            return None
        
        try:
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            return result['translatedText']
        except Exception as e:
            print(f"Error translating text: {e}")
            return None

    def auto_translate_fields(self, data: dict, fields_to_translate: list) -> dict:
        """
        Automatically translate fields to ensure:
        - name/description always contain French text
        - name_ar/description_ar always contain Arabic text
        
        Args:
            data: Dictionary containing the data to process
            fields_to_translate: List of field names to translate (without _ar suffix)
        Returns:
            Updated data dictionary with translated fields
        """
        if not self.client:
            print("Warning: Google Cloud Translation client not available. Skipping translation.")
            return data
        
        for field in fields_to_translate:
            ar_field = f"{field}_ar"
            original_value = data.get(field, '').strip()
            ar_value = data.get(ar_field, '').strip()
            
            # Case 1: Only main field has content (name/description provided)
            if original_value and not ar_value:
                print(f"Processing {field}: main field has content, translating to Arabic")
                
                # Detect language of the main field
                detected_lang = self.detect_language(original_value)
                if not detected_lang:
                    print(f"Could not detect language for {field}: {original_value}")
                    continue
                
                print(f"Detected language for {field}: {detected_lang}")
                
                if detected_lang in ['ar', 'arabic']:
                    # If main field is Arabic, translate to French and keep Arabic in _ar field
                    french_text = self.translate_text(original_value, 'fr', detected_lang)
                    if french_text:
                        data[field] = french_text  # Store French in main field
                        data[ar_field] = original_value  # Keep Arabic in _ar field
                        print(f"Translated Arabic {field} to French: {french_text}")
                    else:
                        print(f"Failed to translate Arabic {field} to French")
                else:
                    # If main field is not Arabic, translate to Arabic for _ar field
                    arabic_text = self.translate_text(original_value, 'ar', detected_lang)
                    if arabic_text:
                        data[ar_field] = arabic_text  # Store Arabic translation in _ar field
                        print(f"Translated {detected_lang} {field} to Arabic: {arabic_text}")
                    else:
                        print(f"Failed to translate {detected_lang} {field} to Arabic")
            
            # Case 2: Only _ar field has content (name_ar/description_ar provided)
            elif ar_value and not original_value:
                print(f"Processing {field}: _ar field has content, translating to French")
                
                # Detect language of the _ar field
                detected_lang = self.detect_language(ar_value)
                if not detected_lang:
                    print(f"Could not detect language for {ar_field}: {ar_value}")
                    continue
                
                print(f"Detected language for {ar_field}: {detected_lang}")
                
                if detected_lang in ['ar', 'arabic']:
                    # If _ar field is Arabic, translate to French for main field
                    french_text = self.translate_text(ar_value, 'fr', detected_lang)
                    if french_text:
                        data[field] = french_text  # Store French translation in main field
                        print(f"Translated Arabic {ar_field} to French: {french_text}")
                    else:
                        print(f"Failed to translate Arabic {ar_field} to French")
                else:
                    # If _ar field is not Arabic, this is unexpected but handle it
                    print(f"Warning: {ar_field} contains non-Arabic text: {ar_value}")
            
            # Case 3: Both fields have content - skip translation
            elif original_value and ar_value:
                print(f"Skipping translation for {field} as both {field} and {ar_field} have content")
            
            # Case 4: Neither field has content - skip translation
            else:
                print(f"Skipping translation for {field} as both fields are empty")
        
        return data

# Create a global instance
translation_service = TranslationService() 