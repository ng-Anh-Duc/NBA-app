# salesforce_nba_crewai.py
"""
Salesforce NBA Application using CrewAI
Multi-agent system for intelligent action planning
"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import streamlit as st
from simple_salesforce import Salesforce
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models for Type Safety
class AccountAnalysis(BaseModel):
    account_id: str
    health_score: int = Field(ge=1, le=10)
    insights: List[str]
    risks: List[str]
    opportunities: List[Dict[str, Any]]

class NextBestActionRecommendation(BaseModel):
    title: str
    description: str
    priority: str
    rationale: str
    expected_impact: str
    required_resources: List[str]

class ActionPlan(BaseModel):
    account_id: str
    selected_action: NextBestActionRecommendation
    steps: List[Dict[str, Any]]
    timeline_days: int
    success_metrics: List[str]
    risk_mitigation: List[str]

# Custom Tools for Agents
class SalesforceDataTool(BaseTool):
    """Tool for fetching Salesforce data"""
    name: str = "salesforce_data_fetcher"
    description: str = "Fetches comprehensive data from Salesforce for a given account"
    
    def __init__(self, sf_connection: Salesforce):
        super().__init__()
        self.sf = sf_connection
    
    def _run(self, account_id: str) -> Dict[str, Any]:
        """Fetch account data from Salesforce"""
        try:
            # Account data
            account_query = f"""
            SELECT Id, Name, Type, Industry, AnnualRevenue, NumberOfEmployees,
                   Rating, AccountSource, Description, LastActivityDate
            FROM Account WHERE Id = '{account_id}'
            """
            account = self.sf.query(account_query)['records'][0]
            
            # Related data
            contacts = self.sf.query(f"SELECT * FROM Contact WHERE AccountId = '{account_id}'")['records']
            opportunities = self.sf.query(f"SELECT * FROM Opportunity WHERE AccountId = '{account_id}'")['records']
            cases = self.sf.query(f"SELECT * FROM Case WHERE AccountId = '{account_id}' LIMIT 10")['records']
            
            return {
                "account": account,
                "contacts": contacts,
                "opportunities": opportunities,
                "cases": cases
            }
        except Exception as e:
            logger.error(f"Error fetching Salesforce data: {e}")
            return {"error": str(e)}

@tool
def analyze_customer_sentiment(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze customer sentiment from cases and interactions"""
    cases = account_data.get('cases', [])
    
    # Simple sentiment analysis based on case data
    high_priority_cases = [c for c in cases if c.get('Priority') == 'High']
    open_cases = [c for c in cases if c.get('Status') != 'Closed']
    
    sentiment_score = 10
    if len(high_priority_cases) > 2:
        sentiment_score -= 3
    if len(open_cases) > 5:
        sentiment_score -= 2
    
    return {
        "sentiment_score": sentiment_score,
        "high_priority_issues": len(high_priority_cases),
        "open_cases": len(open_cases),
        "recommendation": "Address high-priority cases immediately" if sentiment_score < 7 else "Maintain current service level"
    }

