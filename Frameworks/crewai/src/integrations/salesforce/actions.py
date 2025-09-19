"""Salesforce action implementations."""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from .client import SalesforceClient
from ...core.exceptions import SalesforceConnectionError

class SalesforceActions:
    """Handle Salesforce actions and updates."""
    
    def __init__(self, client: SalesforceClient):
        self.client = client
    
    def create_task(
        self,
        account_id: str,
        subject: str,
        description: str,
        due_date: str,
        priority: str = "Normal",
        assigned_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a task in Salesforce."""
        logger.info(f"Creating task: {subject}")
        
        task_data = {
            'Subject': subject,
            'Description': description,
            'ActivityDate': due_date,
            'Status': 'Not Started',
            'Priority': priority,
            'WhatId': account_id
        }
        
        if assigned_to:
            task_data['OwnerId'] = assigned_to
        
        try:
            result = self.client.connection.Task.create(task_data)
            logger.info(f"Task created successfully: {result['id']}")
            return {
                'success': True,
                'id': result['id'],
                'message': f'Task "{subject}" created successfully'
            }
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create task: {e}'
            }
    
    def update_opportunity(
        self,
        opportunity_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update opportunity fields."""
        logger.info(f"Updating opportunity {opportunity_id}")
        
        try:
            self.client.connection.Opportunity.update(opportunity_id, updates)
            logger.info("Opportunity updated successfully")
            return {
                'success': True,
                'id': opportunity_id,
                'message': 'Opportunity updated successfully'
            }
        except Exception as e:
            logger.error(f"Failed to update opportunity: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to update opportunity: {e}'
            }
    
    def create_case(
        self,
        account_id: str,
        subject: str,
        description: str,
        priority: str = "Medium",
        case_type: str = "Question"
    ) -> Dict[str, Any]:
        """Create a case in Salesforce."""
        logger.info(f"Creating case: {subject}")
        
        case_data = {
            'Subject': subject,
            'Description': description,
            'AccountId': account_id,
            'Status': 'New',
            'Priority': priority,
            'Type': case_type,
            'Origin': 'Web'
        }
        
        try:
            result = self.client.connection.Case.create(case_data)
            logger.info(f"Case created successfully: {result['id']}")
            return {
                'success': True,
                'id': result['id'],
                'message': f'Case "{subject}" created successfully'
            }
        except Exception as e:
            logger.error(f"Failed to create case: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create case: {e}'
            }
    
    def log_activity(
        self,
        account_id: str,
        activity_type: str,
        description: str,
        outcome: str
    ) -> Dict[str, Any]:
        """Log an activity in Salesforce."""
        logger.info(f"Logging activity: {activity_type}")
        
        # Create a completed task to log the activity
        task_data = {
            'Subject': f'{activity_type} - {datetime.now().strftime("%Y-%m-%d")}',
            'Description': f'{description}\n\nOutcome: {outcome}',
            'ActivityDate': datetime.now().strftime('%Y-%m-%d'),
            'Status': 'Completed',
            'Priority': 'Normal',
            'WhatId': account_id
        }
        
        try:
            result = self.client.connection.Task.create(task_data)
            logger.info(f"Activity logged successfully: {result['id']}")
            return {
                'success': True,
                'id': result['id'],
                'message': 'Activity logged successfully'
            }
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to log activity: {e}'
            }