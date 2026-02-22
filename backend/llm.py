import os
import time
from typing import List, Dict, Any, Tuple
from groq import Groq

# We rely on GROQ_API_KEY environment variable being set.
client = Groq()

def format_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    """Formats the system prompt with context."""
    if not chunks:
        context_str = "No specific context available from the documentation."
    else:
        context_parts = []
        for i, chunk in enumerate(chunks):
            doc = chunk.get('document', 'Unknown')
            page = chunk.get('page', 'Unknown')
            content = chunk.get('content', '')
            context_parts.append(f"--- Document: {doc} (Page {page}) ---\n{content}\n")
        context_str = "\n".join(context_parts)
    
    system_prompt = f"""You are a helpful customer support chatbot for Clearpath, a project management tool.
Answer the user's question based ONLY on the provided documentation context below.
If the answer cannot be found in the context, explicitly state that you don't know or cannot find it in the documentation.
Do NOT mention other project management tools unless they are part of an integration mentioned in the context.

CONTEXT:
{context_str}
"""
    return system_prompt

def generate_answer(query: str, model_name: str, chunks: List[Dict[str, Any]]) -> Tuple[str, Dict[str, int]]:
    """
    Calls the Groq API and returns the response string and token usage.
    """
    system_prompt = format_prompt(query, chunks)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    # We use chat completions API from Groq
    response = client.chat.completions.create(
        messages=messages,
        model=model_name,
        temperature=0.0,
        max_tokens=1024
    )
    
    content = response.choices[0].message.content
    usage = response.usage
    
    tokens = {
        "input": getattr(usage, "prompt_tokens", 0),
        "output": getattr(usage, "completion_tokens", 0)
    }
    
    return content, tokens
