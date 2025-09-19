# salesforce_nba_autogen.py
"""
Salesforce NBA using Microsoft AutoGen
Multi-agent conversation for collaborative decision making
"""

import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import streamlit as st
from simple_salesforce import Salesforce
import json
import chromadb
from typing import Dict, List, Any, Optional
import pandas as pd

# Configuration
config_list = [
    {
        "model": "gpt-4",
        "api_key": "your-api-key",
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "cache_seed": 42,
}

# Custom Salesforce Integration
class SalesforceIntegration:
    """Handle Salesforce operations for AutoGen agents"""
    
    def __init__(self, username: str, password: str, security_token: str):
        self.sf = Salesforce(username=username, password=password, security_token=security_token)
    
    def get_account_context(self, account_id: str) -> str:
        """Get formatted account context for agents"""
        # Fetch data
        account = self.sf.query(f"SELECT * FROM Account WHERE Id = '{account_id}'")['records'][0]
        opportunities = self.sf.query(f"SELECT * FROM Opportunity WHERE AccountId = '{account_id}'")['records']
        cases = self.sf.query(f"SELECT * FROM Case WHERE AccountId = '{account_id}'")['records']
        
        # Format for agents
        context = f"""
        Account Information:
        - Name: {account['Name']}
        - Industry: {account.get('Industry', 'N/A')}
        - Annual Revenue: ${account.get('AnnualRevenue', 0):,.0f}
        - Number of Employees: {account.get('NumberOfEmployees', 'N/A')}
        
        Opportunities:
        - Total: {len(opportunities)}
        - Open: {len([o for o in opportunities if not o.get('IsClosed')])}
        - Pipeline Value: ${sum(o.get('Amount', 0) for o in opportunities if not o.get('IsClosed')):,.0f}
        
        Support Cases:
        - Total: {len(cases)}
        - Open: {len([c for c in cases if c.get('Status') != 'Closed'])}
        """
        
        return context

# AutoGen Agents
class SalesforceNBAAgents:
    """Create specialized AutoGen agents for Salesforce NBA"""
    
    def __init__(self, llm_config: dict, salesforce: SalesforceIntegration):
        self.llm_config = llm_config
        self.salesforce = salesforce
        
        # Create agents
        self.data_analyst = self._create_data_analyst()
        self.strategist = self._create_strategist()
        self.risk_analyst = self._create_risk_analyst()
        self.execution_planner = self._create_execution_planner()
        self.user_proxy = self._create_user_proxy()
    
    def _create_data_analyst(self) -> AssistantAgent:
        """Create data analyst agent"""
        return AssistantAgent(
            name="DataAnalyst",
            system_message="""You are a Senior Data Analyst specializing in Salesforce CRM data.
            Your role is to:
            1. Analyze account data to identify patterns and trends
            2. Calculate key metrics and KPIs
            3. Identify data quality issues
            4. Provide data-driven insights
            
            Always base your analysis on the provided data and be specific with numbers.""",
            llm_config=self.llm_config,
        )
    
    def _create_strategist(self) -> AssistantAgent:
        """Create customer success strategist agent"""
        return AssistantAgent(
            name="Strategist",
            system_message="""You are a Customer Success Strategist with 10+ years of experience.
            Your role is to:
            1. Develop strategic recommendations based on data analysis
            2. Identify growth opportunities and upsell potential
            3. Create customer retention strategies
            4. Prioritize actions based on business impact
            
            Focus on actionable recommendations that drive customer value and revenue growth.""",
            llm_config=self.llm_config,
        )
    
    def _create_risk_analyst(self) -> AssistantAgent:
        """Create risk analyst agent"""
        return AssistantAgent(
            name="RiskAnalyst",
            system_message="""You are a Risk Analyst specializing in customer churn and account health.
            Your role is to:
            1. Identify churn risks and early warning signs
            2. Assess account health and stability
            3. Recommend risk mitigation strategies
            4. Monitor compliance and contractual risks
            
            Be thorough in identifying potential risks and provide specific mitigation actions.""",
            llm_config=self.llm_config,
        )
    
    def _create_execution_planner(self) -> AssistantAgent:
        """Create execution planner agent"""
        return AssistantAgent(
            name="ExecutionPlanner",
            system_message="""You are an Execution Planning Specialist who creates detailed action plans.
            Your role is to:
            1. Convert strategies into specific, executable tasks
            2. Create timelines and assign responsibilities
            3. Define success metrics and KPIs
            4. Structure tasks for Salesforce implementation
            
            Always provide clear, step-by-step plans with specific Salesforce actions.""",
            llm_config=self.llm_config,
        )
    
    def _create_user_proxy(self) -> UserProxyAgent:
        """Create user proxy for human interaction"""
        return UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",  # Set to "ALWAYS" for human-in-the-loop
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )

