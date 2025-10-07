import streamlit as st
import json
import os

# Add custom CSS for saved articles page
st.markdown("""
    <style>
    .stExpander {
        background-color: #1a1f25;
        border-radius: 4px;
        margin-bottom: 1rem;
        border: 1px solid #3a3f47;
    }
    .stMarkdown h1 {
        color: #ff4b4b;
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }
    .stMarkdown h3 {
        color: #ff4b4b;
        font-size: 1.2rem;
        margin-top: 1.5rem;
    }
    a {
        color: #ff4b4b !important;
        text-decoration: none;
    }
    a:hover {
        color: #ff6b6b !important;
        text-decoration: underline;
    }
    hr {
        border-color: #3a3f47;
        margin: 1.5rem 0;
    }
    .sources {
        background-color: #262730;
        padding: 1rem;
        border-radius: 4px;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def load_saved_articles():
    # Get absolute path
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))
    saved_file = os.path.join(current_dir, "saved_articles.json")
    
    # Show file path being checked
    st.sidebar.write(f"Looking for saved articles at: {saved_file}")
    
    if os.path.exists(saved_file):
        try:
            with open(saved_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                st.sidebar.success(f"Found {len(articles)} articles")
                return articles, current_dir
        except json.JSONDecodeError:
            st.sidebar.error("Error reading saved articles file")
            return [], current_dir
    else:
        st.sidebar.warning("No saved articles file found")
        return [], current_dir

def read_analysis_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading analysis file: {str(e)}"

def extract_headline_and_content(content):
    """Extract headline and clean content from the analysis"""
    if not content:
        return None, None
    
    # Split content into lines while preserving empty lines
    lines = content.splitlines(keepends=True)
    headline = None
    content_lines = []
    content_started = False
    
    for line in lines:
        # Check for headline
        if not headline and line.lower().strip().startswith('headline:'):
            headline = line.replace('Headline:', '').strip()
            content_started = True
            continue
        
        # After finding headline, collect remaining content including empty lines
        if content_started:
            content_lines.append(line)
        # If no explicit headline found, use first non-empty line as headline
        elif not headline and line.strip() and len(line.strip()) < 150:
            headline = line.strip()
            content_started = True
            continue
    
    # Join content lines preserving all original line breaks
    cleaned_content = ''.join(content_lines)
    
    return headline, cleaned_content

def main():
    st.title("📚 Saved Articles")
    
    # Add refresh button
    if st.button("🔄 Refresh"):
        st.rerun()
    
    saved_articles, current_dir = load_saved_articles()
    
    if not saved_articles:
        st.info("No saved analyses yet. Go to the main page to analyze and save articles.")
        return

    for idx, article in enumerate(reversed(saved_articles), 1):
        # Get the analysis content first
        if isinstance(article['analysis'], str) and article['analysis'].startswith("Analysis saved to"):
            filename = article['analysis'].split("Analysis saved to ")[-1].strip()
            filepath = os.path.join(current_dir, filename)
            analysis_content = read_analysis_file(filepath)
        else:
            analysis_content = article['analysis']
        
        # Extract headline and clean content
        headline, clean_content = extract_headline_and_content(analysis_content)
        expander_title = headline if headline else f"Analysis {idx} - {article['timestamp']}"
        
        with st.expander(expander_title, expanded=False):
            if headline:
                st.markdown(f"# {headline}")
            
            if clean_content:
                st.markdown(clean_content)
            
            # Display sources at the bottom
            st.markdown("---")
            st.markdown("### Sources")
            st.markdown(f"📰 [CNN Article]({article['url1']})")
            st.markdown(f"📰 [Fox News Article]({article['url2']})")

if _name_ == "_main_":
    main()