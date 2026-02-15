"""MockFactory Resource Clients"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class VPC:
    """VPC resource"""
    id: str
    cidr_block: str
    state: str
    oci_vcn_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class Lambda:
    """Lambda function resource"""
    id: str
    function_name: str
    runtime: str
    memory_mb: int
    timeout: int
    state: str
    arn: Optional[str] = None


@dataclass
class DynamoDB:
    """DynamoDB table resource"""
    id: str
    table_name: str
    partition_key: str
    partition_key_type: str
    item_count: int
    state: str


@dataclass
class SQS:
    """SQS queue resource"""
    id: str
    queue_name: str
    queue_url: str
    visibility_timeout: int
    message_count: int


@dataclass
class Storage:
    """Storage bucket resource"""
    id: str
    bucket_name: str
    region: str
    size_bytes: int


class VPCResource:
    """VPC resource client"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        cidr_block: str,
        enable_dns_hostnames: bool = True,
        enable_dns_support: bool = True,
        tags: Optional[Dict[str, str]] = None,
    ) -> VPC:
        """
        Create a VPC

        Args:
            cidr_block: CIDR block (e.g., "10.0.0.0/16")
            enable_dns_hostnames: Enable DNS hostnames
            enable_dns_support: Enable DNS support
            tags: Optional tags

        Returns:
            VPC object

        Example:
            >>> vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
            >>> print(vpc.id)
            vpc-abc123
        """
        response = self.client.post("/aws/vpc", json={
            "Action": "CreateVpc",
            "CidrBlock": cidr_block,
            "EnableDnsHostnames": enable_dns_hostnames,
            "EnableDnsSupport": enable_dns_support,
            "Tags": tags or {},
        })

        return VPC(
            id=response["VpcId"],
            cidr_block=response["CidrBlock"],
            state=response["State"],
            oci_vcn_id=response.get("OciVcnId"),
            tags=response.get("Tags"),
        )

    def delete(self, vpc_id: str) -> bool:
        """Delete a VPC"""
        self.client.post("/aws/vpc", json={
            "Action": "DeleteVpc",
            "VpcId": vpc_id,
        })
        return True

    def list(self) -> List[VPC]:
        """List all VPCs"""
        response = self.client.post("/aws/vpc", json={
            "Action": "DescribeVpcs",
        })

        return [
            VPC(
                id=vpc["VpcId"],
                cidr_block=vpc["CidrBlock"],
                state=vpc["State"],
                oci_vcn_id=vpc.get("OciVcnId"),
                tags=vpc.get("Tags"),
            )
            for vpc in response.get("Vpcs", [])
        ]


class LambdaResource:
    """Lambda resource client"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        function_name: str,
        runtime: str,
        handler: str = "index.handler",
        memory_mb: int = 128,
        timeout: int = 30,
        code_zip: Optional[bytes] = None,
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> Lambda:
        """
        Create a Lambda function

        Args:
            function_name: Function name
            runtime: Runtime (python3.9, nodejs18.x, etc.)
            handler: Handler function
            memory_mb: Memory in MB
            timeout: Timeout in seconds
            code_zip: Function code as ZIP bytes
            environment_variables: Environment variables

        Returns:
            Lambda object

        Example:
            >>> fn = mf.lambda_function.create(
            ...     function_name="my-api",
            ...     runtime="python3.9",
            ...     memory_mb=256
            ... )
            >>> print(fn.id)
            lambda-xyz789
        """
        import base64

        response = self.client.post("/aws/lambda", json={
            "Action": "CreateFunction",
            "FunctionName": function_name,
            "Runtime": runtime,
            "Handler": handler,
            "MemorySize": memory_mb,
            "Timeout": timeout,
            "Code": {
                "ZipFile": base64.b64encode(code_zip).decode() if code_zip else None
            },
            "Environment": {
                "Variables": environment_variables or {}
            }
        })

        return Lambda(
            id=response["FunctionId"],
            function_name=response["FunctionName"],
            runtime=response["Runtime"],
            memory_mb=response["MemorySize"],
            timeout=response["Timeout"],
            state=response["State"],
            arn=response.get("FunctionArn"),
        )

    def invoke(
        self,
        function_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a Lambda function

        Args:
            function_name: Function name
            payload: Input payload (JSON)

        Returns:
            Function response
        """
        response = self.client.post("/aws/lambda", json={
            "Action": "Invoke",
            "FunctionName": function_name,
            "Payload": payload or {},
        })

        return response.get("Payload", {})

    def delete(self, function_name: str) -> bool:
        """Delete a Lambda function"""
        self.client.post("/aws/lambda", json={
            "Action": "DeleteFunction",
            "FunctionName": function_name,
        })
        return True


