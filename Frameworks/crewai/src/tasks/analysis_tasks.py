"""Analysis task definitions."""

from crewai import Task
from crewai.agent import Agent
from typing import Dict, Any

class AnalysisTasks:
    """Factory for analysis tasks."""
    
    def create_data_analysis_task(self, agent: Agent) -> Task:
        """Create data analysis task."""
        return Task(
            description="""
            Analyze the provided Salesforce account data and deliver comprehensive insights:
            
            1. Calculate key account metrics:
               - Health score (1-10)
               - Revenue metrics and trends
               - Activity levels and engagement
               - Support ticket patterns
            
            2. Identify patterns and anomalies:
               - Unusual activity spikes or drops
               - Changes in buying behavior
               - Support issue trends
            
            3. Assess data quality:
               - Missing critical information
               - Data inconsistencies
               - Areas needing attention
            
            Provide specific, quantified insights with supporting data.
            Format your analysis in a structured way with clear sections.
            """,
            agent=agent,
            expected_output="Comprehensive data analysis with metrics, patterns, and insights"
        )
    
    def create_risk_assessment_task(self, agent: Agent) -> Task:
        """Create risk assessment task."""
        return Task(
            description="""
            Perform a thorough risk assessment of the account:
            
            1. Churn risk indicators:
               - Declining engagement metrics
               - Unresolved issues
               - Contract renewal timeline
               - Competitive threats
            
            2. Financial risks:
               - Payment history
               - Budget constraints
               - Economic factors
            
            3. Relationship risks:
               - Key contact changes
               - Stakeholder satisfaction
               - Executive engagement level
            
            4. Operational risks:
               - Product adoption issues
               - Integration challenges
               - Support ticket escalations
            
            Provide risk scores and specific mitigation recommendations.
            """,
            agent=agent,
            expected_output="Detailed risk assessment with scores and mitigation strategies"
        )