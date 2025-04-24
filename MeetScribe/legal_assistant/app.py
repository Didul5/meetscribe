"""
Main Streamlit application for the Legal Assistant.
"""
import streamlit as st
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="LegalMind Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import pages after setting page config
from ui.pages import PageManager

# Add custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f6fa;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4682b4;
        color: white;
    }
    
    div.stButton > button:first-child {
        background-color: #4682b4;
        color: white;
        border-radius: 4px;
    }
    
    div.stButton > button:hover {
        background-color: #5a96c7;
        color: white;
    }
    
    div[data-testid="stSidebarNav"] {
        background-image: linear-gradient(#4682b4, #57a5d8);
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        border-radius: 10px;
    }
    
    div[data-testid="stSidebarNav"] > ul {
        color: white;
    }
    
    .stProgress > div > div > div > div {
        background-color: #4682b4;
    }
    
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .legal-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Custom CSS for priority indicators */
    .priority-high {
        color: white;
        background-color: #FF5733;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .priority-medium {
        color: white;
        background-color: #FFC300;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .priority-low {
        color: white;
        background-color: #36A2EB;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point."""
    # Initialize the page manager
    page_manager = PageManager()
    
    # Render the current page
    page_manager.render()

if __name__ == "__main__":
    main()