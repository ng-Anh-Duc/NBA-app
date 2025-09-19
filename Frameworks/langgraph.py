# salesforce_nba_langgraph.py
"""
Salesforce NBA using LangGraph
Stateful workflow with conditional routing
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.checkpoint import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate
import operator
import streamlit as st
from simple_salesforce import Salesforce
import json
import pandas as pd

# State Definition
class SalesforceNBAState(TypedDict):
    """State for the NBA workflow"""
    account_id: str
    account_data: dict
    analysis: dict
    recommendations: list
    selected_action: dict
    action_plan: dict
    execution_results: list
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    error: str

# Tools
@tool
def fetch_salesforce_data(account_id: str, connection_params: dict) -> dict:
    """Fetch comprehensive Salesforce data for an account"""
    sf = Salesforce(**connection_params)
    
    # Fetch all relevant data
    account = sf.query(f"SELECT * FROM Account WHERE Id = '{account_id}'")['records'][0]
    contacts = sf.query(f"SELECT * FROM Contact WHERE AccountId = '{account_id}'")['records']
    opportunities = sf.query(f"SELECT * FROM Opportunity WHERE AccountId = '{account_id}'")['records']
    cases = sf.query(f"SELECT * FROM Case WHERE AccountId = '{account_id}' ORDER BY CreatedDate DESC LIMIT 20")['records']
    
    return {
        "account": account,
        "contacts": contacts,
        "opportunities": opportunities,
        "cases": cases,
        "summary": {
            "total_contacts": len(contacts),
            "open_opportunities": len([o for o in opportunities if not o.get('IsClosed')]),
            "total_opportunity_value": sum(o.get('Amount', 0) for o in opportunities if not o.get('IsClosed')),
            "open_cases": len([c for c in cases if c.get('Status') != 'Closed'])
        }
    }

@tool
def analyze_account_health(account_data: dict) -> dict:
    """Analyze account health and identify patterns"""
    account = account_data['account']
    summary = account_data['summary']
    
    # Calculate health score
    health_score = 10
    insights = []
    risks = []
    
    # Analyze opportunities
    if summary['open_opportunities'] == 0:
        health_score -= 2
        risks.append("No open opportunities - potential churn risk")
    
    if summary['total_opportunity_value'] < account.get('AnnualRevenue', 0) * 0.1:
        health_score -= 1
        risks.append("Low pipeline value relative to annual revenue")
    
    # Analyze cases
    if summary['open_cases'] > 5:
        health_score -= 2
        risks.append(f"High number of open cases ({summary['open_cases']})")
    
    # Positive indicators
    if summary['total_contacts'] > 5:
        insights.append("Strong relationship with multiple contacts")
    
    return {
        "health_score": max(1, health_score),
        "insights": insights,
        "risks": risks,
        "summary": summary
    }

@tool
def create_salesforce_task(task_details: dict, connection_params: dict) -> dict:
    """Create a task in Salesforce"""
    sf = Salesforce(**connection_params)
    
    result = sf.Task.create({
        'Subject': task_details['subject'],
        'Description': task_details['description'],
        'ActivityDate': task_details['due_date'],
        'Status': 'Not Started',
        'Priority': task_details.get('priority', 'Normal'),
        'WhatId': task_details['account_id']
    })
    
    return {"success": True, "task_id": result['id']}

# LangGraph Nodes
class SalesforceNBAWorkflow:
    """Workflow for Salesforce NBA using LangGraph"""
    
    def __init__(self, llm, salesforce_connection):
        self.llm = llm
        self.sf_connection = salesforce_connection
        self.tools = [fetch_salesforce_data, analyze_account_health, create_salesforce_task]
        self.tool_executor = ToolExecutor(self.tools)
        
        # Build the graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(SalesforceNBAState)
        
        # Add nodes
        workflow.add_node("fetch_data", self.fetch_data_node)
        workflow.add_node("analyze", self.analyze_node)
        workflow.add_node("recommend", self.recommend_node)
        workflow.add_node("plan", self.plan_node)
        workflow.add_node("execute", self.execute_node)
        workflow.add_node("error_handler", self.error_handler_node)
        
        # Add edges
        workflow.set_entry_point("fetch_data")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "fetch_data",
            self.route_after_fetch,
            {
                "analyze": "analyze",
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("analyze", "recommend")
        workflow.add_edge("recommend", "plan")
        
        workflow.add_conditional_edges(
            "plan",
            self.route_after_plan,
            {
                "execute": "execute",
                "end": END
            }
        )
        
        workflow.add_edge("execute", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def fetch_data_node(self, state: SalesforceNBAState) -> SalesforceNBAState:
        """Node to fetch Salesforce data"""
        try:
            account_data = fetch_salesforce_data.invoke({
                "account_id": state["account_id"],
                "connection_params": self.sf_connection
            })
            
            state["account_data"] = account_data
            state["messages"].append(
                AIMessage(content=f"Successfully fetched data for account {state['account_id']}")
            )
            state["next_step"] = "analyze"
        except Exception as e:
            state["error"] = str(e)
            state["next_step"] = "error"
        
        return state
    
    def analyze_node(self, state: SalesforceNBAState) -> SalesforceNBAState:
        """Node to analyze account data"""
        analysis = analyze_account_health.invoke({"account_data": state["account_data"]})
        
        # Use LLM for deeper analysis
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Salesforce data analyst. Analyze the account data and provide insights."),
            ("human", f"Account data: {json.dumps(state['account_data'], indent=2)}\n\nHealth analysis: {json.dumps(analysis, indent=2)}")
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        state["analysis"] = {
            **analysis,
            "llm_insights": response.content
        }
        state["messages"].append(AIMessage(content="Account analysis completed"))
        
        return state
    
    def recommend_node(self, state: SalesforceNBAState) -> SalesforceNBAState:
        """Node to generate NBA recommendations"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a customer success strategist. Based on the account analysis, 
            recommend the top 3 Next Best Actions. For each action provide:
            - Title
            - Description
            - Priority (High/Medium/Low)
            - Expected impact
            - Rationale
            
            Format as JSON array."""),
            ("human", f"Analysis: {json.dumps(state['analysis'], indent=2)}")
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        # Parse recommendations (in practice, use output parser)
        recommendations = [
            {
                "title": "Renewal Campaign",
                "description": "Launch targeted renewal campaign",
                "priority": "High",
                "impact": "Secure $100k renewal",
                "rationale": "Contract expires soon"
            },
            {
                "title": "Upsell Opportunity",
                "description": "Present new product features",
                "priority": "Medium",
                "impact": "20% revenue increase",
                "rationale": "Growing usage patterns"
            }
        ]
        
        state["recommendations"] = recommendations
        state["messages"].append(AIMessage(content="Generated NBA recommendations"))
        
        return state
    
    def plan_node(self, state: SalesforceNBAState) -> SalesforceNBAState:
        """Node to create action plan"""
        # For demo, use first recommendation
        selected_action = state["recommendations"][0] if state["recommendations"] else None
        
        if not selected_action:
            state["next_step"] = "end"
            return state
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a detailed action plan for the selected Next Best Action.
            Include specific Salesforce tasks with due dates and owners.
            Format as JSON with 'steps' array."""),
            ("human", f"Selected action: {json.dumps(selected_action, indent=2)}")
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        # Parse plan
        action_plan = {
            "selected_action": selected_action,
            "steps": [
                {
                    "type": "task",
                    "subject": "Review account contract",
                    "description": "Review contract terms and prepare renewal proposal",
                    "due_date": "2024-01-15",
                    "owner": "Account Manager"
                },
                {
                    "type": "task",
                    "subject": "Schedule renewal meeting",
                    "description": "Schedule meeting with key stakeholders",
                    "due_date": "2024-01-20",
                    "owner": "Account Manager"
                }
            ]
        }
        
        state["action_plan"] = action_plan
        state["selected_action"] = selected_action
        state["next_step"] = "execute"
        
        return state
    
    def execute_node(self, state: SalesforceNBAState) -> SalesforceNBAState:
        """Node to execute the action plan"""
        results = []
        
        for step in state["action_plan"]["steps"]:
            if step["type"] == "task":
                result = create_salesforce_task.invoke({
                    "task_details": {
                        "subject": step["subject"],
                        "description": step["description"],
                        "due_date": step["due_date"],
                        "account_id": state["account_id"]
                    },
                    "connection_params": self.sf_connection
                })
                results.append(result)
        
        state["execution_results"] = results
        state["messages"].append(
            AIMessage(content=f"Successfully executed {len(results)} tasks")
        )
        
        return state
    
    def error_handler_node(self, state: SalesforceNBAState) -> SalesforceNBAState:
        """Node to handle errors"""
        state["messages"].append(
            AIMessage(content=f"Error occurred: {state.get('error', 'Unknown error')}")
        )
        return state
    
    def route_after_fetch(self, state: SalesforceNBAState) -> Literal["analyze", "error"]:
        """Routing logic after fetch"""
        return "analyze" if state.get("next_step") == "analyze" else "error"
    
    def route_after_plan(self, state: SalesforceNBAState) -> Literal["execute", "end"]:
        """Routing logic after planning"""
        return "execute" if state.get("next_step") == "execute" else "end"

