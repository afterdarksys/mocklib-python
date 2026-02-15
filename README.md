# MockLib - Python SDK

Python client library for MockFactory - multi-language cloud emulation platform.

## Installation

```bash
pip install mocklib
```

## Quick Start

```python
from mocklib import MockFactory

# Initialize client
mf = MockFactory(api_key="mf_...")

# Create a VPC
vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
print(f"Created VPC: {vpc.id}")

# Create a Lambda function
lambda_fn = mf.lambda_function.create(
    function_name="my-api",
    runtime="python3.9",
    memory_mb=256
)
print(f"Created Lambda: {lambda_fn.function_name}")

# Create a DynamoDB table
table = mf.dynamodb.create_table(
    table_name="users",
    partition_key="user_id"
)
print(f"Created table: {table.table_name}")
```

## Features

- **Cloud Resources**: VPC, Lambda, DynamoDB, SQS, S3
- **Multi-Provider**: AWS, GCP, Azure emulation
- **Hierarchical Organization**: Organizations, domains, clouds, projects
- **Resource Grouping**: UUID-based project IDs
- **Type Safety**: Full type hints and dataclasses

## Hierarchical Resources (NEW)

MockLib now supports complete organizational hierarchy:

### Organizations

```python
# Create an organization
org = mf.organization.create(
    name="acme-corp",
    plan="pro",
    description="Acme Corporation"
)

# Add users to organization
mf.organization.add_user("acme-corp", "john.doe", role="admin")
```

### Domains

```python
# Create a domain
domain = mf.domain.create(
    domain="example.com",
    organization="acme-corp",
    verified=True,
    dns_records=["A:1.2.3.4", "MX:mail.example.com"]
)

# Verify domain
mf.domain.verify("example.com")
```

### Cloud Environments

```python
# Create cloud environments
dev_cloud = mf.cloud.create(
    name="dev-cloud",
    provider="aws",
    region="us-east-1",
    organization="acme-corp"
)

prod_cloud = mf.cloud.create(
    name="prod-cloud",
    provider="aws",
    region="us-west-2",
    organization="acme-corp"
)
```

### Projects

```python
# Create a project
project = mf.project.create(
    name="web-app",
    environment="production",
    organization="acme-corp"
)

# Create and bind resources
vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
mf.project.bind_resource(project.project_id, "vpc", vpc.id)

lambda_fn = mf.lambda_function.create(
    function_name="api-handler",
    runtime="python3.9"
)
mf.project.bind_resource(project.project_id, "lambda", lambda_fn.id)
```

## Organizational Hierarchy

```
Organization (acme-corp)
  ├── Domains (example.com, acme.io)
  ├── Cloud Environments (dev-cloud, prod-cloud)
  │   ├── VPCs
  │   ├── Lambda Functions
  │   ├── DynamoDB Tables
  │   └── Other Resources
  └── Projects (UUID-based)
      └── Grouped Resources
```

## Supported Resources

### Compute
- **VPC**: Virtual Private Cloud with CIDR blocks
- **Lambda**: Serverless function execution

### Storage
- **DynamoDB**: NoSQL database tables
- **S3/GCS/Azure**: Object storage buckets

### Messaging
- **SQS**: Message queuing

### Organizational
- **Organization**: Top-level organization with plans
- **Domain**: DNS domains with verification
- **Cloud**: Cloud environments (AWS/GCP/Azure)
- **Project**: UUID-based resource grouping

### IAM (Identity and Access Management)
- **IAM Users**: Create and manage IAM users
- **IAM Groups**: User groups with shared permissions
- **IAM Roles**: Service roles with trust policies
- **IAM Policies**: Fine-grained permission policies
- **Access Keys**: Programmatic access credentials
- **Permission Checks**: Validate user permissions
- **Policy Simulation**: Test policy evaluation
- **Resource-based Policies**: Attach policies to resources

### Data Generators
- **Users**: Generate realistic test users
- **Employees**: Generate employee data with departments
- **Organizations**: Generate company structures
- **Network Configs**: Generate VPC and subnet configurations
- **IAM Policies**: Generate common policy templates
- **Test Scenarios**: Generate complete test environments

### Utility Helpers
- **Binary/Hex**: bin2hex, hex2bin conversions
- **IP Operations**: ip2bin, bin2ip, ip2long, long2ip
- **IPv6**: Expand, compress, validate IPv6 addresses
- **CIDR**: Calculate ranges, check IP membership, detect overlaps
- **Encoding**: Base64, URL encoding/decoding
- **Hashing**: MD5, SHA1, SHA256, SHA512
- **UUIDs**: Generate and validate UUIDs
- **Time**: Timestamps, ISO8601, relative time
- **Strings**: Slugify, random strings, passwords
- **JSON/YAML**: Convert, validate, format
- **AWS ARNs**: Parse, build, validate ARNs
- **URLs**: Parse, build, encode/decode

