"""Salesforce client implementation."""

from typing import Dict, Any, List, Optional
from simple_salesforce import Salesforce
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from ...config.settings import salesforce_settings
from ...models.account import Account, Contact, Opportunity, Case, Task
from ...core.exceptions import SalesforceConnectionError

class SalesforceClient:
    """Client for Salesforce operations."""
    
    def __init__(self):
        self._connection: Optional[Salesforce] = None
    
    @property
    def connection(self) -> Salesforce:
        """Get or create Salesforce connection."""
        if not self._connection:
            self._connect()
        return self._connection
    
    def _connect(self) -> None:
        """Establish Salesforce connection."""
        try:
            self._connection = Salesforce(
                username=salesforce_settings.username,
                password=salesforce_settings.password,
                security_token=salesforce_settings.security_token,
                domain=salesforce_settings.domain
            )
            logger.info("Successfully connected to Salesforce")
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {e}")
            raise SalesforceConnectionError(f"Connection failed: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_account(self, account_id: str) -> Account:
        """Get account with all related data."""
        logger.info(f"Fetching account {account_id}")
        
        # Fetch account
        account_data = self._fetch_account(account_id)
        
        # Fetch related data
        contacts = self._fetch_contacts(account_id)
        opportunities = self._fetch_opportunities(account_id)
        cases = self._fetch_cases(account_id)
        tasks = self._fetch_tasks(account_id)
        
        # Create Account model
        return Account(
            id=account_data['Id'],
            name=account_data['Name'],
            type=account_data.get('Type'),
            industry=account_data.get('Industry'),
            annual_revenue=account_data.get('AnnualRevenue', 0),
            number_of_employees=account_data.get('NumberOfEmployees', 0),
            rating=account_data.get('Rating'),
            description=account_data.get('Description'),
            contacts=[self._parse_contact(c) for c in contacts],
            opportunities=[self._parse_opportunity(o) for o in opportunities],
            cases=[self._parse_case(c) for c in cases],
            tasks=[self._parse_task(t) for t in tasks]
        )
    
    async def get_account_async(self, account_id: str) -> Account:
        """Async version of get_account."""
        # In practice, use aiohttp or async salesforce client
        return self.get_account(account_id)
    
    def _fetch_account(self, account_id: str) -> Dict[str, Any]:
        """Fetch account record."""
        query = f"""
        SELECT Id, Name, Type, Industry, AnnualRevenue, NumberOfEmployees,
               Rating, AccountSource, Description, LastActivityDate,
               CreatedDate, LastModifiedDate
        FROM Account
        WHERE Id = '{account_id}'
        """
        result = self.connection.query(query)
        if not result['records']:
            raise ValueError(f"Account {account_id} not found")
        return result['records'][0]
    
    def _fetch_contacts(self, account_id: str) -> List[Dict[str, Any]]:
        """Fetch related contacts."""
        query = f"""
        SELECT Id, Name, Title, Email, Phone, LastActivityDate
        FROM Contact
        WHERE AccountId = '{account_id}'
        """
        return self.connection.query(query)['records']
    
    def _fetch_opportunities(self, account_id: str) -> List[Dict[str, Any]]:
        """Fetch opportunities."""
        query = f"""
        SELECT Id, Name, StageName, Amount, CloseDate, Probability,
               Type, LeadSource, IsClosed, IsWon
        FROM Opportunity
        WHERE AccountId = '{account_id}'
        ORDER BY CloseDate DESC
        """
        return self.connection.query(query)['records']
    
    def _fetch_cases(self, account_id: str) -> List[Dict[str, Any]]:
        """Fetch recent cases."""
        query = f"""
        SELECT Id, CaseNumber, Subject, Status, Priority, CreatedDate
        FROM Case
        WHERE AccountId = '{account_id}'
        ORDER BY CreatedDate DESC
        LIMIT 20
        """
        return self.connection.query(query)['records']
    
    def _fetch_tasks(self, account_id: str) -> List[Dict[str, Any]]:
        """Fetch recent tasks."""
        query = f"""
        SELECT Id, Subject, Status, ActivityDate, Description
        FROM Task
        WHERE AccountId = '{account_id}'
        ORDER BY ActivityDate DESC
        LIMIT 20
        """
        return self.connection.query(query)['records']
    
    def _parse_contact(self, data: Dict[str, Any]) -> Contact:
        """Parse contact data."""
        return Contact(
            id=data['Id'],
            name=data['Name'],
            title=data.get('Title'),
            email=data.get('Email'),
            phone=data.get('Phone'),
            last_activity_date=data.get('LastActivityDate')
        )
    
    def _parse_opportunity(self, data: Dict[str, Any]) -> Opportunity:
        """Parse opportunity data."""
        return Opportunity(
            id=data['Id'],
            name=data['Name'],
            stage_name=data['StageName'],
            amount=data.get('Amount', 0),
            close_date=data['CloseDate'],
            probability=data.get('Probability', 0),
            is_closed=data.get('IsClosed', False),
            is_won=data.get('IsWon', False)
        )
    
    def _parse_case(self, data: Dict[str, Any]) -> Case:
        """Parse case data."""
        return Case(
            id=data['Id'],
            case_number=data['CaseNumber'],
            subject=data['Subject'],
            status=data['Status'],
            priority=data['Priority'],
            created_date=data['CreatedDate']
        )
    
    def _parse_task(self, data: Dict[str, Any]) -> Task:
        """Parse task data."""
        return Task(
            id=data['Id'],
            subject=data['Subject'],
            status=data['Status'],
            activity_date=data.get('ActivityDate'),
            description=data.get('Description')
        )