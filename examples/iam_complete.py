"""
Example: Complete IAM (Identity and Access Management) Setup

This example demonstrates how to create and manage IAM users, groups, roles,
policies, and permissions using the MockLib Python SDK.
"""

from mocklib import MockFactory

# Initialize client with API key
mf = MockFactory(api_key="mf_...")

# ============================================================================
# ORGANIZATIONAL SETUP
# ============================================================================

# Create organization and cloud environment
org = mf.organization.create(name="acme-corp", plan="pro")
dev_cloud = mf.cloud.create(name="dev-cloud", provider="aws", organization="acme-corp")
prod_cloud = mf.cloud.create(name="prod-cloud", provider="aws", organization="acme-corp")

print("✓ Created organization and cloud environments")

# ============================================================================
# IAM USERS
# ============================================================================

# Create IAM users
john = mf.iam.create_user(
    username="john.smith",
    organization="acme-corp",
    cloud="dev-cloud"
)
print(f"\n✓ Created IAM user: {john.username}")
print(f"  ARN: {john.arn}")

alice = mf.iam.create_user(
    username="alice.johnson",
    path="/admins/",
    organization="acme-corp",
    cloud="prod-cloud"
)
print(f"✓ Created IAM user: {alice.username} at path {alice.path}")

# Create service account user
api_user = mf.iam.create_user(
    username="api-service",
    path="/service-accounts/",
    cloud="dev-cloud"
)
print(f"✓ Created service account: {api_user.username}")

# ============================================================================
# IAM GROUPS
# ============================================================================

# Create IAM groups
developers = mf.iam.create_group(
    group_name="developers",
    organization="acme-corp",
    cloud="dev-cloud",
    description="Development team members"
)
print(f"\n✓ Created IAM group: {developers.group_name}")

admins = mf.iam.create_group(
    group_name="admins",
    organization="acme-corp",
    cloud="prod-cloud",
    description="System administrators"
)
print(f"✓ Created IAM group: {admins.group_name}")

# Add users to groups
mf.iam.add_user_to_group(username="john.smith", group_name="developers")
mf.iam.add_user_to_group(username="alice.johnson", group_name="admins")
print("✓ Added users to groups")

# ============================================================================
# IAM POLICIES
# ============================================================================

# Create S3 read-only policy
s3_read_policy = mf.iam.create_policy(
    policy_name="s3-read-only",
    policy_document={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": "*"
            }
        ]
    },
    description="Read-only access to S3 buckets",
    organization="acme-corp"
)
print(f"\n✓ Created policy: {s3_read_policy.policy_name}")

# Create admin policy
admin_policy = mf.iam.create_policy(
    policy_name="admin-access",
    policy_document={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    },
    description="Full administrative access",
    organization="acme-corp",
    cloud="prod-cloud"
)
print(f"✓ Created policy: {admin_policy.policy_name}")

