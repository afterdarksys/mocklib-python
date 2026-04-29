"""
MockLib - Python SDK for MockFactory

Example:
    from mocklib import MockFactory

    mf = MockFactory(api_key="mf_...")
    vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
    print(f"Created VPC: {vpc.id}")
"""

__version__ = "0.2.0"

from .client import MockFactory
from .resources import (
    # AWS core dataclasses
    VPC,
    Lambda,
    DynamoDB,
    SQS,
    Storage,
    EC2Instance,
    STSIdentity,
    STSCredentials,
    HostedZone,
    SNSTopic,
    # OCI dataclasses
    OCIInstance,
    OCIBucket,
    OCIVCN,
    OCIVolume,
    # GCP dataclasses
    GCPInstance,
    GCPNetwork,
    GCPDisk,
    # Azure dataclasses
    AzureResourceGroup,
    AzureVirtualMachine,
    AzureDisk,
    # IAM dataclasses
    IAMUser,
    IAMGroup,
    IAMRole,
    IAMPolicy,
    IAMAccessKey,
    # Org/project dataclasses
    Organization,
    Domain,
    Cloud,
    Project,
    # Resource clients
    VPCResource,
    LambdaResource,
    DynamoDBResource,
    SQSResource,
    StorageResource,
    EC2Resource,
    STSResource,
    Route53Resource,
    SNSResource,
    OCIResource,
    GCPComputeResource,
    AzureResource,
    IAMResource,
    OrganizationResource,
    DomainResource,
    CloudResource,
    ProjectResource,
    GeneratorResource,
    UtilitiesResource,
)
from .exceptions import MockFactoryError, APIError, AuthenticationError

__all__ = [
    # Client
    "MockFactory",
    # AWS core dataclasses
    "VPC",
    "Lambda",
    "DynamoDB",
    "SQS",
    "Storage",
    "EC2Instance",
    "STSIdentity",
    "STSCredentials",
    "HostedZone",
    "SNSTopic",
    # OCI dataclasses
    "OCIInstance",
    "OCIBucket",
    "OCIVCN",
    "OCIVolume",
    # GCP dataclasses
    "GCPInstance",
    "GCPNetwork",
    "GCPDisk",
    # Azure dataclasses
    "AzureResourceGroup",
    "AzureVirtualMachine",
    "AzureDisk",
    # IAM dataclasses
    "IAMUser",
    "IAMGroup",
    "IAMRole",
    "IAMPolicy",
    "IAMAccessKey",
    # Org/project dataclasses
    "Organization",
    "Domain",
    "Cloud",
    "Project",
    # Resource clients
    "VPCResource",
    "LambdaResource",
    "DynamoDBResource",
    "SQSResource",
    "StorageResource",
    "EC2Resource",
    "STSResource",
    "Route53Resource",
    "SNSResource",
    "OCIResource",
    "GCPComputeResource",
    "AzureResource",
    "IAMResource",
    "OrganizationResource",
    "DomainResource",
    "CloudResource",
    "ProjectResource",
    "GeneratorResource",
    "UtilitiesResource",
    # Exceptions
    "MockFactoryError",
    "APIError",
    "AuthenticationError",
]
