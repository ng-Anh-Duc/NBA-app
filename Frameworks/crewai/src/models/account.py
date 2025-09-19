"""Account data models."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from ..core.base_classes import BaseEntity

class Contact(BaseModel):
    """Contact model."""
    id: str
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    last_activity_date: Optional[datetime] = None

class Opportunity(BaseModel):
    """Opportunity model."""
    id: str
    name: str
    stage_name: str
    amount: Optional[float] = 0
    close_date: datetime
    probability: Optional[float] = 0
    is_closed: bool = False
    is_won: bool = False

class Case(BaseModel):
    """Case model."""
    id: str
    case_number: str
    subject: str
    status: str
    priority: str
    created_date: datetime

class Task(BaseModel):
    """Task model."""
    id: str
    subject: str
    status: str
    activity_date: Optional[datetime] = None
    description: Optional[str] = None

class Account(BaseEntity):
    """Account model with all related data."""
    name: str
    type: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = 0
    number_of_employees: Optional[int] = 0
    rating: Optional[str] = None
    description: Optional[str] = None
    
    # Related entities
    contacts: List[Contact] = Field(default_factory=list)
    opportunities: List[Opportunity] = Field(default_factory=list)
    cases: List[Case] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    
    # Computed properties
    @property
    def open_opportunities_count(self) -> int:
        return len([o for o in self.opportunities if not o.is_closed])
    
    @property
    def total_pipeline_value(self) -> float:
        return sum(o.amount for o in self.opportunities if not o.is_closed)
    
    @property
    def open_cases_count(self) -> int:
        return len([c for c in self.cases if c.status != 'Closed'])