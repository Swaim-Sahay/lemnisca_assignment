
import re
import backend.config as config

COMPLEX_KEYWORDS = {"compare", "difference", "why", "troubleshoot", "issue", "error", "explain", "resolve"}

def classify_query(query: str) -> str:
    """
    Deterministically classify a query as 'simple' or 'complex'.
    Returns: 'simple' or 'complex'
    """
    query_lower = query.lower()
    
    # Rule 1: Length > 15 words
    words = query_lower.split()
    if len(words) > 15:
        return "complex"
        
    # Rule 2: Multi-part questions (more than one question mark)
    if query.count('?') > 1:
        return "complex"
        
    # Rule 3: Complex intent keywords
    if any(keyword in words for keyword in COMPLEX_KEYWORDS):
        return "complex"
        
    return "simple"

def get_model_for_classification(classification: str) -> str:
    """Returns the Groq model string based on classification."""
    if classification == "complex":
        return config.GROQ_MODEL_COMPLEX
    return config.GROQ_MODEL_SIMPLE
