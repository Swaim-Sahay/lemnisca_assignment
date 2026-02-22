from typing import List

REFUSAL_PHRASES = [
    "i don't know",
    "i don't have",
    "i cannot confirm",
    "i couldn't find",
    "not mentioned",
    "cannot find",
    "i am sorry, but i don't have",
    "the provided documents do not mention"
]

COMPETITORS = [
    "jira",
    "asana",
    "monday.com",
    "trello",
    "clickup",
    "notion"
]

def evaluate_response(response: str, num_chunks: int) -> List[str]:
    """
    Evaluates the final LLM response and retrieved chunks to determine flags.
    Returns: List of flag strings.
    """
    flags = set()
    resp_lower = response.lower()
    
    # Flag 1: refusal
    is_refusal = any(phrase in resp_lower for phrase in REFUSAL_PHRASES)
    if is_refusal:
        flags.add("refusal")
        
    # Flag 2: no_context
    if num_chunks == 0 and not is_refusal:
        flags.add("no_context")
        
    # Flag 3: competitor_mention (Domain-specific check)
    if any(competitor in resp_lower for competitor in COMPETITORS):
        flags.add("competitor_mention")
        
    return list(flags)
