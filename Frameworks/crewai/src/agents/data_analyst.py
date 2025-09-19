"""Data analyst agent implementation."""

from typing import List, Any
from .base_agent import BaseNBAAgent
from ..tools.analysis_tools import (
    analyze_customer_sentiment,
    calculate_account_metrics,
    identify_trends
)

class DataAnalystAgent(BaseNBAAgent):
    """Data analyst agent for account analysis."""
    
    @property
    def role(self) -> str:
        return "Senior Data Analyst"
    
    @property
    def goal(self) -> str:
        return "Analyze Salesforce account data to identify patterns, risks, and opportunities"
    
    @property
    def backstory(self) -> str:
        return """You are an expert data analyst with 10+ years of experience in CRM analytics.
                You excel at finding hidden patterns in customer data and identifying both risks and opportunities.
        Your analysis is always data-driven, thorough, and actionable. You have a keen eye for detail
        and can spot trends that others might miss. You're particularly skilled at:
        - Statistical analysis and trend identification
        - Customer behavior pattern recognition
        - Risk scoring and predictive analytics
        - Data quality assessment
        """
    
    @property
    def tools(self) -> List[Any]:
        return [
            analyze_customer_sentiment,
            calculate_account_metrics,
            identify_trends
        ]
    
    @property
    def allow_delegation(self) -> bool:
        return False