## IAM (Identity and Access Management)

MockLib provides complete IAM functionality for access control and permissions:

```python
# Create IAM users
user = mf.iam.create_user(
    username="john.smith",
    organization="acme-corp",
    cloud="dev-cloud"
)

# Create IAM groups
group = mf.iam.create_group(
    group_name="developers",
    organization="acme-corp",
    description="Development team"
)

# Create IAM policies
policy = mf.iam.create_policy(
    policy_name="s3-read-only",
    policy_document={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": "*"
        }]
    }
)

# Attach policies
mf.iam.attach_user_policy(username="john.smith", policy_name="s3-read-only")
mf.iam.add_user_to_group(username="john.smith", group_name="developers")

# Create access keys
access_key = mf.iam.create_access_key(username="john.smith")
print(f"Access Key: {access_key.access_key_id}")
print(f"Secret: {access_key.secret_access_key}")

# Check permissions
result = mf.iam.check_permission(
    username="john.smith",
    action="s3:GetObject",
    resource="my-bucket/file.txt"
)
print(f"Allowed: {result['allowed']}")
```

## Data Generators

Generate realistic test data for your mock infrastructure:

```python
# Generate users
users = mf.generator.generate_users(
    count=50,
    role="mixed",
    organization="acme-corp",
    domain="acme.com"
)

# Generate employees
employees = mf.generator.generate_employees(
    count=100,
    organization="acme-corp",
    departments=["engineering", "sales", "hr"]
)

# Generate organizations
orgs = mf.generator.generate_organizations(count=10)

# Generate network configuration
network = mf.generator.generate_network_config(
    cloud="prod-cloud",
    vpc_cidr="10.0.0.0/16",
    subnets=4
)

# Generate IAM policies
policies = mf.generator.generate_iam_policies(
    policy_type="common",
    services=["s3", "dynamodb", "lambda"]
)

# Generate complete test scenario
scenario = mf.generator.generate_test_scenario("enterprise")
```

## Utility Helpers

Perform common transformations and operations:

```python
# Binary/Hex conversion
hex_val = mf.utilities.bin2hex("11010101")  # "d5"
binary = mf.utilities.hex2bin("d5")  # "11010101"

# IP address operations
binary_ip = mf.utilities.ip2bin("192.168.1.1")
ip = mf.utilities.bin2ip("11000000101010000000000100000001")
long_ip = mf.utilities.ip2long("192.168.1.1")  # 3232235777

# CIDR operations
range_info = mf.utilities.cidr_to_range("10.0.0.0/24")
in_range = mf.utilities.ip_in_cidr("10.0.0.50", "10.0.0.0/24")
overlap = mf.utilities.cidr_overlap("10.0.0.0/24", "10.0.0.128/25")

# IPv6 operations
expanded = mf.utilities.expand_ipv6("2001:db8::1")
compressed = mf.utilities.compress_ipv6("2001:0db8:0000:0000:0000:0000:0000:0001")

# Encoding/decoding
encoded = mf.utilities.base64_encode("Hello World")
decoded = mf.utilities.base64_decode(encoded)

# Hashing
md5_hash = mf.utilities.md5("Hello World")
sha256_hash = mf.utilities.sha256("Hello World")

# UUIDs
uuid = mf.utilities.generate_uuid(version=4)
is_valid = mf.utilities.validate_uuid(uuid)

# Time operations
unix_ts = mf.utilities.timestamp(format="unix")
iso_ts = mf.utilities.iso8601(unix_ts)
relative = mf.utilities.time_ago(unix_ts)

# String operations
slug = mf.utilities.slugify("Hello World & Stuff!")  # "hello-world-stuff"
random_str = mf.utilities.random_string(length=32, charset="hex")
password = mf.utilities.random_password(length=20, include_symbols=True)

# JSON/YAML operations
json_obj = mf.utilities.yaml_to_json(yaml_string)
yaml_str = mf.utilities.json_to_yaml(json_object)
validation = mf.utilities.validate_json(json_string)

# AWS ARN operations
parsed = mf.utilities.parse_arn("arn:aws:iam::123456789:user/john")
arn = mf.utilities.build_arn(service="s3", resource="bucket/my-bucket")
is_valid_arn = mf.utilities.validate_arn(arn)

# URL operations
parsed_url = mf.utilities.parse_url("https://api.example.com:8080/v1/users?page=1")
url = mf.utilities.build_url(scheme="https", host="api.example.com", path="/v1")
```

## Examples

See the [examples/](examples/) directory for complete examples:

