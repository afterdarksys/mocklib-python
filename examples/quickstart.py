"""
MockLib Python SDK - Quick Start Example

Run:
    export MOCKFACTORY_API_KEY="mf_..."
    python examples/quickstart.py
"""

from mocklib import MockFactory

# Initialize client (reads MOCKFACTORY_API_KEY from environment)
mf = MockFactory()

print("MockLib Python SDK - Quick Start\n")

# Create VPC
print("Creating VPC...")
vpc = mf.vpc.create(
    cidr_block="10.0.0.0/16",
    tags={"Name": "demo-vpc", "Purpose": "testing"}
)
print(f"✓ Created VPC: {vpc.id}")
print(f"  CIDR: {vpc.cidr_block}")
print(f"  State: {vpc.state}\n")

# Create Lambda function
print("Creating Lambda function...")
lambda_fn = mf.lambda_function.create(
    function_name="demo-function",
    runtime="python3.9",
    memory_mb=256,
    timeout=30,
    environment_variables={
        "ENV": "testing",
        "DEBUG": "true"
    }
)
print(f"✓ Created Lambda: {lambda_fn.id}")
print(f"  Name: {lambda_fn.function_name}")
print(f"  Runtime: {lambda_fn.runtime}")
print(f"  Memory: {lambda_fn.memory_mb}MB\n")

# Create DynamoDB table
print("Creating DynamoDB table...")
table = mf.dynamodb.create_table(
    table_name="users",
    partition_key="user_id",
    partition_key_type="S",
    sort_key="created_at",
    sort_key_type="N",
)
print(f"✓ Created DynamoDB table: {table.id}")
print(f"  Name: {table.table_name}")
print(f"  Partition Key: {table.partition_key}\n")

# Create SQS queue
print("Creating SQS queue...")
queue = mf.sqs.create_queue(
    queue_name="background-jobs",
    visibility_timeout=30,
)
print(f"✓ Created SQS queue: {queue.id}")
print(f"  Name: {queue.queue_name}")
print(f"  URL: {queue.queue_url}\n")

# List all VPCs
print("Listing all VPCs...")
vpcs = mf.vpc.list()
print(f"✓ Found {len(vpcs)} VPC(s)")
for v in vpcs:
    print(f"  - {v.id}: {v.cidr_block} ({v.state})")

print("\n✅ Demo complete!")
print("💰 Estimated cost: ~$0.05 (metadata operations are cheap!)")
print("\nClean up:")
print(f"  mf.vpc.delete('{vpc.id}')")
print(f"  mf.lambda_function.delete('{lambda_fn.function_name}')")
