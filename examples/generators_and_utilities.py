"""
Example: Data Generators and Utility Helpers

This example demonstrates how to use the MockFactory data generators and
utility helpers for creating realistic test data and performing common
transformations.
"""

from mocklib import MockFactory

# Initialize client with API key
mf = MockFactory(api_key="mf_...")

# ============================================================================
# DATA GENERATORS
# ============================================================================

print("=" * 60)
print("DATA GENERATORS")
print("=" * 60)

# Generate realistic users
print("\n📝 Generating users...")
users = mf.generator.generate_users(
    count=10,
    role="mixed",
    organization="acme-corp",
    cloud="dev-cloud",
    domain="acme.com"
)
print(f"✓ Generated {len(users)} users")
for user in users[:3]:
    print(f"  • {user['username']}: {user['email']} ({user['role']})")

# Generate employees with departments
print("\n👥 Generating employees...")
employees = mf.generator.generate_employees(
    count=50,
    organization="acme-corp",
    departments=["engineering", "sales", "marketing", "hr"]
)
print(f"✓ Generated {len(employees)} employees")

# Count by department
dept_counts = {}
for emp in employees:
    dept = emp["department"]
    dept_counts[dept] = dept_counts.get(dept, 0) + 1

for dept, count in dept_counts.items():
    print(f"  • {dept.title()}: {count} employees")

# Generate organizations
print("\n🏢 Generating organizations...")
orgs = mf.generator.generate_organizations(count=5)
print(f"✓ Generated {len(orgs)} organizations")
for org in orgs:
    print(f"  • {org['name']}: {org['industry']} ({org.get('plan', 'free')} plan)")

# Generate network configuration
print("\n🌐 Generating network config...")
network = mf.generator.generate_network_config(
    cloud="prod-cloud",
    vpc_cidr="10.0.0.0/16",
    subnets=4
)
print(f"✓ Generated network configuration")
print(f"  VPC CIDR: {network.get('vpc', {}).get('cidr_block')}")
print(f"  Subnets: {len(network.get('subnets', []))}")
for subnet in network.get('subnets', [])[:3]:
    print(f"    - {subnet.get('name')}: {subnet.get('cidr')}")

# Generate IAM policies
print("\n🔐 Generating IAM policies...")
policies = mf.generator.generate_iam_policies(
    policy_type="common",
    services=["s3", "dynamodb", "lambda"]
)
print(f"✓ Generated {len(policies)} IAM policies")
for policy in policies:
    print(f"  • {policy['policy_name']}: {policy.get('description', 'No description')}")

# Generate complete test scenario
print("\n🎬 Generating test scenario...")
scenario = mf.generator.generate_test_scenario(scenario="startup")
print(f"✓ Generated 'startup' test scenario")
print(f"  Organization: {scenario.get('organization', {}).get('name')}")
print(f"  Employees: {scenario.get('employees', 0)}")
print(f"  Clouds: {len(scenario.get('clouds', []))}")
print(f"  Projects: {len(scenario.get('projects', []))}")
print(f"  IAM Users: {scenario.get('iam_users', 0)}")

# ============================================================================
# UTILITY HELPERS - Binary/Hex Conversion
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: Binary/Hex Conversion")
print("=" * 60)

# Binary to Hex
binary = "11010101"
hex_val = mf.utilities.bin2hex(binary)
print(f"\nBinary {binary} → Hex {hex_val}")

# Hex to Binary
hex_str = "ff"
bin_val = mf.utilities.hex2bin(hex_str)
print(f"Hex {hex_str} → Binary {bin_val}")

# ============================================================================
# UTILITY HELPERS - IP Address Conversion
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: IP Address Conversion")
print("=" * 60)

# IP to Binary
ip = "192.168.1.1"
ip_binary = mf.utilities.ip2bin(ip)
print(f"\nIP {ip} → Binary {ip_binary}")

# Binary to IP
bin_ip = "11000000101010000000000100000001"
ip_from_bin = mf.utilities.bin2ip(bin_ip)
print(f"Binary {bin_ip} → IP {ip_from_bin}")

# IP to Long
ip_long = mf.utilities.ip2long("192.168.1.1")
print(f"\nIP 192.168.1.1 → Long {ip_long}")

# Long to IP
ip_from_long = mf.utilities.long2ip(3232235777)
print(f"Long 3232235777 → IP {ip_from_long}")

# ============================================================================
# UTILITY HELPERS - CIDR Operations
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: CIDR Operations")
print("=" * 60)

# CIDR to Range
cidr = "10.0.0.0/24"
cidr_range = mf.utilities.cidr_to_range(cidr)
print(f"\nCIDR {cidr}:")
print(f"  Start IP: {cidr_range['start_ip']}")
print(f"  End IP: {cidr_range['end_ip']}")
print(f"  Total IPs: {cidr_range['total_ips']}")

