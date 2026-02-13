"""MockLib Exceptions"""


class MockFactoryError(Exception):
    """Base exception for MockFactory SDK"""
    pass


class APIError(MockFactoryError):
    """API request failed"""
    pass


class AuthenticationError(MockFactoryError):
    """Authentication failed (invalid API key)"""
    pass


class ResourceNotFoundError(MockFactoryError):
    """Resource not found"""
    pass


class ValidationError(MockFactoryError):
    """Invalid parameters"""
    pass
