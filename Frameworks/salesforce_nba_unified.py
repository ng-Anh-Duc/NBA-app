# salesforce_nba_unified.py
"""
Unified Salesforce NBA Application
Compare different AI frameworks side by side
"""

import streamlit as st
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import plotly.graph_objects as go

# Base Framework Interface
class AIFramework(ABC):
    """Abstract base class for AI frameworks"""
    
    @abstractmethod
    def name(self) -> str:
        """Framework name"""
        pass
    
    @abstractmethod
    def analyze_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze account and return insights"""
        pass
    
    @abstractmethod
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate NBA recommendations"""
        pass
    
    @abstractmethod
    def create_action_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Create action plan"""
        pass

# Framework Implementations
class CrewAIFramework(AIFramework):
    """CrewAI implementation"""
    
    def name(self) -> str:
        return "CrewAI"
    
    def analyze_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate CrewAI multi-agent analysis
        time.sleep(2)  # Simulate processing
        return {
            "framework": "CrewAI",
            "health_score": 8,
            "insights": [
                "Multi-agent collaboration identified cross-sell opportunity",
                "Data analyst agent found revenue growth pattern",
                "Risk agent detected minor service issues"
            ],
            "agent_contributions": {
                "DataAnalyst": "Identified 15% YoY growth",
                "Strategist": "Recommended product expansion",
                "RiskAnalyst": "Flagged 2 open high-priority cases"
            }
        }
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Cross-sell Premium Features",
                "priority": "High",
                "confidence": 0.85,
                "reasoning": "Based on usage patterns and growth trajectory"
            },
            {
                "title": "Proactive Support Engagement",
                "priority": "Medium",
                "confidence": 0.75,
                "reasoning": "Address cases before escalation"
            }
        ]
    
    def create_action_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "steps": [
                {"task": "Analyze feature usage", "owner": "CSM", "due_days": 3},
                {"task": "Prepare proposal", "owner": "Sales", "due_days": 7},
                {"task": "Schedule demo", "owner": "SE", "due_days": 10}
            ],
            "timeline": 14,
            "resources": ["CSM", "Sales Rep", "Solution Engineer"]
        }

class LangGraphFramework(AIFramework):
    """LangGraph implementation"""
    
    def name(self) -> str:
        return "LangGraph"
    
    def analyze_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(2)
        return {
            "framework": "LangGraph",
            "health_score": 7.5,
            "insights": [
                "Workflow identified decision point for renewal",
                "Conditional routing suggests intervention needed",
                "State machine shows positive trajectory with risks"
            ],
            "workflow_path": ["fetch_data", "analyze", "risk_assessment", "opportunity_identification"]
        }
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Renewal Acceleration Program",
                "priority": "High",
                "confidence": 0.90,
                "reasoning": "Workflow analysis shows renewal decision approaching"
            },
            {
                "title": "Executive Business Review",
                "priority": "High",
                "confidence": 0.80,
                "reasoning": "Strengthen relationship before renewal"
            }
        ]
    
    def create_action_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "steps": [
                {"task": "Prepare renewal analysis", "owner": "AM", "due_days": 5},
                {"task": "Schedule EBR", "owner": "CSM", "due_days": 7},
                {"task": "Create value proposition", "owner": "Sales", "due_days": 10}
            ],
            "timeline": 21,
            "checkpoints": ["Initial outreach", "EBR completion", "Proposal delivery"]
        }

class AutoGenFramework(AIFramework):
    """AutoGen implementation"""
    
    def name(self) -> str:
        return "AutoGen"
    
    def analyze_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(2)
        return {
            "framework": "AutoGen",
            "health_score": 8.2,
            "insights": [
                "Collaborative analysis revealed expansion readiness",
                "Risk analyst identified low churn probability",
                "Consensus reached on growth strategy"
            ],
            "agent_consensus": {
                "agreement_level": 0.85,
                "dissenting_opinions": ["Timeline aggressive per ExecutionPlanner"],
                "key_discussion_points": ["Budget availability", "Technical readiness"]
            }
        }
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Enterprise Upgrade Campaign",
                "priority": "High",
                "confidence": 0.88,
                "reasoning": "All agents agree on expansion opportunity"
            },
            {
                "title": "Success Plan Refresh",
                "priority": "Medium",
                "confidence": 0.82,
                "reasoning": "Align success metrics with growth"
            }
        ]
    
    def create_action_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "steps": [
                {"task": "ROI analysis", "owner": "CSM", "due_days": 4},
                {"task": "Technical assessment", "owner": "SE", "due_days": 6},
                {"task": "Proposal creation", "owner": "Sales", "due_days": 12}
            ],
            "timeline": 18,
            "agent_assignments": {
                "DataAnalyst": "Provide metrics",
                "Strategist": "Review proposal",
                "ExecutionPlanner": "Monitor progress"
            }
        }

# Framework Orchestrator
class FrameworkOrchestrator:
    """Orchestrate multiple frameworks for comparison"""
    
    def __init__(self):
        self.frameworks = {
            "CrewAI": CrewAIFramework(),
            "LangGraph": LangGraphFramework(),
            "AutoGen": AutoGenFramework()
        }
    
    async def run_parallel_analysis(self, account_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Run all frameworks in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                name: executor.submit(framework.analyze_account, account_data)
                for name, framework in self.frameworks.items()
            }
            
            for name, future in futures.items():
                results[name] = future.result()
        
        return results
    
    def compare_recommendations(self, all_recommendations: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        """Compare recommendations across frameworks"""
        comparison_data = []
        
        for framework, recommendations in all_recommendations.items():
            for rec in recommendations:
                comparison_data.append({
                    "Framework": framework,
                    "Recommendation": rec["title"],
                    "Priority": rec["priority"],
                    "Confidence": rec["confidence"]
                })
        
        return pd.DataFrame(comparison_data)
    
    def generate_consensus(self, all_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate consensus from all frameworks"""
        health_scores = [analysis["health_score"] for analysis in all_analyses.values()]
        all_insights = []
        
        for analysis in all_analyses.values():
            all_insights.extend(analysis["insights"])
        
        return {
            "average_health_score": sum(health_scores) / len(health_scores),
            "health_score_variance": max(health_scores) - min(health_scores),
            "total_insights": len(all_insights),
            "framework_agreement": self._calculate_agreement(all_analyses)
        }
    
    def _calculate_agreement(self, analyses: Dict[str, Dict[str, Any]]) -> float:
        """Calculate agreement level between frameworks"""
        scores = [a["health_score"] for a in analyses.values()]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        return 1 - (variance / 10)  # Normalize to 0-1