# IP in CIDR
is_in_range = mf.utilities.ip_in_cidr("10.0.0.50", "10.0.0.0/24")
print(f"\nIs 10.0.0.50 in 10.0.0.0/24? {is_in_range}")

# CIDR Overlap
overlap = mf.utilities.cidr_overlap("10.0.0.0/24", "10.0.0.128/25")
print(f"Do 10.0.0.0/24 and 10.0.0.128/25 overlap? {overlap}")

# ============================================================================
# UTILITY HELPERS - IPv6
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: IPv6 Operations")
print("=" * 60)

# Expand IPv6
compressed = "2001:db8::1"
expanded = mf.utilities.expand_ipv6(compressed)
print(f"\nCompressed: {compressed}")
print(f"Expanded: {expanded}")

# Compress IPv6
full_ipv6 = "2001:0db8:0000:0000:0000:0000:0000:0001"
compressed_ipv6 = mf.utilities.compress_ipv6(full_ipv6)
print(f"\nFull: {full_ipv6}")
print(f"Compressed: {compressed_ipv6}")

# Validate IPv6
is_valid = mf.utilities.is_valid_ipv6("2001:db8::1")
print(f"\nIs '2001:db8::1' valid IPv6? {is_valid}")

# ============================================================================
# UTILITY HELPERS - Encoding/Decoding
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: Encoding/Decoding")
print("=" * 60)

# Base64 Encode
original = "Hello World"
encoded = mf.utilities.base64_encode(original)
print(f"\nOriginal: {original}")
print(f"Base64 Encoded: {encoded}")

# Base64 Decode
decoded = mf.utilities.base64_decode(encoded)
print(f"Base64 Decoded: {decoded}")

# URL Encode
url_text = "hello world & stuff"
url_encoded = mf.utilities.url_encode(url_text)
print(f"\nOriginal: {url_text}")
print(f"URL Encoded: {url_encoded}")

# URL Decode
url_decoded = mf.utilities.url_decode(url_encoded)
print(f"URL Decoded: {url_decoded}")

# ============================================================================
# UTILITY HELPERS - Hashing
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: Hashing")
print("=" * 60)

data = "Hello World"
print(f"\nData: {data}")
print(f"MD5: {mf.utilities.md5(data)}")
print(f"SHA1: {mf.utilities.sha1(data)}")
print(f"SHA256: {mf.utilities.sha256(data)}")
print(f"SHA512: {mf.utilities.sha512(data)[:64]}...")

# ============================================================================
# UTILITY HELPERS - UUIDs
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: UUIDs")
print("=" * 60)

# Generate UUID v4
uuid_v4 = mf.utilities.generate_uuid(version=4)
print(f"\nGenerated UUID v4: {uuid_v4}")

# Validate UUID
is_valid_uuid = mf.utilities.validate_uuid(uuid_v4)
print(f"Is valid UUID? {is_valid_uuid}")

# ============================================================================
# UTILITY HELPERS - Time Operations
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: Time Operations")
print("=" * 60)

# Get timestamp
unix_ts = mf.utilities.timestamp(format="unix")
print(f"\nUnix Timestamp: {unix_ts}")

iso_ts = mf.utilities.timestamp(format="iso8601")
print(f"ISO8601: {iso_ts}")

# Convert to ISO8601
iso_from_unix = mf.utilities.iso8601(1640995200)
print(f"\nUnix 1640995200 → ISO8601: {iso_from_unix}")

# Parse time
parsed = mf.utilities.parse_time("2022-01-01T00:00:00Z")
print(f"ISO8601 '2022-01-01T00:00:00Z' → Unix: {parsed}")

# Time ago
relative = mf.utilities.time_ago(1640995200)
print(f"1640995200 was: {relative}")

# ============================================================================
# UTILITY HELPERS - String Operations
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: String Operations")
print("=" * 60)

# Slugify
text = "Hello World & Stuff!"
slug = mf.utilities.slugify(text)
print(f"\nOriginal: {text}")
print(f"Slug: {slug}")

# Random string
random_str = mf.utilities.random_string(length=32, charset="hex")
print(f"\nRandom hex string (32 chars): {random_str}")

# Random password
password = mf.utilities.random_password(
    length=20,
    include_symbols=True,
    include_numbers=True,
    include_uppercase=True,
    include_lowercase=True
)
print(f"Random password (20 chars): {password}")

# ============================================================================
# UTILITY HELPERS - JSON/YAML
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: JSON/YAML Operations")
print("=" * 60)

# YAML to JSON
yaml_str = """
name: John Doe
age: 30
roles:
  - developer
  - admin
"""
json_obj = mf.utilities.yaml_to_json(yaml_str)
print(f"\nYAML → JSON:")
print(f"  Name: {json_obj.get('name')}")
print(f"  Age: {json_obj.get('age')}")
print(f"  Roles: {json_obj.get('roles')}")