- `hierarchical_resources.py` - Full organizational setup
- `iam_complete.py` - Complete IAM setup with policies and permissions
- `generators_and_utilities.py` - Data generation and utility helpers
- `basic_usage.py` - Simple cloud resources
- `storage.py` - Storage bucket operations
- `messaging.py` - SQS queues

## Authentication

Set your API key via environment variable:

```bash
export MOCKFACTORY_API_KEY="mf_..."
```

Or pass it directly:

```python
mf = MockFactory(api_key="mf_...")
```

Get your API key from [mockfactory.io/dashboard](https://mockfactory.io/dashboard)

## Use Cases

### Integration Testing
Test your cloud applications without AWS credentials or bills.

### CI/CD Pipelines
Run integration tests in GitHub Actions, GitLab CI, Jenkins.

### Multi-Tenant Testing
Create separate organizations and projects for each tenant.

### Environment Isolation
Isolate dev, staging, and production infrastructure.

### Local Development
Develop and test locally without cloud infrastructure.

## API Reference

### MockFactory Client

```python
mf = MockFactory(
    api_key="mf_...",
    api_url="https://api.mockfactory.io/v1",
    environment_id="optional-env-id"
)
```

### VPC Resource

```python
vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
vpcs = mf.vpc.list()
mf.vpc.delete(vpc.id)
```

### Lambda Resource

```python
fn = mf.lambda_function.create(
    function_name="my-function",
    runtime="python3.9",
    memory_mb=256,
    timeout=30
)
result = mf.lambda_function.invoke(function_name="my-function", payload={"key": "value"})
mf.lambda_function.delete(function_name="my-function")
```

### DynamoDB Resource

```python
table = mf.dynamodb.create_table(table_name="users", partition_key="user_id")
mf.dynamodb.put_item(table_name="users", item={"user_id": "123", "name": "John"})
item = mf.dynamodb.get_item(table_name="users", key={"user_id": "123"})
```

### Organization Resource

```python
org = mf.organization.create(name="acme", plan="pro")
orgs = mf.organization.list(plan="pro")
org = mf.organization.get("acme")
mf.organization.add_user("acme", "john.doe", role="admin")
mf.organization.remove_user("acme", "john.doe")
mf.organization.delete("acme")
```

### Domain Resource

```python
domain = mf.domain.create(domain="example.com", organization="acme", verified=True)
domains = mf.domain.list(organization="acme", verified=True)
domain = mf.domain.get("example.com")
mf.domain.verify("example.com")
mf.domain.delete("example.com")
```

### Cloud Resource

```python
cloud = mf.cloud.create(name="dev", provider="aws", region="us-east-1", organization="acme")
clouds = mf.cloud.list(provider="aws", organization="acme")
cloud = mf.cloud.get("dev")
mf.cloud.delete("dev")
```

### Project Resource

```python
project = mf.project.create(name="web-app", environment="production", organization="acme")
projects = mf.project.list(organization="acme", environment="production")
project = mf.project.get(project_id="550e8400-...")
mf.project.bind_resource(project_id="550e8400-...", resource_type="vpc", resource_id="vpc-123")
mf.project.unbind_resource(project_id="550e8400-...", resource_type="vpc", resource_id="vpc-123")
mf.project.delete(project_id="550e8400-...", delete_resources=True)
```

### IAM Resource

```python
# Users
user = mf.iam.create_user(username="john.smith", organization="acme", cloud="dev")
users = mf.iam.list_users(organization="acme")
user = mf.iam.get_user(username="john.smith")
mf.iam.delete_user(username="john.smith")

# Groups
group = mf.iam.create_group(group_name="developers", organization="acme")
mf.iam.add_user_to_group(username="john.smith", group_name="developers")
mf.iam.remove_user_from_group(username="john.smith", group_name="developers")

# Roles
role = mf.iam.create_role(role_name="lambda-execution", trust_policy={...}, cloud="dev")

# Policies
policy = mf.iam.create_policy(policy_name="s3-read", policy_document={...}, organization="acme")
policies = mf.iam.list_policies(organization="acme")
policy = mf.iam.get_policy(policy_name="s3-read")
mf.iam.delete_policy(policy_name="s3-read")

# Policy Attachments
mf.iam.attach_user_policy(username="john.smith", policy_name="s3-read")
mf.iam.attach_group_policy(group_name="developers", policy_name="s3-read")
mf.iam.attach_role_policy(role_name="lambda-execution", policy_name="s3-read")

# Access Keys
key = mf.iam.create_access_key(username="john.smith")
keys = mf.iam.list_access_keys(username="john.smith")
mf.iam.delete_access_key(username="john.smith", access_key_id="AKIA...")

# Permissions
result = mf.iam.check_permission(username="john", action="s3:GetObject", resource="bucket/key")
result = mf.iam.simulate_policy(policy_name="s3-read", action="s3:GetObject", resource="bucket")

# Resource-based Policies
mf.iam.create_resource_policy(resource_type="lambda", resource_id="my-func", policy_document={...})
policy_doc = mf.iam.get_resource_policy(resource_type="lambda", resource_id="my-func")
mf.iam.delete_resource_policy(resource_type="lambda", resource_id="my-func")
```

### Generator Resource

```python
# Generate users
users = mf.generator.generate_users(count=50, role="mixed", organization="acme", domain="acme.com")

# Generate employees
employees = mf.generator.generate_employees(count=100, organization="acme", departments=["eng", "sales"])

# Generate organizations
orgs = mf.generator.generate_organizations(count=10)

# Generate network config
network = mf.generator.generate_network_config(cloud="prod", vpc_cidr="10.0.0.0/16", subnets=4)

# Generate IAM policies
policies = mf.generator.generate_iam_policies(policy_type="common", services=["s3", "dynamodb"])

# Generate test scenario
scenario = mf.generator.generate_test_scenario(scenario="startup")  # or "enterprise", "multi-cloud", "dev-team"
```

### Utilities Resource

```python
# Binary/Hex
hex_val = mf.utilities.bin2hex("11010101")
binary = mf.utilities.hex2bin("d5")

# IP Operations
binary_ip = mf.utilities.ip2bin("192.168.1.1")
ip = mf.utilities.bin2ip("11000000101010000000000100000001")
long_ip = mf.utilities.ip2long("192.168.1.1")
ip_from_long = mf.utilities.long2ip(3232235777)

# IPv6
expanded = mf.utilities.expand_ipv6("2001:db8::1")
compressed = mf.utilities.compress_ipv6("2001:0db8:0000:0000:0000:0000:0000:0001")
is_valid = mf.utilities.is_valid_ipv6("2001:db8::1")

# CIDR
range_info = mf.utilities.cidr_to_range("10.0.0.0/24")
in_range = mf.utilities.ip_in_cidr("10.0.0.50", "10.0.0.0/24")
overlap = mf.utilities.cidr_overlap("10.0.0.0/24", "10.0.0.128/25")

# Encoding
encoded = mf.utilities.base64_encode("Hello")
decoded = mf.utilities.base64_decode("SGVsbG8=")
url_encoded = mf.utilities.url_encode("hello world")
url_decoded = mf.utilities.url_decode("hello%20world")

# Hashing
md5 = mf.utilities.md5("data")
sha1 = mf.utilities.sha1("data")
sha256 = mf.utilities.sha256("data")
sha512 = mf.utilities.sha512("data")

# UUIDs
uuid = mf.utilities.generate_uuid(version=4)
is_valid = mf.utilities.validate_uuid(uuid)

# Time
unix_ts = mf.utilities.timestamp(format="unix")
iso = mf.utilities.iso8601(unix_timestamp=1640995200)
parsed_ts = mf.utilities.parse_time("2022-01-01T00:00:00Z")
relative = mf.utilities.time_ago(1640995200)

# Strings
slug = mf.utilities.slugify("Hello World!")
random_str = mf.utilities.random_string(length=32, charset="hex")
password = mf.utilities.random_password(length=20, include_symbols=True)

# JSON/YAML
json_obj = mf.utilities.yaml_to_json(yaml_string)
yaml_str = mf.utilities.json_to_yaml(json_object)
is_valid = mf.utilities.validate_yaml(yaml_string)
is_valid = mf.utilities.validate_json(json_string)
minified = mf.utilities.minify_json(json_string)
pretty = mf.utilities.pretty_json(json_string, indent=2)

# ARNs
parsed = mf.utilities.parse_arn("arn:aws:iam::123456789:user/john")
arn = mf.utilities.build_arn(service="s3", resource="bucket/my-bucket", account="123456789")
is_valid = mf.utilities.validate_arn(arn)

# URLs
parsed_url = mf.utilities.parse_url("https://api.example.com:8080/v1/users?page=1")
url = mf.utilities.build_url(scheme="https", host="api.example.com", path="/v1", query={"page": "1"})
```

## Development

```bash
# Clone repository
git clone https://github.com/mockfactory/mocklib-python
cd mocklib-python

# Install in development mode
pip install -e .

# Run tests
pytest

# Type checking
mypy mocklib/
```

## License

MIT

## Links

- Website: [mockfactory.io](https://mockfactory.io)
- Documentation: [docs.mockfactory.io](https://docs.mockfactory.io)
- PyPI: [pypi.org/project/mocklib](https://pypi.org/project/mocklib)
- GitHub: [github.com/mockfactory/mocklib-python](https://github.com/mockfactory/mocklib-python)

## Support

- Email: support@mockfactory.io
- Issues: [github.com/mockfactory/mocklib-python/issues](https://github.com/mockfactory/mocklib-python/issues)
