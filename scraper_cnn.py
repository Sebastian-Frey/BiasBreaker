import requests
from bs4 import BeautifulSoup
import re
import string
import os
from requests.exceptions import RequestException
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import langdetect

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def is_url_accessible(url, headers):
    try:
        response = requests.head(url, headers=headers, timeout=10)
        return response.status_code == 200
    except RequestException:
        return False

def translate_with_gpt(text):
    """Translate text to English using ChatGPT"""
    try:
        # Detect language
        lang = langdetect.detect(text)
        
        # Return original text if already English
        if lang == 'en':
            return text, lang
            
        # Prepare translation prompt
        prompt = f"""Translate the following text from {lang} to English. 
        Maintain the original meaning and tone while ensuring natural English flow.
        Text to translate:
        {text}"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional translator skilled in maintaining context and nuance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        return response.choices[0].message.content, lang
        
    except Exception as e:
        return f"Translation error: {str(e)}", None

def extract_headline(content):
    """Extract headline from the analysis content more reliably"""
    if not content:
        return None
    
    lines = content.strip().split('\n')
    
    # Look for common headline patterns
    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        line = line.strip()
        # Check for explicit headline marker
        if line.lower().startswith('headline:'):
            return line.replace('Headline:', '').strip()
        # Check for first non-empty line that's not a metadata marker
        if line and not any(marker in line.lower() for marker in ['source', 'article', 'opening paragraph', 'body']):
            # Verify it's not too long to be a headline (usually under 150 chars)
            if len(line) < 150:
                return line
    
    return None

def get_article_text_from_urls(url1, url2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    articles = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx, url in enumerate([url1, url2], 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # CNN layout
            paragraphs = soup.find_all("div", {"data-component": "text-block"})
            if not paragraphs:
                article_tag = soup.find("article")
                if article_tag:
                    paragraphs = article_tag.find_all("p")

            if not paragraphs:
                return f"Error: Couldn't find content for Article {idx}"

            article_text = "\n".join(p.get_text() for p in paragraphs)

            # Clean up the text while preserving structure
            article_text = article_text.replace('"', '"').replace('"', '"')
            article_text = article_text.replace(''', "'").replace(''', "'")
            article_text = article_text.replace('–', '-').replace('—', '-')
            
            # Split into paragraphs and clean each paragraph individually
            paragraphs = article_text.split('\n')
            cleaned_paragraphs = []
            
            for paragraph in paragraphs:
                if paragraph.strip():  # Only process non-empty paragraphs
                    # Clean punctuation while preserving structure
                    spaced = re.sub(r"([{}])".format(re.escape(string.punctuation)), r" \1 ", paragraph)
                    cleaned = re.sub(r'\s+', ' ', spaced).strip()
                    if cleaned:  # Add only non-empty cleaned paragraphs
                        cleaned_paragraphs.append(cleaned)
            
            # Join paragraphs with double line breaks for better readability
            cleaned = '\n\n'.join(cleaned_paragraphs)
            articles.append(cleaned)

        except Exception as e:
            return f"Error with Article {idx}: {str(e)}"

    # Create 'articles' directory if it doesn't exist
    if not os.path.exists('articles'):
        os.makedirs('articles')

    try:
        # Translate articles if needed
        translated_articles = []
        source_languages = []
        
        for idx, article in enumerate(articles, 1):
            translated, lang = translate_with_gpt(article)
            if translated.startswith("Translation error"):
                return f"Error translating Article {idx}: {translated}"
            translated_articles.append(translated)
            source_languages.append(lang)

        # Prepare the prompt for GPT
        prompt = f"""You are an experienced journalist writing a news article that synthesizes information from two different sources covering the same event. 

        Important Context:
        Source 1 was {f'translated from {source_languages[0]}' if source_languages[0] != 'en' else 'originally in English'}.
        Source 2 was {f'translated from {source_languages[1]}' if source_languages[1] != 'en' else 'originally in English'}.
        
        Your task is to write one cohesive, well-structured news article that:

        Includes all shared facts and overlapping content between the two sources in a clear, neutral, and professional journalistic tone.

        Clearly highlights and attributes any differences in reporting. For example: "Source A reports 4 deaths, while Source B reports 5."

        Explicitly identifies the source when citing information that is specific to one article.

        Format your article exactly as follows, maintaining all line breaks:

        Headline: [Your headline here]

        [Opening paragraph summarizing the key event]


        [Subsequent paragraphs with exactly two line breaks between them]


        Important:
        - Start with "Headline: " followed by your headline
        - Use exactly TWO blank lines between paragraphs (press Enter three times)
        - Keep paragraphs concise (3-5 sentences)
        - Use clear source attribution
        - Highlight differences in reporting but write in a neutral tone one cohesive article

        Below are the two source articles:
        Article 1:
        {translated_articles[0]}


        Article 2:
        {translated_articles[1]}

        Write your article now, ensuring proper paragraph spacing."""

        # Adjust the response parameters to preserve formatting
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional news analyst. Maintain exact formatting with double line breaks between paragraphs. Never compress multiple line breaks."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        # Save the unified analysis with preserved line breaks
        unified_file = f"articles/unified_{timestamp}.txt"
        with open(unified_file, 'w', encoding='utf-8') as f:
            # Ensure line breaks are preserved in the saved file
            content = response.choices[0].message.content
            # Replace any accidentally compressed line breaks
            content = re.sub(r'\n{2,}', '\n\n\n', content)
            f.write(content)
        
        return f"Analysis saved to {unified_file}"

    except Exception as e:
        return f"Error in comparison: {str(e)}"

if __name__ == "__main__":
    url1 = "https://edition.cnn.com/2025/04/22/politics/abrego-garcia-judge-xinis-justice-that-ends-now/index.html"
    url2 = "https://www.foxnews.com/politics/president-trump-blasts-courts-getting-way-deportation-agenda"
    
    result = get_article_text_from_urls(url1, url2)
    print(result)