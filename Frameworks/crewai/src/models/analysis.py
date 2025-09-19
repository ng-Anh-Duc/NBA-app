"""Analysis data models."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from ..core.base_classes import BaseEntity

class HealthMetrics(BaseModel):
    """Health metrics for an account."""
    score: int = Field(ge=1, le=10)
    factors: Dict[str, float] = Field(default_factory=dict)
    
class AccountAnalysis(BaseEntity):
    """Account analysis results."""
    account_id: str
    health_metrics: HealthMetrics
    insights: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    sentiment_score: float = Field(ge=0, le=10)
    
    # Agent contributions
    agent_insights: Dict[str, List[str]] = Field(default_factory=dict)