class DynamoDBResource:
    """DynamoDB resource client"""

    def __init__(self, client):
        self.client = client

    def create_table(
        self,
        table_name: str,
        partition_key: str,
        partition_key_type: str = "S",
        sort_key: Optional[str] = None,
        sort_key_type: str = "S",
    ) -> DynamoDB:
        """
        Create a DynamoDB table

        Args:
            table_name: Table name
            partition_key: Partition key attribute name
            partition_key_type: Type (S=string, N=number, B=binary)
            sort_key: Optional sort key
            sort_key_type: Sort key type

        Returns:
            DynamoDB object
        """
        response = self.client.post("/aws/dynamodb", json={
            "Action": "CreateTable",
            "TableName": table_name,
            "PartitionKey": partition_key,
            "PartitionKeyType": partition_key_type,
            "SortKey": sort_key,
            "SortKeyType": sort_key_type,
        })

        return DynamoDB(
            id=response["TableId"],
            table_name=response["TableName"],
            partition_key=response["PartitionKey"],
            partition_key_type=response["PartitionKeyType"],
            item_count=0,
            state=response["State"],
        )

    def put_item(
        self,
        table_name: str,
        item: Dict[str, Any],
    ) -> bool:
        """Put an item into DynamoDB table"""
        self.client.post("/aws/dynamodb", json={
            "Action": "PutItem",
            "TableName": table_name,
            "Item": item,
        })
        return True

    def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Get an item from DynamoDB table"""
        response = self.client.post("/aws/dynamodb", json={
            "Action": "GetItem",
            "TableName": table_name,
            "Key": key,
        })
        return response.get("Item")


class SQSResource:
    """SQS resource client"""

    def __init__(self, client):
        self.client = client

    def create_queue(
        self,
        queue_name: str,
        visibility_timeout: int = 30,
        message_retention: int = 345600,
    ) -> SQS:
        """
        Create an SQS queue

        Args:
            queue_name: Queue name
            visibility_timeout: Visibility timeout in seconds
            message_retention: Message retention in seconds

        Returns:
            SQS object
        """
        response = self.client.post("/aws/sqs", json={
            "Action": "CreateQueue",
            "QueueName": queue_name,
            "VisibilityTimeout": visibility_timeout,
            "MessageRetentionPeriod": message_retention,
        })

        return SQS(
            id=response["QueueId"],
            queue_name=response["QueueName"],
            queue_url=response["QueueUrl"],
            visibility_timeout=visibility_timeout,
            message_count=0,
        )

    def send_message(
        self,
        queue_url: str,
        message_body: str,
    ) -> str:
        """Send a message to SQS queue"""
        response = self.client.post("/aws/sqs", json={
            "Action": "SendMessage",
            "QueueUrl": queue_url,
            "MessageBody": message_body,
        })
        return response["MessageId"]

    def receive_messages(
        self,
        queue_url: str,
        max_messages: int = 1,
    ) -> List[Dict[str, Any]]:
        """Receive messages from SQS queue"""
        response = self.client.post("/aws/sqs", json={
            "Action": "ReceiveMessage",
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": max_messages,
        })
        return response.get("Messages", [])


class StorageResource:
    """Storage (S3/GCS/Azure) resource client"""

    def __init__(self, client):
        self.client = client

    def create_bucket(
        self,
        bucket_name: str,
        provider: str = "s3",
        region: str = "us-east-1",
    ) -> Storage:
        """
        Create a storage bucket

        Args:
            bucket_name: Bucket name
            provider: s3, gcs, or azure
            region: Region

        Returns:
            Storage object
        """
        response = self.client.post("/storage/bucket", json={
            "Action": "CreateBucket",
            "BucketName": bucket_name,
            "Provider": provider,
            "Region": region,
        })

        return Storage(
            id=response["BucketId"],
            bucket_name=response["BucketName"],
            region=response["Region"],
            size_bytes=0,
        )

    def upload_file(
        self,
        bucket_name: str,
        key: str,
        data: bytes,
    ) -> bool:
        """Upload file to storage bucket"""
        import base64

        self.client.post("/storage/object", json={
            "Action": "PutObject",
            "BucketName": bucket_name,
            "Key": key,
            "Data": base64.b64encode(data).decode(),
        })
        return True


@dataclass
class Organization:
    """Organization resource"""
    id: str
    org_id: str
    name: str
    plan: str
    owner: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Domain:
    """Domain resource"""
    id: str
    domain_id: str
    domain: str
    verified: bool
    organization: Optional[str] = None
    dns_records: Optional[List[str]] = None


@dataclass
class Cloud:
    """Cloud environment resource"""
    id: str
    cloud_id: str
    name: str
    provider: str
    region: str
    organization: Optional[str] = None


@dataclass
class Project:
    """Project resource"""
    id: str
    project_id: str
    name: str
    environment: str
    organization: Optional[str] = None
    description: Optional[str] = None


class OrganizationResource:
    """Organization resource client"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        name: str,
        plan: str = "free",
        description: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> Organization:
        """
        Create an organization

        Args:
            name: Organization name
            plan: Plan type (free, pro, enterprise)
            description: Organization description
            owner: Owner user ID

        Returns:
            Organization object

        Example:
            >>> org = mf.organization.create(
            ...     name="acme-corp",
            ...     plan="pro",
            ...     description="Acme Corporation"
            ... )
            >>> print(org.org_id)
            550e8400-e29b-41d4-a716-446655440000
        """
        response = self.client.post("/mock/organization", json={
            "name": name,
            "plan": plan,
            "description": description,
            "owner": owner,
        })

        return Organization(
            id=response["id"],
            org_id=response["org_id"],
            name=response["name"],
            plan=response["plan"],
            owner=response.get("owner"),
            description=response.get("description"),
        )

    def list(self, plan: Optional[str] = None) -> List[Organization]:
        """List all organizations"""
        response = self.client.get("/mock/organization", params={"plan": plan} if plan else {})

        return [
            Organization(
                id=org["id"],
                org_id=org["org_id"],
                name=org["name"],
                plan=org["plan"],
                owner=org.get("owner"),
                description=org.get("description"),
            )
            for org in response.get("organizations", [])
        ]

    def get(self, name: str) -> Organization:
        """Get organization by name"""
        response = self.client.get(f"/mock/organization/{name}")

        return Organization(
            id=response["id"],
            org_id=response["org_id"],
            name=response["name"],
            plan=response["plan"],
            owner=response.get("owner"),
            description=response.get("description"),
        )

    def delete(self, name: str) -> bool:
        """Delete an organization"""
        self.client.delete(f"/mock/organization/{name}")
        return True

    def add_user(self, org_name: str, username: str, role: str = "member") -> bool:
        """Add a user to an organization"""
        self.client.post(f"/mock/organization/{org_name}/users", json={
            "username": username,
            "role": role,
        })
        return True

    def remove_user(self, org_name: str, username: str) -> bool:
        """Remove a user from an organization"""
        self.client.delete(f"/mock/organization/{org_name}/users/{username}")
        return True


