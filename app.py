"""
Reading Buddy — Streamlit entry point.

Run with:  streamlit run app.py
"""

import streamlit as st
from src.book_search import search_books, format_for_display
from src.ai_assistant import ask_question

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Reading Buddy",
    page_icon="📚",
    layout="centered",
)

st.title("📚 Reading Buddy")
st.caption("Ask questions about your book — spoiler free.")

# ── Session state defaults ──────────────────────────────────────────────────────
# session_state persists between Streamlit re-runs (every user interaction).
# We initialise keys here so the rest of the app can safely read them.
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None  # dict from book_search
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []     # list of {role, content} dicts


# ── Section 1: Book search ──────────────────────────────────────────────────────
st.header("1. Find your book")

search_query = st.text_input(
    "Search by title or author",
    placeholder="e.g. Harry Potter, Dune, Jane Austen…",
)

if search_query:
    with st.spinner("Searching Open Library…"):
        try:
            results = search_books(search_query)
        except ConnectionError as e:
            st.error(str(e))
            results = []

    if not results:
        st.warning("No results found. Try a different search term.")
    else:
        labels = [format_for_display(b) for b in results]
        choice_index = st.selectbox(
            "Select your book",
            range(len(labels)),
            format_func=lambda i: labels[i],
        )

        if st.button("Confirm this book"):
            st.session_state.selected_book = results[choice_index]
            st.session_state.chat_history = []  # reset chat when book changes
            st.success(f"Book set to: **{results[choice_index]['title']}**")

# ── Section 2: Reading progress ─────────────────────────────────────────────────
if st.session_state.selected_book:
    book = st.session_state.selected_book
    st.divider()
    st.header("2. Where are you in the book?")

    progress_mode = st.radio(
        "How would you like to specify your progress?",
        ["Page number", "Chapter number", "Percentage"],
        horizontal=True,
    )

    if progress_mode == "Page number":
        total = book.get("pages") or 500
        page = st.slider("Current page", min_value=1, max_value=total, value=1)
        progress_str = f"page {page} of {total}"

    elif progress_mode == "Chapter number":
        chapter = st.number_input("Current chapter", min_value=1, step=1, value=1)
        progress_str = f"chapter {chapter}"

    else:
        pct = st.slider("Percentage read", min_value=0, max_value=100, value=0)
        progress_str = f"{pct}% through the book"

    st.caption(f"Progress: **{progress_str}** — Claude will only discuss content up to this point.")

    # ── Section 3: Chat ─────────────────────────────────────────────────────────
    st.divider()
    st.header("3. Ask your question")

    # Show previous messages in this session
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask anything about the book…")

    if question:
        # Show the user's message immediately
        with st.chat_message("user"):
            st.markdown(question)

        # Call Claude
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    answer = ask_question(
                        question=question,
                        title=book["title"],
                        author=book["author"],
                        progress=progress_str,
                        conversation_history=st.session_state.chat_history,
                    )
                    st.markdown(answer)

                    # Append both turns to history for multi-turn conversation
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
