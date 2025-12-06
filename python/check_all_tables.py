"""Check all tables in the database"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import get_snowflake_session

session = get_snowflake_session()
print("\n📋 Checking all tables in database...\n")

# Get all tables
result = session.sql("SHOW TABLES").collect()

print("Available Tables:")
print("-" * 60)
for row in result:
    row_count = row['rows'] if 'rows' in row.asDict() else 'N/A'
    print(f"  - {row['name']} (rows: {row_count})")

# Check if STOCK_RAW exists
stock_raw_exists = any(row['name'] == 'STOCK_RAW' for row in result)
raw_stock_exists = any(row['name'] == 'RAW_STOCK' for row in result)

print("\n" + "=" * 60)
print(f"STOCK_RAW exists: {stock_raw_exists}")
print(f"RAW_STOCK exists: {raw_stock_exists}")
print("=" * 60)

session.close()