# Streamlit UI
def create_unified_app():
    st.set_page_config(page_title="Salesforce NBA Framework Comparison", layout="wide")
    
    st.title("🔬 Salesforce NBA - AI Framework Comparison")
    st.markdown("Compare CrewAI, LangGraph, and AutoGen approaches side by side")
    
    # Initialize orchestrator
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = FrameworkOrchestrator()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Salesforce connection (simplified for demo)
        account_id = st.text_input("Account ID", value="001XX000003DHPh")
        
        # Framework selection
        st.subheader("Active Frameworks")
        use_crewai = st.checkbox("CrewAI", value=True)
        use_langgraph = st.checkbox("LangGraph", value=True)
        use_autogen = st.checkbox("AutoGen", value=True)
        
        # Execution mode
        execution_mode = st.radio("Execution Mode", ["Parallel", "Sequential"])
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Framework Analysis")
        
        # Mock account data for demo
        account_data = {
            "id": account_id,
            "name": "Acme Corporation",
            "revenue": 5000000,
            "employees": 500,
            "opportunities": 5,
            "cases": 3
        }
        
        if st.button("Run Analysis", type="primary"):
            # Run analysis
            with st.spinner("Running multi-framework analysis..."):
                # Run frameworks
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                all_results = loop.run_until_complete(
                    st.session_state.orchestrator.run_parallel_analysis(account_data)
                )
                st.session_state.results = all_results
            
            # Display results in tabs
            tabs = st.tabs(list(all_results.keys()) + ["Comparison"])
            
            # Individual framework results
            for i, (framework, result) in enumerate(all_results.items()):
                with tabs[i]:
                    st.subheader(f"{framework} Analysis")
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Health Score", f"{result['health_score']}/10")
                    with col2:
                        st.metric("Insights", len(result['insights']))
                    with col3:
                        st.metric("Confidence", "High")
                    
                    # Insights
                    st.write("**Key Insights:**")
                    for insight in result['insights']:
                        st.info(f"💡 {insight}")
                    
                    # Framework-specific details
                    if framework == "CrewAI" and "agent_contributions" in result:
                        st.write("**Agent Contributions:**")
                        for agent, contribution in result["agent_contributions"].items():
                            st.write(f"- **{agent}:** {contribution}")
                    
                    elif framework == "LangGraph" and "workflow_path" in result:
                        st.write("**Workflow Path:**")
                        st.write(" → ".join(result["workflow_path"]))
                    
                    elif framework == "AutoGen" and "agent_consensus" in result:
                        st.write("**Agent Consensus:**")
                        consensus = result["agent_consensus"]
                        st.progress(consensus["agreement_level"])
                        st.write(f"Agreement Level: {consensus['agreement_level']*100:.0f}%")
            
            # Comparison tab
            with tabs[-1]:
                st.subheader("Framework Comparison")
                
                # Consensus metrics
                consensus = st.session_state.orchestrator.generate_consensus(all_results)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Avg Health Score", f"{consensus['average_health_score']:.1f}")
                with col2:
                    st.metric("Score Variance", f"{consensus['health_score_variance']:.1f}")
                with col3:
                    st.metric("Total Insights", consensus['total_insights'])
                with col4:
                    st.metric("Agreement", f"{consensus['framework_agreement']*100:.0f}%")
                
                # Visualization
                fig = go.Figure()
                
                frameworks = list(all_results.keys())
                health_scores = [all_results[f]["health_score"] for f in frameworks]
                
                fig.add_trace(go.Bar(
                    x=frameworks,
                    y=health_scores,
                    text=health_scores,
                    textposition='auto',
                ))
                
                fig.update_layout(
                    title="Health Score Comparison",
                    yaxis_title="Health Score",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.header("Recommendations")
        
        if 'results' in st.session_state:
            # Get recommendations from each framework
            all_recommendations = {}
                        for framework_name, framework in st.session_state.orchestrator.frameworks.items():
                if framework_name in st.session_state.results:
                    analysis = st.session_state.results[framework_name]
                    recommendations = framework.generate_recommendations(analysis)
                    all_recommendations[framework_name] = recommendations
            
            # Display recommendations
            st.subheader("All Recommendations")
            
            # Create comparison dataframe
            comparison_df = st.session_state.orchestrator.compare_recommendations(all_recommendations)
            
            # Display as grouped bar chart
            fig = go.Figure()
            
            for framework in comparison_df['Framework'].unique():
                framework_data = comparison_df[comparison_df['Framework'] == framework]
                fig.add_trace(go.Bar(
                    name=framework,
                    x=framework_data['Recommendation'],
                    y=framework_data['Confidence'],
                    text=[f"{c:.0%}" for c in framework_data['Confidence']],
                    textposition='auto',
                ))
            
            fig.update_layout(
                title="Recommendation Confidence by Framework",
                xaxis_title="Recommendation",
                yaxis_title="Confidence",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendation details
            st.subheader("Top Recommendations")
            
            # Sort by confidence and display top 3
            top_recs = comparison_df.nlargest(3, 'Confidence')
            
            for _, rec in top_recs.iterrows():
                with st.expander(f"{rec['Recommendation']} ({rec['Framework']})"):
                    st.write(f"**Priority:** {rec['Priority']}")
                    st.write(f"**Confidence:** {rec['Confidence']:.0%}")
                    
                    # Get the full recommendation details
                    framework = st.session_state.orchestrator.frameworks[rec['Framework']]
                    full_recs = framework.generate_recommendations(st.session_state.results[rec['Framework']])
                    matching_rec = next(r for r in full_recs if r['title'] == rec['Recommendation'])
                    
                    st.write(f"**Reasoning:** {matching_rec['reasoning']}")
                    
                    # Action plan button
                    if st.button(f"Create Action Plan", key=f"plan_{rec['Framework']}_{rec['Recommendation']}"):
                        plan = framework.create_action_plan(matching_rec)
                        st.session_state.selected_plan = plan
                        st.session_state.selected_framework = rec['Framework']
    
    # Action Plan Section
    if 'selected_plan' in st.session_state:
        st.header("📋 Action Plan")
        st.subheader(f"Generated by {st.session_state.selected_framework}")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Timeline visualization
            plan = st.session_state.selected_plan
            
            # Create Gantt chart
            fig = go.Figure()
            
            for i, step in enumerate(plan['steps']):
                fig.add_trace(go.Scatter(
                    x=[0, step['due_days']],
                    y=[i, i],
                    mode='lines+markers+text',
                    name=step['task'],
                    text=[step['owner'], f"Day {step['due_days']}"],
                    textposition="top center",
                    line=dict(width=20),
                    marker=dict(size=10)
                ))
            
            fig.update_layout(
                title="Action Plan Timeline",
                xaxis_title="Days",
                yaxis_title="Tasks",
                height=300,
                showlegend=False,
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(plan['steps']))),
                    ticktext=[s['task'] for s in plan['steps']]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Total Timeline", f"{plan['timeline']} days")
            st.metric("Total Steps", len(plan['steps']))
            
            if 'resources' in plan:
                st.write("**Required Resources:**")
                for resource in plan['resources']:
                    st.write(f"• {resource}")
        
        # Detailed steps
        st.subheader("Detailed Steps")
        
        for i, step in enumerate(plan['steps']):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{i+1}. {step['task']}**")
            with col2:
                st.write(f"Owner: {step['owner']}")
            with col3:
                st.write(f"Due: Day {step['due_days']}")
        
        # Export options
        st.subheader("Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export to Salesforce"):
                st.success("✅ Tasks created in Salesforce")
        
        with col2:
            if st.button("Download as PDF"):
                st.success("📄 PDF downloaded")
        
        with col3:
            if st.button("Send via Email"):
                st.success("📧 Email sent")

# Performance Comparison Dashboard
def create_performance_dashboard():
    st.header("📊 Framework Performance Metrics")
    
    # Mock performance data
    performance_data = {
        "Framework": ["CrewAI", "LangGraph", "AutoGen"],
        "Execution Time (s)": [2.3, 1.8, 2.5],
        "Token Usage": [1500, 1200, 1800],
        "Accuracy Score": [0.92, 0.89, 0.91],
        "User Satisfaction": [4.5, 4.3, 4.4]
    }
    
    df = pd.DataFrame(performance_data)
    
    # Create subplots
    col1, col2 = st.columns(2)
    
    with col1:
        # Execution time comparison
        fig = go.Figure(data=[
            go.Bar(
                x=df['Framework'],
                y=df['Execution Time (s)'],
                text=df['Execution Time (s)'],
                textposition='auto',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
        ])
        fig.update_layout(title="Execution Time Comparison", yaxis_title="Time (seconds)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Token usage comparison
        fig = go.Figure(data=[
            go.Bar(
                x=df['Framework'],
                y=df['Token Usage'],
                text=df['Token Usage'],
                textposition='auto',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
        ])
        fig.update_layout(title="Token Usage Comparison", yaxis_title="Tokens")
        st.plotly_chart(fig, use_container_width=True)
    
    # Radar chart for comprehensive comparison
    categories = ['Execution Time', 'Token Efficiency', 'Accuracy', 'User Satisfaction', 'Feature Richness']
    
    fig = go.Figure()
    
    # Normalize data for radar chart
    crewai_scores = [0.7, 0.6, 0.92, 0.9, 0.95]
    langgraph_scores = [0.9, 0.8, 0.89, 0.86, 0.85]
    autogen_scores = [0.6, 0.5, 0.91, 0.88, 0.9]
    
    fig.add_trace(go.Scatterpolar(
        r=crewai_scores,
        theta=categories,
        fill='toself',
        name='CrewAI'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=langgraph_scores,
        theta=categories,
        fill='toself',
        name='LangGraph'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=autogen_scores,
        theta=categories,
        fill='toself',
        name='AutoGen'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Framework Capability Comparison"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations based on use case
    st.subheader("Framework Recommendations by Use Case")
    
    use_cases = {
        "Complex Multi-Agent Collaboration": {
            "best": "CrewAI",
            "reason": "Excellent agent orchestration and role specialization"
        },
        "Stateful Workflow Management": {
            "best": "LangGraph",
            "reason": "Superior state management and conditional routing"
        },
        "Human-in-the-Loop Scenarios": {
            "best": "AutoGen",
            "reason": "Built-in support for human intervention and approval"
        },
        "RAG-Enhanced Analysis": {
            "best": "AutoGen",
            "reason": "Native RAG support with vector databases"
        },
        "Rapid Prototyping": {
            "best": "LangGraph",
            "reason": "Intuitive graph-based workflow design"
        }
    }
    
    for use_case, recommendation in use_cases.items():
        with st.expander(use_case):
            st.write(f"**Recommended Framework:** {recommendation['best']}")
            st.write(f"**Reason:** {recommendation['reason']}")

# Main app
def main():
    st.set_page_config(
        page_title="Salesforce NBA Framework Comparison",
        page_icon="🔬",
        layout="wide"
    )
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Framework Comparison", "Performance Dashboard", "Documentation"]
    )
    
    if page == "Framework Comparison":
        create_unified_app()
    elif page == "Performance Dashboard":
        create_performance_dashboard()
    else:
        st.header("📚 Documentation")
        
        st.markdown("""
        ## Framework Comparison Guide
        
        ### CrewAI
        - **Strengths:** Multi-agent collaboration, role-based agents, delegation
        - **Best for:** Complex scenarios requiring specialized expertise
        - **Limitations:** Higher token usage, longer execution time
        
        ### LangGraph
        - **Strengths:** State management, conditional routing, workflow visualization
        - **Best for:** Complex workflows with decision points
        - **Limitations:** Steeper learning curve
        
        ### AutoGen
        - **Strengths:** Human-in-the-loop, RAG integration, conversation patterns
        - **Best for:** Scenarios requiring human oversight or historical context
        - **Limitations:** More complex setup
        
        ### Choosing the Right Framework
        
        1. **Use CrewAI when:**
           - You need specialized agents with different expertise
           - Complex problems requiring collaboration
           - Clear role definitions are important
        
        2. **Use LangGraph when:**
           - You have complex conditional logic
           - State management is critical
           - You need visual workflow representation
        
        3. **Use AutoGen when:**
           - Human approval is required
           - You need RAG capabilities
           - Conversation history is important
        """)

if __name__ == "__main__":
    main()