# AutoGen Workflow Manager
class AutoGenNBAWorkflow:
    """Manage the AutoGen multi-agent workflow"""
    
    def __init__(self, agents: SalesforceNBAAgents):
        self.agents = agents
        
        # Create group chat
        self.group_chat = GroupChat(
            agents=[
                agents.data_analyst,
                agents.strategist,
                agents.risk_analyst,
                agents.execution_planner,
                agents.user_proxy
            ],
            messages=[],
            max_round=20,
            speaker_selection_method="round_robin",  # Can be "auto" for dynamic selection
        )
        
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=agents.llm_config,
        )
    
    def analyze_account(self, account_context: str) -> Dict[str, Any]:
        """Run the full NBA analysis workflow"""
        # Initial message to start the conversation
        initial_message = f"""
        Please analyze this Salesforce account and provide Next Best Action recommendations.
        
        {account_context}
        
        The workflow should be:
        1. DataAnalyst: Analyze the account data and provide insights
        2. RiskAnalyst: Assess risks and account health
        3. Strategist: Recommend Next Best Actions based on the analysis
        4. ExecutionPlanner: Create a detailed action plan for the top recommendation
        
        Let's begin with the data analysis.
        """
        
        # Start the group chat
        self.agents.user_proxy.initiate_chat(
            self.manager,
            message=initial_message,
        )
        
        # Extract results from conversation
        return self._extract_results()
    
    def _extract_results(self) -> Dict[str, Any]:
        """Extract structured results from the conversation"""
        messages = self.group_chat.messages
        
        results = {
            "analysis": {},
            "risks": [],
            "recommendations": [],
            "action_plan": {}
        }
        
        # Parse messages from each agent
        for msg in messages:
            if msg.get("name") == "DataAnalyst":
                # Extract analysis insights
                results["analysis"]["insights"] = msg.get("content", "")
            elif msg.get("name") == "RiskAnalyst":
                # Extract risks
                results["risks"].append(msg.get("content", ""))
            elif msg.get("name") == "Strategist":
                # Extract recommendations
                results["recommendations"].append(msg.get("content", ""))
            elif msg.get("name") == "ExecutionPlanner":
                # Extract action plan
                results["action_plan"]["details"] = msg.get("content", "")
        
        return results

