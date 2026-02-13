"""
MockLib - Python SDK for MockFactory

Example:
    from mocklib import MockFactory

    mf = MockFactory(api_key="mf_...")
    vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
    print(f"Created VPC: {vpc.id}")
"""

__version__ = "0.1.0"

from .client import MockFactory
from .resources import VPC, Lambda, DynamoDB, SQS, Storage
from .exceptions import MockFactoryError, APIError, AuthenticationError

__all__ = [
    "MockFactory",
    "VPC",
    "Lambda",
    "DynamoDB",
    "SQS",
    "Storage",
    "MockFactoryError",
    "APIError",
    "AuthenticationError",
]
