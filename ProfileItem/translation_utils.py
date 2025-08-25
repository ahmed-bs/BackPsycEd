import os
import re
from typing import Optional
from googletrans import Translator
from django.conf import settings

class TranslationService:
    def __init__(self):
        # Initialize the googletrans Translator
        try:
            self.translator = Translator()
            print("googletrans Translator initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize googletrans Translator: {e}")
            self.translator = None
        
        # Fallback translations for common terms (in case googletrans fails)
        self.fallback_translations = {
            # Education terms
            'education': 'التعليم',
            'category': 'فئة',
            'learning': 'التعلم',
            'teaching': 'التدريس',
            'student': 'طالب',
            'teacher': 'معلم',
            'school': 'مدرسة',
            'class': 'فصل',
            'course': 'دورة',
            'lesson': 'درس',
            'item': 'عنصر',
            'domain': 'مجال',
            'comment': 'تعليق',
            'commentaire': 'تعليق',
            
            # Health terms
            'health': 'الصحة',
            'medical': 'طبي',
            'therapy': 'علاج',
            'treatment': 'معالجة',
            'doctor': 'طبيب',
            'patient': 'مريض',
            'hospital': 'مستشفى',
            'medicine': 'دواء',
            
            # General terms
            'this': 'هذا',
            'is': 'هو',
            'a': 'أ',
            'for': 'ل',
            'of': 'من',
            'the': 'ال',
            'and': 'و',
            'with': 'مع',
            'in': 'في',
            'on': 'على',
            'at': 'في',
            'to': 'إلى',
            'from': 'من',
            'by': 'بواسطة',
            'about': 'حول',
            'test': 'اختبار',
            'example': 'مثال',
            'sample': 'عينة',
            'purpose': 'غرض',
            'purposes': 'أغراض',
        }

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text
        Returns language code (e.g., 'en', 'ar', 'fr')
        """
        if not text:
            return None
        
        # Try googletrans language detection first
        if self.translator:
            try:
                result = self.translator.detect(text)
                return result.lang
            except Exception as e:
                print(f"googletrans language detection failed: {e}")
        
        # Fallback to simple language detection based on character sets
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        latin_chars = sum(1 for char in text if '\u0020' <= char <= '\u007F')
        
        if arabic_chars > latin_chars:
            return 'ar'
        elif latin_chars > arabic_chars:
            return 'en'  # Assume English for Latin characters
        else:
            return 'en'  # Default to English

    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> Optional[str]:
        """
        Translate text to target language using googletrans
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'en', 'ar', 'fr')
            source_language: Source language code (optional, will auto-detect if not provided)
        Returns:
            Translated text or None if translation fails
        """
        if not text:
            return None
        
        # Try googletrans translation first
        if self.translator:
            try:
                result = self.translator.translate(
                    text,
                    dest=target_language,
                    src=source_language
                )
                return result.text
            except Exception as e:
                print(f"googletrans translation failed: {e}")
        
        # Fallback to simple translation
        return self.fallback_translate(text, target_language, source_language)

    def fallback_translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> Optional[str]:
        """
        Simple fallback translation using predefined translations
        """
        if target_language == 'ar':
            # Simple English to Arabic translation
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                # Clean the word (remove punctuation)
                clean_word = re.sub(r'[^\w\s]', '', word)
                if clean_word in self.fallback_translations:
                    translated_words.append(self.fallback_translations[clean_word])
                else:
                    # If no translation found, keep the original word
                    translated_words.append(word)
            
            return ' '.join(translated_words)
        
        elif target_language == 'fr':
            # Simple Arabic to French translation (reverse lookup)
            arabic_to_french = {v: k for k, v in self.fallback_translations.items()}
            words = text.split()
            translated_words = []
            
            for word in words:
                if word in arabic_to_french:
                    translated_words.append(arabic_to_french[word])
                else:
                    translated_words.append(word)
            
            return ' '.join(translated_words)
        
        return text

    def auto_translate_fields(self, data: dict, fields_to_translate: list) -> dict:
        """
        Automatically translate fields to ensure:
        - name/description/comentaire always contain French text
        - name_ar/description_ar/commentaire_ar always contain Arabic text
        
        Args:
            data: Dictionary containing the data to process
            fields_to_translate: List of field names to translate (without _ar suffix)
        Returns:
            Updated data dictionary with translated fields
        """
        for field in fields_to_translate:
            ar_field = f"{field}_ar"
            original_value = data.get(field, '')
            if original_value is not None:
                original_value = original_value.strip()
            else:
                original_value = ''
            ar_value = data.get(ar_field, '')
            if ar_value is not None:
                ar_value = ar_value.strip()
            else:
                ar_value = ''
            
            # Case 1: Only main field has content (name/description/comentaire provided)
            if original_value and not ar_value:
                print(f"Processing {field}: main field has content, translating to Arabic")
                
                # Detect language of the main field
                detected_lang = self.detect_language(original_value)
                if not detected_lang:
                    print(f"Could not detect language for {field}: {original_value}")
                    continue
                
                print(f"Detected language for {field}: {detected_lang}")
                
                if detected_lang in ['ar', 'arabic']:
                    # If main field is Arabic, translate to French for main field, keep Arabic in _ar field
                    french_text = self.translate_text(original_value, 'fr', detected_lang)
                    if french_text:
                        data[field] = french_text  # Store French translation in main field
                        data[ar_field] = original_value  # Keep original Arabic in _ar field
                        print(f"Translated Arabic {field} to French: {french_text}")
                    else:
                        print(f"Failed to translate Arabic {field} to French")
                else:
                    # If main field is French/English, translate to Arabic for _ar field
                    arabic_text = self.translate_text(original_value, 'ar', detected_lang)
                    if arabic_text:
                        data[ar_field] = arabic_text  # Store Arabic translation in _ar field
                        print(f"Translated {detected_lang} {field} to Arabic: {arabic_text}")
                    else:
                        print(f"Failed to translate {detected_lang} {field} to Arabic")
            
            # Case 2: Only _ar field has content (name_ar/description_ar/commentaire_ar provided)
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

    def smart_translate_fields(self, data: dict, fields_to_translate: list, changed_fields: list) -> dict:
        """
        Smart translation that only translates fields that haven't changed.
        If a field was changed, its corresponding _ar field will be translated to match.
        If an _ar field was changed, the main field will be translated to match.
        
        Args:
            data: Dictionary containing the data to process
            fields_to_translate: List of field names to translate (without _ar suffix)
            changed_fields: List of fields that were actually changed in the request
        Returns:
            Updated data dictionary with smart translations
        """
        print(f"Starting smart_translate_fields with data: {data}")
        print(f"Fields to translate: {fields_to_translate}")
        print(f"Changed fields: {changed_fields}")
        
        for field in fields_to_translate:
            ar_field = f"{field}_ar"
            original_value = data.get(field, '')
            if original_value is not None:
                original_value = original_value.strip()
            else:
                original_value = ''
            ar_value = data.get(ar_field, '')
            if ar_value is not None:
                ar_value = ar_value.strip()
            else:
                ar_value = ''
            
            # Check if main field was changed
            main_field_changed = field in changed_fields
            ar_field_changed = ar_field in changed_fields
            
            print(f"Processing {field}: main_changed={main_field_changed}, ar_changed={ar_field_changed}")
            
            # Case 1: Main field was changed, translate it to Arabic for _ar field
            if main_field_changed and not ar_field_changed:
                print(f"Main field {field} was changed, translating to Arabic")
                detected_lang = self.detect_language(original_value)
                if detected_lang and detected_lang not in ['ar', 'arabic']:
                    # Main field is French/English, translate to Arabic
                    arabic_text = self.translate_text(original_value, 'ar', detected_lang)
                    if arabic_text:
                        data[ar_field] = arabic_text
                        print(f"Translated French {field} to Arabic: {arabic_text}")
                    else:
                        print(f"Failed to translate French {field} to Arabic")
                elif detected_lang in ['ar', 'arabic']:
                    # If main field is Arabic, translate to French and swap
                    french_text = self.translate_text(original_value, 'fr', detected_lang)
                    if french_text:
                        data[field] = french_text
                        data[ar_field] = original_value
                        print(f"Swapped Arabic {field} to French: {french_text}")
            
            # Case 2: Arabic field was changed, translate it to French for main field
            elif ar_field_changed and not main_field_changed:
                print(f"Arabic field {ar_field} was changed, translating to French")
                detected_lang = self.detect_language(ar_value)
                if detected_lang in ['ar', 'arabic']:
                    french_text = self.translate_text(ar_value, 'fr', detected_lang)
                    if french_text:
                        data[field] = french_text
                        print(f"Translated {ar_field} to French: {french_text}")
                    else:
                        print(f"Failed to translate {ar_field} to French")
                else:
                    # If _ar field is not Arabic, translate main field to Arabic
                    main_lang = self.detect_language(original_value)
                    if main_lang and main_lang not in ['ar', 'arabic']:
                        arabic_text = self.translate_text(original_value, 'ar', main_lang)
                        if arabic_text:
                            data[ar_field] = arabic_text
                            print(f"Translated French {field} to Arabic: {arabic_text}")
            
            # Case 3: Both fields were changed - ensure they're in correct languages
            elif main_field_changed and ar_field_changed:
                print(f"Both {field} and {ar_field} were changed, ensuring correct languages")
                main_lang = self.detect_language(original_value)
                ar_lang = self.detect_language(ar_value)
                
                # Ensure main field is French/English and _ar field is Arabic
                if main_lang in ['ar', 'arabic']:
                    # Main field is Arabic, translate to French
                    french_text = self.translate_text(original_value, 'fr', main_lang)
                    if french_text:
                        data[field] = french_text
                        print(f"Translated Arabic {field} to French: {french_text}")
                
                if ar_lang not in ['ar', 'arabic']:
                    # _ar field is not Arabic, translate main field to Arabic
                    if main_lang and main_lang not in ['ar', 'arabic']:
                        arabic_text = self.translate_text(original_value, 'ar', main_lang)
                        if arabic_text:
                            data[ar_field] = arabic_text
                            print(f"Translated French {field} to Arabic: {arabic_text}")
            
            # Case 4: Neither field was changed - no translation needed
            else:
                print(f"Neither {field} nor {ar_field} was changed, skipping translation")
        
        print(f"Final smart translated data: {data}")
        return data

# Create a global instance
translation_service = TranslationService()
