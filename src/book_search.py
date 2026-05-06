"""
Book search via the Open Library API.
Docs: https://openlibrary.org/developers/api
No API key required.
"""

import requests

SEARCH_URL = "https://openlibrary.org/search.json"


def search_books(query: str, max_results: int = 8) -> list[dict]:
    """
    Search Open Library for books matching `query`.

    Returns a list of dicts, each with:
        title      (str)
        author     (str)
        year       (int | None)
        pages      (int | None)
        edition    (str | None)
        ol_key     (str)  — Open Library work identifier
    """
    if not query.strip():
        return []

    try:
        response = requests.get(
            SEARCH_URL,
            params={"q": query, "limit": max_results, "fields": "key,title,author_name,first_publish_year,number_of_pages_median,edition_count"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Could not reach Open Library: {e}") from e

    docs = response.json().get("docs", [])
    return [_parse_doc(doc) for doc in docs]


def _parse_doc(doc: dict) -> dict:
    authors = doc.get("author_name", [])
    return {
        "title": doc.get("title", "Unknown title"),
        "author": ", ".join(authors) if authors else "Unknown author",
        "year": doc.get("first_publish_year"),
        "pages": doc.get("number_of_pages_median"),
        "edition": f"{doc.get('edition_count', '?')} edition(s)",
        "ol_key": doc.get("key", ""),
    }


def format_for_display(book: dict) -> str:
    """Return a single-line label suitable for a Streamlit selectbox."""
    year = f" ({book['year']})" if book["year"] else ""
    pages = f" — {book['pages']} pages" if book["pages"] else ""
    return f"{book['title']} — {book['author']}{year}{pages}"
