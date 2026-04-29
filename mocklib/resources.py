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

    # ---- Subnets ----

    def create_subnet(
        self,
        vpc_id: str,
        cidr_block: str,
        availability_zone: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a subnet in a VPC"""
        body: Dict[str, Any] = {
            "Action": "CreateSubnet",
            "VpcId": vpc_id,
            "CidrBlock": cidr_block,
            "Tags": tags or {},
        }
        if availability_zone:
            body["AvailabilityZone"] = availability_zone
        return self.client.post("/aws/vpc", json=body)

    def describe_subnets(
        self,
        subnet_ids: Optional[List[str]] = None,
        vpc_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Describe subnets"""
        body: Dict[str, Any] = {"Action": "DescribeSubnets"}
        if subnet_ids:
            body["SubnetIds"] = subnet_ids
        if vpc_id:
            body["VpcId"] = vpc_id
        response = self.client.post("/aws/vpc", json=body)
        return response.get("Subnets", [])

    def delete_subnet(self, subnet_id: str) -> bool:
        """Delete a subnet"""
        self.client.post("/aws/vpc", json={
            "Action": "DeleteSubnet",
            "SubnetId": subnet_id,
        })
        return True

    # ---- Security Groups ----

    def create_security_group(
        self,
        group_name: str,
        description: str,
        vpc_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a security group"""
        body: Dict[str, Any] = {
            "Action": "CreateSecurityGroup",
            "GroupName": group_name,
            "Description": description,
            "Tags": tags or {},
        }
        if vpc_id:
            body["VpcId"] = vpc_id
        return self.client.post("/aws/vpc", json=body)

    def describe_security_groups(
        self,
        group_ids: Optional[List[str]] = None,
        vpc_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Describe security groups"""
        body: Dict[str, Any] = {"Action": "DescribeSecurityGroups"}
        if group_ids:
            body["GroupIds"] = group_ids
        if vpc_id:
            body["VpcId"] = vpc_id
        response = self.client.post("/aws/vpc", json=body)
        return response.get("SecurityGroups", [])

    def delete_security_group(self, group_id: str) -> bool:
        """Delete a security group"""
        self.client.post("/aws/vpc", json={
            "Action": "DeleteSecurityGroup",
            "GroupId": group_id,
        })
        return True

    def authorize_ingress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> bool:
        """Authorize inbound rules for a security group"""
        self.client.post("/aws/vpc", json={
            "Action": "AuthorizeSecurityGroupIngress",
            "GroupId": group_id,
            "IpPermissions": ip_permissions,
        })
        return True

    def authorize_egress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> bool:
        """Authorize outbound rules for a security group"""
        self.client.post("/aws/vpc", json={
            "Action": "AuthorizeSecurityGroupEgress",
            "GroupId": group_id,
            "IpPermissions": ip_permissions,
        })
        return True

    # ---- Internet Gateways ----

    def create_internet_gateway(
        self,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create an internet gateway"""
        return self.client.post("/aws/vpc", json={
            "Action": "CreateInternetGateway",
            "Tags": tags or {},
        })

    def describe_internet_gateways(
        self,
        igw_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Describe internet gateways"""
        body: Dict[str, Any] = {"Action": "DescribeInternetGateways"}
        if igw_ids:
            body["InternetGatewayIds"] = igw_ids
        response = self.client.post("/aws/vpc", json=body)
        return response.get("InternetGateways", [])

    def attach_internet_gateway(self, igw_id: str, vpc_id: str) -> bool:
        """Attach an internet gateway to a VPC"""
        self.client.post("/aws/vpc", json={
            "Action": "AttachInternetGateway",
            "InternetGatewayId": igw_id,
            "VpcId": vpc_id,
        })
        return True

    def detach_internet_gateway(self, igw_id: str, vpc_id: str) -> bool:
        """Detach an internet gateway from a VPC"""
        self.client.post("/aws/vpc", json={
            "Action": "DetachInternetGateway",
            "InternetGatewayId": igw_id,
            "VpcId": vpc_id,
        })
        return True

    def delete_internet_gateway(self, igw_id: str) -> bool:
        """Delete an internet gateway"""
        self.client.post("/aws/vpc", json={
            "Action": "DeleteInternetGateway",
            "InternetGatewayId": igw_id,
        })
        return True

    # ---- Route Tables ----

    def create_route_table(
        self,
        vpc_id: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a route table"""
        return self.client.post("/aws/vpc", json={
            "Action": "CreateRouteTable",
            "VpcId": vpc_id,
            "Tags": tags or {},
        })

    def describe_route_tables(
        self,
        route_table_ids: Optional[List[str]] = None,
        vpc_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Describe route tables"""
        body: Dict[str, Any] = {"Action": "DescribeRouteTables"}
        if route_table_ids:
            body["RouteTableIds"] = route_table_ids
        if vpc_id:
            body["VpcId"] = vpc_id
        response = self.client.post("/aws/vpc", json=body)
        return response.get("RouteTables", [])

    def create_route(
        self,
        route_table_id: str,
        destination_cidr_block: str,
        gateway_id: Optional[str] = None,
        instance_id: Optional[str] = None,
    ) -> bool:
        """Create a route in a route table"""
        body: Dict[str, Any] = {
            "Action": "CreateRoute",
            "RouteTableId": route_table_id,
            "DestinationCidrBlock": destination_cidr_block,
        }
        if gateway_id:
            body["GatewayId"] = gateway_id
        if instance_id:
            body["InstanceId"] = instance_id
        self.client.post("/aws/vpc", json=body)
        return True

    def associate_route_table(
        self,
        route_table_id: str,
        subnet_id: str,
    ) -> str:
        """Associate a route table with a subnet"""
        response = self.client.post("/aws/vpc", json={
            "Action": "AssociateRouteTable",
            "RouteTableId": route_table_id,
            "SubnetId": subnet_id,
        })
        return response.get("AssociationId", "")

    def delete_route_table(self, route_table_id: str) -> bool:
        """Delete a route table"""
        self.client.post("/aws/vpc", json={
            "Action": "DeleteRouteTable",
            "RouteTableId": route_table_id,
        })
        return True


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

        response = self.client.post("/lambda/2015-03-31/functions", json={
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

    def list(self) -> List[Dict[str, Any]]:
        """List all Lambda functions"""
        response = self.client.get("/lambda/2015-03-31/functions")
        return response.get("Functions", [])

    def get(self, function_name: str) -> Dict[str, Any]:
        """Get a Lambda function by name"""
        return self.client.get(f"/lambda/2015-03-31/functions/{function_name}")

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
        response = self.client.post(
            f"/lambda/2015-03-31/functions/{function_name}/invocations",
            json=payload or {},
        )

        return response.get("Payload", response)

    def delete(self, function_name: str) -> bool:
        """Delete a Lambda function"""
        self.client.delete(f"/lambda/2015-03-31/functions/{function_name}")
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

    def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Update an item in a DynamoDB table"""
        response = self.client.post("/aws/dynamodb", json={
            "Action": "UpdateItem",
            "TableName": table_name,
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values or {},
            "ExpressionAttributeNames": expression_attribute_names or {},
        })
        return response.get("Attributes", {})

    def delete_item(
        self,
        table_name: str,
        key: Dict[str, Any],
    ) -> bool:
        """Delete an item from a DynamoDB table"""
        self.client.post("/aws/dynamodb", json={
            "Action": "DeleteItem",
            "TableName": table_name,
            "Key": key,
        })
        return True

    def query(
        self,
        table_name: str,
        key_condition_expression: str,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Query a DynamoDB table"""
        body: Dict[str, Any] = {
            "Action": "Query",
            "TableName": table_name,
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values or {},
            "ExpressionAttributeNames": expression_attribute_names or {},
        }
        if limit is not None:
            body["Limit"] = limit
        response = self.client.post("/aws/dynamodb", json=body)
        return response.get("Items", [])

    def scan(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Scan a DynamoDB table"""
        body: Dict[str, Any] = {
            "Action": "Scan",
            "TableName": table_name,
        }
        if filter_expression:
            body["FilterExpression"] = filter_expression
        if expression_attribute_values:
            body["ExpressionAttributeValues"] = expression_attribute_values
        if limit is not None:
            body["Limit"] = limit
        response = self.client.post("/aws/dynamodb", json=body)
        return response.get("Items", [])

    def batch_write_item(
        self,
        request_items: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Batch write items to one or more DynamoDB tables"""
        response = self.client.post("/aws/dynamodb", json={
            "Action": "BatchWriteItem",
            "RequestItems": request_items,
        })
        return response.get("UnprocessedItems", {})

    def batch_get_item(
        self,
        request_items: Dict[str, Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Batch get items from one or more DynamoDB tables"""
        response = self.client.post("/aws/dynamodb", json={
            "Action": "BatchGetItem",
            "RequestItems": request_items,
        })
        return response.get("Responses", {})


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

    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """Delete a message from an SQS queue"""
        self.client.post("/aws/sqs", json={
            "Action": "DeleteMessage",
            "QueueUrl": queue_url,
            "ReceiptHandle": receipt_handle,
        })
        return True

    def delete_queue(self, queue_url: str) -> bool:
        """Delete an SQS queue"""
        self.client.post("/aws/sqs", json={
            "Action": "DeleteQueue",
            "QueueUrl": queue_url,
        })
        return True

    def get_queue_attributes(
        self,
        queue_url: str,
        attribute_names: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Get attributes of an SQS queue"""
        response = self.client.post("/aws/sqs", json={
            "Action": "GetQueueAttributes",
            "QueueUrl": queue_url,
            "AttributeNames": attribute_names or ["All"],
        })
        return response.get("Attributes", {})

    def purge_queue(self, queue_url: str) -> bool:
        """Purge all messages from an SQS queue"""
        self.client.post("/aws/sqs", json={
            "Action": "PurgeQueue",
            "QueueUrl": queue_url,
        })
        return True


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

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
    ) -> List[Dict[str, Any]]:
        """List objects in a storage bucket"""
        body: Dict[str, Any] = {
            "Action": "ListObjects",
            "BucketName": bucket_name,
            "MaxKeys": max_keys,
        }
        if prefix:
            body["Prefix"] = prefix
        response = self.client.post("/storage/object", json=body)
        return response.get("Contents", [])

    def get_object(
        self,
        bucket_name: str,
        key: str,
    ) -> bytes:
        """Download an object from a storage bucket"""
        import base64

        response = self.client.post("/storage/object", json={
            "Action": "GetObject",
            "BucketName": bucket_name,
            "Key": key,
        })
        encoded = response.get("Body", "")
        return base64.b64decode(encoded) if encoded else b""

    def delete_object(
        self,
        bucket_name: str,
        key: str,
    ) -> bool:
        """Delete an object from a storage bucket"""
        self.client.post("/storage/object", json={
            "Action": "DeleteObject",
            "BucketName": bucket_name,
            "Key": key,
        })
        return True

    def head_object(
        self,
        bucket_name: str,
        key: str,
    ) -> Dict[str, Any]:
        """Get metadata for an object without downloading it"""
        response = self.client.post("/storage/object", json={
            "Action": "HeadObject",
            "BucketName": bucket_name,
            "Key": key,
        })
        return response

    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
    ) -> bool:
        """Copy an object within or between storage buckets"""
        self.client.post("/storage/object", json={
            "Action": "CopyObject",
            "SourceBucket": source_bucket,
            "SourceKey": source_key,
            "DestinationBucket": dest_bucket,
            "DestinationKey": dest_key,
        })
        return True


# ==============================================================================
# AWS EC2
# ==============================================================================

@dataclass
class EC2Instance:
    """EC2 instance resource"""
    instance_id: str
    instance_type: str
    state: str
    image_id: Optional[str] = None
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class EC2Resource:
    """EC2 resource client"""

    def __init__(self, client):
        self.client = client

    def run_instances(
        self,
        image_id: str,
        instance_type: str,
        min_count: int = 1,
        max_count: int = 1,
        key_name: Optional[str] = None,
        security_group_ids: Optional[List[str]] = None,
        subnet_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[EC2Instance]:
        """
        Launch one or more EC2 instances

        Args:
            image_id: AMI ID
            instance_type: Instance type (e.g., t3.micro)
            min_count: Minimum number of instances
            max_count: Maximum number of instances
            key_name: Key pair name
            security_group_ids: Security group IDs
            subnet_id: Subnet ID
            tags: Instance tags

        Returns:
            List of EC2Instance objects
        """
        body: Dict[str, Any] = {
            "Action": "RunInstances",
            "ImageId": image_id,
            "InstanceType": instance_type,
            "MinCount": min_count,
            "MaxCount": max_count,
            "Tags": tags or {},
        }
        if key_name:
            body["KeyName"] = key_name
        if security_group_ids:
            body["SecurityGroupIds"] = security_group_ids
        if subnet_id:
            body["SubnetId"] = subnet_id

        response = self.client.post("/ec2/", json=body)
        return [
            EC2Instance(
                instance_id=inst["InstanceId"],
                instance_type=inst["InstanceType"],
                state=inst.get("State", {}).get("Name", inst.get("State", "pending")),
                image_id=inst.get("ImageId"),
                public_ip=inst.get("PublicIpAddress"),
                private_ip=inst.get("PrivateIpAddress"),
                tags=inst.get("Tags"),
            )
            for inst in response.get("Instances", [])
        ]

    def describe_instances(
        self,
        instance_ids: Optional[List[str]] = None,
    ) -> List[EC2Instance]:
        """Describe EC2 instances"""
        body: Dict[str, Any] = {"Action": "DescribeInstances"}
        if instance_ids:
            body["InstanceIds"] = instance_ids
        response = self.client.post("/ec2/", json=body)
        instances = []
        for reservation in response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                instances.append(EC2Instance(
                    instance_id=inst["InstanceId"],
                    instance_type=inst["InstanceType"],
                    state=inst.get("State", {}).get("Name", inst.get("State", "")),
                    image_id=inst.get("ImageId"),
                    public_ip=inst.get("PublicIpAddress"),
                    private_ip=inst.get("PrivateIpAddress"),
                    tags=inst.get("Tags"),
                ))
        return instances

    def start_instances(self, instance_ids: List[str]) -> List[Dict[str, Any]]:
        """Start stopped EC2 instances"""
        response = self.client.post("/ec2/", json={
            "Action": "StartInstances",
            "InstanceIds": instance_ids,
        })
        return response.get("StartingInstances", [])

    def stop_instances(
        self,
        instance_ids: List[str],
        force: bool = False,
    ) -> List[Dict[str, Any]]:
        """Stop running EC2 instances"""
        response = self.client.post("/ec2/", json={
            "Action": "StopInstances",
            "InstanceIds": instance_ids,
            "Force": force,
        })
        return response.get("StoppingInstances", [])

    def terminate_instances(self, instance_ids: List[str]) -> List[Dict[str, Any]]:
        """Terminate EC2 instances"""
        response = self.client.post("/ec2/", json={
            "Action": "TerminateInstances",
            "InstanceIds": instance_ids,
        })
        return response.get("TerminatingInstances", [])

    def describe_images(
        self,
        image_ids: Optional[List[str]] = None,
        owners: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Describe AMI images"""
        body: Dict[str, Any] = {"Action": "DescribeImages"}
        if image_ids:
            body["ImageIds"] = image_ids
        if owners:
            body["Owners"] = owners
        response = self.client.post("/ec2/", json=body)
        return response.get("Images", [])

    def describe_availability_zones(self) -> List[Dict[str, Any]]:
        """Describe availability zones"""
        response = self.client.post("/ec2/", json={"Action": "DescribeAvailabilityZones"})
        return response.get("AvailabilityZones", [])

    def describe_instance_types(
        self,
        instance_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Describe EC2 instance types"""
        body: Dict[str, Any] = {"Action": "DescribeInstanceTypes"}
        if instance_types:
            body["InstanceTypes"] = instance_types
        response = self.client.post("/ec2/", json=body)
        return response.get("InstanceTypes", [])


# ==============================================================================
# AWS STS
# ==============================================================================

@dataclass
class STSIdentity:
    """STS caller identity"""
    account: str
    arn: str
    user_id: str


@dataclass
class STSCredentials:
    """STS temporary credentials"""
    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: str


class STSResource:
    """STS resource client"""

    def __init__(self, client):
        self.client = client

    def get_caller_identity(self) -> STSIdentity:
        """
        Return details about the IAM user or role whose credentials are used

        Returns:
            STSIdentity object
        """
        response = self.client.post("/sts/", json={"Action": "GetCallerIdentity"})
        return STSIdentity(
            account=response["Account"],
            arn=response["Arn"],
            user_id=response["UserId"],
        )

    def assume_role(
        self,
        role_arn: str,
        role_session_name: str,
        duration_seconds: int = 3600,
        external_id: Optional[str] = None,
    ) -> STSCredentials:
        """
        Assume an IAM role and return temporary credentials

        Args:
            role_arn: ARN of the role to assume
            role_session_name: Session name identifier
            duration_seconds: Credential lifetime in seconds
            external_id: Optional external ID for cross-account trust

        Returns:
            STSCredentials object
        """
        body: Dict[str, Any] = {
            "Action": "AssumeRole",
            "RoleArn": role_arn,
            "RoleSessionName": role_session_name,
            "DurationSeconds": duration_seconds,
        }
        if external_id:
            body["ExternalId"] = external_id
        response = self.client.post("/sts/", json=body)
        creds = response.get("Credentials", response)
        return STSCredentials(
            access_key_id=creds["AccessKeyId"],
            secret_access_key=creds["SecretAccessKey"],
            session_token=creds["SessionToken"],
            expiration=creds["Expiration"],
        )

    def get_session_token(
        self,
        duration_seconds: int = 43200,
        serial_number: Optional[str] = None,
        token_code: Optional[str] = None,
    ) -> STSCredentials:
        """
        Return temporary credentials for the current IAM user

        Args:
            duration_seconds: Credential lifetime in seconds
            serial_number: MFA device serial number
            token_code: MFA token code

        Returns:
            STSCredentials object
        """
        body: Dict[str, Any] = {
            "Action": "GetSessionToken",
            "DurationSeconds": duration_seconds,
        }
        if serial_number:
            body["SerialNumber"] = serial_number
        if token_code:
            body["TokenCode"] = token_code
        response = self.client.post("/sts/", json=body)
        creds = response.get("Credentials", response)
        return STSCredentials(
            access_key_id=creds["AccessKeyId"],
            secret_access_key=creds["SecretAccessKey"],
            session_token=creds["SessionToken"],
            expiration=creds["Expiration"],
        )


# ==============================================================================
# AWS Route53
# ==============================================================================

@dataclass
class HostedZone:
    """Route53 hosted zone"""
    id: str
    name: str
    private_zone: bool
    record_count: Optional[int] = None
    comment: Optional[str] = None


class Route53Resource:
    """Route53 resource client"""

    def __init__(self, client):
        self.client = client

    def create_hosted_zone(
        self,
        name: str,
        private_zone: bool = False,
        comment: Optional[str] = None,
    ) -> HostedZone:
        """
        Create a hosted zone

        Args:
            name: Domain name (e.g., example.com)
            private_zone: Whether the zone is private
            comment: Optional comment

        Returns:
            HostedZone object
        """
        body: Dict[str, Any] = {
            "Action": "CreateHostedZone",
            "Name": name,
            "PrivateZone": private_zone,
        }
        if comment:
            body["Comment"] = comment
        response = self.client.post("/route53/", json=body)
        zone = response.get("HostedZone", response)
        return HostedZone(
            id=zone["Id"],
            name=zone["Name"],
            private_zone=zone.get("Config", {}).get("PrivateZone", private_zone),
            record_count=zone.get("ResourceRecordSetCount"),
            comment=zone.get("Config", {}).get("Comment"),
        )

    def list_hosted_zones(self) -> List[HostedZone]:
        """List all hosted zones"""
        response = self.client.post("/route53/", json={"Action": "ListHostedZones"})
        return [
            HostedZone(
                id=zone["Id"],
                name=zone["Name"],
                private_zone=zone.get("Config", {}).get("PrivateZone", False),
                record_count=zone.get("ResourceRecordSetCount"),
                comment=zone.get("Config", {}).get("Comment"),
            )
            for zone in response.get("HostedZones", [])
        ]

    def get_hosted_zone(self, zone_id: str) -> HostedZone:
        """Get a hosted zone by ID"""
        response = self.client.post("/route53/", json={
            "Action": "GetHostedZone",
            "Id": zone_id,
        })
        zone = response.get("HostedZone", response)
        return HostedZone(
            id=zone["Id"],
            name=zone["Name"],
            private_zone=zone.get("Config", {}).get("PrivateZone", False),
            record_count=zone.get("ResourceRecordSetCount"),
            comment=zone.get("Config", {}).get("Comment"),
        )

    def change_resource_record_sets(
        self,
        zone_id: str,
        changes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create, update, or delete DNS resource record sets

        Args:
            zone_id: Hosted zone ID
            changes: List of change dicts (Action, ResourceRecordSet)

        Returns:
            ChangeInfo dict
        """
        response = self.client.post("/route53/", json={
            "Action": "ChangeResourceRecordSets",
            "HostedZoneId": zone_id,
            "Changes": changes,
        })
        return response.get("ChangeInfo", response)

    def list_resource_record_sets(
        self,
        zone_id: str,
        start_record_name: Optional[str] = None,
        start_record_type: Optional[str] = None,
        max_items: int = 300,
    ) -> List[Dict[str, Any]]:
        """List DNS resource record sets in a hosted zone"""
        body: Dict[str, Any] = {
            "Action": "ListResourceRecordSets",
            "HostedZoneId": zone_id,
            "MaxItems": max_items,
        }
        if start_record_name:
            body["StartRecordName"] = start_record_name
        if start_record_type:
            body["StartRecordType"] = start_record_type
        response = self.client.post("/route53/", json=body)
        return response.get("ResourceRecordSets", [])

    def get_change(self, change_id: str) -> Dict[str, Any]:
        """Get the status of a change batch"""
        response = self.client.post("/route53/", json={
            "Action": "GetChange",
            "Id": change_id,
        })
        return response.get("ChangeInfo", response)


# ==============================================================================
# AWS SNS
# ==============================================================================

@dataclass
class SNSTopic:
    """SNS topic resource"""
    topic_arn: str
    name: Optional[str] = None


class SNSResource:
    """SNS resource client"""

    def __init__(self, client):
        self.client = client

    def create_topic(
        self,
        name: str,
        attributes: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> SNSTopic:
        """
        Create an SNS topic

        Args:
            name: Topic name
            attributes: Topic attributes
            tags: Topic tags

        Returns:
            SNSTopic object
        """
        response = self.client.post("/sns/", json={
            "Action": "CreateTopic",
            "Name": name,
            "Attributes": attributes or {},
            "Tags": tags or {},
        })
        return SNSTopic(
            topic_arn=response["TopicArn"],
            name=name,
        )

    def list_topics(self) -> List[SNSTopic]:
        """List all SNS topics"""
        response = self.client.post("/sns/", json={"Action": "ListTopics"})
        return [
            SNSTopic(topic_arn=t["TopicArn"])
            for t in response.get("Topics", [])
        ]

    def publish(
        self,
        topic_arn: str,
        message: str,
        subject: Optional[str] = None,
        message_attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Publish a message to an SNS topic

        Args:
            topic_arn: Topic ARN
            message: Message body
            subject: Optional subject
            message_attributes: Optional message attributes

        Returns:
            MessageId string
        """
        body: Dict[str, Any] = {
            "Action": "Publish",
            "TopicArn": topic_arn,
            "Message": message,
        }
        if subject:
            body["Subject"] = subject
        if message_attributes:
            body["MessageAttributes"] = message_attributes
        response = self.client.post("/sns/", json=body)
        return response["MessageId"]

    def subscribe(
        self,
        topic_arn: str,
        protocol: str,
        endpoint: str,
        attributes: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Subscribe an endpoint to an SNS topic

        Args:
            topic_arn: Topic ARN
            protocol: Protocol (http, https, email, sqs, lambda, etc.)
            endpoint: Endpoint URL or ARN
            attributes: Subscription attributes

        Returns:
            SubscriptionArn string
        """
        body: Dict[str, Any] = {
            "Action": "Subscribe",
            "TopicArn": topic_arn,
            "Protocol": protocol,
            "Endpoint": endpoint,
        }
        if attributes:
            body["Attributes"] = attributes
        response = self.client.post("/sns/", json=body)
        return response["SubscriptionArn"]


# ==============================================================================
# OCI (Oracle Cloud Infrastructure)
# ==============================================================================

@dataclass
class OCIInstance:
    """OCI compute instance"""
    id: str
    display_name: str
    lifecycle_state: str
    shape: Optional[str] = None
    compartment_id: Optional[str] = None
    availability_domain: Optional[str] = None


@dataclass
class OCIBucket:
    """OCI Object Storage bucket"""
    name: str
    namespace: str
    compartment_id: Optional[str] = None


@dataclass
class OCIVCN:
    """OCI Virtual Cloud Network"""
    id: str
    display_name: str
    cidr_block: str
    lifecycle_state: str
    compartment_id: Optional[str] = None


@dataclass
class OCIVolume:
    """OCI block volume"""
    id: str
    display_name: str
    lifecycle_state: str
    size_in_gbs: Optional[int] = None
    availability_domain: Optional[str] = None


class OCIResource:
    """OCI resource client"""

    def __init__(self, client):
        self.client = client

    # ---- Object Storage ----

    def namespace(self) -> str:
        """Get the Object Storage namespace"""
        response = self.client.get("/n")
        return response.get("value", response) if isinstance(response, dict) else response

    def list_buckets(self, namespace: str, compartment_id: str) -> List[OCIBucket]:
        """
        List buckets in a namespace

        Args:
            namespace: Object Storage namespace
            compartment_id: Compartment OCID

        Returns:
            List of OCIBucket objects
        """
        response = self.client.get(
            f"/n/{namespace}/b",
            params={"compartmentId": compartment_id},
        )
        return [
            OCIBucket(
                name=b["name"],
                namespace=namespace,
                compartment_id=b.get("compartmentId"),
            )
            for b in (response if isinstance(response, list) else response.get("items", []))
        ]

    def create_bucket(
        self,
        namespace: str,
        name: str,
        compartment_id: str,
        public_access_type: str = "NoPublicAccess",
    ) -> OCIBucket:
        """
        Create a bucket

        Args:
            namespace: Object Storage namespace
            name: Bucket name
            compartment_id: Compartment OCID
            public_access_type: Access type (NoPublicAccess, ObjectRead, ObjectReadWithoutList)

        Returns:
            OCIBucket object
        """
        response = self.client.post(f"/n/{namespace}/b", json={
            "name": name,
            "compartmentId": compartment_id,
            "publicAccessType": public_access_type,
        })
        return OCIBucket(
            name=response.get("name", name),
            namespace=namespace,
            compartment_id=response.get("compartmentId", compartment_id),
        )

    def delete_bucket(self, namespace: str, bucket: str) -> bool:
        """Delete a bucket"""
        self.client.delete(f"/n/{namespace}/b/{bucket}")
        return True

    def put_object(
        self,
        namespace: str,
        bucket: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """
        Upload an object to OCI Object Storage

        Args:
            namespace: Object Storage namespace
            bucket: Bucket name
            object_name: Object name/key
            data: Object data as bytes
            content_type: Content type

        Returns:
            True on success
        """
        import base64

        self.client.request(
            "PUT",
            f"/n/{namespace}/b/{bucket}/o/{object_name}",
            json={
                "data": base64.b64encode(data).decode(),
                "contentType": content_type,
            },
        )
        return True

    def get_object(self, namespace: str, bucket: str, object_name: str) -> bytes:
        """Download an object from OCI Object Storage"""
        import base64

        response = self.client.get(f"/n/{namespace}/b/{bucket}/o/{object_name}")
        encoded = response.get("data", "") if isinstance(response, dict) else response
        return base64.b64decode(encoded) if encoded else b""

    def delete_object(self, namespace: str, bucket: str, object_name: str) -> bool:
        """Delete an object from OCI Object Storage"""
        self.client.delete(f"/n/{namespace}/b/{bucket}/o/{object_name}")
        return True

    def list_objects(
        self,
        namespace: str,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """List objects in an OCI bucket"""
        params: Dict[str, Any] = {"limit": limit}
        if prefix:
            params["prefix"] = prefix
        response = self.client.get(f"/n/{namespace}/b/{bucket}/o", params=params)
        items = response if isinstance(response, list) else response.get("objects", [])
        return items

    # ---- Compute Instances ----

    def create_instance(
        self,
        compartment_id: str,
        availability_domain: str,
        shape: str,
        display_name: str,
        subnet_id: Optional[str] = None,
        image_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> OCIInstance:
        """
        Create an OCI compute instance

        Args:
            compartment_id: Compartment OCID
            availability_domain: Availability domain
            shape: Instance shape (e.g., VM.Standard2.1)
            display_name: Display name
            subnet_id: Optional subnet OCID
            image_id: Optional image OCID
            metadata: Optional instance metadata

        Returns:
            OCIInstance object
        """
        body: Dict[str, Any] = {
            "compartmentId": compartment_id,
            "availabilityDomain": availability_domain,
            "shape": shape,
            "displayName": display_name,
        }
        if subnet_id:
            body["createVnicDetails"] = {"subnetId": subnet_id}
        if image_id:
            body["sourceDetails"] = {"sourceType": "image", "imageId": image_id}
        if metadata:
            body["metadata"] = metadata

        response = self.client.post("/20160918/instances", json=body)
        return OCIInstance(
            id=response["id"],
            display_name=response.get("displayName", display_name),
            lifecycle_state=response.get("lifecycleState", "PROVISIONING"),
            shape=response.get("shape", shape),
            compartment_id=response.get("compartmentId", compartment_id),
            availability_domain=response.get("availabilityDomain", availability_domain),
        )

    def list_instances(
        self,
        compartment_id: str,
    ) -> List[OCIInstance]:
        """List OCI compute instances"""
        response = self.client.get(
            "/20160918/instances",
            params={"compartmentId": compartment_id},
        )
        items = response if isinstance(response, list) else response.get("items", [])
        return [
            OCIInstance(
                id=inst["id"],
                display_name=inst.get("displayName", ""),
                lifecycle_state=inst.get("lifecycleState", ""),
                shape=inst.get("shape"),
                compartment_id=inst.get("compartmentId"),
                availability_domain=inst.get("availabilityDomain"),
            )
            for inst in items
        ]

    def get_instance(self, instance_id: str) -> OCIInstance:
        """Get an OCI compute instance by ID"""
        response = self.client.get(f"/20160918/instances/{instance_id}")
        return OCIInstance(
            id=response["id"],
            display_name=response.get("displayName", ""),
            lifecycle_state=response.get("lifecycleState", ""),
            shape=response.get("shape"),
            compartment_id=response.get("compartmentId"),
            availability_domain=response.get("availabilityDomain"),
        )

    def stop_instance(self, instance_id: str) -> bool:
        """Stop an OCI compute instance"""
        self.client.post(f"/20160918/instances/{instance_id}/actions/stop", json={})
        return True

    def start_instance(self, instance_id: str) -> bool:
        """Start an OCI compute instance"""
        self.client.post(f"/20160918/instances/{instance_id}/actions/start", json={})
        return True

    def reset_instance(self, instance_id: str) -> bool:
        """Reset (hard reboot) an OCI compute instance"""
        self.client.post(f"/20160918/instances/{instance_id}/actions/reset", json={})
        return True

    def delete_instance(self, instance_id: str) -> bool:
        """Terminate an OCI compute instance"""
        self.client.delete(f"/20160918/instances/{instance_id}")
        return True

    # ---- Networking ----

    def create_vcn(
        self,
        compartment_id: str,
        cidr_block: str,
        display_name: str,
    ) -> OCIVCN:
        """
        Create an OCI Virtual Cloud Network

        Args:
            compartment_id: Compartment OCID
            cidr_block: CIDR block
            display_name: Display name

        Returns:
            OCIVCN object
        """
        response = self.client.post("/20160918/vcns", json={
            "compartmentId": compartment_id,
            "cidrBlock": cidr_block,
            "displayName": display_name,
        })
        return OCIVCN(
            id=response["id"],
            display_name=response.get("displayName", display_name),
            cidr_block=response.get("cidrBlock", cidr_block),
            lifecycle_state=response.get("lifecycleState", "PROVISIONING"),
            compartment_id=response.get("compartmentId", compartment_id),
        )

    def list_vcns(self, compartment_id: str) -> List[OCIVCN]:
        """List OCI Virtual Cloud Networks"""
        response = self.client.get(
            "/20160918/vcns",
            params={"compartmentId": compartment_id},
        )
        items = response if isinstance(response, list) else response.get("items", [])
        return [
            OCIVCN(
                id=vcn["id"],
                display_name=vcn.get("displayName", ""),
                cidr_block=vcn.get("cidrBlock", ""),
                lifecycle_state=vcn.get("lifecycleState", ""),
                compartment_id=vcn.get("compartmentId"),
            )
            for vcn in items
        ]

    def get_vcn(self, vcn_id: str) -> OCIVCN:
        """Get an OCI VCN by ID"""
        response = self.client.get(f"/20160918/vcns/{vcn_id}")
        return OCIVCN(
            id=response["id"],
            display_name=response.get("displayName", ""),
            cidr_block=response.get("cidrBlock", ""),
            lifecycle_state=response.get("lifecycleState", ""),
            compartment_id=response.get("compartmentId"),
        )

    def delete_vcn(self, vcn_id: str) -> bool:
        """Delete an OCI VCN"""
        self.client.delete(f"/20160918/vcns/{vcn_id}")
        return True

    def create_subnet(
        self,
        compartment_id: str,
        vcn_id: str,
        cidr_block: str,
        display_name: str,
        availability_domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an OCI subnet"""
        body: Dict[str, Any] = {
            "compartmentId": compartment_id,
            "vcnId": vcn_id,
            "cidrBlock": cidr_block,
            "displayName": display_name,
        }
        if availability_domain:
            body["availabilityDomain"] = availability_domain
        return self.client.post("/20160918/subnets", json=body)

    def list_subnets(self, compartment_id: str, vcn_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List OCI subnets"""
        params: Dict[str, Any] = {"compartmentId": compartment_id}
        if vcn_id:
            params["vcnId"] = vcn_id
        response = self.client.get("/20160918/subnets", params=params)
        return response if isinstance(response, list) else response.get("items", [])

    def create_internet_gateway(
        self,
        compartment_id: str,
        vcn_id: str,
        display_name: str,
        is_enabled: bool = True,
    ) -> Dict[str, Any]:
        """Create an OCI internet gateway"""
        return self.client.post("/20160918/internetGateways", json={
            "compartmentId": compartment_id,
            "vcnId": vcn_id,
            "displayName": display_name,
            "isEnabled": is_enabled,
        })

    def create_route_table(
        self,
        compartment_id: str,
        vcn_id: str,
        display_name: str,
        route_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create an OCI route table"""
        return self.client.post("/20160918/routeTables", json={
            "compartmentId": compartment_id,
            "vcnId": vcn_id,
            "displayName": display_name,
            "routeRules": route_rules or [],
        })

    def create_security_list(
        self,
        compartment_id: str,
        vcn_id: str,
        display_name: str,
        ingress_security_rules: Optional[List[Dict[str, Any]]] = None,
        egress_security_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create an OCI security list"""
        return self.client.post("/20160918/securityLists", json={
            "compartmentId": compartment_id,
            "vcnId": vcn_id,
            "displayName": display_name,
            "ingressSecurityRules": ingress_security_rules or [],
            "egressSecurityRules": egress_security_rules or [],
        })

    # ---- Identity ----

    def get_tenancy(self, tenancy_id: str) -> Dict[str, Any]:
        """Get tenancy details"""
        return self.client.get(f"/20160918/tenancy/{tenancy_id}")

    def create_compartment(
        self,
        compartment_id: str,
        name: str,
        description: str,
    ) -> Dict[str, Any]:
        """Create a compartment"""
        return self.client.post("/20160918/compartments", json={
            "compartmentId": compartment_id,
            "name": name,
            "description": description,
        })

    def list_compartments(self, compartment_id: str) -> List[Dict[str, Any]]:
        """List compartments"""
        response = self.client.get(
            "/20160918/compartments",
            params={"compartmentId": compartment_id},
        )
        return response if isinstance(response, list) else response.get("items", [])

    def create_user(
        self,
        compartment_id: str,
        name: str,
        description: str,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an OCI IAM user"""
        body: Dict[str, Any] = {
            "compartmentId": compartment_id,
            "name": name,
            "description": description,
        }
        if email:
            body["email"] = email
        return self.client.post("/20160918/users", json=body)

    def list_users(self, compartment_id: str) -> List[Dict[str, Any]]:
        """List OCI IAM users"""
        response = self.client.get(
            "/20160918/users",
            params={"compartmentId": compartment_id},
        )
        return response if isinstance(response, list) else response.get("items", [])

    def create_group(
        self,
        compartment_id: str,
        name: str,
        description: str,
    ) -> Dict[str, Any]:
        """Create an OCI IAM group"""
        return self.client.post("/20160918/groups", json={
            "compartmentId": compartment_id,
            "name": name,
            "description": description,
        })

    def create_policy(
        self,
        compartment_id: str,
        name: str,
        description: str,
        statements: List[str],
    ) -> Dict[str, Any]:
        """Create an OCI IAM policy"""
        return self.client.post("/20160918/policies", json={
            "compartmentId": compartment_id,
            "name": name,
            "description": description,
            "statements": statements,
        })

    # ---- Block Volumes ----

    def create_volume(
        self,
        compartment_id: str,
        availability_domain: str,
        display_name: str,
        size_in_gbs: int = 50,
    ) -> OCIVolume:
        """
        Create an OCI block volume

        Args:
            compartment_id: Compartment OCID
            availability_domain: Availability domain
            display_name: Display name
            size_in_gbs: Size in GB

        Returns:
            OCIVolume object
        """
        response = self.client.post("/20160918/volumes", json={
            "compartmentId": compartment_id,
            "availabilityDomain": availability_domain,
            "displayName": display_name,
            "sizeInGBs": size_in_gbs,
        })
        return OCIVolume(
            id=response["id"],
            display_name=response.get("displayName", display_name),
            lifecycle_state=response.get("lifecycleState", "PROVISIONING"),
            size_in_gbs=response.get("sizeInGBs", size_in_gbs),
            availability_domain=response.get("availabilityDomain", availability_domain),
        )

    def list_volumes(self, compartment_id: str) -> List[OCIVolume]:
        """List OCI block volumes"""
        response = self.client.get(
            "/20160918/volumes",
            params={"compartmentId": compartment_id},
        )
        items = response if isinstance(response, list) else response.get("items", [])
        return [
            OCIVolume(
                id=vol["id"],
                display_name=vol.get("displayName", ""),
                lifecycle_state=vol.get("lifecycleState", ""),
                size_in_gbs=vol.get("sizeInGBs"),
                availability_domain=vol.get("availabilityDomain"),
            )
            for vol in items
        ]

    def get_volume(self, volume_id: str) -> OCIVolume:
        """Get an OCI block volume by ID"""
        response = self.client.get(f"/20160918/volumes/{volume_id}")
        return OCIVolume(
            id=response["id"],
            display_name=response.get("displayName", ""),
            lifecycle_state=response.get("lifecycleState", ""),
            size_in_gbs=response.get("sizeInGBs"),
            availability_domain=response.get("availabilityDomain"),
        )

    def delete_volume(self, volume_id: str) -> bool:
        """Delete an OCI block volume"""
        self.client.delete(f"/20160918/volumes/{volume_id}")
        return True

    def attach_volume(
        self,
        instance_id: str,
        volume_id: str,
        attachment_type: str = "iscsi",
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Attach a volume to an instance"""
        body: Dict[str, Any] = {
            "instanceId": instance_id,
            "volumeId": volume_id,
            "type": attachment_type,
        }
        if display_name:
            body["displayName"] = display_name
        return self.client.post("/20160918/volumeAttachments", json=body)

    # ---- Container Registry ----

    def list_repositories(self, compartment_id: str) -> List[Dict[str, Any]]:
        """List OCI container repositories"""
        response = self.client.get(
            "/20180917/repositories",
            params={"compartmentId": compartment_id},
        )
        return response if isinstance(response, list) else response.get("items", [])

    def create_repository(
        self,
        compartment_id: str,
        display_name: str,
        is_public: bool = False,
    ) -> Dict[str, Any]:
        """Create an OCI container repository"""
        return self.client.post("/20180917/repositories", json={
            "compartmentId": compartment_id,
            "displayName": display_name,
            "isPublic": is_public,
        })

    def get_repository(self, repository_id: str) -> Dict[str, Any]:
        """Get an OCI container repository by ID"""
        return self.client.get(f"/20180917/repositories/{repository_id}")

    def delete_repository(self, repository_id: str) -> bool:
        """Delete an OCI container repository"""
        self.client.delete(f"/20180917/repositories/{repository_id}")
        return True


# ==============================================================================
# GCP Compute
# ==============================================================================

@dataclass
class GCPInstance:
    """GCP Compute Engine instance"""
    name: str
    zone: str
    status: str
    machine_type: Optional[str] = None
    network_interfaces: Optional[List[Dict[str, Any]]] = None
    disks: Optional[List[Dict[str, Any]]] = None


@dataclass
class GCPNetwork:
    """GCP VPC network"""
    name: str
    self_link: Optional[str] = None
    auto_create_subnetworks: Optional[bool] = None


@dataclass
class GCPDisk:
    """GCP persistent disk"""
    name: str
    zone: str
    status: str
    size_gb: Optional[int] = None
    disk_type: Optional[str] = None


class GCPComputeResource:
    """GCP Compute Engine resource client"""

    def __init__(self, client):
        self.client = client

    def list_zones(self, project: str) -> List[Dict[str, Any]]:
        """
        List all zones for a GCP project

        Args:
            project: GCP project ID

        Returns:
            List of zone dicts
        """
        response = self.client.get(f"/gcp/compute/v1/projects/{project}/zones")
        return response.get("items", [])

    def list_machine_types(self, project: str, zone: str) -> List[Dict[str, Any]]:
        """List machine types available in a zone"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/machineTypes"
        )
        return response.get("items", [])

    def list_images(self, project: str) -> List[Dict[str, Any]]:
        """List images available in a project"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/global/images"
        )
        return response.get("items", [])

    def create_instance(
        self,
        project: str,
        zone: str,
        name: str,
        machine_type: str,
        network_interfaces: Optional[List[Dict[str, Any]]] = None,
        disks: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> GCPInstance:
        """
        Create a GCP Compute Engine instance

        Args:
            project: GCP project ID
            zone: Zone (e.g., us-central1-a)
            name: Instance name
            machine_type: Machine type (e.g., n1-standard-1)
            network_interfaces: Network interface configs
            disks: Disk configs
            metadata: Instance metadata
            tags: Network tags

        Returns:
            GCPInstance object
        """
        body: Dict[str, Any] = {
            "name": name,
            "machineType": f"zones/{zone}/machineTypes/{machine_type}",
            "networkInterfaces": network_interfaces or [{"network": "global/networks/default"}],
            "disks": disks or [],
        }
        if metadata:
            body["metadata"] = metadata
        if tags:
            body["tags"] = {"items": tags}

        response = self.client.post(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances",
            json=body,
        )
        return GCPInstance(
            name=response.get("name", name),
            zone=zone,
            status=response.get("status", "PROVISIONING"),
            machine_type=machine_type,
            network_interfaces=response.get("networkInterfaces"),
            disks=response.get("disks"),
        )

    def list_instances(self, project: str, zone: str) -> List[GCPInstance]:
        """List GCP Compute Engine instances in a zone"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances"
        )
        return [
            GCPInstance(
                name=inst["name"],
                zone=zone,
                status=inst.get("status", ""),
                machine_type=inst.get("machineType", ""),
                network_interfaces=inst.get("networkInterfaces"),
                disks=inst.get("disks"),
            )
            for inst in response.get("items", [])
        ]

    def list_all_instances(self, project: str) -> Dict[str, List[GCPInstance]]:
        """List all GCP Compute Engine instances aggregated across zones"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/aggregated/instances"
        )
        result: Dict[str, List[GCPInstance]] = {}
        for zone_key, zone_data in response.get("items", {}).items():
            zone_instances = zone_data.get("instances", [])
            zone_name = zone_key.replace("zones/", "")
            result[zone_name] = [
                GCPInstance(
                    name=inst["name"],
                    zone=zone_name,
                    status=inst.get("status", ""),
                    machine_type=inst.get("machineType", ""),
                    network_interfaces=inst.get("networkInterfaces"),
                    disks=inst.get("disks"),
                )
                for inst in zone_instances
            ]
        return result

    def get_instance(self, project: str, zone: str, instance: str) -> GCPInstance:
        """Get a GCP Compute Engine instance"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances/{instance}"
        )
        return GCPInstance(
            name=response["name"],
            zone=zone,
            status=response.get("status", ""),
            machine_type=response.get("machineType", ""),
            network_interfaces=response.get("networkInterfaces"),
            disks=response.get("disks"),
        )

    def start_instance(self, project: str, zone: str, instance: str) -> Dict[str, Any]:
        """Start a GCP Compute Engine instance"""
        return self.client.post(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/start",
            json={},
        )

    def stop_instance(self, project: str, zone: str, instance: str) -> Dict[str, Any]:
        """Stop a GCP Compute Engine instance"""
        return self.client.post(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/stop",
            json={},
        )

    def reset_instance(self, project: str, zone: str, instance: str) -> Dict[str, Any]:
        """Reset a GCP Compute Engine instance"""
        return self.client.post(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/reset",
            json={},
        )

    def delete_instance(self, project: str, zone: str, instance: str) -> bool:
        """Delete a GCP Compute Engine instance"""
        self.client.delete(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/instances/{instance}"
        )
        return True

    # ---- Networks ----

    def create_network(
        self,
        project: str,
        name: str,
        auto_create_subnetworks: bool = True,
        description: Optional[str] = None,
    ) -> GCPNetwork:
        """
        Create a GCP VPC network

        Args:
            project: GCP project ID
            name: Network name
            auto_create_subnetworks: Automatically create subnets
            description: Network description

        Returns:
            GCPNetwork object
        """
        body: Dict[str, Any] = {
            "name": name,
            "autoCreateSubnetworks": auto_create_subnetworks,
        }
        if description:
            body["description"] = description
        response = self.client.post(
            f"/gcp/compute/v1/projects/{project}/global/networks",
            json=body,
        )
        return GCPNetwork(
            name=response.get("name", name),
            self_link=response.get("selfLink"),
            auto_create_subnetworks=response.get("autoCreateSubnetworks", auto_create_subnetworks),
        )

    def list_networks(self, project: str) -> List[GCPNetwork]:
        """List GCP VPC networks"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/global/networks"
        )
        return [
            GCPNetwork(
                name=net["name"],
                self_link=net.get("selfLink"),
                auto_create_subnetworks=net.get("autoCreateSubnetworks"),
            )
            for net in response.get("items", [])
        ]

    def delete_network(self, project: str, network: str) -> bool:
        """Delete a GCP VPC network"""
        self.client.delete(
            f"/gcp/compute/v1/projects/{project}/global/networks/{network}"
        )
        return True

    def create_subnetwork(
        self,
        project: str,
        region: str,
        name: str,
        network: str,
        ip_cidr_range: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a GCP subnetwork"""
        body: Dict[str, Any] = {
            "name": name,
            "network": f"global/networks/{network}",
            "ipCidrRange": ip_cidr_range,
        }
        if description:
            body["description"] = description
        return self.client.post(
            f"/gcp/compute/v1/projects/{project}/regions/{region}/subnetworks",
            json=body,
        )

    def list_subnetworks(self, project: str, region: str) -> List[Dict[str, Any]]:
        """List GCP subnetworks in a region"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/regions/{region}/subnetworks"
        )
        return response.get("items", [])

    # ---- Firewalls ----

    def create_firewall(
        self,
        project: str,
        name: str,
        network: str,
        allowed: List[Dict[str, Any]],
        source_ranges: Optional[List[str]] = None,
        target_tags: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a GCP firewall rule

        Args:
            project: GCP project ID
            name: Firewall rule name
            network: Network name or self-link
            allowed: List of allowed protocols/ports (e.g., [{"IPProtocol": "tcp", "ports": ["80"]}])
            source_ranges: Source IP ranges (CIDR)
            target_tags: Target network tags
            description: Rule description

        Returns:
            Firewall rule dict
        """
        body: Dict[str, Any] = {
            "name": name,
            "network": f"global/networks/{network}",
            "allowed": allowed,
        }
        if source_ranges:
            body["sourceRanges"] = source_ranges
        if target_tags:
            body["targetTags"] = target_tags
        if description:
            body["description"] = description
        return self.client.post(
            f"/gcp/compute/v1/projects/{project}/global/firewalls",
            json=body,
        )

    def list_firewalls(self, project: str) -> List[Dict[str, Any]]:
        """List GCP firewall rules"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/global/firewalls"
        )
        return response.get("items", [])

    def update_firewall(
        self,
        project: str,
        firewall: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a GCP firewall rule"""
        return self.client.request(
            "PATCH",
            f"/gcp/compute/v1/projects/{project}/global/firewalls/{firewall}",
            json=updates,
        )

    def delete_firewall(self, project: str, firewall: str) -> bool:
        """Delete a GCP firewall rule"""
        self.client.delete(
            f"/gcp/compute/v1/projects/{project}/global/firewalls/{firewall}"
        )
        return True

    # ---- Disks ----

    def create_disk(
        self,
        project: str,
        zone: str,
        name: str,
        size_gb: int,
        disk_type: str = "pd-standard",
        source_image: Optional[str] = None,
    ) -> GCPDisk:
        """
        Create a GCP persistent disk

        Args:
            project: GCP project ID
            zone: Zone
            name: Disk name
            size_gb: Size in GB
            disk_type: Disk type (pd-standard, pd-ssd, pd-balanced)
            source_image: Optional source image

        Returns:
            GCPDisk object
        """
        body: Dict[str, Any] = {
            "name": name,
            "sizeGb": str(size_gb),
            "type": f"zones/{zone}/diskTypes/{disk_type}",
        }
        if source_image:
            body["sourceImage"] = source_image
        response = self.client.post(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/disks",
            json=body,
        )
        return GCPDisk(
            name=response.get("name", name),
            zone=zone,
            status=response.get("status", "CREATING"),
            size_gb=int(response.get("sizeGb", size_gb)),
            disk_type=disk_type,
        )

    def list_disks(self, project: str, zone: str) -> List[GCPDisk]:
        """List GCP persistent disks in a zone"""
        response = self.client.get(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/disks"
        )
        return [
            GCPDisk(
                name=disk["name"],
                zone=zone,
                status=disk.get("status", ""),
                size_gb=int(disk.get("sizeGb", 0)) if disk.get("sizeGb") else None,
                disk_type=disk.get("type", ""),
            )
            for disk in response.get("items", [])
        ]

    def delete_disk(self, project: str, zone: str, disk: str) -> bool:
        """Delete a GCP persistent disk"""
        self.client.delete(
            f"/gcp/compute/v1/projects/{project}/zones/{zone}/disks/{disk}"
        )
        return True


# ==============================================================================
# Azure
# ==============================================================================

@dataclass
class AzureResourceGroup:
    """Azure resource group"""
    name: str
    location: str
    subscription_id: str
    provisioning_state: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class AzureVirtualMachine:
    """Azure virtual machine"""
    name: str
    resource_group: str
    location: str
    subscription_id: str
    vm_size: Optional[str] = None
    provisioning_state: Optional[str] = None
    os_type: Optional[str] = None


@dataclass
class AzureDisk:
    """Azure managed disk"""
    name: str
    resource_group: str
    location: str
    subscription_id: str
    size_gb: Optional[int] = None
    sku: Optional[str] = None
    provisioning_state: Optional[str] = None


class AzureResource:
    """Azure resource client"""

    def __init__(self, client):
        self.client = client

    # ---- Resource Groups ----

    def create_resource_group(
        self,
        subscription_id: str,
        name: str,
        location: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> AzureResourceGroup:
        """
        Create an Azure resource group

        Args:
            subscription_id: Azure subscription ID
            name: Resource group name
            location: Azure region (e.g., eastus)
            tags: Optional tags

        Returns:
            AzureResourceGroup object
        """
        response = self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{name}",
            json={"location": location, "tags": tags or {}},
        )
        return AzureResourceGroup(
            name=response.get("name", name),
            location=response.get("location", location),
            subscription_id=subscription_id,
            provisioning_state=response.get("properties", {}).get("provisioningState"),
            tags=response.get("tags"),
        )

    def list_resource_groups(
        self,
        subscription_id: str,
    ) -> List[AzureResourceGroup]:
        """List Azure resource groups"""
        response = self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups"
        )
        return [
            AzureResourceGroup(
                name=rg["name"],
                location=rg.get("location", ""),
                subscription_id=subscription_id,
                provisioning_state=rg.get("properties", {}).get("provisioningState"),
                tags=rg.get("tags"),
            )
            for rg in response.get("value", [])
        ]

    # ---- Virtual Networks ----

    def create_vnet(
        self,
        subscription_id: str,
        resource_group: str,
        vnet_name: str,
        location: str,
        address_prefixes: List[str],
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create an Azure Virtual Network

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            vnet_name: Virtual network name
            location: Azure region
            address_prefixes: Address space CIDR blocks
            tags: Optional tags

        Returns:
            VNet resource dict
        """
        return self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/virtualNetworks/{vnet_name}",
            json={
                "location": location,
                "tags": tags or {},
                "properties": {
                    "addressSpace": {"addressPrefixes": address_prefixes}
                },
            },
        )

    def get_vnet(
        self,
        subscription_id: str,
        resource_group: str,
        vnet_name: str,
    ) -> Dict[str, Any]:
        """Get an Azure Virtual Network"""
        return self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/virtualNetworks/{vnet_name}"
        )

    def list_vnets(
        self,
        subscription_id: str,
        resource_group: str,
    ) -> List[Dict[str, Any]]:
        """List Azure Virtual Networks in a resource group"""
        response = self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/virtualNetworks"
        )
        return response.get("value", [])

    def delete_vnet(
        self,
        subscription_id: str,
        resource_group: str,
        vnet_name: str,
    ) -> bool:
        """Delete an Azure Virtual Network"""
        self.client.delete(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/virtualNetworks/{vnet_name}"
        )
        return True

    def create_subnet(
        self,
        subscription_id: str,
        resource_group: str,
        vnet_name: str,
        subnet_name: str,
        address_prefix: str,
    ) -> Dict[str, Any]:
        """Create an Azure subnet"""
        return self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}",
            json={"properties": {"addressPrefix": address_prefix}},
        )

    def get_subnet(
        self,
        subscription_id: str,
        resource_group: str,
        vnet_name: str,
        subnet_name: str,
    ) -> Dict[str, Any]:
        """Get an Azure subnet"""
        return self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}"
        )

    # ---- Network Security Groups ----

    def create_nsg(
        self,
        subscription_id: str,
        resource_group: str,
        nsg_name: str,
        location: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create an Azure Network Security Group"""
        return self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}",
            json={"location": location, "tags": tags or {}},
        )

    def get_nsg(
        self,
        subscription_id: str,
        resource_group: str,
        nsg_name: str,
    ) -> Dict[str, Any]:
        """Get an Azure Network Security Group"""
        return self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}"
        )

    def create_security_rule(
        self,
        subscription_id: str,
        resource_group: str,
        nsg_name: str,
        rule_name: str,
        priority: int,
        protocol: str,
        direction: str,
        access: str,
        source_address_prefix: str = "*",
        destination_address_prefix: str = "*",
        source_port_range: str = "*",
        destination_port_range: str = "*",
    ) -> Dict[str, Any]:
        """
        Create an Azure NSG security rule

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            nsg_name: NSG name
            rule_name: Rule name
            priority: Rule priority (100–4096)
            protocol: Protocol (Tcp, Udp, Icmp, *)
            direction: Inbound or Outbound
            access: Allow or Deny
            source_address_prefix: Source address prefix
            destination_address_prefix: Destination address prefix
            source_port_range: Source port range
            destination_port_range: Destination port range

        Returns:
            Security rule dict
        """
        return self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}"
            f"/securityRules/{rule_name}",
            json={
                "properties": {
                    "priority": priority,
                    "protocol": protocol,
                    "direction": direction,
                    "access": access,
                    "sourceAddressPrefix": source_address_prefix,
                    "destinationAddressPrefix": destination_address_prefix,
                    "sourcePortRange": source_port_range,
                    "destinationPortRange": destination_port_range,
                }
            },
        )

    # ---- Network Interfaces ----

    def create_nic(
        self,
        subscription_id: str,
        resource_group: str,
        nic_name: str,
        location: str,
        subnet_id: str,
        public_ip_id: Optional[str] = None,
        nsg_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create an Azure Network Interface"""
        ip_config: Dict[str, Any] = {
            "name": "ipconfig1",
            "properties": {"subnet": {"id": subnet_id}},
        }
        if public_ip_id:
            ip_config["properties"]["publicIPAddress"] = {"id": public_ip_id}

        body: Dict[str, Any] = {
            "location": location,
            "tags": tags or {},
            "properties": {
                "ipConfigurations": [ip_config],
            },
        }
        if nsg_id:
            body["properties"]["networkSecurityGroup"] = {"id": nsg_id}

        return self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/networkInterfaces/{nic_name}",
            json=body,
        )

    def get_nic(
        self,
        subscription_id: str,
        resource_group: str,
        nic_name: str,
    ) -> Dict[str, Any]:
        """Get an Azure Network Interface"""
        return self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/networkInterfaces/{nic_name}"
        )

    # ---- Public IP Addresses ----

    def create_public_ip(
        self,
        subscription_id: str,
        resource_group: str,
        pip_name: str,
        location: str,
        allocation_method: str = "Dynamic",
        sku: str = "Basic",
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create an Azure Public IP Address"""
        return self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/publicIPAddresses/{pip_name}",
            json={
                "location": location,
                "sku": {"name": sku},
                "tags": tags or {},
                "properties": {
                    "publicIPAllocationMethod": allocation_method,
                },
            },
        )

    def get_public_ip(
        self,
        subscription_id: str,
        resource_group: str,
        pip_name: str,
    ) -> Dict[str, Any]:
        """Get an Azure Public IP Address"""
        return self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Network/publicIPAddresses/{pip_name}"
        )

    # ---- Managed Disks ----

    def create_disk(
        self,
        subscription_id: str,
        resource_group: str,
        disk_name: str,
        location: str,
        size_gb: int,
        sku: str = "Standard_LRS",
        os_type: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> AzureDisk:
        """
        Create an Azure managed disk

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            disk_name: Disk name
            location: Azure region
            size_gb: Disk size in GB
            sku: Storage SKU (Standard_LRS, Premium_LRS, UltraSSD_LRS)
            os_type: Optional OS type (Windows, Linux)
            tags: Optional tags

        Returns:
            AzureDisk object
        """
        body: Dict[str, Any] = {
            "location": location,
            "sku": {"name": sku},
            "tags": tags or {},
            "properties": {"diskSizeGB": size_gb},
        }
        if os_type:
            body["properties"]["osType"] = os_type

        response = self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/disks/{disk_name}",
            json=body,
        )
        return AzureDisk(
            name=response.get("name", disk_name),
            resource_group=resource_group,
            location=response.get("location", location),
            subscription_id=subscription_id,
            size_gb=response.get("properties", {}).get("diskSizeGB", size_gb),
            sku=response.get("sku", {}).get("name", sku),
            provisioning_state=response.get("properties", {}).get("provisioningState"),
        )

    def get_disk(
        self,
        subscription_id: str,
        resource_group: str,
        disk_name: str,
    ) -> AzureDisk:
        """Get an Azure managed disk"""
        response = self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/disks/{disk_name}"
        )
        return AzureDisk(
            name=response.get("name", disk_name),
            resource_group=resource_group,
            location=response.get("location", ""),
            subscription_id=subscription_id,
            size_gb=response.get("properties", {}).get("diskSizeGB"),
            sku=response.get("sku", {}).get("name"),
            provisioning_state=response.get("properties", {}).get("provisioningState"),
        )

    def list_disks(
        self,
        subscription_id: str,
        resource_group: str,
    ) -> List[AzureDisk]:
        """List Azure managed disks in a resource group"""
        response = self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/disks"
        )
        return [
            AzureDisk(
                name=disk["name"],
                resource_group=resource_group,
                location=disk.get("location", ""),
                subscription_id=subscription_id,
                size_gb=disk.get("properties", {}).get("diskSizeGB"),
                sku=disk.get("sku", {}).get("name"),
                provisioning_state=disk.get("properties", {}).get("provisioningState"),
            )
            for disk in response.get("value", [])
        ]

    def delete_disk(
        self,
        subscription_id: str,
        resource_group: str,
        disk_name: str,
    ) -> bool:
        """Delete an Azure managed disk"""
        self.client.delete(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/disks/{disk_name}"
        )
        return True

    # ---- Virtual Machines ----

    def create_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
        location: str,
        vm_size: str,
        admin_username: str,
        nic_id: str,
        image_reference: Optional[Dict[str, str]] = None,
        os_disk_type: str = "Standard_LRS",
        admin_password: Optional[str] = None,
        ssh_public_key: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> AzureVirtualMachine:
        """
        Create an Azure Virtual Machine

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            vm_name: VM name
            location: Azure region
            vm_size: VM size (e.g., Standard_D2s_v3)
            admin_username: Admin username
            nic_id: Network interface resource ID
            image_reference: OS image reference dict
            os_disk_type: OS disk storage type
            admin_password: Admin password (Windows/Linux password auth)
            ssh_public_key: SSH public key (Linux)
            tags: Optional tags

        Returns:
            AzureVirtualMachine object
        """
        os_profile: Dict[str, Any] = {
            "computerName": vm_name,
            "adminUsername": admin_username,
        }
        if admin_password:
            os_profile["adminPassword"] = admin_password
        if ssh_public_key:
            os_profile["linuxConfiguration"] = {
                "disablePasswordAuthentication": True,
                "ssh": {
                    "publicKeys": [{
                        "path": f"/home/{admin_username}/.ssh/authorized_keys",
                        "keyData": ssh_public_key,
                    }]
                },
            }

        body: Dict[str, Any] = {
            "location": location,
            "tags": tags or {},
            "properties": {
                "hardwareProfile": {"vmSize": vm_size},
                "osProfile": os_profile,
                "storageProfile": {
                    "imageReference": image_reference or {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "18.04-LTS",
                        "version": "latest",
                    },
                    "osDisk": {
                        "createOption": "FromImage",
                        "managedDisk": {"storageAccountType": os_disk_type},
                    },
                },
                "networkProfile": {
                    "networkInterfaces": [{"id": nic_id}],
                },
            },
        }

        response = self.client.request(
            "PUT",
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}",
            json=body,
        )
        return AzureVirtualMachine(
            name=response.get("name", vm_name),
            resource_group=resource_group,
            location=response.get("location", location),
            subscription_id=subscription_id,
            vm_size=response.get("properties", {}).get("hardwareProfile", {}).get("vmSize", vm_size),
            provisioning_state=response.get("properties", {}).get("provisioningState"),
        )

    def get_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> AzureVirtualMachine:
        """Get an Azure Virtual Machine"""
        response = self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        )
        return AzureVirtualMachine(
            name=response.get("name", vm_name),
            resource_group=resource_group,
            location=response.get("location", ""),
            subscription_id=subscription_id,
            vm_size=response.get("properties", {}).get("hardwareProfile", {}).get("vmSize"),
            provisioning_state=response.get("properties", {}).get("provisioningState"),
        )

    def list_vms(
        self,
        subscription_id: str,
        resource_group: str,
    ) -> List[AzureVirtualMachine]:
        """List Azure Virtual Machines in a resource group"""
        response = self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines"
        )
        return [
            AzureVirtualMachine(
                name=vm["name"],
                resource_group=resource_group,
                location=vm.get("location", ""),
                subscription_id=subscription_id,
                vm_size=vm.get("properties", {}).get("hardwareProfile", {}).get("vmSize"),
                provisioning_state=vm.get("properties", {}).get("provisioningState"),
            )
            for vm in response.get("value", [])
        ]

    def start_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> bool:
        """Start an Azure Virtual Machine"""
        self.client.post(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}/start",
            json={},
        )
        return True

    def stop_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> bool:
        """Stop (power off) an Azure Virtual Machine"""
        self.client.post(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}/powerOff",
            json={},
        )
        return True

    def deallocate_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> bool:
        """Deallocate an Azure Virtual Machine"""
        self.client.post(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}/deallocate",
            json={},
        )
        return True

    def restart_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> bool:
        """Restart an Azure Virtual Machine"""
        self.client.post(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}/restart",
            json={},
        )
        return True

    def delete_vm(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> bool:
        """Delete an Azure Virtual Machine"""
        self.client.delete(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        )
        return True

    def get_vm_instance_view(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
    ) -> Dict[str, Any]:
        """Get the instance view of an Azure Virtual Machine"""
        return self.client.get(
            f"/azure/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}/instanceView"
        )


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
