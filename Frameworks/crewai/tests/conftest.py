"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from src.models.account import Account, Contact, Opportunity
from src.models.analysis import AccountAnalysis, HealthMetrics
from src.integrations.salesforce.client import SalesforceClient

@pytest.fixture
def mock_salesforce_client():
    """Mock Salesforce client."""
    client = Mock(spec=SalesforceClient)
    
    # Mock account data
    client.get_account.return_value = Account(
        id="001XX000003DHPh",
        name="Test Account",
        industry="Technology",
        annual_revenue=1000000,
        contacts=[
            Contact(
                id="003XX000004TMM2",
                name="John Doe",
                title="CEO",
                email="john@test.com"
            )
        ],
        opportunities=[
            Opportunity(
                id="006XX000002QJQO",
                name="Test Opportunity",
                stage_name="Negotiation",
                amount=50000,
                close_date="2024-03-01",
                is_closed=False,
                is_won=False
            )
        ]
    )
    
    return client

@pytest.fixture
def mock_llm():
    """Mock LLM provider."""
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content="Test response")
    return llm

@pytest.fixture
def sample_analysis():
    """Sample analysis result."""
    return AccountAnalysis(
        account_id="001XX000003DHPh",
        health_metrics=HealthMetrics(score=8, factors={"engagement": 0.8}),
        insights=["Strong engagement", "Growth potential"],
        risks=["Contract renewal approaching"],
        opportunities=["Upsell opportunity identified"]
    )