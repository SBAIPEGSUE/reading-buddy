"""
Claude-powered spoiler-free reading assistant.
Uses the Anthropic API with a carefully constructed system prompt
to ensure answers never reveal content beyond the reader's current position.
"""

import os
import time
from typing import List, Optional
from dotenv import load_dotenv
import anthropic

load_dotenv()  # reads .env file and makes its values available via os.environ


def _build_system_prompt(title: str, author: str, progress: str) -> str:
    """
    Construct the system prompt that enforces spoiler-free behaviour.

    The progress string describes where the user is, e.g.:
        "page 120 of 350"
        "chapter 5"
        "45% through"
    """
    return f"""You are a knowledgeable and enthusiastic reading assistant helping someone who is currently reading "{title}" by {author}.

The reader has reached: {progress}.

Your strict rules:
1. NEVER reveal plot events, character developments, or information that occurs AFTER the reader's current position.
2. If a question can only be answered with spoiler content, say so warmly and offer to discuss it once they reach that point.
3. You MAY discuss themes, writing style, historical context, and authorial background freely — these are not spoilers.
4. Keep answers conversational and encouraging — you want the reader to enjoy the book.
5. If you are unsure whether something is a spoiler, err on the side of caution."""


def ask_question(
    question: str,
    title: str,
    author: str,
    progress: str,
    conversation_history: Optional[List[dict]] = None,
) -> str:
    """
    Send the reader's question to Claude and return the answer.

    Args:
        question:             The reader's question.
        title:                Book title.
        author:               Book author.
        progress:             Human-readable progress string (e.g. "page 120 of 350").
        conversation_history: List of prior {role, content} dicts for multi-turn chat.

    Returns:
        Claude's answer as a string.

    Raises:
        EnvironmentError: If ANTHROPIC_API_KEY is not set.
        anthropic.APIError: On API failures.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Please add your key to the .env file."
        )

    client = anthropic.Anthropic(api_key=api_key)

    messages = list(conversation_history or [])
    messages.append({"role": "user", "content": question})

    # Retry up to 3 times if the API is temporarily overloaded
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=_build_system_prompt(title, author, progress),
                messages=messages,
            )
            return response.content[0].text
        except anthropic.APIStatusError as e:
            if e.status_code == 529 and attempt < 2:
                time.sleep(2 ** attempt)  # wait 1s, then 2s before retrying
            else:
                raise
