"""Main Streamlit application."""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.settings import app_settings
from app.pages import home, analysis, recommendations, execution
from app.components.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="Salesforce NBA - CrewAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

def main():
    """Main application entry point."""
    
    # Render sidebar
    render_sidebar()
    
    # Route to appropriate page
    if not st.session_state.authenticated:
        home.render_login_page()
    else:
        if st.session_state.current_page == 'home':
            home.render_home_page()
        elif st.session_state.current_page == 'analysis':
            analysis.render_analysis_page()
        elif st.session_state.current_page == 'recommendations':
            recommendations.render_recommendations_page()
        elif st.session_state.current_page == 'execution':
            execution.render_execution_page()

if __name__ == "__main__":
    main()