# RAG-Enhanced AutoGen
class RAGEnhancedNBAWorkflow:
    """AutoGen workflow with RAG for historical context"""
    
    def __init__(self, agents: SalesforceNBAAgents, docs_path: str = "./salesforce_docs"):
        self.agents = agents
        self.docs_path = docs_path
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection("salesforce_nba")
        
        # Create RAG-enhanced agents
        self.rag_assistant = RetrieveAssistantAgent(
            name="RAGAssistant",
            system_message="You are an assistant with access to historical Salesforce data and best practices.",
            llm_config=agents.llm_config,
            retrieve_config={
                "task": "qa",
                "docs_path": docs_path,
                "chunk_token_size": 1000,
                "model": "gpt-4",
                "client": self.chroma_client,
                "collection_name": "salesforce_nba",
                "get_or_create": True,
            },
        )
        
        self.rag_user_proxy = RetrieveUserProxyAgent(
            name="RAGUserProxy",
            human_input_mode="NEVER",
            retrieve_config={
                "task": "qa",
                "docs_path": docs_path,
            },
        )
    
    def analyze_with_context(self, account_context: str, query: str) -> str:
        """Analyze account with historical context"""
        # First, retrieve relevant historical information
        self.rag_user_proxy.initiate_chat(
            self.rag_assistant,
            problem=f"{query}\n\nCurrent Account Context:\n{account_context}",
        )
        
        # Get the response
        return self.rag_assistant.last_message()["content"]

# Streamlit UI for AutoGen
def create_autogen_app():
    st.title("🤝 Salesforce NBA - AutoGen Multi-Agent System")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Salesforce credentials
        sf_username = st.text_input("Salesforce Username")
        sf_password = st.text_input("Salesforce Password", type="password")
        sf_token = st.text_input("Security Token", type="password")
        
        # OpenAI configuration
        openai_key = st.text_input("OpenAI API Key", type="password")
        
        if st.button("Initialize Agents"):
            # Configure LLM
            config_list = [{"model": "gpt-4", "api_key": openai_key}]
            llm_config = {"config_list": config_list, "temperature": 0.7}
            
            # Initialize Salesforce
            sf_integration = SalesforceIntegration(sf_username, sf_password, sf_token)
            
            # Create agents
            agents = SalesforceNBAAgents(llm_config, sf_integration)
            workflow = AutoGenNBAWorkflow(agents)
            
            st.session_state.workflow = workflow
            st.session_state.sf_integration = sf_integration
            st.success("Agents initialized!")
    
    # Main interface
    if 'workflow' in st.session_state:
        st.header("Account Analysis")
        
        account_id = st.text_input("Enter Salesforce Account ID")
        
        if st.button("Start Multi-Agent Analysis"):
            with st.spinner("Agents collaborating..."):
                # Get account context
                context = st.session_state.sf_integration.get_account_context(account_id)
                
                # Display context
                with st.expander("Account Context"):
                    st.text(context)
                
                # Run workflow
                results = st.session_state.workflow.analyze_account(context)
                
                # Display results
                st.header("Analysis Results")
                
                # Show conversation
                with st.expander("Agent Conversation"):
                    for msg in st.session_state.workflow.group_chat.messages:
                        agent_name = msg.get("name", "Unknown")
                        content = msg.get("content", "")
                        st.write(f"**{agent_name}:**")
                        st.write(content)
                        st.divider()
                
                # Structured results
                if results.get("recommendations"):
                    st.subheader("Recommendations")
                    for rec in results["recommendations"]:
                        st.write(rec)
                
                if results.get("action_plan"):
                    st.subheader("Action Plan")
                    st.write(results["action_plan"].get("details", ""))
        
        # RAG-enhanced analysis
        st.header("Historical Context Analysis")
        
        if st.checkbox("Enable RAG for historical insights"):
            query = st.text_area("Ask about similar accounts or best practices")
            
            if st.button("Analyze with Historical Context"):
                with st.spinner("Searching historical data..."):
                    # Initialize RAG workflow if not exists
                    if 'rag_workflow' not in st.session_state:
                        st.session_state.rag_workflow = RAGEnhancedNBAWorkflow(
                            st.session_state.workflow.agents,
                            docs_path="./salesforce_docs"
                        )
                    
                    # Get context and analyze
                    context = st.session_state.sf_integration.get_account_context(account_id)
                    response = st.session_state.rag_workflow.analyze_with_context(context, query)
                    
                    st.subheader("Historical Insights")
                    st.write(response)

if __name__ == "__main__":
    create_autogen_app()