"""Analysis page for the Streamlit app."""

import streamlit as st
import asyncio
from src.workflows.nba_workflow import NBAWorkflow
from app.components.metrics import render_health_metrics
from app.components.charts import render_analysis_charts

def render_analysis_page():
    """Render the analysis page."""
    st.title("🔍 Account Analysis")
    
    # Account selection
    col1, col2 = st.columns([3, 1])
    with col1:
        account_id = st.text_input(
            "Enter Salesforce Account ID",
            placeholder="001XX000003DHPh"
        )
    with col2:
        analyze_button = st.button(
            "Analyze Account",
            type="primary",
            disabled=not account_id
        )
    
    if analyze_button and account_id:
        run_analysis(account_id)
    
    # Display results if available
    if 'analysis_result' in st.session_state:
        display_analysis_results(st.session_state.analysis_result)

def run_analysis(account_id: str):
    """Run the analysis workflow."""
    with st.spinner("🤖 CrewAI agents analyzing account..."):
        try:
            # Get workflow from session state
            workflow: NBAWorkflow = st.session_state.workflow
            
            # Run analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(
                workflow.run_analysis(account_id)
            )
            
            # Store results
            st.session_state.analysis_result = analysis
            st.session_state.current_account_id = account_id
            st.success("Analysis completed successfully!")
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.exception(e)

def display_analysis_results(analysis):
    """Display analysis results."""
    # Health metrics
    st.header("Account Health Overview")
    render_health_metrics(analysis)
    
    # Insights and risks
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Key Insights")
        for insight in analysis.insights:
            st.info(insight)
        
        st.subheader("🎯 Opportunities")
        for opportunity in analysis.opportunities:
            st.success(opportunity)
    
    with col2:
        st.subheader("⚠️ Risk Factors")
        for risk in analysis.risks:
            st.warning(risk)
        
        st.subheader("📊 Metrics")
        render_analysis_charts(analysis)
    
    # Agent contributions
    if analysis.agent_insights:
        st.header("🤖 Agent Contributions")
        tabs = st.tabs(list(analysis.agent_insights.keys()))
        
        for i, (agent, insights) in enumerate(analysis.agent_insights.items()):
            with tabs[i]:
                for insight in insights:
                    st.write(f"• {insight}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("Generate Recommendations →", type="primary"):
            st.session_state.current_page = 'recommendations'
            st.rerun()