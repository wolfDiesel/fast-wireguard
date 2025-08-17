"""
Internationalization support for FastWG
"""

import os
import gettext as gettext_module
from typing import Optional


class I18nManager:
    """Internationalization manager"""
    
    def __init__(self, locale_dir: str = None):
        self.locale_dir = locale_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'locale'
        )
        self.current_language = 'en'
        self._translation = None
        self._setup_translation()
    
    def _setup_translation(self):
        """Setup translation based on environment"""
        # Get language from environment
        lang = os.environ.get('FASTWG_LANG', 'en')
        
        # Fallback to system locale if not set
        if lang == 'en':
            system_lang = os.environ.get('LANG', 'en_US.UTF-8')
            if system_lang.startswith('ru'):
                lang = 'ru'
        
        self.set_language(lang)
    
    def set_language(self, language: str):
        """Set current language"""
        self.current_language = language
        
        try:
            if language == 'ru':
                # For Russian, use our custom translations
                self._translation = gettext_module.translation(
                    'fastwg',
                    self.locale_dir,
                    languages=['ru'],
                    fallback=True
                )
            else:
                # For English, use no translation (identity)
                self._translation = gettext_module.NullTranslations()
        except Exception:
            # Fallback to English
            self._translation = gettext_module.NullTranslations()
    
    def gettext(self, message: str) -> str:
        """Get translated message"""
        if self._translation:
            return self._translation.gettext(message)
        return message
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Get translated message with plural forms"""
        if self._translation:
            return self._translation.ngettext(singular, plural, n)
        return singular if n == 1 else plural


# Global instance
_i18n = I18nManager()


def gettext(message: str) -> str:
    """Get translated message"""
    return _i18n.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Get translated message with plural forms"""
    return _i18n.ngettext(singular, plural, n)


def set_language(language: str):
    """Set current language"""
    _i18n.set_language(language)


def get_current_language() -> str:
    """Get current language"""
    return _i18n.current_language
