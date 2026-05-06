"""
Reading Buddy — Streamlit entry point.

Run with:  streamlit run app.py
"""

import streamlit as st
from src.book_search import search_books, format_for_display
from src.ai_assistant import ask_question
from src.storage import load_shelf, save_book, is_on_shelf

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Reading Buddy",
    page_icon="📚",
    layout="wide",
)

# ── Custom styling ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:wght@600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Lora', serif; font-weight: 600; color: #1C1C1E; }

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] { background-color: #F7F7F7 !important; }

[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

input, textarea, [data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid #E0E0E0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stButton"] > button {
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border: none;
    transition: opacity 0.2s;
}
[data-testid="stButton"] > button:hover { opacity: 0.85; }

[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 4px 8px;
    margin-bottom: 4px;
}

hr { border-color: #EBEBEB; }

[data-testid="stCaptionContainer"] { color: #888; font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)


def render_rocks(rating: float) -> str:
    """Return an HTML string of rock emojis representing a half-rock rating out of 5."""
    rocks = ""
    for i in range(1, 6):
        if rating >= i:
            rocks += "🪨"
        elif rating >= i - 0.5:
            rocks += '<span style="opacity:0.35; font-size:0.9em;">🪨</span>'
        else:
            rocks += '<span style="opacity:0.15; font-size:0.9em;">🪨</span>'
    return rocks


# ── Session state defaults ──────────────────────────────────────────────────────
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "progress_str" not in st.session_state:
    st.session_state.progress_str = ""
if "show_log_form" not in st.session_state:
    st.session_state.show_log_form = False

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("assets/mascot.png", use_container_width=True)
    except Exception:
        pass

    st.markdown("""
        <div style='text-align:center; padding: 4px 0 8px 0;'>
            <span style='font-family:Inter,sans-serif; font-size:1.5rem; font-weight:600; color:#1C1C1E;'>Reading Buddy</span><br>
            <span style='font-family:Inter,sans-serif; font-size:0.8rem; color:#C4813A;'>your spoiler-free reading companion</span>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.header("Your book")

    search_query = st.text_input(
        "Search by title or author",
        placeholder="e.g. 1984, Dune, Austen…",
    )

    if search_query:
        with st.spinner("Searching…"):
            try:
                results = search_books(search_query)
            except ConnectionError as e:
                st.error(str(e))
                results = []

        if not results:
            st.warning("No results found.")
        else:
            labels = [format_for_display(b) for b in results]
            choice_index = st.selectbox(
                "Select your book",
                range(len(labels)),
                format_func=lambda i: labels[i],
            )

            if st.button("Confirm this book", use_container_width=True):
                st.session_state.selected_book = results[choice_index]
                st.session_state.chat_history = []
                st.session_state.show_log_form = False
                st.success(f"Set to **{results[choice_index]['title']}**")

    # ── Progress ────────────────────────────────────────────────────────────────
    if st.session_state.selected_book:
        book = st.session_state.selected_book
        st.divider()
        st.header("Your progress")

        progress_mode = st.radio(
            "Track by",
            ["Page number", "Chapter number", "Percentage"],
        )

        if progress_mode == "Page number":
            total = book.get("pages") or 500
            page = st.slider("Current page", min_value=1, max_value=total, value=1)
            st.session_state.progress_str = f"page {page} of {total}"

        elif progress_mode == "Chapter number":
            chapter = st.number_input("Current chapter", min_value=1, step=1, value=1)
            st.session_state.progress_str = f"chapter {chapter}"

        else:
            pct = st.slider("Percentage read", min_value=0, max_value=100, value=0)
            st.session_state.progress_str = f"{pct}% through the book"

        st.caption(f"Progress locked at: **{st.session_state.progress_str}**")

        # ── Finished this book? ─────────────────────────────────────────────────
        st.divider()
        already_logged = is_on_shelf(book["title"], book["author"])

        if already_logged:
            st.success("✓ On your shelf")
            if st.button("Update my review", use_container_width=True):
                st.session_state.show_log_form = True
        else:
            if st.button("📖  Finished this book?", use_container_width=True):
                st.session_state.show_log_form = True

    # ── My Shelf ────────────────────────────────────────────────────────────────
    shelf = load_shelf()
    if shelf:
        st.divider()
        with st.expander(f"My Shelf  ({len(shelf)} book{'s' if len(shelf) != 1 else ''})", expanded=False):
            for entry in reversed(shelf):
                st.markdown(
                    f"**{entry['title']}** — {entry['author']}<br>"
                    f"<span style='font-size:1.1rem;'>{render_rocks(entry['rating'])}</span> "
                    f"<span style='font-size:0.75rem; color:#888;'>{entry['date_finished']}</span>",
                    unsafe_allow_html=True,
                )
                if entry.get("review"):
                    st.caption(f'"{entry["review"]}"')
                st.markdown("<hr style='margin:6px 0; border-color:#E8E8E8;'>", unsafe_allow_html=True)

# ── Log form (main area, shown when button clicked) ────────────────────────────
if st.session_state.get("show_log_form") and st.session_state.selected_book:
    book = st.session_state.selected_book
    st.markdown(f"### Log: {book['title']}")

    RATING_OPTIONS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    rating = st.select_slider(
        "Your rating",
        options=RATING_OPTIONS,
        value=4.0,
        format_func=lambda v: f"{v} 🪨",
    )
    st.markdown(
        f"<div style='font-size:1.6rem; letter-spacing:2px; margin:-8px 0 12px 0;'>{render_rocks(rating)}</div>",
        unsafe_allow_html=True,
    )

    review = st.text_area(
        "Your review  (optional)",
        placeholder="What did you think?",
        max_chars=500,
    )

    col_save, col_cancel = st.columns([1, 1])
    with col_save:
        if st.button("Save to shelf", use_container_width=True):
            save_book(book["title"], book["author"], rating, review)
            st.session_state.show_log_form = False
            st.success("Added to your shelf!")
            st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_log_form = False
            st.rerun()

    st.divider()

# ── Main area: chat ─────────────────────────────────────────────────────────────
if not st.session_state.selected_book:
    st.markdown(
        """
        <div style='text-align:center; padding: 80px 0 40px 0;'>
            <h2>Welcome to Reading Buddy</h2>
            <p style='font-size:1.1rem;'>Search for your book in the sidebar to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    book = st.session_state.selected_book
    st.markdown(
        f"### {book['title']} &nbsp; <span style='font-size:0.9rem; font-weight:normal;'>by {book['author']}</span>",
        unsafe_allow_html=True,
    )
    st.caption(f"Answering up to: {st.session_state.progress_str}")
    st.divider()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask anything about the book…")

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    answer = ask_question(
                        question=question,
                        title=book["title"],
                        author=book["author"],
                        progress=st.session_state.progress_str,
                        conversation_history=st.session_state.chat_history,
                    )
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

                except EnvironmentError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    if st.session_state.chat_history:
        if st.button("Clear chat"):
            st.session_state.chat_history = []
            st.rerun()
