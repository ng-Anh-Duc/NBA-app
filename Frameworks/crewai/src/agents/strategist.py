"""Customer success strategist agent."""

from typing import List, Any
from .base_agent import BaseNBAAgent
from ..tools.analysis_tools import (
    identify_upsell_opportunities,
    assess_renewal_probability,
    create_growth_strategy
)

class StrategistAgent(BaseNBAAgent):
    """Strategic planning agent."""
    
    @property
    def role(self) -> str:
        return "Customer Success Strategist"
    
    @property
    def goal(self) -> str:
        return "Develop strategic Next Best Actions based on account analysis"
    
    @property
    def backstory(self) -> str:
        return """You are a seasoned customer success strategist who has helped hundreds of companies
        grow their accounts. You think strategically about customer relationships and always consider
        both short-term wins and long-term value creation. Your expertise includes:
        - Account growth strategies
        - Customer retention and expansion
        - Value realization planning
        - Executive relationship building
        You always prioritize actions that drive mutual value for both the customer and the company.
        """
    
    @property
    def tools(self) -> List[Any]:
        return [
            identify_upsell_opportunities,
            assess_renewal_probability,
            create_growth_strategy
        ]
    
    @property
    def allow_delegation(self) -> bool:
        return True