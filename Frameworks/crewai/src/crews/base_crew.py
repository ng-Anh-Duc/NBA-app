"""Base crew class."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from crewai import Crew, Process
from crewai.agent import Agent
from crewai.task import Task

class BaseNBACrew(ABC):
    """Base class for NBA crews."""
    
    def __init__(self, agents: List[Agent], verbose: bool = True):
        self.agents = agents
        self.verbose = verbose
        self._crew: Optional[Crew] = None
    
    @property
    @abstractmethod
    def tasks(self) -> List[Task]:
        """Get crew tasks."""
        pass
    
    @property
    def process(self) -> Process:
        """Crew process type."""
        return Process.sequential
    
    @property
    def crew(self) -> Crew:
        """Get or create the crew."""
        if not self._crew:
            self._crew = Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=self.process,
                verbose=self.verbose
            )
        return self._crew
    
    def execute(self, inputs: Dict[str, Any]) -> Any:
        """Execute the crew."""
        return self.crew.kickoff(inputs=inputs)