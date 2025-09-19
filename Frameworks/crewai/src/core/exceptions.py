"""Custom exceptions for the application."""

class SalesforceNBAException(Exception):
    """Base exception for the application."""
    pass

class SalesforceConnectionError(SalesforceNBAException):
    """Raised when Salesforce connection fails."""
    pass

class LLMProviderError(SalesforceNBAException):
    """Raised when LLM provider encounters an error."""
    pass

class AgentExecutionError(SalesforceNBAException):
    """Raised when agent execution fails."""
    pass

class ValidationError(SalesforceNBAException):
    """Raised when validation fails."""
    pass