# Create DynamoDB write policy
dynamodb_write_policy = mf.iam.create_policy(
    policy_name="dynamodb-write",
    policy_document={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/*"
            }
        ]
    },
    description="Write access to DynamoDB tables",
    cloud="dev-cloud"
)
print(f"✓ Created policy: {dynamodb_write_policy.policy_name}")

# ============================================================================
# ATTACH POLICIES
# ============================================================================

# Attach policies to users
mf.iam.attach_user_policy(username="john.smith", policy_name="s3-read-only")
mf.iam.attach_user_policy(username="alice.johnson", policy_name="admin-access")
print("\n✓ Attached policies to users")

# Attach policies to groups
mf.iam.attach_group_policy(group_name="developers", policy_name="s3-read-only")
mf.iam.attach_group_policy(group_name="developers", policy_name="dynamodb-write")
mf.iam.attach_group_policy(group_name="admins", policy_name="admin-access")
print("✓ Attached policies to groups")

# ============================================================================
# IAM ROLES
# ============================================================================

# Create Lambda execution role
lambda_role = mf.iam.create_role(
    role_name="lambda-execution-role",
    trust_policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    },
    description="Execution role for Lambda functions",
    cloud="dev-cloud"
)
print(f"\n✓ Created IAM role: {lambda_role.role_name}")
print(f"  ARN: {lambda_role.arn}")

# Create EC2 instance role
ec2_role = mf.iam.create_role(
    role_name="ec2-instance-role",
    trust_policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    },
    description="Role for EC2 instances",
    cloud="prod-cloud"
)
print(f"✓ Created IAM role: {ec2_role.role_name}")

# Attach policies to roles
mf.iam.attach_role_policy(role_name="lambda-execution-role", policy_name="dynamodb-write")
mf.iam.attach_role_policy(role_name="ec2-instance-role", policy_name="s3-read-only")
print("✓ Attached policies to roles")

# ============================================================================
# ACCESS KEYS
# ============================================================================

# Create access key for programmatic access
access_key = mf.iam.create_access_key(
    username="api-service",
    description="API access key for service account"
)
print(f"\n✓ Created access key for {access_key.username}")
print(f"  Access Key ID: {access_key.access_key_id}")
print(f"  Secret Access Key: {access_key.secret_access_key}")
print(f"  Status: {access_key.status}")
print("  ⚠️  Save these credentials - the secret won't be shown again!")

# List access keys for a user (secrets are not returned)
keys = mf.iam.list_access_keys(username="api-service")
print(f"✓ User has {len(keys)} access key(s)")

# ============================================================================
# PERMISSION CHECKS
# ============================================================================

print("\n" + "="*60)
print("PERMISSION CHECKS")
print("="*60)

# Check if user has permission for specific actions
result = mf.iam.check_permission(
    username="john.smith",
    action="s3:GetObject",
    resource="my-bucket/data.txt",
    cloud="dev-cloud"
)
print(f"\nPermission check for john.smith:")
print(f"  Action: s3:GetObject")
print(f"  Resource: my-bucket/data.txt")
print(f"  Decision: {'✓ ALLOWED' if result.get('allowed') else '✗ DENIED'}")

result = mf.iam.check_permission(
    username="john.smith",
    action="ec2:RunInstances",
    resource="*",
    cloud="dev-cloud"
)
print(f"\nPermission check for john.smith:")
print(f"  Action: ec2:RunInstances")
print(f"  Resource: *")
print(f"  Decision: {'✓ ALLOWED' if result.get('allowed') else '✗ DENIED'}")

# ============================================================================
# POLICY SIMULATION
# ============================================================================

print("\n" + "="*60)
print("POLICY SIMULATION")
print("="*60)

# Simulate policy evaluation
sim_result = mf.iam.simulate_policy(
    policy_name="s3-read-only",
    action="s3:GetObject",
    resource="test-bucket/file.txt"
)
print(f"\nSimulation result for 's3-read-only' policy:")
print(f"  Action: s3:GetObject")
print(f"  Decision: {sim_result.get('decision', 'unknown').upper()}")

sim_result = mf.iam.simulate_policy(
    policy_name="s3-read-only",
    action="s3:PutObject",
    resource="test-bucket/file.txt"
)
print(f"\nSimulation result for 's3-read-only' policy:")
print(f"  Action: s3:PutObject")
print(f"  Decision: {sim_result.get('decision', 'unknown').upper()}")

# ============================================================================
# RESOURCE-BASED POLICIES
# ============================================================================

print("\n" + "="*60)
print("RESOURCE-BASED POLICIES")
print("="*60)

# Create a Lambda function
lambda_fn = mf.lambda_function.create(
    function_name="my-api-function",
    runtime="python3.9",
    memory_mb=256
)
print(f"\n✓ Created Lambda function: {lambda_fn.function_name}")

# Attach resource-based policy to allow API Gateway to invoke it
mf.iam.create_resource_policy(
    resource_type="lambda",
    resource_id="my-api-function",
    policy_document={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "apigateway.amazonaws.com"
                },
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:*:*:function:my-api-function"
            }
        ]
    }
)
print("✓ Attached resource-based policy to Lambda function")
print("  Allows: API Gateway to invoke the function")

# Get resource policy
policy_doc = mf.iam.get_resource_policy(
    resource_type="lambda",
    resource_id="my-api-function"
)
print(f"✓ Retrieved resource policy: {len(policy_doc.get('Statement', []))} statement(s)")

# ============================================================================
# COMPLETE SCENARIO: Cross-Cloud IAM Setup
# ============================================================================

print("\n" + "="*60)
print("CROSS-CLOUD IAM SETUP")
print("="*60)

def setup_cross_cloud_iam():
    """Set up IAM across multiple cloud environments"""

    # Create users in different clouds
    dev_user = mf.iam.create_user(
        username="dev.user",
        cloud="dev-cloud",
        organization="acme-corp"
    )

    prod_user = mf.iam.create_user(
        username="prod.user",
        cloud="prod-cloud",
        organization="acme-corp"
    )

    print(f"\n✓ Created cloud-specific users:")
    print(f"  Dev: {dev_user.username} (cloud: {dev_user.cloud})")
    print(f"  Prod: {prod_user.username} (cloud: {prod_user.cloud})")

    # Create cloud-specific policies
    dev_policy = mf.iam.create_policy(
        policy_name="dev-environment-access",
        policy_document={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["*"],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "aws:RequestedRegion": "us-east-1"
                        }
                    }
                }
            ]
        },
        cloud="dev-cloud"
    )

    prod_policy = mf.iam.create_policy(
        policy_name="prod-read-only",
        policy_document={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:Describe*",
                        "s3:Get*",
                        "s3:List*",
                        "dynamodb:GetItem",
                        "dynamodb:Query",
                        "dynamodb:Scan"
                    ],
                    "Resource": "*"
                }
            ]
        },
        cloud="prod-cloud"
    )

    print(f"\n✓ Created cloud-specific policies:")
    print(f"  {dev_policy.policy_name} (cloud: {dev_policy.cloud})")
    print(f"  {prod_policy.policy_name} (cloud: {prod_policy.cloud})")

    # Attach policies
    mf.iam.attach_user_policy(username="dev.user", policy_name="dev-environment-access")
    mf.iam.attach_user_policy(username="prod.user", policy_name="prod-read-only")

    print("\n✓ Attached cloud-specific policies to users")

    return dev_user, prod_user

dev_user, prod_user = setup_cross_cloud_iam()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*60)
print("IAM SETUP SUMMARY")
print("="*60)

# List all IAM users
users = mf.iam.list_users(organization="acme-corp")
print(f"\nIAM Users ({len(users)}):")
for user in users:
    print(f"  • {user.username} ({user.cloud or 'no cloud'})")

# List all policies
policies = mf.iam.list_policies(organization="acme-corp")
print(f"\nIAM Policies ({len(policies)}):")
for policy in policies:
    print(f"  • {policy.policy_name}")
    if policy.attached_to:
        print(f"    Attached to: {', '.join(policy.attached_to)}")

print("\n✅ Complete IAM setup finished!")
print("\nKey Features Demonstrated:")
print("  • IAM Users, Groups, and Roles")
print("  • IAM Policies with JSON policy documents")
print("  • Policy attachments to users, groups, and roles")
print("  • Access keys for programmatic access")
print("  • Permission checks and policy simulation")
print("  • Resource-based policies")
print("  • Cross-cloud IAM setup")
print("  • Organization-wide IAM management")