# Streamlit UI for LangGraph
def create_langgraph_app():
    st.title("🔄 Salesforce NBA - LangGraph Workflow")
    
    # Initialize workflow
    if 'workflow' not in st.session_state:
        # Setup (would come from UI inputs)
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        sf_connection = {
            "username": st.sidebar.text_input("Username"),
            "password": st.sidebar.text_input("Password", type="password"),
            "security_token": st.sidebar.text_input("Token", type="password")
        }
        
        if st.sidebar.button("Initialize Workflow"):
            st.session_state.workflow = SalesforceNBAWorkflow(llm, sf_connection)
            st.success("Workflow initialized!")
    
    # Main interface
    if 'workflow' in st.session_state:
        account_id = st.text_input("Enter Account ID")
        
        if st.button("Run NBA Workflow"):
            # Initialize state
            initial_state = {
                "account_id": account_id,
                "account_data": {},
                "analysis": {},
                "recommendations": [],
                "selected_action": {},
                "action_plan": {},
                "execution_results": [],
                "messages": [HumanMessage(content=f"Analyze account {account_id}")],
                "next_step": "",
                "error": ""
            }
            
            # Run workflow
            with st.spinner("Running workflow..."):
                config = {"configurable": {"thread_id": account_id}}
                                final_state = st.session_state.workflow.workflow.invoke(initial_state, config)
            
            # Display results
            st.header("Workflow Results")
            
            # Show messages
            with st.expander("Workflow Messages"):
                for msg in final_state["messages"]:
                    if isinstance(msg, HumanMessage):
                        st.write(f"👤 **Human:** {msg.content}")
                    elif isinstance(msg, AIMessage):
                        st.write(f"🤖 **AI:** {msg.content}")
            
            # Show analysis
            if final_state.get("analysis"):
                st.subheader("Account Analysis")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Health Score", f"{final_state['analysis']['health_score']}/10")
                with col2:
                    st.metric("Open Opportunities", final_state['analysis']['summary']['open_opportunities'])
                with col3:
                    st.metric("Open Cases", final_state['analysis']['summary']['open_cases'])
                
                # Insights and risks
                if final_state['analysis'].get('insights'):
                    st.write("**Insights:**")
                    for insight in final_state['analysis']['insights']:
                        st.info(f"💡 {insight}")
                
                if final_state['analysis'].get('risks'):
                    st.write("**Risks:**")
                    for risk in final_state['analysis']['risks']:
                        st.warning(f"⚠️ {risk}")
            
            # Show recommendations
            if final_state.get("recommendations"):
                st.subheader("Next Best Actions")
                for rec in final_state["recommendations"]:
                    with st.expander(f"{rec['priority']} Priority: {rec['title']}"):
                        st.write(f"**Description:** {rec['description']}")
                        st.write(f"**Expected Impact:** {rec['impact']}")
                        st.write(f"**Rationale:** {rec['rationale']}")
            
            # Show execution results
            if final_state.get("execution_results"):
                st.subheader("Execution Results")
                for result in final_state["execution_results"]:
                    if result.get("success"):
                        st.success(f"✅ Created task: {result['task_id']}")
                    else:
                        st.error("❌ Task creation failed")

if __name__ == "__main__":
    create_langgraph_app()