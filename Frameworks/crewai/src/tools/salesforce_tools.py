"""Salesforce-specific tools for agents."""

from typing import Dict, Any, List
from langchain.tools import tool
from ..integrations.salesforce.client import SalesforceClient
from ..models.account import Account

@tool
def fetch_account_data(account_id: str) -> Dict[str, Any]:
    """
    Fetch comprehensive account data from Salesforce.
    
    Args:
        account_id: Salesforce account ID
        
    Returns:
        Dictionary containing account data and related records
    """
    client = SalesforceClient()
    account = client.get_account(account_id)
    return account.dict()

@tool
def get_account_activity_summary(account_id: str) -> Dict[str, Any]:
    """
    Get summary of recent account activities.
    
    Args:
        account_id: Salesforce account ID
        
    Returns:
        Dictionary with activity summary
    """
    client = SalesforceClient()
    return client.get_activity_summary(account_id)

@tool
def search_similar_accounts(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search for similar accounts based on criteria.
    
    Args:
        criteria: Search criteria (industry, size, etc.)
        
    Returns:
        List of similar accounts
    """
    client = SalesforceClient()
    return client.search_accounts(criteria)