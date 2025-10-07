## BiasBreaker — Create Unbiased News From Two Sources

BiasBreaker is a Streamlit app that takes two news articles on the same topic (e.g., CNN and Fox News), translates them to English if needed, and synthesizes a single, neutral, well-structured article that highlights overlaps and clearly attributes differences. It’s designed to demonstrate practical AI-product thinking: scraping, light NLP cleanup, LLM prompting for journalistic tone and structure, and a simple UX to compare, save, and revisit results.

### Why this is interesting
- **Real-world utility**: Surfaces consensus and discrepancies across outlets, helping readers reason about events with less bias.
- **Thoughtful prompt-engineering**: Enforces headline, paragraph structure, attribution rules, and explicit difference-highlighting.
- **End-to-end product**: From URL input to storage and a curated “Saved Articles” view for later reading and sharing.

## How it works (high level)
- **Scrape and clean**: `scraper_cnn.py` fetches both URLs, extracts article text using BeautifulSoup, and performs light punctuation/whitespace cleanup.
- **Translate if needed**: Non‑English content is auto‑detected and translated to English via OpenAI before synthesis.
- **Synthesize a neutral article**: A carefully crafted prompt asks GPT to produce one cohesive article that:
  - Includes shared facts
  - Attributes outlet-specific claims
  - Highlights reported differences (e.g., different counts, timelines)
  - Preserves exact formatting with a `Headline:` and double line breaks
- **Save outputs**:
  - The unified article is written to `articles/unified_YYYYMMDD_HHMMSS.txt`
  - A compact record (timestamp, result pointer or text, original URLs) is appended to `saved_articles.json`
- **Revisit saved items**: The multi-page `pages/saved_articles.py` view displays previously saved analyses with the extracted headline, full content, and links back to sources.

## App structure (files you’ll care about)
- `app.py`: Streamlit UI for entering two URLs, running the analysis, previewing, and saving.
- `scraper_cnn.py`: Fetches pages, cleans text, translates when needed, prompts GPT, and saves the unified article file.
- `pages/saved_articles.py`: Lists saved analyses, extracts the headline, and shows sources.
- `articles/`: Folder where unified article `.txt` files are saved.
- `saved_articles.json`: Lightweight index of saved analyses with timestamps and URLs.

## Setup
1) Python environment
- Python 3.10+ recommended.

2) Install dependencies
```bash
pip install streamlit requests beautifulsoup4 openai python-dotenv langdetect
```

3) Create a .env file
- The app reads secrets from environment variables via `python-dotenv` [[memory:7185352]]. Create a file named `.env` in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

4) Run the app
```bash
streamlit run app.py
```

## Using the app
- Paste two article URLs (e.g., one from CNN and one from Fox News).
- Click “Compare Articles”. The app will scrape, translate if necessary, and synthesize the unbiased article.
- Expand “View Analysis” to read the output.
- Click “Save Analysis” to store it. Then open the “Saved Articles” page (Streamlit’s sidebar Pages) to revisit your saved items.

## What’s under the hood (a bit deeper)
- `get_article_text_from_urls(url1, url2)` in `scraper_cnn.py`:
  - Requests each page with a desktop user-agent, parses with BeautifulSoup, and extracts likely content blocks.
  - Normalizes punctuation and whitespace while preserving paragraph boundaries.
  - Detects language and translates to English via OpenAI when needed.
  - Prompts GPT to generate a neutral article with strict formatting rules (headline first, two blank lines between paragraphs, clear attribution for differences).
  - Saves the final article to `articles/unified_*.txt` and returns the save path.
- `save_article` in `app.py` maintains a JSON index (`saved_articles.json`) with timestamps, URLs, and the analysis reference.
- `pages/saved_articles.py` loads the JSON index, rehydrates content from disk when needed, extracts the headline, and renders the full article plus source links.

## Troubleshooting
- **API key errors**: Ensure `.env` exists and includes `OPENAI_API_KEY`. Restart the app after changes.
- **Blocked or unusual article layouts**: Some pages may not expose expected content blocks. Try another URL or copy the canonical article link.
- **Rate limits**: If you run many comparisons quickly, you may hit OpenAI rate limits; wait and retry.

## Notes on ethics and limitations
- This tool aims to reduce bias by surfacing overlaps and clearly marking differences. It does not “eliminate” bias; it improves transparency so readers can reason more clearly.
- Outputs depend on the quality and completeness of the input sources.

## Roadmap ideas
- Add more robust content extraction for additional outlets/layouts
- Allow more than two sources and visualize the agreement graph
- Optional citations inline for each paragraph
- Scheduled runs on trending topics with a daily digest

---

If you’re a recruiter or collaborator: this project demonstrates shipping a focused AI feature end-to-end—scraping, translation, prompt design for factual synthesis, simple persistence, and a clean UX for reading and recall. Happy to discuss extensions and production hardening.
