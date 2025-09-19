import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
import google.generativeai as genai
from datetime import datetime
import json
import time
from typing import Dict, List, Any

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'sf_connection' not in st.session_state:
    st.session_state.sf_connection = None
if 'account_data' not in st.session_state:
    st.session_state.account_data = None
if 'nba_recommendation' not in st.session_state:
    st.session_state.nba_recommendation = None
if 'action_plan' not in st.session_state:
    st.session_state.action_plan = None

class SalesforceConnector:
    def __init__(self, username, password, security_token, domain='login'):
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain
        )
    
    def get_account_data(self, account_id):
        """Fetch comprehensive account data"""
        account_data = {}
        
        # Get Account details
        account_query = f"""
        SELECT Id, Name, Type, Industry, AnnualRevenue, NumberOfEmployees,
               Rating, AccountSource, Description, LastActivityDate,
               CreatedDate, LastModifiedDate
        FROM Account
        WHERE Id = '{account_id}'
        """
        account_data['account'] = self.sf.query(account_query)['records'][0]
        
        # Get related Contacts
        contacts_query = f"""
        SELECT Id, Name, Title, Email, Phone, LastActivityDate
        FROM Contact
        WHERE AccountId = '{account_id}'
        """
        account_data['contacts'] = self.sf.query(contacts_query)['records']
        
        # Get Opportunities
        opps_query = f"""
        SELECT Id, Name, StageName, Amount, CloseDate, Probability,
               Type, LeadSource, IsClosed, IsWon
        FROM Opportunity
        WHERE AccountId = '{account_id}'
        ORDER BY CloseDate DESC
        """
        account_data['opportunities'] = self.sf.query(opps_query)['records']
        
        # Get Cases
        cases_query = f"""
        SELECT Id, CaseNumber, Subject, Status, Priority, CreatedDate
        FROM Case
        WHERE AccountId = '{account_id}'
        ORDER BY CreatedDate DESC
        LIMIT 10
        """
        account_data['cases'] = self.sf.query(cases_query)['records']
        
        # Get Activities
        tasks_query = f"""
        SELECT Id, Subject, Status, ActivityDate, Description
        FROM Task
        WHERE AccountId = '{account_id}'
        ORDER BY ActivityDate DESC
        LIMIT 10
        """
        account_data['tasks'] = self.sf.query(tasks_query)['records']
        
        return account_data
    
    def create_task(self, account_id, subject, description, due_date):
        """Create a new task in Salesforce"""
        task_data = {
            'Subject': subject,
            'Description': description,
            'ActivityDate': due_date,
            'Status': 'Not Started',
            'Priority': 'Normal',
            'WhatId': account_id
        }
        return self.sf.Task.create(task_data)
    
    def update_opportunity(self, opp_id, stage_name, next_step=None):
        """Update opportunity stage"""
        update_data = {'StageName': stage_name}
        if next_step:
            update_data['NextStep'] = next_step
        return self.sf.Opportunity.update(opp_id, update_data)
    
    def create_case(self, account_id, subject, description):
        """Create a new case"""
        case_data = {
            'Subject': subject,
            'Description': description,
            'AccountId': account_id,
            'Status': 'New',
            'Priority': 'Medium'
        }
        return self.sf.Case.create(case_data)

class GeminiAnalyzer:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_account_for_nba(self, account_data):
        """Analyze account data and generate Next Best Action"""
        prompt = f"""
        Analyze this Salesforce account data and provide Next Best Action recommendations:
        
        Account: {json.dumps(account_data['account'], indent=2)}
        Contacts: {json.dumps(account_data['contacts'], indent=2)}
        Opportunities: {json.dumps(account_data['opportunities'], indent=2)}
        Recent Cases: {json.dumps(account_data['cases'], indent=2)}
        Recent Tasks: {json.dumps(account_data['tasks'], indent=2)}
        
        Based on this data, provide:
        1. Current account health assessment
        2. Key insights and patterns
        3. Top 3 Next Best Actions with rationale
        4. Risk factors to monitor
        
        Format your response as JSON with these keys:
        - health_score (1-10)
        - insights (list of key insights)
        - next_best_actions (list of 3 actions with title, description, priority, and rationale)
        - risks (list of risk factors)
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
    def create_action_plan(self, nba_recommendation, selected_action):
        """Create detailed action plan for selected NBA"""
        prompt = f"""
        Create a detailed action plan for this Next Best Action:
        
        Action: {json.dumps(selected_action, indent=2)}
        Context: {json.dumps(nba_recommendation, indent=2)}
        
        Generate a step-by-step action plan that can be executed in Salesforce.
        Include specific tasks, timelines, and success metrics.
        
        Format as JSON with:
        - steps (list of steps with: type, title, description, due_date, salesforce_action)
        - success_metrics (list of measurable outcomes)
        - timeline (overall timeline in days)
        
        Salesforce action types can be: create_task, update_opportunity, create_case, send_email
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)

def execute_action_plan(sf_connector, account_id, action_plan):
    """Execute the approved action plan in Salesforce"""
    results = []
    
    for step in action_plan['steps']:
        try:
            if step['salesforce_action'] == 'create_task':
                result = sf_connector.create_task(
                    account_id,
                    step['title'],
                    step['description'],
                    step['due_date']
                )
                results.append({
                    'step': step['title'],
                    'status': 'success',
                    'id': result['id']
                })
            
            elif step['salesforce_action'] == 'update_opportunity':
                # This would need the opportunity ID from the context
                results.append({
                    'step': step['title'],
                    'status': 'pending',
                    'message': 'Opportunity update requires manual selection'
                })
            
            elif step['salesforce_action'] == 'create_case':
                result = sf_connector.create_case(
                    account_id,
                    step['title'],
                    step['description']
                )
                results.append({
                    'step': step['title'],
                    'status': 'success',
                    'id': result['id']
                })
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            results.append({
                'step': step['title'],
                'status': 'error',
                'message': str(e)
            })
    
    return results

