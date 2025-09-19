# Add these additional features to enhance the app

class EnhancedSalesforceConnector(SalesforceConnector):
    def send_email(self, to_addresses, subject, body, account_id):
        """Send email through Salesforce"""
        email_data = {
            'ToAddress': to_addresses,
            'Subject': subject,
            'TextBody': body,
            'WhatId': account_id,
            'SaveAsActivity': True
        }
        return self.sf.EmailMessage.create(email_data)
    
    def get_account_insights(self, account_id):
        """Get additional insights like churn risk, upsell potential"""
        # Calculate days since last activity
        activities_query = f"""
        SELECT MAX(ActivityDate) as LastActivity
        FROM Task
        WHERE AccountId = '{account_id}' AND Status = 'Completed'
        """
        
        # Get contract information
        contracts_query = f"""
        SELECT Id, Status, EndDate, ContractTerm
        FROM Contract
        WHERE AccountId = '{account_id}'
        """
        
        return {
            'activities': self.sf.query(activities_query)['records'],
            'contracts': self.sf.query(contracts_query)['records']
        }
    
    def create_opportunity(self, account_id, name, amount, close_date, stage='Prospecting'):
        """Create new opportunity"""
        opp_data = {
            'Name': name,
            'AccountId': account_id,
            'Amount': amount,
            'CloseDate': close_date,
            'StageName': stage
        }
        return self.sf.Opportunity.create(opp_data)

# Add monitoring and tracking
def create_execution_report(results, action_plan):
    """Generate execution report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'plan_summary': action_plan['steps'][0]['title'] if action_plan['steps'] else 'No plan',
        'total_steps': len(action_plan['steps']),
        'successful_steps': len([r for r in results if r['status'] == 'success']),
        'failed_steps': len([r for r in results if r['status'] == 'error']),
        'pending_steps': len([r for r in results if r['status'] == 'pending']),
        'details': results
    }
    return report

# Add to the main app after execution
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []

# After executing actions
if results:
    report = create_execution_report(results, plan)
    st.session_state.execution_history.append(report)
    
    # Download report
    st.download_button(
        label="Download Execution Report",
        data=json.dumps(report, indent=2),
        file_name=f"nba_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# Add visualization components
import plotly.graph_objects as go
import plotly.express as px

def create_opportunity_pipeline_chart(opportunities):
    """Create pipeline visualization"""
    stages = {}
    for opp in opportunities:
        stage = opp['StageName']
        amount = opp.get('Amount', 0) or 0
        if stage not in stages:
            stages[stage] = 0
        stages[stage] += amount
    
    fig = px.funnel(
        y=list(stages.keys()),
        x=list(stages.values()),
        title="Opportunity Pipeline"
    )
    return fig

# Add to the account display section
if st.session_state.account_data and st.session_state.account_data['opportunities']:
    st.plotly_chart(create_opportunity_pipeline_chart(st.session_state.account_data['opportunities']))

# Add batch processing capability
def process_multiple_accounts(sf_connector, gemini_analyzer, account_ids):
    """Process multiple accounts for NBA"""
    results = []
    progress_bar = st.progress(0)
    
    for i, account_id in enumerate(account_ids):
        try:
            # Fetch account data
            account_data = sf_connector.get_account_data(account_id)
            
            # Generate NBA
            nba = gemini_analyzer.analyze_account_for_nba(account_data)
            
            results.append({
                'account_id': account_id,
                'account_name': account_data['account']['Name'],
                'health_score': nba['health_score'],
                'top_action': nba['next_best_actions'][0]['title'] if nba['next_best_actions'] else 'None'
            })
            
            progress_bar.progress((i + 1) / len(account_ids))
            
        except Exception as e:
            results.append({
                'account_id': account_id,
                'error': str(e)
            })
    
    return pd.DataFrame(results)

# Add configuration file support
def save_configuration(config_name, config_data):
    """Save app configuration"""
    config = {
        'name': config_name,
        'created_at': datetime.now().isoformat(),
        'gemini_model': 'gemini-pro',
        'salesforce_domain': config_data.get('domain', 'login'),
        'action_preferences': config_data.get('preferences', {}),
        'automation_rules': config_data.get('rules', {})
    }
    return config

def load_configuration(config_file):
    """Load saved configuration"""
    return json.load(config_file)

# Add error handling and retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def robust_salesforce_query(sf_connection, query):
    """Execute Salesforce query with retry logic"""
    return sf_connection.query(query)

# Add custom action templates
ACTION_TEMPLATES = {
    'renewal_campaign': {
        'name': 'Contract Renewal Campaign',
        'steps': [
            {'type': 'create_task', 'title': 'Review contract terms', 'days_offset': 0},
            {'type': 'create_task', 'title': 'Prepare renewal proposal', 'days_offset': 7},
            {'type': 'send_email', 'title': 'Send renewal notice', 'days_offset': 14},
            {'type': 'create_opportunity', 'title': 'Create renewal opportunity', 'days_offset': 21}
        ]
    },
    'win_back_campaign': {
        'name': 'Win-Back Campaign',
        'steps': [
            {'type': 'create_case', 'title': 'Investigate churn reasons', 'days_offset': 0},
            {'type': 'create_task', 'title': 'Reach out to key contact', 'days_offset': 3},
            {'type': 'create_opportunity', 'title': 'Win-back opportunity', 'days_offset': 7}
        ]
    }
}