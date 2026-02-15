"""
Example: Using MockFactory hierarchical resources

This example demonstrates how to create and manage organizations, domains,
clouds, and projects using the MockLib Python SDK.
"""

from mocklib import MockFactory

# Initialize client with API key
mf = MockFactory(api_key="mf_...")

# ============================================================================
# ORGANIZATIONS
# ============================================================================

# Create an organization
org = mf.organization.create(
    name="acme-corp",
    plan="pro",
    description="Acme Corporation"
)
print(f"Created organization: {org.name} (ID: {org.org_id})")

# List all organizations
orgs = mf.organization.list()
for org in orgs:
    print(f"  - {org.name} ({org.plan})")

# Add users to organization
mf.organization.add_user("acme-corp", "john.doe", role="admin")
mf.organization.add_user("acme-corp", "jane.smith", role="member")

# ============================================================================
# DOMAINS
# ============================================================================

# Create a domain
domain = mf.domain.create(
    domain="example.com",
    organization="acme-corp",
    verified=False,
    dns_records=["A:1.2.3.4", "MX:mail.example.com"]
)
print(f"\nCreated domain: {domain.domain} (ID: {domain.domain_id})")

# Verify the domain
mf.domain.verify("example.com")
print("Domain verified!")

# List domains for organization
domains = mf.domain.list(organization="acme-corp")
for dom in domains:
    verified_status = "✓ Verified" if dom.verified else "✗ Not verified"
    print(f"  - {dom.domain} ({verified_status})")

# ============================================================================
# CLOUD ENVIRONMENTS
# ============================================================================

# Create cloud environments
dev_cloud = mf.cloud.create(
    name="dev-cloud",
    provider="aws",
    region="us-east-1",
    organization="acme-corp"
)
print(f"\nCreated cloud: {dev_cloud.name} (ID: {dev_cloud.cloud_id})")

prod_cloud = mf.cloud.create(
    name="prod-cloud",
    provider="aws",
    region="us-west-2",
    organization="acme-corp"
)
print(f"Created cloud: {prod_cloud.name} (ID: {prod_cloud.cloud_id})")

# List clouds for organization
clouds = mf.cloud.list(organization="acme-corp")
for cloud in clouds:
    print(f"  - {cloud.name} ({cloud.provider} - {cloud.region})")

# ============================================================================
# PROJECTS
# ============================================================================

# Create a project
project = mf.project.create(
    name="web-app",
    environment="production",
    organization="acme-corp",
    description="Main web application"
)
print(f"\nCreated project: {project.name} (ID: {project.project_id})")

# Create resources within the project
vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
print(f"Created VPC: {vpc.id}")

# Bind resources to project
mf.project.bind_resource(project.project_id, "vpc", vpc.id)
print(f"Bound VPC to project {project.name}")

# Create Lambda function and bind to project
lambda_fn = mf.lambda_function.create(
    function_name="api-handler",
    runtime="python3.9",
    memory_mb=256
)
mf.project.bind_resource(project.project_id, "lambda", lambda_fn.id)
print(f"Created and bound Lambda function: {lambda_fn.function_name}")

# ============================================================================
# COMPLETE EXAMPLE: Full hierarchical setup
# ============================================================================

def setup_complete_environment():
    """Set up a complete organizational environment"""

    # 1. Create organization
    org = mf.organization.create(
        name="startup-inc",
        plan="free",
        description="Startup Inc."
    )

    # 2. Create domain
    domain = mf.domain.create(
        domain="startup.io",
        organization="startup-inc",
        verified=True
    )

    # 3. Create cloud environments
    dev_cloud = mf.cloud.create(
        name="dev",
        provider="aws",
        region="us-east-1",
        organization="startup-inc"
    )

    staging_cloud = mf.cloud.create(
        name="staging",
        provider="aws",
        region="us-east-1",
        organization="startup-inc"
    )

    prod_cloud = mf.cloud.create(
        name="production",
        provider="aws",
        region="us-west-2",
        organization="startup-inc"
    )

    # 4. Create projects for each environment
    projects = {}
    for env_name, cloud_name in [
        ("development", "dev"),
        ("staging", "staging"),
        ("production", "production")
    ]:
        project = mf.project.create(
            name=f"api-{env_name}",
            environment=env_name,
            organization="startup-inc",
            description=f"API project for {env_name}"
        )
        projects[env_name] = project
        print(f"Created project: {project.name} ({project.project_id})")

    # 5. Create infrastructure in each project
    for env_name, project in projects.items():
        # Create VPC
        vpc = mf.vpc.create(cidr_block=f"10.{['development', 'staging', 'production'].index(env_name)}.0.0/16")
        mf.project.bind_resource(project.project_id, "vpc", vpc.id)

        # Create DynamoDB table
        table = mf.dynamodb.create_table(
            table_name=f"users-{env_name}",
            partition_key="user_id"
        )
        mf.project.bind_resource(project.project_id, "dynamodb", table.id)

        # Create SQS queue
        queue = mf.sqs.create_queue(
            queue_name=f"tasks-{env_name}"
        )
        mf.project.bind_resource(project.project_id, "sqs", queue.id)

        print(f"  Environment {env_name}: VPC, DynamoDB, SQS created and bound")

    print("\n✅ Complete environment setup finished!")
    print(f"Organization: {org.name}")
    print(f"Domain: {domain.domain}")
    print(f"Clouds: 3 (dev, staging, production)")
    print(f"Projects: {len(projects)}")

    return org, domain, projects


# Run the complete setup
print("\n" + "="*60)
print("COMPLETE ENVIRONMENT SETUP")
print("="*60 + "\n")

org, domain, projects = setup_complete_environment()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Organization ID: {org.org_id}")
print(f"Domain: {domain.domain}")
for env_name, project in projects.items():
    print(f"  Project ({env_name}): {project.project_id}")