# Streamlit UI
st.title("🚀 Salesforce AI-Powered Next Best Action")

# Sidebar for authentication
with st.sidebar:
    st.header("Configuration")
    
    if not st.session_state.authenticated:
        st.subheader("Salesforce Credentials")
        sf_username = st.text_input("Username")
        sf_password = st.text_input("Password", type="password")
        sf_token = st.text_input("Security Token", type="password")
        sf_domain = st.selectbox("Domain", ["login", "test"])
        
        st.subheader("Gemini API")
        gemini_api_key = st.text_input("Gemini API Key", type="password")
        
        if st.button("Connect"):
            try:
                sf_connector = SalesforceConnector(
                    sf_username, sf_password, sf_token, sf_domain
                )
                gemini_analyzer = GeminiAnalyzer(gemini_api_key)
                
                st.session_state.sf_connection = sf_connector
                st.session_state.gemini_analyzer = gemini_analyzer
                st.session_state.authenticated = True
                st.success("Connected successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")
    else:
        st.success("✅ Connected")
        if st.button("Disconnect"):
            st.session_state.authenticated = False
            st.session_state.sf_connection = None
            st.rerun()

# Main content
if st.session_state.authenticated:
    # Account selection
    st.header("1️⃣ Select Account")
    account_id = st.text_input("Enter Salesforce Account ID")
    
    if st.button("Fetch Account Data"):
        with st.spinner("Fetching account data..."):
            try:
                account_data = st.session_state.sf_connection.get_account_data(account_id)
                st.session_state.account_data = account_data
                st.success("Account data fetched successfully!")
            except Exception as e:
                st.error(f"Error fetching account: {str(e)}")
    
    # Display account data
    if st.session_state.account_data:
        account = st.session_state.account_data['account']
        st.subheader(f"Account: {account['Name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Industry", account.get('Industry', 'N/A'))
            st.metric("Type", account.get('Type', 'N/A'))
        with col2:
            st.metric("Annual Revenue", f"${account.get('AnnualRevenue', 0):,.0f}")
            st.metric("Employees", account.get('NumberOfEmployees', 'N/A'))
        with col3:
            st.metric("Rating", account.get('Rating', 'N/A'))
            st.metric("Open Opportunities", len(st.session_state.account_data['opportunities']))
        
        # Analyze with AI
        st.header("2️⃣ AI Analysis & Next Best Action")
        if st.button("Generate Next Best Actions"):
            with st.spinner("Analyzing account data with AI..."):
                try:
                    nba = st.session_state.gemini_analyzer.analyze_account_for_nba(
                        st.session_state.account_data
                    )
                    st.session_state.nba_recommendation = nba
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
        
        # Display NBA recommendations
        if st.session_state.nba_recommendation:
            nba = st.session_state.nba_recommendation
            
            st.subheader("Account Health")
            st.progress(nba['health_score'] / 10)
            st.write(f"Health Score: {nba['health_score']}/10")
            
            st.subheader("Key Insights")
            for insight in nba['insights']:
                st.info(f"💡 {insight}")
            
            st.subheader("Recommended Next Best Actions")
            selected_action = None
            for i, action in enumerate(nba['next_best_actions']):
                with st.expander(f"{action['priority']} Priority: {action['title']}"):
                    st.write(action['description'])
                    st.write(f"**Rationale:** {action['rationale']}")
                    if st.button(f"Select this action", key=f"action_{i}"):
                        selected_action = action
                        st.session_state.selected_action = action
            
            # Create action plan
            if 'selected_action' in st.session_state:
                st.header("3️⃣ Action Plan")
                if st.button("Generate Action Plan"):
                    with st.spinner("Creating detailed action plan..."):
                        try:
                            plan = st.session_state.gemini_analyzer.create_action_plan(
                                st.session_state.nba_recommendation,
                                st.session_state.selected_action
                            )
                            st.session_state.action_plan = plan
                            st.success("Action plan created!")
                        except Exception as e:
                            st.error(f"Error creating plan: {str(e)}")
            
            # Display and execute action plan
            if st.session_state.action_plan:
                plan = st.session_state.action_plan
                
                st.subheader("Proposed Action Steps")
                for step in plan['steps']:
                    st.write(f"**{step['title']}**")
                    st.write(f"- {step['description']}")
                    st.write(f"- Due: {step['due_date']}")
                    st.write(f"- Action Type: {step['salesforce_action']}")
                    st.divider()
                
                st.subheader("Success Metrics")
                for metric in plan['success_metrics']:
                    st.write(f"✅ {metric}")
                
                st.write(f"**Timeline:** {plan['timeline']} days")
                
                # Execute plan
                st.header("4️⃣ Execute Plan")
                st.warning("⚠️ This will create records in Salesforce. Please review carefully.")
                
                if st.button("Execute Action Plan", type="primary"):
                    with st.spinner("Executing actions in Salesforce..."):
                        results = execute_action_plan(
                            st.session_state.sf_connection,
                            account_id,
                            plan
                        )
                        
                        st.subheader("Execution Results")
                        for result in results:
                            if result['status'] == 'success':
                                st.success(f"✅ {result['step']} - Created (ID: {result['id']})")
                            elif result['status'] == 'pending':
                                st.warning(f"⏳ {result['step']} - {result['message']}")
                            else:
                                st.error(f"❌ {result['step']} - {result['message']}")
else:
    st.info("Please connect to Salesforce and Gemini in the sidebar to get started.")