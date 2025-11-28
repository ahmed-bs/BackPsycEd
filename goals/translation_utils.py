import os
import re
from typing import Optional

class TranslationService:
    def __init__(self):
        # Initialize the googletrans Translator with lazy import
        self.translator = None
        try:
            from googletrans import Translator
            self.translator = Translator()
            print("googletrans Translator initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize googletrans Translator: {e}")
            self.translator = None
        
        # Fallback translations for common terms (in case googletrans fails)
        self.fallback_translations = {
            # Goal terms
            'goal': 'هدف',
            'goals': 'أهداف',
            'objective': 'هدف',
            'objectives': 'أهداف',
            'target': 'هدف',
            'targets': 'أهداف',
            'aim': 'هدف',
            'aims': 'أهداف',
            'purpose': 'غرض',
            'purposes': 'أغراض',
            'achievement': 'إنجاز',
            'achievements': 'إنجازات',
            'outcome': 'نتيجة',
            'outcomes': 'نتائج',
            'result': 'نتيجة',
            'results': 'نتائج',
            'milestone': 'معلم',
            'milestones': 'معالم',
            'deadline': 'موعد نهائي',
            'priority': 'أولوية',
            'priorities': 'أولويات',
            
            # Priority levels
            'high': 'عالي',
            'medium': 'متوسط',
            'low': 'منخفض',
            'urgent': 'عاجل',
            'important': 'مهم',
            'critical': 'حرج',
            'normal': 'عادي',
            
            # Education terms
            'education': 'التعليم',
            'learning': 'التعلم',
            'teaching': 'التدريس',
            'student': 'طالب',
            'teacher': 'معلم',
            'school': 'مدرسة',
            'class': 'فصل',
            'course': 'دورة',
            'lesson': 'درس',
            'progress': 'تقدم',
            'improvement': 'تحسن',
            'development': 'تطوير',
            'growth': 'نمو',
            'success': 'نجاح',
            'performance': 'أداء',
            'evaluation': 'تقييم',
            'assessment': 'تقييم',
            'skill': 'مهارة',
            'skills': 'مهارات',
            'ability': 'قدرة',
            'abilities': 'قدرات',
            'competence': 'كفاءة',
            'competency': 'كفاءة',
            'knowledge': 'معرفة',
            'understanding': 'فهم',
            
            # Health terms
            'health': 'الصحة',
            'medical': 'طبي',
            'patient': 'مريض',
            'doctor': 'طبيب',
            'hospital': 'مستشفى',
            'medicine': 'دواء',
            'behavior': 'سلوك',
            'behavioral': 'سلوكي',
            'psychological': 'نفسي',
            'mental': 'عقلي',
            'emotional': 'عاطفي',
            'social': 'اجتماعي',
            'cognitive': 'إدراكي',
            'physical': 'جسدي',
            'therapy': 'علاج',
            'treatment': 'معالجة',
            'intervention': 'تدخل',
            'support': 'دعم',
            'assistance': 'مساعدة',
            'help': 'مساعدة',
            
            # Action terms
            'improve': 'تحسين',
            'increase': 'زيادة',
            'decrease': 'تقليل',
            'maintain': 'الحفاظ على',
            'develop': 'تطوير',
            'enhance': 'تعزيز',
            'strengthen': 'تقوية',
            'build': 'بناء',
            'create': 'إنشاء',
            'establish': 'تأسيس',
            'achieve': 'تحقيق',
            'reach': 'الوصول إلى',
            'attain': 'تحقيق',
            'complete': 'إكمال',
            'finish': 'إنهاء',
            'master': 'إتقان',
            'learn': 'تعلم',
            'understand': 'فهم',
            'demonstrate': 'إظهار',
            'practice': 'ممارسة',
            'apply': 'تطبيق',
            'use': 'استخدام',
            'utilize': 'استخدام',
            
            # Time terms
            'date': 'تاريخ',
            'time': 'وقت',
            'duration': 'مدة',
            'period': 'فترة',
            'week': 'أسبوع',
            'weeks': 'أسابيع',
            'month': 'شهر',
            'months': 'أشهر',
            'year': 'سنة',
            'years': 'سنوات',
            'day': 'يوم',
            'days': 'أيام',
            'today': 'اليوم',
            'yesterday': 'أمس',
            'tomorrow': 'غداً',
            'morning': 'صباح',
            'afternoon': 'ظهر',
            'evening': 'مساء',
            'night': 'ليل',
            'schedule': 'جدول',
            'deadline': 'موعد نهائي',
            'timeline': 'الجدول الزمني',
            
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
            'description': 'وصف',
            'title': 'عنوان',
            'name': 'اسم',
            'detail': 'تفصيل',
            'details': 'تفاصيل',
            'information': 'معلومات',
            'data': 'بيانات',
            'plan': 'خطة',
            'planning': 'تخطيط',
            'strategy': 'استراتيجية',
            'method': 'طريقة',
            'approach': 'نهج',
            'technique': 'تقنية',
            'way': 'طريقة',
            'means': 'وسيلة',
            'tool': 'أداة',
            'tools': 'أدوات',
            'resource': 'مورد',
            'resources': 'موارد',
            'material': 'مادة',
            'materials': 'مواد',
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
        - title/description always contain French text
        - title_ar/description_ar always contain Arabic text
        
        Args:
            data: Dictionary containing the data to process
            fields_to_translate: List of field names to translate (without _ar suffix)
        Returns:
            Updated data dictionary with translated fields
        """
        for field in fields_to_translate:
            ar_field = f"{field}_ar"
            original_value = data.get(field, '').strip()
            ar_value = data.get(ar_field, '').strip()
            
            # Case 1: Only main field has content (title/description provided)
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
            
            # Case 2: Only _ar field has content (title_ar/description_ar provided)
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
