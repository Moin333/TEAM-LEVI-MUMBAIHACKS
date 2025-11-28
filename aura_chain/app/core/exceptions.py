class RateLimitError(Exception):
    """Raised when API rate limit is hit"""
    pass

class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class DataError(Exception):
    """Raised when data processing fails"""
    pass