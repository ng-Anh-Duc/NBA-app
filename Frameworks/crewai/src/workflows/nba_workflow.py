"""Main NBA workflow orchestration."""

from typing import Dict, Any, List, Optional
from ..models.account import Account
from ..models.analysis import AccountAnalysis
from ..models.recommendations import NextBestAction
from ..models.action_plan import ActionPlan
from ..crews.analysis_crew import AnalysisCrew
from ..crews.strategy_crew import StrategyCrew
from ..crews.execution_crew import ExecutionCrew
from ..integrations.salesforce.client import SalesforceClient
from loguru import logger

class NBAWorkflow:
    """Orchestrates the complete NBA workflow."""
    
    def __init__(
        self,
        salesforce_client: SalesforceClient,
        analysis_crew: AnalysisCrew,
        strategy_crew: StrategyCrew,
        execution_crew: ExecutionCrew
    ):
        self.sf_client = salesforce_client
        self.analysis_crew = analysis_crew
        self.strategy_crew = strategy_crew
        self.execution_crew = execution_crew
    
    async def run_analysis(self, account_id: str) -> AccountAnalysis:
        """Run account analysis."""
        logger.info(f"Starting analysis for account {account_id}")
        
        # Fetch account data
        account = await self.sf_client.get_account_async(account_id)
        
        # Run analysis crew
        analysis_result = self.analysis_crew.execute({
            "account_data": account.dict()
        })
        
        # Parse and structure results
        analysis = AccountAnalysis(
            account_id=account_id,
            **self._parse_analysis_results(analysis_result)
        )
        
        logger.info(f"Analysis completed. Health score: {analysis.health_metrics.score}")
        return analysis
    
    async def generate_recommendations(
        self,
        analysis: AccountAnalysis
    ) -> List[NextBestAction]:
        """Generate NBA recommendations."""
        logger.info("Generating recommendations")
        
        # Run strategy crew
        strategy_result = self.strategy_crew.execute({
            "analysis": analysis.dict()
        })
        
        # Parse recommendations
        recommendations = self._parse_recommendations(strategy_result)
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    async def create_action_plan(
        self,
        account_id: str,
        selected_action: NextBestAction
    ) -> ActionPlan:
        """Create detailed action plan."""
        logger.info(f"Creating action plan for: {selected_action.title}")
        
        # Run execution crew
        plan_result = self.execution_crew.execute({
            "account_id": account_id,
            "selected_action": selected_action.dict()
        })
        
        # Parse action plan
        action_plan = self._parse_action_plan(plan_result)
        
        logger.info(f"Action plan created with {len(action_plan.steps)} steps")
        return action_plan
    
    def _parse_analysis_results(self, raw_result: Any) -> Dict[str, Any]:
        """Parse raw analysis results."""
        # Implementation depends on crew output format
        return {
            "health_metrics": {
                "score": 8,
                "factors": {"engagement": 0.8, "revenue": 0.9}
            },
            "insights": ["Insight 1", "Insight 2"],
            "risks": ["Risk 1"],
            "opportunities": ["Opportunity 1"]
        }
    
    def _parse_recommendations(self, raw_result: Any) -> List[NextBestAction]:
        """Parse raw recommendations."""
        # Implementation depends on crew output format
        return [
            NextBestAction(
                title="Renewal Campaign",
                                description="Launch targeted renewal campaign",
                priority="High",
                rationale="Contract expires in 60 days",
                expected_impact="Secure $100k renewal",
                confidence_score=0.85
            )
        ]
    
    def _parse_action_plan(self, raw_result: Any) -> ActionPlan:
        """Parse raw action plan."""
        # Implementation depends on crew output format
        return ActionPlan(
            title="Renewal Campaign Execution",
            steps=[
                {
                    "type": "create_task",
                    "title": "Review contract terms",
                    "description": "Analyze current contract and usage",
                    "due_date": "2024-01-15",
                    "owner": "Account Manager"
                }
            ],
            timeline_days=30,
            success_metrics=["Contract renewed", "Revenue retained"],
            resources_required=["Account Manager", "Customer Success Manager"]
        )