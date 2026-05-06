# Reading Buddy

A spoiler-free reading assistant powered by Claude AI. Search for any book, tell it how far you've read, and ask questions — without worrying about accidental spoilers.

## Features

- Search any book via the [Open Library](https://openlibrary.org/) database
- Specify your reading progress by page, chapter, or percentage
- Ask questions in a conversational chat interface
- Claude answers only based on what you've read so far

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| AI | [Claude](https://www.anthropic.com/) via the Anthropic API |
| Book data | [Open Library API](https://openlibrary.org/developers/api) (free, no key needed) |
| Language | Python 3.11+ |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/reading-buddy.git
cd reading-buddy
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
```

Open `.env` and replace `your-api-key-here` with your real Anthropic API key.  
Get one at [console.anthropic.com](https://console.anthropic.com/).

### 5. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Project Structure

```
reading-buddy/
├── .env.example        # API key template (copy to .env and fill in)
├── .gitignore          # Keeps secrets out of git
├── requirements.txt    # Python dependencies
├── app.py              # Streamlit UI
└── src/
    ├── book_search.py  # Open Library API integration
    └── ai_assistant.py # Claude API + spoiler-free prompt logic
```

## Roadmap

- [ ] Reading session timer (track how long you read each day)
- [ ] Reading history dashboard
- [ ] Mobile focus mode (block distractions while reading)

## Security

API keys are managed via a `.env` file which is excluded from version control by `.gitignore`. Never commit your `.env` file.
