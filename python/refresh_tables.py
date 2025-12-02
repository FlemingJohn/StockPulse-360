"""
Force Refresh Dynamic Tables and Verify Data
"""

from config import get_snowflake_session

def refresh_and_verify():
    """Force refresh dynamic tables and verify data."""
    
    print("🔄 Connecting to Snowflake...")
    session = get_snowflake_session()
    
    # Check raw data
    print("\n📊 Checking RAW_STOCK table...")
    raw_count = session.sql("SELECT COUNT(*) as count FROM raw_stock").collect()[0]['COUNT']
    print(f"   Rows in RAW_STOCK: {raw_count}")
    
    if raw_count == 0:
        print("❌ No data in RAW_STOCK! Please run load_sample_data.py first.")
        return
    
    # Show sample raw data
    print("\n📋 Sample RAW_STOCK data:")
    sample = session.sql("SELECT * FROM raw_stock LIMIT 5").collect()
    for row in sample:
        print(f"   {row}")
    
    # Force refresh dynamic tables
    print("\n🔄 Force refreshing STOCK_STATS...")
    try:
        session.sql("ALTER DYNAMIC TABLE stock_stats REFRESH").collect()
        print("   ✅ STOCK_STATS refreshed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔄 Force refreshing STOCK_HEALTH...")
    try:
        session.sql("ALTER DYNAMIC TABLE stock_health REFRESH").collect()
        print("   ✅ STOCK_HEALTH refreshed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔄 Force refreshing REORDER_RECOMMENDATIONS...")
    try:
        session.sql("ALTER DYNAMIC TABLE reorder_recommendations REFRESH").collect()
        print("   ✅ REORDER_RECOMMENDATIONS refreshed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Wait a moment for refresh
    import time
    print("\n⏳ Waiting 5 seconds for refresh to complete...")
    time.sleep(5)
    
    # Verify counts
    print("\n📊 Verifying dynamic tables...")
    
    stats_count = session.sql("SELECT COUNT(*) as count FROM stock_stats").collect()[0]['COUNT']
    print(f"   STOCK_STATS: {stats_count} rows")
    
    health_count = session.sql("SELECT COUNT(*) as count FROM stock_health").collect()[0]['COUNT']
    print(f"   STOCK_HEALTH: {health_count} rows")
    
    reorder_count = session.sql("SELECT COUNT(*) as count FROM reorder_recommendations").collect()[0]['COUNT']
    print(f"   REORDER_RECOMMENDATIONS: {reorder_count} rows")
    
    # Check views
    print("\n📊 Checking views...")
    
    risk_count = session.sql("SELECT COUNT(*) as count FROM stock_risk").collect()[0]['COUNT']
    print(f"   STOCK_RISK: {risk_count} rows")
    
    alerts_count = session.sql("SELECT COUNT(*) as count FROM critical_alerts").collect()[0]['COUNT']
    print(f"   CRITICAL_ALERTS: {alerts_count} rows")
    
    # If still 0, try querying the base table directly
    if stats_count == 0:
        print("\n⚠️  STOCK_STATS is still empty. Checking query...")
        print("\n🔍 Testing STOCK_STATS query directly:")
        try:
            test_query = """
            SELECT 
                location,
                item,
                COUNT(*) as record_count
            FROM raw_stock
            GROUP BY location, item
            LIMIT 5
            """
            result = session.sql(test_query).collect()
            print(f"   ✅ Query works! Sample results:")
            for row in result:
                print(f"      {row}")
            
            print("\n💡 The query works, but dynamic table isn't populating.")
            print("   This might be a TARGET_LAG issue. Let's check the table definition...")
            
            # Check dynamic table status
            dt_status = session.sql("""
                SELECT name, scheduling_state, target_lag, data_timestamp
                FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY())
                WHERE name = 'STOCK_STATS'
                ORDER BY data_timestamp DESC
                LIMIT 1
            """).collect()
            
            if dt_status:
                print(f"\n   Dynamic table status: {dt_status[0]}")
            
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    print("\n" + "="*60)
    if risk_count > 0:
        print("✅ SUCCESS! Data is ready for the dashboard!")
        print("🚀 Run: py -m streamlit run streamlit/app.py")
    else:
        print("⚠️  Dynamic tables are not populating.")
        print("💡 Possible solutions:")
        print("   1. Wait a few minutes for auto-refresh (based on TARGET_LAG)")
        print("   2. Check if warehouse is running")
        print("   3. Manually create regular tables instead of dynamic tables")
    
    session.close()

if __name__ == "__main__":
    refresh_and_verify()
