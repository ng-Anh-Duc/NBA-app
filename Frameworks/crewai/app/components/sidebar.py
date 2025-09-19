"""Sidebar component for the Streamlit app."""

import streamlit as st
from src.config.settings import salesforce_settings, llm_settings
from src.integrations.salesforce.client import SalesforceClient
from src.integrations.llm.providers import get_llm_provider
from src.workflows.workflow_manager import WorkflowManager

def render_sidebar():
    """Render the sidebar with navigation and configuration."""
    with st.sidebar:
        st.image("assets/logo.png", width=200)  # Add your logo
        st.title("Salesforce NBA")
        st.caption("Powered by CrewAI 🤖")
        
        st.divider()
        
        if not st.session_state.authenticated:
            render_login_form()
        else:
            render_navigation()
            render_account_info()
            render_settings()

def render_login_form():
    """Render login form in sidebar."""
    st.header("🔐 Authentication")
    
    with st.form("login_form"):
        st.subheader("Salesforce Credentials")
        username = st.text_input("Username", value=salesforce_settings.username)
        password = st.text_input("Password", type="password")
        token = st.text_input("Security Token", type="password")
        
        st.subheader("AI Configuration")
        llm_provider = st.selectbox(
            "LLM Provider",
            ["openai", "google"],
            index=0 if llm_settings.provider == "openai" else 1
        )
        api_key = st.text_input(
            f"{llm_provider.upper()} API Key",
            type="password",
            value=llm_settings.openai_api_key if llm_provider == "openai" else llm_settings.google_api_key
        )
        
        submitted = st.form_submit_button("Connect", type="primary")
        
        if submitted:
            authenticate(username, password, token, llm_provider, api_key)

def authenticate(username, password, token, llm_provider, api_key):
    """Authenticate and initialize services."""
    with st.spinner("Connecting..."):
        try:
            # Update settings
            salesforce_settings.username = username
            salesforce_settings.password = password
            salesforce_settings.security_token = token
            llm_settings.provider = llm_provider
            if llm_provider == "openai":
                llm_settings.openai_api_key = api_key
            else:
                llm_settings.google_api_key = api_key
            
            # Initialize services
            sf_client = SalesforceClient()
            llm = get_llm_provider()
            
            # Create workflow manager
            workflow_manager = WorkflowManager(sf_client, llm)
            
            # Store in session state
            st.session_state.sf_client = sf_client
            st.session_state.llm = llm
            st.session_state.workflow = workflow_manager.create_nba_workflow()
            st.session_state.authenticated = True
            
            st.success("Connected successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

def render_navigation():
    """Render navigation menu."""
    st.header("📍 Navigation")
    
    pages = {
        "home": "🏠 Home",
        "analysis": "🔍 Analysis",
        "recommendations": "💡 Recommendations",
        "execution": "🚀 Execution"
    }
    
    for page_key, page_name in pages.items():
        if st.button(
            page_name,
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if st.session_state.current_page == page_key else "secondary"
        ):
            st.session_state.current_page = page_key
            st.rerun()

def render_account_info():
    """Render current account information."""
    if 'current_account_id' in st.session_state:
        st.header("📊 Current Account")
        st.info(f"ID: {st.session_state.current_account_id}")
        
        if 'analysis_result' in st.session_state:
            analysis = st.session_state.analysis_result
            st.metric(
                "Health Score",
                f"{analysis.health_metrics.score}/10",
                delta=None
            )

def render_settings():
    """Render settings section."""
    with st.expander("⚙️ Settings"):
        st.subheader("Workflow Configuration")
        
        verbose = st.checkbox(
            "Verbose Mode",
            value=True,
            help="Show detailed agent conversations"
        )
        
        max_iterations = st.slider(
            "Max Iterations",
            min_value=5,
            max_value=50,
            value=20,
            help="Maximum conversation rounds"
        )
        
        if st.button("Disconnect"):
            st.session_state.clear()
            st.rerun()