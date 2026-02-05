from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    """Detect language of input text"""
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        logger.warning("Could not detect language, defaulting to English")
        return "en"

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text from source to target language"""
    if source_lang == target_lang:
        return text
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return text

def process_multilingual_query(question: str, target_lang: str = "en") -> tuple:
    """
    Process a multilingual query:
    1. Detect language
    2. Translate to English for RAG
    3. Return translated question and detected language
    """
    detected_lang = detect_language(question)
    
    if detected_lang != target_lang:
        translated_question = translate_text(question, detected_lang, target_lang)
        return translated_question, detected_lang
    
    return question, detected_lang

def translate_response(response: str, target_lang: str) -> str:
    """Translate response back to user's language"""
    if target_lang == "en":
        return response
    
    return translate_text(response, "en", target_lang)
