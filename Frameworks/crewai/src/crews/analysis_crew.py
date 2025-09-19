"""Analysis crew implementation."""

from typing import List, Dict, Any
from crewai import Task
from .base_crew import BaseNBACrew
from ..agents.data_analyst import DataAnalystAgent
from ..agents.risk_analyst import RiskAnalystAgent
from ..tasks.analysis_tasks import AnalysisTasks

class AnalysisCrew(BaseNBACrew):
    """Crew for account analysis."""
    
    def __init__(self, data_analyst: DataAnalystAgent, risk_analyst: RiskAnalystAgent):
        self.data_analyst = data_analyst
        self.risk_analyst = risk_analyst
        super().__init__(
            agents=[data_analyst.agent, risk_analyst.agent]
        )
        self.task_factory = AnalysisTasks()
    
    @property
    def tasks(self) -> List[Task]:
        return [
            self.task_factory.create_data_analysis_task(self.data_analyst.agent),
            self.task_factory.create_risk_assessment_task(self.risk_analyst.agent)
        ]