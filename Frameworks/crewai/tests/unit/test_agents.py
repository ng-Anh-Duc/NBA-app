"""Unit tests for agents."""

import pytest
from src.agents.data_analyst import DataAnalystAgent
from src.agents.strategist import StrategistAgent

class TestDataAnalystAgent:
    """Test data analyst agent."""
    
    def test_agent_initialization(self, mock_llm):
        """Test agent initialization."""
        agent = DataAnalystAgent(mock_llm)
        
        assert agent.role == "Senior Data Analyst"
        assert agent.llm == mock_llm
        assert len(agent.tools) > 0
    
    def test_agent_creation(self, mock_llm):
        """Test CrewAI agent creation."""
        agent = DataAnalystAgent(mock_llm)
        crew_agent = agent.agent
        
        assert crew_agent.role == agent.role
        assert crew_agent.goal == agent.goal
        assert crew_agent.backstory == agent.backstory

class TestStrategistAgent:
    """Test strategist agent."""
    
    def test_delegation_enabled(self, mock_llm):
        """Test that strategist can delegate."""
        agent = StrategistAgent(mock_llm)
        
        assert agent.allow_delegation is True
    
    def test_tools_available(self, mock_llm):
        """Test strategist has required tools."""
        agent = StrategistAgent(mock_llm)
        tool_names = [tool.name for tool in agent.tools]
        
        assert "identify_upsell_opportunities" in tool_names
        assert "assess_renewal_probability" in tool_names