class DomainResource:
    """Domain resource client"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        domain: str,
        organization: Optional[str] = None,
        verified: bool = False,
        dns_records: Optional[List[str]] = None,
    ) -> Domain:
        """
        Create a domain

        Args:
            domain: Domain name
            organization: Organization to bind to
            verified: Whether domain is verified
            dns_records: DNS records to create

        Returns:
            Domain object

        Example:
            >>> domain = mf.domain.create(
            ...     domain="example.com",
            ...     organization="acme-corp",
            ...     verified=True
            ... )
            >>> print(domain.domain_id)
            550e8400-e29b-41d4-a716-446655440001
        """
        response = self.client.post("/mock/domain", json={
            "domain": domain,
            "organization": organization,
            "verified": verified,
            "dns_records": dns_records or [],
        })

        return Domain(
            id=response["id"],
            domain_id=response["domain_id"],
            domain=response["domain"],
            verified=response["verified"],
            organization=response.get("organization"),
            dns_records=response.get("dns_records"),
        )

    def list(
        self,
        organization: Optional[str] = None,
        verified: Optional[bool] = None,
    ) -> List[Domain]:
        """List all domains"""
        params = {}
        if organization:
            params["organization"] = organization
        if verified is not None:
            params["verified"] = verified

        response = self.client.get("/mock/domain", params=params)

        return [
            Domain(
                id=dom["id"],
                domain_id=dom["domain_id"],
                domain=dom["domain"],
                verified=dom["verified"],
                organization=dom.get("organization"),
                dns_records=dom.get("dns_records"),
            )
            for dom in response.get("domains", [])
        ]

    def get(self, domain: str) -> Domain:
        """Get domain by name"""
        response = self.client.get(f"/mock/domain/{domain}")

        return Domain(
            id=response["id"],
            domain_id=response["domain_id"],
            domain=response["domain"],
            verified=response["verified"],
            organization=response.get("organization"),
            dns_records=response.get("dns_records"),
        )

    def verify(self, domain: str) -> bool:
        """Verify a domain"""
        self.client.post(f"/mock/domain/{domain}/verify")
        return True

    def delete(self, domain: str) -> bool:
        """Delete a domain"""
        self.client.delete(f"/mock/domain/{domain}")
        return True


class CloudResource:
    """Cloud environment resource client"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        name: str,
        provider: str = "aws",
        region: str = "us-east-1",
        organization: Optional[str] = None,
    ) -> Cloud:
        """
        Create a cloud environment

        Args:
            name: Cloud environment name
            provider: Provider (aws, gcp, azure, custom)
            region: Region
            organization: Organization to bind to

        Returns:
            Cloud object

        Example:
            >>> cloud = mf.cloud.create(
            ...     name="dev-cloud",
            ...     provider="aws",
            ...     region="us-east-1",
            ...     organization="acme-corp"
            ... )
            >>> print(cloud.cloud_id)
            550e8400-e29b-41d4-a716-446655440002
        """
        response = self.client.post("/mock/cloud", json={
            "name": name,
            "provider": provider,
            "region": region,
            "organization": organization,
        })

        return Cloud(
            id=response["id"],
            cloud_id=response["cloud_id"],
            name=response["name"],
            provider=response["provider"],
            region=response["region"],
            organization=response.get("organization"),
        )

    def list(
        self,
        provider: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> List[Cloud]:
        """List all cloud environments"""
        params = {}
        if provider:
            params["provider"] = provider
        if organization:
            params["organization"] = organization

        response = self.client.get("/mock/cloud", params=params)

        return [
            Cloud(
                id=cld["id"],
                cloud_id=cld["cloud_id"],
                name=cld["name"],
                provider=cld["provider"],
                region=cld["region"],
                organization=cld.get("organization"),
            )
            for cld in response.get("clouds", [])
        ]

    def get(self, name: str) -> Cloud:
        """Get cloud environment by name"""
        response = self.client.get(f"/mock/cloud/{name}")

        return Cloud(
            id=response["id"],
            cloud_id=response["cloud_id"],
            name=response["name"],
            provider=response["provider"],
            region=response["region"],
            organization=response.get("organization"),
        )

    def delete(self, name: str) -> bool:
        """Delete a cloud environment"""
        self.client.delete(f"/mock/cloud/{name}")
        return True


class ProjectResource:
    """Project resource client"""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        name: str,
        environment: str = "development",
        organization: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Project:
        """
        Create a project

        Args:
            name: Project name
            environment: Environment (development, staging, production)
            organization: Organization to bind to
            description: Project description

        Returns:
            Project object

        Example:
            >>> project = mf.project.create(
            ...     name="web-app",
            ...     environment="production",
            ...     organization="acme-corp"
            ... )
            >>> print(project.project_id)
            550e8400-e29b-41d4-a716-446655440003
        """
        response = self.client.post("/mock/project", json={
            "name": name,
            "environment": environment,
            "organization": organization,
            "description": description,
        })

        return Project(
            id=response["id"],
            project_id=response["project_id"],
            name=response["name"],
            environment=response["environment"],
            organization=response.get("organization"),
            description=response.get("description"),
        )

    def list(
        self,
        organization: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> List[Project]:
        """List all projects"""
        params = {}
        if organization:
            params["organization"] = organization
        if environment:
            params["environment"] = environment

        response = self.client.get("/mock/project", params=params)

        return [
            Project(
                id=proj["id"],
                project_id=proj["project_id"],
                name=proj["name"],
                environment=proj["environment"],
                organization=proj.get("organization"),
                description=proj.get("description"),
            )
            for proj in response.get("projects", [])
        ]

    def get(self, project_id: str) -> Project:
        """Get project by ID"""
        response = self.client.get(f"/mock/project/{project_id}")

        return Project(
            id=response["id"],
            project_id=response["project_id"],
            name=response["name"],
            environment=response["environment"],
            organization=response.get("organization"),
            description=response.get("description"),
        )

    def bind_resource(
        self,
        project_id: str,
        resource_type: str,
        resource_id: str,
    ) -> bool:
        """Bind a resource to a project"""
        self.client.post(f"/mock/project/{project_id}/resources", json={
            "resource_type": resource_type,
            "resource_id": resource_id,
        })
        return True

    def unbind_resource(
        self,
        project_id: str,
        resource_type: str,
        resource_id: str,
    ) -> bool:
        """Unbind a resource from a project"""
        self.client.delete(
            f"/mock/project/{project_id}/resources/{resource_type}/{resource_id}"
        )
        return True

    def delete(self, project_id: str, delete_resources: bool = False) -> bool:
        """Delete a project"""
        self.client.delete(
            f"/mock/project/{project_id}",
            params={"delete_resources": delete_resources}
        )
        return True


@dataclass
class IAMUser:
    """IAM User resource"""
    id: str
    username: str
    path: str
    arn: str
    organization: Optional[str] = None
    cloud: Optional[str] = None
    policies: Optional[List[str]] = None


@dataclass
class IAMGroup:
    """IAM Group resource"""
    id: str
    group_name: str
    arn: str
    organization: Optional[str] = None
    cloud: Optional[str] = None
    description: Optional[str] = None
    policies: Optional[List[str]] = None


@dataclass
class IAMRole:
    """IAM Role resource"""
    id: str
    role_name: str
    arn: str
    trust_policy: Dict[str, Any]
    organization: Optional[str] = None
    cloud: Optional[str] = None
    description: Optional[str] = None
    policies: Optional[List[str]] = None


@dataclass
class IAMPolicy:
    """IAM Policy resource"""
    id: str
    policy_name: str
    policy_arn: str
    policy_document: Dict[str, Any]
    description: Optional[str] = None
    organization: Optional[str] = None
    cloud: Optional[str] = None
    attached_to: Optional[List[str]] = None


@dataclass
class IAMAccessKey:
    """IAM Access Key resource"""
    access_key_id: str
    secret_access_key: str
    username: str
    status: str
    created_date: str


class IAMResource:
    """IAM (Identity and Access Management) resource client"""

    def __init__(self, client):
        self.client = client

    # ========================================================================
    # IAM Users
    # ========================================================================

    def create_user(
        self,
        username: str,
        path: str = "/",
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
    ) -> IAMUser:
        """
        Create an IAM user

        Args:
            username: IAM username
            path: User path (default: /)
            organization: Organization to bind to
            cloud: Cloud environment to bind to

        Returns:
            IAMUser object

        Example:
            >>> user = mf.iam.create_user(
            ...     username="john.smith",
            ...     organization="acme-corp",
            ...     cloud="dev-cloud"
            ... )
            >>> print(user.arn)
            arn:aws:iam::123456789:user/john.smith
        """
        response = self.client.post("/iam/user", json={
            "username": username,
            "path": path,
            "organization": organization,
            "cloud": cloud,
        })

        return IAMUser(
            id=response["id"],
            username=response["username"],
            path=response["path"],
            arn=response["arn"],
            organization=response.get("organization"),
            cloud=response.get("cloud"),
            policies=response.get("policies", []),
        )

    def list_users(
        self,
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
    ) -> List[IAMUser]:
        """List IAM users"""
        params = {}
        if organization:
            params["organization"] = organization
        if cloud:
            params["cloud"] = cloud

        response = self.client.get("/iam/user", params=params)

        return [
            IAMUser(
                id=user["id"],
                username=user["username"],
                path=user["path"],
                arn=user["arn"],
                organization=user.get("organization"),
                cloud=user.get("cloud"),
                policies=user.get("policies", []),
            )
            for user in response.get("users", [])
        ]

    def get_user(self, username: str) -> IAMUser:
        """Get IAM user by username"""
        response = self.client.get(f"/iam/user/{username}")

        return IAMUser(
            id=response["id"],
            username=response["username"],
            path=response["path"],
            arn=response["arn"],
            organization=response.get("organization"),
            cloud=response.get("cloud"),
            policies=response.get("policies", []),
        )

    def delete_user(self, username: str) -> bool:
        """Delete an IAM user"""
        self.client.delete(f"/iam/user/{username}")
        return True

    # ========================================================================
    # IAM Groups
    # ========================================================================

    def create_group(
        self,
        group_name: str,
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
        description: Optional[str] = None,
    ) -> IAMGroup:
        """
        Create an IAM group

        Args:
            group_name: Group name
            organization: Organization to bind to
            cloud: Cloud environment to bind to
            description: Group description

        Returns:
            IAMGroup object

        Example:
            >>> group = mf.iam.create_group(
            ...     group_name="developers",
            ...     organization="acme-corp",
            ...     description="Development team"
            ... )
        """
        response = self.client.post("/iam/group", json={
            "group_name": group_name,
            "organization": organization,
            "cloud": cloud,
            "description": description,
        })

        return IAMGroup(
            id=response["id"],
            group_name=response["group_name"],
            arn=response["arn"],
            organization=response.get("organization"),
            cloud=response.get("cloud"),
            description=response.get("description"),
            policies=response.get("policies", []),
        )

    def add_user_to_group(self, username: str, group_name: str) -> bool:
        """Add an IAM user to a group"""
        self.client.post(f"/iam/group/{group_name}/users", json={
            "username": username
        })
        return True

    def remove_user_from_group(self, username: str, group_name: str) -> bool:
        """Remove an IAM user from a group"""
        self.client.delete(f"/iam/group/{group_name}/users/{username}")
        return True

    # ========================================================================
    # IAM Roles
    # ========================================================================

    def create_role(
        self,
        role_name: str,
        trust_policy: Dict[str, Any],
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
        description: Optional[str] = None,
    ) -> IAMRole:
        """
        Create an IAM role

        Args:
            role_name: Role name
            trust_policy: Trust policy document
            organization: Organization to bind to
            cloud: Cloud environment to bind to
            description: Role description

        Returns:
            IAMRole object

        Example:
            >>> role = mf.iam.create_role(
            ...     role_name="lambda-execution",
            ...     trust_policy={"Service": "lambda.amazonaws.com"},
            ...     cloud="prod-cloud"
            ... )
        """
        response = self.client.post("/iam/role", json={
            "role_name": role_name,
            "trust_policy": trust_policy,
            "organization": organization,
            "cloud": cloud,
            "description": description,
        })

        return IAMRole(
            id=response["id"],
            role_name=response["role_name"],
            arn=response["arn"],
            trust_policy=response["trust_policy"],
            organization=response.get("organization"),
            cloud=response.get("cloud"),
            description=response.get("description"),
            policies=response.get("policies", []),
        )

    # ========================================================================
    # IAM Policies
    # ========================================================================

    def create_policy(
        self,
        policy_name: str,
        policy_document: Dict[str, Any],
        description: Optional[str] = None,
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
    ) -> IAMPolicy:
        """
        Create an IAM policy

        Args:
            policy_name: Policy name
            policy_document: Policy document JSON
            description: Policy description
            organization: Organization to bind to
            cloud: Cloud environment to bind to

        Returns:
            IAMPolicy object

        Example:
            >>> policy = mf.iam.create_policy(
            ...     policy_name="s3-read-only",
            ...     policy_document={
            ...         "Version": "2012-10-17",
            ...         "Statement": [{
            ...             "Effect": "Allow",
            ...             "Action": "s3:Get*",
            ...             "Resource": "*"
            ...         }]
            ...     }
            ... )
        """
        response = self.client.post("/iam/policy", json={
            "policy_name": policy_name,
            "policy_document": policy_document,
            "description": description,
            "organization": organization,
            "cloud": cloud,
        })

        return IAMPolicy(
            id=response["id"],
            policy_name=response["policy_name"],
            policy_arn=response["policy_arn"],
            policy_document=response["policy_document"],
            description=response.get("description"),
            organization=response.get("organization"),
            cloud=response.get("cloud"),
            attached_to=response.get("attached_to", []),
        )

    def list_policies(
        self,
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
    ) -> List[IAMPolicy]:
        """List IAM policies"""
        params = {}
        if organization:
            params["organization"] = organization
        if cloud:
            params["cloud"] = cloud

        response = self.client.get("/iam/policy", params=params)

        return [
            IAMPolicy(
                id=pol["id"],
                policy_name=pol["policy_name"],
                policy_arn=pol["policy_arn"],
                policy_document=pol["policy_document"],
                description=pol.get("description"),
                organization=pol.get("organization"),
                cloud=pol.get("cloud"),
                attached_to=pol.get("attached_to", []),
            )
            for pol in response.get("policies", [])
        ]

    def get_policy(self, policy_name: str) -> IAMPolicy:
        """Get IAM policy by name"""
        response = self.client.get(f"/iam/policy/{policy_name}")

        return IAMPolicy(
            id=response["id"],
            policy_name=response["policy_name"],
            policy_arn=response["policy_arn"],
            policy_document=response["policy_document"],
            description=response.get("description"),
            organization=response.get("organization"),
            cloud=response.get("cloud"),
            attached_to=response.get("attached_to", []),
        )

    def delete_policy(self, policy_name: str) -> bool:
        """Delete an IAM policy"""
        self.client.delete(f"/iam/policy/{policy_name}")
        return True

    # ========================================================================
    # Policy Attachments
    # ========================================================================

    def attach_user_policy(self, username: str, policy_name: str) -> bool:
        """Attach a policy to an IAM user"""
        self.client.post(f"/iam/user/{username}/policies", json={
            "policy_name": policy_name
        })
        return True

    def detach_user_policy(self, username: str, policy_name: str) -> bool:
        """Detach a policy from an IAM user"""
        self.client.delete(f"/iam/user/{username}/policies/{policy_name}")
        return True

    def attach_group_policy(self, group_name: str, policy_name: str) -> bool:
        """Attach a policy to an IAM group"""
        self.client.post(f"/iam/group/{group_name}/policies", json={
            "policy_name": policy_name
        })
        return True

    def detach_group_policy(self, group_name: str, policy_name: str) -> bool:
        """Detach a policy from an IAM group"""
        self.client.delete(f"/iam/group/{group_name}/policies/{policy_name}")
        return True

    def attach_role_policy(self, role_name: str, policy_name: str) -> bool:
        """Attach a policy to an IAM role"""
        self.client.post(f"/iam/role/{role_name}/policies", json={
            "policy_name": policy_name
        })
        return True

    def detach_role_policy(self, role_name: str, policy_name: str) -> bool:
        """Detach a policy from an IAM role"""
        self.client.delete(f"/iam/role/{role_name}/policies/{policy_name}")
        return True

    # ========================================================================
    # Access Keys
    # ========================================================================

    def create_access_key(
        self,
        username: str,
        description: Optional[str] = None,
    ) -> IAMAccessKey:
        """
        Create an access key for an IAM user

        Args:
            username: IAM username
            description: Access key description

        Returns:
            IAMAccessKey object with credentials

        Example:
            >>> key = mf.iam.create_access_key(
            ...     username="john.smith",
            ...     description="CLI access"
            ... )
            >>> print(f"Key ID: {key.access_key_id}")
            >>> print(f"Secret: {key.secret_access_key}")
        """
        response = self.client.post(f"/iam/user/{username}/access-keys", json={
            "description": description
        })

        return IAMAccessKey(
            access_key_id=response["access_key_id"],
            secret_access_key=response["secret_access_key"],
            username=response["username"],
            status=response["status"],
            created_date=response["created_date"],
        )

    def list_access_keys(self, username: str) -> List[Dict[str, Any]]:
        """List access keys for an IAM user (without secrets)"""
        response = self.client.get(f"/iam/user/{username}/access-keys")
        return response.get("access_keys", [])

    def delete_access_key(self, username: str, access_key_id: str) -> bool:
        """Delete an access key"""
        self.client.delete(f"/iam/user/{username}/access-keys/{access_key_id}")
        return True

    # ========================================================================
    # Permission Checks & Simulation
    # ========================================================================

    def check_permission(
        self,
        username: str,
        action: str,
        resource: str,
        cloud: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check if a user has permission for an action on a resource

        Args:
            username: IAM username
            action: Action to check (e.g., "s3:GetObject")
            resource: Resource identifier
            cloud: Cloud environment

        Returns:
            Permission check result

        Example:
            >>> result = mf.iam.check_permission(
            ...     username="john.smith",
            ...     action="s3:GetObject",
            ...     resource="my-bucket/key.txt"
            ... )
            >>> print(result["allowed"])
            True
        """
        response = self.client.post("/iam/check-permission", json={
            "username": username,
            "action": action,
            "resource": resource,
            "cloud": cloud,
        })

        return response

    def simulate_policy(
        self,
        policy_name: str,
        action: str,
        resource: str,
        username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulate IAM policy evaluation

        Args:
            policy_name: Policy to simulate
            action: Action to test
            resource: Resource to test
            username: Optional user context

        Returns:
            Simulation result

        Example:
            >>> result = mf.iam.simulate_policy(
            ...     policy_name="s3-read-only",
            ...     action="s3:GetObject",
            ...     resource="bucket/key"
            ... )
            >>> print(result["decision"])
            "allowed"
        """
        response = self.client.post("/iam/simulate-policy", json={
            "policy_name": policy_name,
            "action": action,
            "resource": resource,
            "username": username,
        })

        return response

    # ========================================================================
    # Resource-Based Policies
    # ========================================================================

    def create_resource_policy(
        self,
        resource_type: str,
        resource_id: str,
        policy_document: Dict[str, Any],
    ) -> bool:
        """
        Attach a resource-based policy to a resource

        Args:
            resource_type: Type of resource (vpc, lambda, etc.)
            resource_id: Resource identifier
            policy_document: Policy document

        Example:
            >>> mf.iam.create_resource_policy(
            ...     resource_type="lambda",
            ...     resource_id="my-function",
            ...     policy_document={
            ...         "Version": "2012-10-17",
            ...         "Statement": [{
            ...             "Effect": "Allow",
            ...             "Principal": {"Service": "apigateway.amazonaws.com"},
            ...             "Action": "lambda:InvokeFunction"
            ...         }]
            ...     }
            ... )
        """
        self.client.post(f"/iam/resource-policy/{resource_type}/{resource_id}", json={
            "policy_document": policy_document
        })
        return True

    def get_resource_policy(
        self,
        resource_type: str,
        resource_id: str,
    ) -> Dict[str, Any]:
        """Get resource-based policy"""
        response = self.client.get(f"/iam/resource-policy/{resource_type}/{resource_id}")
        return response.get("policy_document", {})

    def delete_resource_policy(
        self,
        resource_type: str,
        resource_id: str,
    ) -> bool:
        """Delete resource-based policy"""
        self.client.delete(f"/iam/resource-policy/{resource_type}/{resource_id}")
        return True


class GeneratorResource:
    """Data generation utilities for creating realistic test data"""

    def __init__(self, client):
        self.client = client

    def generate_users(
        self,
        count: int = 10,
        role: str = "mixed",
        organization: Optional[str] = None,
        cloud: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic user data

        Args:
            count: Number of users to generate
            role: Role type (user, admin, developer, mixed)
            organization: Organization to bind users to
            cloud: Cloud environment to bind to
            domain: Email domain

        Returns:
            List of user dictionaries

        Example:
            >>> users = mf.generator.generate_users(
            ...     count=5,
            ...     role="developer",
            ...     organization="acme-corp",
            ...     domain="acme.com"
            ... )
            >>> for user in users:
            ...     print(f"{user['username']}: {user['email']}")
        """
        response = self.client.post("/generator/users", json={
            "count": count,
            "role": role,
            "organization": organization,
            "cloud": cloud,
            "domain": domain,
        })

        return response.get("users", [])

    def generate_employees(
        self,
        count: int = 10,
        organization: Optional[str] = None,
        departments: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic employee data with job titles and departments

        Args:
            count: Number of employees to generate
            organization: Organization to bind employees to
            departments: List of departments (default: Engineering, Sales, Marketing, HR, Finance, Operations)

        Returns:
            List of employee dictionaries

        Example:
            >>> employees = mf.generator.generate_employees(
            ...     count=20,
            ...     organization="acme-corp",
            ...     departments=["Engineering", "Sales", "Marketing"]
            ... )
            >>> for emp in employees:
            ...     print(f"{emp['name']} - {emp['job_title']} ({emp['department']})")
        """
        response = self.client.post("/generator/employees", json={
            "count": count,
            "organization": organization,
            "departments": departments,
        })

        return response.get("employees", [])

    def generate_organizations(
        self,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic organization structures

        Args:
            count: Number of organizations to generate

        Returns:
            List of organization dictionaries

        Example:
            >>> orgs = mf.generator.generate_organizations(count=3)
            >>> for org in orgs:
            ...     print(f"{org['name']} - {org['industry']} ({org['size']} employees)")
        """
        response = self.client.post("/generator/organizations", json={
            "count": count,
        })

        return response.get("organizations", [])

    def generate_network_config(
        self,
        cloud: Optional[str] = None,
        vpc_cidr: str = "10.0.0.0/16",
        subnets: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate realistic network configuration

        Args:
            cloud: Cloud environment to bind to
            vpc_cidr: VPC CIDR block
            subnets: Number of subnets to generate

        Returns:
            Network configuration dictionary

        Example:
            >>> config = mf.generator.generate_network_config(
            ...     cloud="prod-cloud",
            ...     vpc_cidr="10.0.0.0/16",
            ...     subnets=4
            ... )
            >>> print(config["vpc"]["cidr"])
            10.0.0.0/16
            >>> for subnet in config["subnets"]:
            ...     print(f"{subnet['name']}: {subnet['cidr']}")
        """
        response = self.client.post("/generator/network-config", json={
            "cloud": cloud,
            "vpc_cidr": vpc_cidr,
            "subnets": subnets,
        })

        return response

    def generate_iam_policies(
        self,
        policy_type: str = "common",
        services: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate common IAM policy templates

        Args:
            policy_type: Type of policies (common, least-privilege, admin, read-only, service-specific)
            services: List of AWS services (s3, ec2, lambda, dynamodb, etc.)

        Returns:
            List of IAM policy dictionaries

        Example:
            >>> policies = mf.generator.generate_iam_policies(
            ...     policy_type="common",
            ...     services=["s3", "dynamodb", "lambda"]
            ... )
            >>> for policy in policies:
            ...     print(f"{policy['policy_name']}: {policy['description']}")
        """
        response = self.client.post("/generator/iam-policies", json={
            "policy_type": policy_type,
            "services": services,
        })

        return response.get("policies", [])

    def generate_test_scenario(
        self,
        scenario: str = "startup",
    ) -> Dict[str, Any]:
        """
        Generate complete test scenarios with all resources

        Args:
            scenario: Scenario type (startup, enterprise, multi-cloud, dev-team)

        Returns:
            Complete scenario dictionary with organizations, users, resources, etc.

        Example:
            >>> scenario = mf.generator.generate_test_scenario("startup")
            >>> print(f"Organization: {scenario['organization']['name']}")
            >>> print(f"Users: {len(scenario['users'])}")
            >>> print(f"Resources: {len(scenario['resources'])}")

        Available scenarios:
            - startup: Small company (5-10 employees, basic infrastructure)
            - enterprise: Large company (100+ employees, complex infrastructure)
            - multi-cloud: Multi-cloud setup (AWS, GCP, Azure)
            - dev-team: Development team environment
        """
        response = self.client.post("/generator/test-scenario", json={
            "scenario": scenario,
        })

        return response


class UtilitiesResource:
    """Utility helpers for common transformations and operations"""

    def __init__(self, client):
        self.client = client

    # ========================================================================
    # Binary/Hex Conversion
    # ========================================================================

    def bin2hex(self, binary: str) -> str:
        """
        Convert binary string to hexadecimal

        Args:
            binary: Binary string (e.g., "11010101")

        Returns:
            Hexadecimal string (e.g., "d5")

        Example:
            >>> mf.utilities.bin2hex("11010101")
            "d5"
        """
        response = self.client.post("/utilities/bin2hex", json={"binary": binary})
        return response["hex"]

    def hex2bin(self, hex_string: str) -> str:
        """
        Convert hexadecimal to binary string

        Args:
            hex_string: Hexadecimal string (e.g., "d5")

        Returns:
            Binary string (e.g., "11010101")

        Example:
            >>> mf.utilities.hex2bin("d5")
            "11010101"
        """
        response = self.client.post("/utilities/hex2bin", json={"hex": hex_string})
        return response["binary"]

    # ========================================================================
    # IP Address Conversion
    # ========================================================================

    def ip2bin(self, ip: str) -> str:
        """
        Convert IP address to binary representation

        Args:
            ip: IP address (e.g., "192.168.1.1")

        Returns:
            Binary representation

        Example:
            >>> mf.utilities.ip2bin("192.168.1.1")
            "11000000101010000000000100000001"
        """
        response = self.client.post("/utilities/ip2bin", json={"ip": ip})
        return response["binary"]

    def bin2ip(self, binary: str) -> str:
        """
        Convert binary to IP address

        Args:
            binary: 32-bit binary string

        Returns:
            IP address

        Example:
            >>> mf.utilities.bin2ip("11000000101010000000000100000001")
            "192.168.1.1"
        """
        response = self.client.post("/utilities/bin2ip", json={"binary": binary})
        return response["ip"]

    def ip2long(self, ip: str) -> int:
        """
        Convert IP address to long integer

        Args:
            ip: IP address (e.g., "192.168.1.1")

        Returns:
            Long integer representation

        Example:
            >>> mf.utilities.ip2long("192.168.1.1")
            3232235777
        """
        response = self.client.post("/utilities/ip2long", json={"ip": ip})
        return response["long"]

    def long2ip(self, long_int: int) -> str:
        """
        Convert long integer to IP address

        Args:
            long_int: Long integer

        Returns:
            IP address

        Example:
            >>> mf.utilities.long2ip(3232235777)
            "192.168.1.1"
        """
        response = self.client.post("/utilities/long2ip", json={"long": long_int})
        return response["ip"]

    # ========================================================================
    # IPv6 Helpers
    # ========================================================================

    def expand_ipv6(self, ipv6: str) -> str:
        """
        Expand compressed IPv6 address to full form

        Args:
            ipv6: Compressed IPv6 address

        Returns:
            Fully expanded IPv6 address

        Example:
            >>> mf.utilities.expand_ipv6("2001:db8::1")
            "2001:0db8:0000:0000:0000:0000:0000:0001"
        """
        response = self.client.post("/utilities/expand-ipv6", json={"ipv6": ipv6})
        return response["expanded"]

    def compress_ipv6(self, ipv6: str) -> str:
        """
        Compress IPv6 address to shortest form

        Args:
            ipv6: IPv6 address

        Returns:
            Compressed IPv6 address

        Example:
            >>> mf.utilities.compress_ipv6("2001:0db8:0000:0000:0000:0000:0000:0001")
            "2001:db8::1"
        """
        response = self.client.post("/utilities/compress-ipv6", json={"ipv6": ipv6})
        return response["compressed"]

    def is_valid_ipv6(self, ipv6: str) -> bool:
        """
        Validate IPv6 address

        Args:
            ipv6: IPv6 address to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> mf.utilities.is_valid_ipv6("2001:db8::1")
            True
        """
        response = self.client.post("/utilities/validate-ipv6", json={"ipv6": ipv6})
        return response["valid"]

    # ========================================================================
    # CIDR Helpers
    # ========================================================================

    def cidr_to_range(self, cidr: str) -> Dict[str, str]:
        """
        Convert CIDR notation to IP range

        Args:
            cidr: CIDR notation (e.g., "10.0.0.0/24")

        Returns:
            Dictionary with start_ip, end_ip, total_ips

        Example:
            >>> result = mf.utilities.cidr_to_range("10.0.0.0/24")
            >>> print(f"{result['start_ip']} - {result['end_ip']}")
            10.0.0.0 - 10.0.0.255
        """
        response = self.client.post("/utilities/cidr-to-range", json={"cidr": cidr})
        return response

    def ip_in_cidr(self, ip: str, cidr: str) -> bool:
        """
        Check if IP address is within CIDR range

        Args:
            ip: IP address
            cidr: CIDR notation

        Returns:
            True if IP is in range, False otherwise

        Example:
            >>> mf.utilities.ip_in_cidr("10.0.0.50", "10.0.0.0/24")
            True
        """
        response = self.client.post("/utilities/ip-in-cidr", json={"ip": ip, "cidr": cidr})
        return response["in_range"]

    def cidr_overlap(self, cidr1: str, cidr2: str) -> bool:
        """
        Check if two CIDR ranges overlap

        Args:
            cidr1: First CIDR notation
            cidr2: Second CIDR notation

        Returns:
            True if ranges overlap, False otherwise

        Example:
            >>> mf.utilities.cidr_overlap("10.0.0.0/24", "10.0.0.128/25")
            True
        """
        response = self.client.post("/utilities/cidr-overlap", json={
            "cidr1": cidr1,
            "cidr2": cidr2
        })
        return response["overlap"]

    # ========================================================================
    # YAML Helpers
    # ========================================================================

    def yaml_to_json(self, yaml_str: str) -> Dict[str, Any]:
        """
        Convert YAML to JSON

        Args:
            yaml_str: YAML string

        Returns:
            JSON object

        Example:
            >>> yaml = "name: John\\nage: 30"
            >>> json_obj = mf.utilities.yaml_to_json(yaml)
            >>> print(json_obj["name"])
            John
        """
        response = self.client.post("/utilities/yaml-to-json", json={"yaml": yaml_str})
        return response["json"]

    def json_to_yaml(self, json_obj: Dict[str, Any]) -> str:
        """
        Convert JSON to YAML

        Args:
            json_obj: JSON object

        Returns:
            YAML string

        Example:
            >>> json_obj = {"name": "John", "age": 30}
            >>> yaml_str = mf.utilities.json_to_yaml(json_obj)
            >>> print(yaml_str)
            name: John
            age: 30
        """
        response = self.client.post("/utilities/json-to-yaml", json={"json": json_obj})
        return response["yaml"]

    def validate_yaml(self, yaml_str: str) -> Dict[str, Any]:
        """
        Validate YAML syntax

        Args:
            yaml_str: YAML string

        Returns:
            Validation result with valid flag and errors if any

        Example:
            >>> result = mf.utilities.validate_yaml("name: John\\nage: 30")
            >>> print(result["valid"])
            True
        """
        response = self.client.post("/utilities/validate-yaml", json={"yaml": yaml_str})
        return response

    # ========================================================================
    # JSON Helpers
    # ========================================================================

    def minify_json(self, json_str: str) -> str:
        """
        Minify JSON string

        Args:
            json_str: JSON string

        Returns:
            Minified JSON

        Example:
            >>> minified = mf.utilities.minify_json('{"name": "John", "age": 30}')
            >>> print(minified)
            {"name":"John","age":30}
        """
        response = self.client.post("/utilities/minify-json", json={"json": json_str})
        return response["minified"]

    def pretty_json(self, json_str: str, indent: int = 2) -> str:
        """
        Pretty print JSON string

        Args:
            json_str: JSON string
            indent: Indentation level

        Returns:
            Formatted JSON

        Example:
            >>> pretty = mf.utilities.pretty_json('{"name":"John","age":30}')
            >>> print(pretty)
            {
              "name": "John",
              "age": 30
            }
        """
        response = self.client.post("/utilities/pretty-json", json={
            "json": json_str,
            "indent": indent
        })
        return response["formatted"]

    def validate_json(self, json_str: str) -> Dict[str, Any]:
        """
        Validate JSON syntax

        Args:
            json_str: JSON string

        Returns:
            Validation result with valid flag and errors if any

        Example:
            >>> result = mf.utilities.validate_json('{"name": "John"}')
            >>> print(result["valid"])
            True
        """
        response = self.client.post("/utilities/validate-json", json={"json": json_str})
        return response

    # ========================================================================
    # Base64 Helpers
    # ========================================================================

    def base64_encode(self, data: str) -> str:
        """
        Encode string to Base64

        Args:
            data: String to encode

        Returns:
            Base64 encoded string

        Example:
            >>> encoded = mf.utilities.base64_encode("Hello World")
            >>> print(encoded)
            SGVsbG8gV29ybGQ=
        """
        response = self.client.post("/utilities/base64-encode", json={"data": data})
        return response["encoded"]

    def base64_decode(self, encoded: str) -> str:
        """
        Decode Base64 string

        Args:
            encoded: Base64 encoded string

        Returns:
            Decoded string

        Example:
            >>> decoded = mf.utilities.base64_decode("SGVsbG8gV29ybGQ=")
            >>> print(decoded)
            Hello World
        """
        response = self.client.post("/utilities/base64-decode", json={"encoded": encoded})
        return response["decoded"]

    # ========================================================================
    # URL Helpers
    # ========================================================================

    def parse_url(self, url: str) -> Dict[str, Any]:
        """
        Parse URL into components

        Args:
            url: URL string

        Returns:
            Dictionary with scheme, host, port, path, query, fragment

        Example:
            >>> result = mf.utilities.parse_url("https://api.example.com:8080/v1/users?page=1#top")
            >>> print(result["host"])
            api.example.com
        """
        response = self.client.post("/utilities/parse-url", json={"url": url})
        return response

    def build_url(
        self,
        scheme: str,
        host: str,
        path: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        port: Optional[int] = None,
    ) -> str:
        """
        Build URL from components

        Args:
            scheme: URL scheme (http, https)
            host: Hostname
            path: URL path
            query: Query parameters
            port: Port number

        Returns:
            Complete URL

        Example:
            >>> url = mf.utilities.build_url(
            ...     scheme="https",
            ...     host="api.example.com",
            ...     path="/v1/users",
            ...     query={"page": "1"}
            ... )
            >>> print(url)
            https://api.example.com/v1/users?page=1
        """
        response = self.client.post("/utilities/build-url", json={
            "scheme": scheme,
            "host": host,
            "path": path,
            "query": query,
            "port": port,
        })
        return response["url"]

    def url_encode(self, data: str) -> str:
        """
        URL encode string

        Args:
            data: String to encode

        Returns:
            URL encoded string

        Example:
            >>> encoded = mf.utilities.url_encode("hello world & stuff")
            >>> print(encoded)
            hello%20world%20%26%20stuff
        """
        response = self.client.post("/utilities/url-encode", json={"data": data})
        return response["encoded"]

    def url_decode(self, encoded: str) -> str:
        """
        URL decode string

        Args:
            encoded: URL encoded string

        Returns:
            Decoded string

        Example:
            >>> decoded = mf.utilities.url_decode("hello%20world%20%26%20stuff")
            >>> print(decoded)
            hello world & stuff
        """
        response = self.client.post("/utilities/url-decode", json={"encoded": encoded})
        return response["decoded"]

    # ========================================================================
    # Hash Helpers
    # ========================================================================

    def md5(self, data: str) -> str:
        """
        Generate MD5 hash

        Args:
            data: Data to hash

        Returns:
            MD5 hash

        Example:
            >>> hash_value = mf.utilities.md5("Hello World")
            >>> print(hash_value)
            b10a8db164e0754105b7a99be72e3fe5
        """
        response = self.client.post("/utilities/md5", json={"data": data})
        return response["hash"]

    def sha1(self, data: str) -> str:
        """Generate SHA1 hash"""
        response = self.client.post("/utilities/sha1", json={"data": data})
        return response["hash"]

    def sha256(self, data: str) -> str:
        """Generate SHA256 hash"""
        response = self.client.post("/utilities/sha256", json={"data": data})
        return response["hash"]

    def sha512(self, data: str) -> str:
        """Generate SHA512 hash"""
        response = self.client.post("/utilities/sha512", json={"data": data})
        return response["hash"]

    # ========================================================================
    # UUID Helpers
    # ========================================================================

    def generate_uuid(self, version: int = 4) -> str:
        """
        Generate UUID

        Args:
            version: UUID version (1, 4, or 5)

        Returns:
            UUID string

        Example:
            >>> uuid = mf.utilities.generate_uuid()
            >>> print(uuid)
            550e8400-e29b-41d4-a716-446655440000
        """
        response = self.client.post("/utilities/generate-uuid", json={"version": version})
        return response["uuid"]

    def validate_uuid(self, uuid_str: str) -> bool:
        """
        Validate UUID format

        Args:
            uuid_str: UUID string to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> valid = mf.utilities.validate_uuid("550e8400-e29b-41d4-a716-446655440000")
            >>> print(valid)
            True
        """
        response = self.client.post("/utilities/validate-uuid", json={"uuid": uuid_str})
        return response["valid"]

    # ========================================================================
    # Time Helpers
    # ========================================================================

    def timestamp(self, format: str = "unix") -> Any:
        """
        Get current timestamp

        Args:
            format: Format (unix, iso8601, rfc3339)

        Returns:
            Timestamp in requested format

        Example:
            >>> ts = mf.utilities.timestamp("unix")
            >>> print(ts)
            1640995200
        """
        response = self.client.post("/utilities/timestamp", json={"format": format})
        return response["timestamp"]

    def iso8601(self, unix_timestamp: Optional[int] = None) -> str:
        """
        Convert Unix timestamp to ISO8601 format

        Args:
            unix_timestamp: Unix timestamp (optional, defaults to now)

        Returns:
            ISO8601 formatted string

        Example:
            >>> iso = mf.utilities.iso8601(1640995200)
            >>> print(iso)
            2022-01-01T00:00:00Z
        """
        response = self.client.post("/utilities/iso8601", json={
            "timestamp": unix_timestamp
        })
        return response["iso8601"]

    def parse_time(self, time_str: str) -> int:
        """
        Parse time string to Unix timestamp

        Args:
            time_str: Time string in various formats

        Returns:
            Unix timestamp

        Example:
            >>> ts = mf.utilities.parse_time("2022-01-01T00:00:00Z")
            >>> print(ts)
            1640995200
        """
        response = self.client.post("/utilities/parse-time", json={"time": time_str})
        return response["timestamp"]

    def time_ago(self, unix_timestamp: int) -> str:
        """
        Convert timestamp to human-readable relative time

        Args:
            unix_timestamp: Unix timestamp

        Returns:
            Human-readable string (e.g., "2 hours ago")

        Example:
            >>> relative = mf.utilities.time_ago(1640995200)
            >>> print(relative)
            2 years ago
        """
        response = self.client.post("/utilities/time-ago", json={
            "timestamp": unix_timestamp
        })
        return response["relative"]

    # ========================================================================
    # String Helpers
    # ========================================================================

    def slugify(self, text: str) -> str:
        """
        Convert text to URL-friendly slug

        Args:
            text: Text to slugify

        Returns:
            Slugified string

        Example:
            >>> slug = mf.utilities.slugify("Hello World & Stuff!")
            >>> print(slug)
            hello-world-stuff
        """
        response = self.client.post("/utilities/slugify", json={"text": text})
        return response["slug"]

    def random_string(self, length: int = 16, charset: str = "alphanumeric") -> str:
        """
        Generate random string

        Args:
            length: Length of string
            charset: Character set (alphanumeric, alpha, numeric, hex)

        Returns:
            Random string

        Example:
            >>> random = mf.utilities.random_string(32, "hex")
            >>> print(random)
            a1b2c3d4e5f6...
        """
        response = self.client.post("/utilities/random-string", json={
            "length": length,
            "charset": charset
        })
        return response["string"]

    def random_password(
        self,
        length: int = 16,
        include_symbols: bool = True,
        include_numbers: bool = True,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
    ) -> str:
        """
        Generate secure random password

        Args:
            length: Password length
            include_symbols: Include symbols (!@#$%^&*)
            include_numbers: Include numbers
            include_uppercase: Include uppercase letters
            include_lowercase: Include lowercase letters

        Returns:
            Random password

        Example:
            >>> password = mf.utilities.random_password(20, include_symbols=True)
            >>> print(password)
            Xa9#bC2$dE5&fG8*
        """
        response = self.client.post("/utilities/random-password", json={
            "length": length,
            "include_symbols": include_symbols,
            "include_numbers": include_numbers,
            "include_uppercase": include_uppercase,
            "include_lowercase": include_lowercase,
        })
        return response["password"]

    # ========================================================================
    # ARN Helpers
    # ========================================================================

    def parse_arn(self, arn: str) -> Dict[str, str]:
        """
        Parse AWS ARN into components

        Args:
            arn: ARN string

        Returns:
            Dictionary with partition, service, region, account, resource

        Example:
            >>> result = mf.utilities.parse_arn("arn:aws:iam::123456789:user/john")
            >>> print(result["service"])
            iam
        """
        response = self.client.post("/utilities/parse-arn", json={"arn": arn})
        return response

    def build_arn(
        self,
        service: str,
        resource: str,
        account: Optional[str] = None,
        region: Optional[str] = None,
        partition: str = "aws",
    ) -> str:
        """
        Build AWS ARN from components

        Args:
            service: AWS service (e.g., iam, s3, lambda)
            resource: Resource identifier
            account: AWS account ID
            region: AWS region
            partition: AWS partition (default: aws)

        Returns:
            Complete ARN

        Example:
            >>> arn = mf.utilities.build_arn(
            ...     service="iam",
            ...     resource="user/john",
            ...     account="123456789"
            ... )
            >>> print(arn)
            arn:aws:iam::123456789:user/john
        """
        response = self.client.post("/utilities/build-arn", json={
            "service": service,
            "resource": resource,
            "account": account,
            "region": region,
            "partition": partition,
        })
        return response["arn"]

    def validate_arn(self, arn: str) -> bool:
        """
        Validate ARN format

        Args:
            arn: ARN string to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> valid = mf.utilities.validate_arn("arn:aws:iam::123456789:user/john")
            >>> print(valid)
            True
        """
        response = self.client.post("/utilities/validate-arn", json={"arn": arn})
        return response["valid"]
