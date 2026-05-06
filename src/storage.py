"""
Handles reading and writing the bookshelf data to a local JSON file.
Books are stored in data/bookshelf.json.
"""

import json
import os
from datetime import date
from typing import List

SHELF_PATH = "data/bookshelf.json"


def load_shelf() -> List[dict]:
    """Return all logged books, or an empty list if none saved yet."""
    if not os.path.exists(SHELF_PATH):
        return []
    with open(SHELF_PATH, "r") as f:
        return json.load(f).get("books", [])


def save_book(title: str, author: str, rating: float, review: str) -> None:
    """Add a finished book to the shelf, or update it if already logged."""
    books = load_shelf()

    # Replace existing entry for the same book if it exists
    books = [b for b in books if not (b["title"] == title and b["author"] == author)]

    books.append({
        "title": title,
        "author": author,
        "rating": rating,
        "review": review,
        "date_finished": date.today().isoformat(),
    })

    os.makedirs(os.path.dirname(SHELF_PATH), exist_ok=True)
    with open(SHELF_PATH, "w") as f:
        json.dump({"books": books}, f, indent=2)


def is_on_shelf(title: str, author: str) -> bool:
    """Return True if this book has already been logged."""
    return any(
        b["title"] == title and b["author"] == author
        for b in load_shelf()
    )
