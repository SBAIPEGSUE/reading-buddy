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
    layout="wide",
)

# ── Session state defaults ──────────────────────────────────────────────────────
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "progress_str" not in st.session_state:
    st.session_state.progress_str = ""

# ── Sidebar: book selection & progress ─────────────────────────────────────────
with st.sidebar:
    try:
        st.image("assets/logo.png", use_container_width=True)
    except Exception:
        st.title("📚 Reading Buddy")

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
                st.success(f"Set to **{results[choice_index]['title']}**")

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

    # Display chat history
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
