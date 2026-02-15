# MockLib Python Examples

This directory contains examples demonstrating how to use the MockLib Python SDK.

## Examples

### Basic Cloud Resources

- **basic_usage.py** - Simple VPC, Lambda, and DynamoDB examples
- **storage.py** - S3/GCS/Azure storage bucket examples
- **messaging.py** - SQS queue examples

### Hierarchical Resources (NEW)

- **hierarchical_resources.py** - Complete guide to organizations, domains, clouds, and projects

## Hierarchical Organization Structure

MockLib now supports a complete organizational hierarchy:

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

### Quick Start: Organizations

```python
from mocklib import MockFactory

mf = MockFactory(api_key="mf_...")

# Create an organization
org = mf.organization.create(
    name="acme-corp",
    plan="pro",
    description="Acme Corporation"
)

# Add users to the organization
mf.organization.add_user("acme-corp", "john.doe", role="admin")
```

### Quick Start: Domains

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

### Quick Start: Cloud Environments

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

### Quick Start: Projects

```python
# Create a project with UUID-based ID
project = mf.project.create(
    name="web-app",
    environment="production",
    organization="acme-corp",
    description="Main web application"
)

# Create resources
vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
lambda_fn = mf.lambda_function.create(
    function_name="api-handler",
    runtime="python3.9"
)

# Bind resources to project
mf.project.bind_resource(project.project_id, "vpc", vpc.id)
mf.project.bind_resource(project.project_id, "lambda", lambda_fn.id)
```

## Running Examples

All examples require a MockFactory API key. Set it as an environment variable:

```bash
export MOCKFACTORY_API_KEY="mf_..."
```

Or pass it directly:

```python
mf = MockFactory(api_key="mf_...")
```

Then run any example:

```bash
python examples/hierarchical_resources.py
```

## API Documentation

For full API documentation, see:
- [MockFactory Documentation](https://mockfactory.io/docs)
- [Python SDK Reference](https://github.com/mockfactory/mocklib-python)

## Use Cases

### Multi-Tenant Testing
Create separate organizations, clouds, and projects for each tenant to test multi-tenant applications.

### Environment Isolation
Use cloud environments and projects to isolate dev, staging, and production infrastructure.

### Resource Organization
Group related resources (VPCs, Lambda functions, databases) under projects for better organization and cleanup.

### Team Collaboration
Add team members to organizations with different roles (admin, member) to test collaborative features.

## Support

For questions or issues:
- GitHub: [github.com/mockfactory/mocklib-python/issues](https://github.com/mockfactory/mocklib-python/issues)
- Email: support@mockfactory.io
