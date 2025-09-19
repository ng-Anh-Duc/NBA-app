"""Base classes for the application."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class BaseEntity(BaseModel):
    """Base entity class with common fields."""
    id: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True

class BaseService(ABC):
    """Base service class."""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the service logic."""
        pass

class BaseRepository(ABC):
    """Base repository class."""
    
    @abstractmethod
    def get(self, id: str) -> Optional[BaseEntity]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def create(self, entity: BaseEntity) -> BaseEntity:
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, id: str, entity: BaseEntity) -> BaseEntity:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete entity."""
        pass