# JSON to YAML
json_data = {"name": "Jane Doe", "role": "engineer", "active": True}
yaml_output = mf.utilities.json_to_yaml(json_data)
print(f"\nJSON → YAML:")
print(yaml_output)

# Validate JSON
json_str = '{"name": "John", "age": 30}'
validation = mf.utilities.validate_json(json_str)
print(f"\nJSON Validation: {validation}")

# Pretty print JSON
pretty = mf.utilities.pretty_json(json_str, indent=4)
print(f"\nPretty JSON:")
print(pretty)

# ============================================================================
# UTILITY HELPERS - AWS ARN Operations
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: AWS ARN Operations")
print("=" * 60)

# Parse ARN
arn = "arn:aws:iam::123456789:user/john.smith"
parsed_arn = mf.utilities.parse_arn(arn)
print(f"\nParsed ARN: {arn}")
print(f"  Partition: {parsed_arn['partition']}")
print(f"  Service: {parsed_arn['service']}")
print(f"  Account: {parsed_arn['account']}")
print(f"  Resource: {parsed_arn['resource']}")

# Build ARN
built_arn = mf.utilities.build_arn(
    service="s3",
    resource="bucket/my-bucket",
    region="us-east-1",
    account="123456789"
)
print(f"\nBuilt ARN: {built_arn}")

# Validate ARN
is_valid_arn = mf.utilities.validate_arn(arn)
print(f"Is valid ARN? {is_valid_arn}")

# ============================================================================
# UTILITY HELPERS - URL Operations
# ============================================================================

print("\n" + "=" * 60)
print("UTILITY HELPERS: URL Operations")
print("=" * 60)

# Parse URL
url = "https://api.example.com:8080/v1/users?page=1&limit=10#results"
parsed_url = mf.utilities.parse_url(url)
print(f"\nParsed URL: {url}")
print(f"  Scheme: {parsed_url['scheme']}")
print(f"  Host: {parsed_url['host']}")
print(f"  Port: {parsed_url.get('port')}")
print(f"  Path: {parsed_url['path']}")
print(f"  Query: {parsed_url.get('query')}")
print(f"  Fragment: {parsed_url.get('fragment')}")

# Build URL
built_url = mf.utilities.build_url(
    scheme="https",
    host="api.mockfactory.io",
    path="/v1/users",
    query={"page": "1", "limit": "20"},
    port=443
)
print(f"\nBuilt URL: {built_url}")

# ============================================================================
# COMPLETE WORKFLOW EXAMPLE
# ============================================================================

print("\n" + "=" * 60)
print("COMPLETE WORKFLOW: Generate & Apply Test Environment")
print("=" * 60)

print("\n🚀 Setting up complete test environment...")

# 1. Generate organization
print("\n1️⃣ Creating organization...")
orgs = mf.generator.generate_organizations(count=1)
org = orgs[0]
print(f"   ✓ Organization: {org['name']}")

# 2. Generate employees
print("\n2️⃣ Generating employees...")
employees = mf.generator.generate_employees(count=25, organization=org['name'])
print(f"   ✓ Generated {len(employees)} employees")

# 3. Generate network config
print("\n3️⃣ Creating network infrastructure...")
network = mf.generator.generate_network_config(
    cloud="prod-cloud",
    vpc_cidr="10.0.0.0/16",
    subnets=4
)
print(f"   ✓ VPC with {len(network.get('subnets', []))} subnets")

# 4. Generate IAM setup
print("\n4️⃣ Setting up IAM...")
iam_users = mf.generator.generate_users(
    count=20,
    role="mixed",
    organization=org['name'],
    domain=f"{org['name']}.com"
)
policies = mf.generator.generate_iam_policies(
    policy_type="common",
    services=["s3", "dynamodb", "lambda"]
)
print(f"   ✓ {len(iam_users)} IAM users")
print(f"   ✓ {len(policies)} IAM policies")

# 5. Generate UUIDs for resources
print("\n5️⃣ Generating resource identifiers...")
project_id = mf.utilities.generate_uuid()
vpc_id = mf.utilities.generate_uuid()
print(f"   ✓ Project ID: {project_id}")
print(f"   ✓ VPC ID: {vpc_id}")

print("\n✅ Test environment setup complete!")
print(f"   • Organization: {org['name']}")
print(f"   • Employees: {len(employees)}")
print(f"   • IAM Users: {len(iam_users)}")
print(f"   • IAM Policies: {len(policies)}")
print(f"   • Network Subnets: {len(network.get('subnets', []))}")
print(f"   • Resource IDs: {project_id}, {vpc_id}")

print("\n" + "=" * 60)
print("Example Complete!")
print("=" * 60)
