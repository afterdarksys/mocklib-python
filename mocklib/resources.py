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
