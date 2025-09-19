"""Base agent class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from crewai import Agent
from langchain_core.language_models import BaseLanguageModel

class BaseNBAAgent(ABC):
    """Base class for NBA agents."""
    
    def __init__(self, llm: BaseLanguageModel, verbose: bool = True):
        self.llm = llm
        self.verbose = verbose
        self._agent: Optional[Agent] = None
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Agent role."""
        pass
    
    @property
    @abstractmethod
    def goal(self) -> str:
        """Agent goal."""
        pass
    
    @property
    @abstractmethod
    def backstory(self) -> str:
        """Agent backstory."""
        pass
    
    @property
    def tools(self) -> List[Any]:
        """Agent tools."""
        return []
    
    @property
    def agent(self) -> Agent:
        """Get or create the CrewAI agent."""
        if not self._agent:
            self._agent = Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                verbose=self.verbose,
                allow_delegation=self.allow_delegation,
                llm=self.llm,
                tools=self.tools
            )
        return self._agent
    
    @property
    def allow_delegation(self) -> bool:
        """Whether agent can delegate tasks."""
        return False