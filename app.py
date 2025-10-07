import streamlit as st
import os
from datetime import datetime
import json
from scraper_cnn import get_article_text_from_urls

# Page configuration
st.set_page_config(
    page_title="News Article Analyzer",
    page_icon="📰",
    layout="wide"
)

# Custom CSS with improved styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Title styling */
    .title {
        text-align: center;
        color: #ff4b4b;
        margin-bottom: 3rem;
        font-size: 2.5rem;
        font-weight: 600;
        padding-bottom: 1rem;
        border-bottom: 2px solid #3a3f47;
    }
    
    /* URL input styling */
    .url-input {
        background-color: #1a1f25;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid #3a3f47;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff6b6b 0%, #ff8b8b 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        background-color: #262730;
        color: #fafafa;
        border: 1px solid #3a3f47;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #ff4b4b;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2);
    }
    
    /* Labels and text */
    .label {
        color: #fafafa;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

def save_article(analysis, urls):
    """Save article analysis and metadata to JSON"""
    try:
        # Get absolute path and create directory if it doesn't exist
        current_dir = os.path.dirname(os.path.abspath(__file__))
        saved_file = os.path.join(current_dir, "saved_articles.json")
        
        # Debug prints to streamlit sidebar for visibility
        st.sidebar.write(f"Saving to: {saved_file}")
        
        article_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": analysis,
            "url1": urls[0],
            "url2": urls[1]
        }
        
        # Initialize or load saved_articles
        try:
            if os.path.exists(saved_file):
                with open(saved_file, 'r', encoding='utf-8') as f:
                    saved_articles = json.load(f)
                    if not isinstance(saved_articles, list):
                        saved_articles = []
            else:
                saved_articles = []
        except Exception:
            saved_articles = []
        
        # Append new article
        saved_articles.append(article_data)
        
        # Save with explicit encoding
        with open(saved_file, 'w', encoding='utf-8') as f:
            json.dump(saved_articles, f, indent=4, ensure_ascii=False)
            
        # Verify save was successful
        if os.path.exists(saved_file):
            st.sidebar.success(f"Saved successfully! Total articles: {len(saved_articles)}")
            return True
            
        return False
            
    except Exception as e:
        st.sidebar.error(f"Error saving: {str(e)}")
        return False

def main():
    st.markdown("<h1 class='title'>News Article Comparison Analysis</h1>", unsafe_allow_html=True)

    # Create a container for URL inputs
    with st.container():
        st.markdown("<div class='url-input'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<p class='label'>CNN Article URL</p>", unsafe_allow_html=True)
            url1 = st.text_input("", 
                placeholder="https://www.cnn.com/...",
                label_visibility="collapsed")
        
        with col2:
            st.markdown("<p class='label'>Fox News Article URL</p>", unsafe_allow_html=True)
            url2 = st.text_input("", 
                placeholder="https://www.foxnews.com/...",
                label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Center the compare button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        compare_button = st.button("Compare Articles", use_container_width=True)

    # Initialize session states
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'saved' not in st.session_state:
        st.session_state.saved = False

    if compare_button:
        if url1 and url2:
            # Reset saved state for new analysis
            st.session_state.saved = False
            
            with st.spinner('Analyzing articles... This might take a minute.'):
                try:
                    result = get_article_text_from_urls(url1, url2)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        # Store analysis directly in session state
                        st.session_state.analysis = result
                        st.success("Analysis completed successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter both URLs to proceed with the analysis.")
    
    # Show the analysis and save button in a single place
    if st.session_state.analysis and not st.session_state.saved:
        with st.expander("View Analysis", expanded=True):
            st.markdown(st.session_state.analysis)
            
            # Only show save button if not saved
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("💾 Save Analysis", key="save_button", use_container_width=True):
                    if save_article(st.session_state.analysis, [url1, url2]):
                        st.success("Analysis saved! View it in the Saved Articles page.")
                        st.session_state.saved = True
                        st.rerun()

if __name__ == "__main__":
    main()