"""Quick script to check RAW_STOCK table structure"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import get_snowflake_session

session = get_snowflake_session()
print("\n🔍 Checking RAW_STOCK table structure...\n")

# Get table description
result = session.sql("DESC TABLE RAW_STOCK").collect()

print("Column Name | Type | Nullable")
print("-" * 50)
for row in result:
    print(f"{row['name']} | {row['type']} | {row['null?']}")

print("\n📋 Column names list:")
columns = [row['name'] for row in result]
print(columns)

session.close()
