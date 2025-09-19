"""Analysis tools for agents."""

from typing import Dict, Any, List
from langchain.tools import tool
import pandas as pd
from datetime import datetime, timedelta

@tool
def analyze_customer_sentiment(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze customer sentiment based on cases and interactions.
    
    Args:
        account_data: Account data including cases and activities
        
    Returns:
        Sentiment analysis results
    """
    cases = account_data.get('cases', [])
    
    # Calculate sentiment metrics
    high_priority_cases = [c for c in cases if c.get('priority') == 'High']
    open_cases = [c for c in cases if c.get('status') != 'Closed']
    
    # Simple sentiment scoring
    sentiment_score = 10
    if len(high_priority_cases) > 2:
        sentiment_score -= 3
    if len(open_cases) > 5:
        sentiment_score -= 2
    
    # Recent case trend
    recent_cases = [
        c for c in cases 
        if datetime.fromisoformat(c.get('created_date', '')) > datetime.now() - timedelta(days=30)
    ]
    
    return {
        "sentiment_score": max(0, sentiment_score),
        "high_priority_issues": len(high_priority_cases),
        "open_cases": len(open_cases),
        "recent_case_trend": len(recent_cases),
        "recommendation": "Address high-priority cases immediately" if sentiment_score < 7 else "Maintain current service level"
    }

@tool
def calculate_account_metrics(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate key account metrics.
    
    Args:
        account_data: Account data
        
    Returns:
        Dictionary of calculated metrics
    """
    opportunities = account_data.get('opportunities', [])
    
    # Calculate metrics
    total_pipeline = sum(opp.get('amount', 0) for opp in opportunities if not opp.get('is_closed'))
    won_revenue = sum(opp.get('amount', 0) for opp in opportunities if opp.get('is_won'))
    win_rate = len([o for o in opportunities if o.get('is_won')]) / len(opportunities) if opportunities else 0
    
    # Average deal size
    closed_deals = [o for o in opportunities if o.get('is_closed')]
    avg_deal_size = sum(o.get('amount', 0) for o in closed_deals) / len(closed_deals) if closed_deals else 0
    
    return {
        "total_pipeline_value": total_pipeline,
        "won_revenue": won_revenue,
        "win_rate": win_rate,
        "average_deal_size": avg_deal_size,
        "open_opportunities": len([o for o in opportunities if not o.get('is_closed')]),
        "growth_potential": "High" if total_pipeline > account_data.get('annual_revenue', 0) * 0.2 else "Medium"
    }

@tool
def identify_trends(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify trends in account data.
    
    Args:
        account_data: Historical account data
        
    Returns:
        Identified trends and patterns
    """
    opportunities = account_data.get('opportunities', [])
    
    # Convert to DataFrame for analysis
    if opportunities:
        df = pd.DataFrame(opportunities)
        df['close_date'] = pd.to_datetime(df['close_date'])
        
        # Monthly opportunity trend
        monthly_opps = df.groupby(df['close_date'].dt.to_period('M')).size()
        trend = "increasing" if monthly_opps.is_monotonic_increasing else "stable"
        
        # Stage progression
        stage_distribution = df['stage_name'].value_counts().to_dict()
        
        return {
            "opportunity_trend": trend,
            "stage_distribution": stage_distribution,
            "insights": [
                f"Opportunity creation trend is {trend}",
                f"Most opportunities are in {max(stage_distribution, key=stage_distribution.get)} stage"
            ]
        }
    
    return {
        "opportunity_trend": "no_data",
        "insights": ["Insufficient data for trend analysis"]
    }