@tool
def calculate_revenue_potential(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate revenue potential and upsell opportunities"""
    opportunities = account_data.get('opportunities', [])
    account = account_data.get('account', {})
    
    # Calculate metrics
    total_pipeline = sum(opp.get('Amount', 0) for opp in opportunities if not opp.get('IsClosed'))
    won_revenue = sum(opp.get('Amount', 0) for opp in opportunities if opp.get('IsWon'))
    annual_revenue = account.get('AnnualRevenue', 0)
    
    # Identify potential
    growth_potential = "High" if total_pipeline > annual_revenue * 0.2 else "Medium"
    
    return {
        "total_pipeline": total_pipeline,
        "won_revenue": won_revenue,
        "annual_revenue": annual_revenue,
        "growth_potential": growth_potential,
        "upsell_opportunity": total_pipeline * 0.3  # Estimated upsell
    }

# CrewAI Agents
class SalesforceNBAAgents:
    """Factory for creating specialized agents"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def create_data_analyst_agent(self) -> Agent:
        return Agent(
            role='Senior Data Analyst',
            goal='Analyze Salesforce account data to identify patterns, risks, and opportunities',
            backstory="""You are an expert data analyst with 10+ years of experience in CRM analytics.
            You excel at finding hidden patterns in customer data and identifying both risks and opportunities.
            Your analysis is always data-driven and actionable.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[analyze_customer_sentiment, calculate_revenue_potential]
        )
    
    def create_strategy_agent(self) -> Agent:
        return Agent(
            role='Customer Success Strategist',
            goal='Develop strategic Next Best Actions based on account analysis',
            backstory="""You are a seasoned customer success strategist who has helped hundreds of companies
            grow their accounts. You think strategically about customer relationships and always consider
            both short-term wins and long-term value creation.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    def create_execution_agent(self) -> Agent:
        return Agent(
            role='Sales Operations Manager',
            goal='Create detailed, executable action plans for Salesforce',
            backstory="""You are a detail-oriented operations manager who excels at turning strategies
            into concrete action plans. You understand Salesforce inside-out and know exactly how to
            structure activities for maximum efficiency and tracking.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

# CrewAI Tasks
class SalesforceNBATasks:
    """Factory for creating tasks"""
    
    @staticmethod
    def create_analysis_task(agent: Agent, account_data: Dict[str, Any]) -> Task:
        return Task(
            description=f"""
            Analyze the following Salesforce account data and provide comprehensive insights:
            
            Account Data: {json.dumps(account_data, indent=2)}
            
            Your analysis should include:
            1. Overall account health score (1-10)
            2. Key insights about the account's current state
            3. Identified risks that need attention
            4. Growth opportunities
            5. Customer sentiment analysis
            6. Revenue potential assessment
            
            Provide a structured analysis that will help determine the best actions to take.
            """,
            agent=agent,
            expected_output="Comprehensive account analysis with health score, insights, risks, and opportunities"
        )
    
    @staticmethod
    def create_strategy_task(agent: Agent, context: List[Task]) -> Task:
        return Task(
            description="""
            Based on the account analysis, develop 3 strategic Next Best Actions.
            
            For each action, provide:
            1. Clear title and description
            2. Priority level (High/Medium/Low)
            3. Detailed rationale
            4. Expected business impact
            5. Required resources
            6. Success criteria
            
            Consider both immediate needs and long-term account growth.
            Prioritize actions that will have the highest positive impact.
            """,
            agent=agent,
            context=context,
            expected_output="Three prioritized Next Best Actions with detailed recommendations"
        )
    
    @staticmethod
    def create_planning_task(agent: Agent, selected_action: str, context: List[Task]) -> Task:
        return Task(
            description=f"""
            Create a detailed execution plan for the following Next Best Action:
            
            {selected_action}
            
            Your plan should include:
            1. Step-by-step tasks with specific Salesforce actions
            2. Timeline with due dates for each step
            3. Task assignments and owners
            4. Success metrics and KPIs
            5. Risk mitigation strategies
            6. Follow-up activities
            
            Each step should be directly executable in Salesforce with clear instructions.
            """,
            agent=agent,
            context=context,
            expected_output="Detailed action plan with executable Salesforce tasks and timeline"
        )

# Main CrewAI Application
class SalesforceNBACrewAI:
    """Main application using CrewAI"""
    
    def __init__(self, salesforce_connection: Salesforce, llm_provider: str = "openai"):
        self.sf = salesforce_connection
        self.sf_tool = SalesforceDataTool(salesforce_connection)
        
        # Initialize LLM
        if llm_provider == "openai":
            self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        else:
            self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
        
        # Initialize agents
        self.agents = SalesforceNBAAgents(self.llm)
        self.data_analyst = self.agents.create_data_analyst_agent()
        self.strategist = self.agents.create_strategy_agent()
        self.execution_planner = self.agents.create_execution_agent()
    
    def analyze_account(self, account_id: str) -> AccountAnalysis:
        """Run account analysis crew"""
        # Fetch account data
        account_data = self.sf_tool._run(account_id)
        
        # Create analysis task
        analysis_task = SalesforceNBATasks.create_analysis_task(
            self.data_analyst, 
            account_data
        )
        
        # Create and run crew
        analysis_crew = Crew(
            agents=[self.data_analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = analysis_crew.kickoff()
        
        # Parse and return structured result
        # In practice, you'd parse the LLM output into AccountAnalysis
        return AccountAnalysis(
            account_id=account_id,
            health_score=8,  # Parsed from result
            insights=["Key insight 1", "Key insight 2"],
            risks=["Risk 1", "Risk 2"],
            opportunities=[{"type": "upsell", "value": 50000}]
        )
    
    def generate_recommendations(self, analysis: AccountAnalysis) -> List[NextBestActionRecommendation]:
        """Generate NBA recommendations"""
        # Create tasks
        analysis_task = Task(
            description=f"Account analysis completed: {analysis.json()}",
            agent=self.data_analyst,
            expected_output="Analysis summary"
        )
        
        strategy_task = SalesforceNBATasks.create_strategy_task(
            self.strategist,
            [analysis_task]
        )
        
        # Create and run crew
        strategy_crew = Crew(
            agents=[self.data_analyst, self.strategist],
            tasks=[analysis_task, strategy_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = strategy_crew.kickoff()
        
        # Parse and return recommendations
        # In practice, parse the LLM output
        return [
            NextBestActionRecommendation(
                title="Renewal Campaign",
                description="Launch targeted renewal campaign",
                priority="High",
                rationale="Contract expires in 60 days",
                expected_impact="Secure $100k renewal",
                required_resources=["Sales rep", "Success manager"]
            )
        ]
    
    def create_action_plan(self, account_id: str, selected_action: NextBestActionRecommendation) -> ActionPlan:
        """Create detailed action plan"""
        planning_task = SalesforceNBATasks.create_planning_task(
            self.execution_planner,
            selected_action.json(),
            []
        )
        
        planning_crew = Crew(
            agents=[self.execution_planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = planning_crew.kickoff()
        
        # Parse and return action plan
        return ActionPlan(
            account_id=account_id,
            selected_action=selected_action,
            steps=[
                {
                    "type": "create_task",
                    "title": "Review contract terms",
                    "due_date": "2024-01-15",
                    "owner": "John Doe"
                }
            ],
            timeline_days=30,
            success_metrics=["Contract renewed", "No service disruption"],
            risk_mitigation=["Early engagement", "Executive alignment"]
        )

# Streamlit UI with CrewAI
def create_crewai_app():
    st.title("🤖 Salesforce NBA - CrewAI Multi-Agent System")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Salesforce credentials
        sf_username = st.text_input("Salesforce Username")
        sf_password = st.text_input("Salesforce Password", type="password")
        sf_token = st.text_input("Security Token", type="password")
        
        # LLM selection
        llm_provider = st.selectbox("LLM Provider", ["openai", "gemini"])
        api_key = st.text_input(f"{llm_provider.upper()} API Key", type="password")
        
        if st.button("Initialize Crew"):
            # Set up connections and crew
            sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)
            st.session_state.crew = SalesforceNBACrewAI(sf, llm_provider)
            st.success("Crew initialized!")
    
    # Main workflow
    if 'crew' in st.session_state:
        st.header("1️⃣ Account Analysis")
        account_id = st.text_input("Enter Salesforce Account ID")
        
        if st.button("Analyze Account"):
            with st.spinner("Data Analyst Agent working..."):
                analysis = st.session_state.crew.analyze_account(account_id)
                st.session_state.analysis = analysis
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Health Score", f"{analysis.health_score}/10")
                with col2:
                    st.metric("Risk Level", len(analysis.risks))
                
                st.subheader("Insights")
                for insight in analysis.insights:
                    st.info(f"💡 {insight}")
        
        if 'analysis' in st.session_state:
            st.header("2️⃣ Strategic Recommendations")
            if st.button("Generate Next Best Actions"):
                with st.spinner("Strategy Agent thinking..."):
                    recommendations = st.session_state.crew.generate_recommendations(
                        st.session_state.analysis
                                            )
                    st.session_state.recommendations = recommendations
                    
                    # Display recommendations
                    for i, rec in enumerate(recommendations):
                        with st.expander(f"{rec.priority} Priority: {rec.title}"):
                            st.write(f"**Description:** {rec.description}")
                            st.write(f"**Rationale:** {rec.rationale}")
                            st.write(f"**Expected Impact:** {rec.expected_impact}")
                            st.write(f"**Required Resources:** {', '.join(rec.required_resources)}")
                            
                            if st.button(f"Select this action", key=f"select_{i}"):
                                st.session_state.selected_action = rec
                                st.success(f"Selected: {rec.title}")
        
        if 'selected_action' in st.session_state:
            st.header("3️⃣ Action Planning")
            if st.button("Create Execution Plan"):
                with st.spinner("Execution Agent creating plan..."):
                    plan = st.session_state.crew.create_action_plan(
                        account_id,
                        st.session_state.selected_action
                    )
                    st.session_state.action_plan = plan
                    
                    # Display plan
                    st.subheader("Execution Timeline")
                    st.write(f"**Duration:** {plan.timeline_days} days")
                    
                    # Show steps
                    for step in plan.steps:
                        st.write(f"📌 **{step['title']}**")
                        st.write(f"   Due: {step['due_date']} | Owner: {step['owner']}")
                    
                    st.subheader("Success Metrics")
                    for metric in plan.success_metrics:
                        st.write(f"✅ {metric}")

if __name__ == "__main__":
    create_crewai_app()