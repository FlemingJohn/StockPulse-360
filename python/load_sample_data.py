"""
Sample Data Loader for StockPulse 360
Loads sample stock data into Snowflake for testing
"""

from config import get_snowflake_session
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample stock data for testing."""
    
    # Sample data
    locations = ['Hospital A', 'Hospital B', 'Clinic C', 'Warehouse D', 'Pharmacy E']
    items = [
        'Paracetamol', 'Insulin', 'Bandages', 'Syringes', 'Gloves',
        'Masks', 'Sanitizer', 'Antibiotics', 'Thermometers', 'Blood Pressure Monitor'
    ]
    
    data = []
    base_date = datetime.now() - timedelta(days=30)
    
    # Generate 30 days of data
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        
        for location in locations:
            for item in items:
                # Random stock levels
                current_stock = random.randint(50, 1000)
                issued_qty = random.randint(10, 100)
                received_qty = random.randint(0, 200) if day % 7 == 0 else 0  # Receive weekly
                
                data.append({
                    'location': location,
                    'item': item,
                    'current_stock': current_stock,
                    'issued_qty': issued_qty,
                    'received_qty': received_qty,
                    'last_updated_date': current_date.date()
                })
    
    return pd.DataFrame(data)

def load_data_to_snowflake():
    """Load sample data into Snowflake."""
    
    print("🔄 Generating sample data...")
    df = generate_sample_data()
    print(f"✅ Generated {len(df)} rows of sample data")
    
    print("\n🔄 Connecting to Snowflake...")
    session = get_snowflake_session()
    
    print("🔄 Loading data into RAW_STOCK table...")
    
    # Convert pandas DataFrame to Snowpark DataFrame and write to table
    snowpark_df = session.create_dataframe(df)
    
    # Write to table (append mode)
    snowpark_df.write.mode("append").save_as_table("raw_stock")
    
    print("✅ Data loaded successfully!")
    
    # Verify
    count = session.sql("SELECT COUNT(*) as count FROM raw_stock").collect()[0]['COUNT']
    print(f"\n📊 Total rows in RAW_STOCK: {count}")
    
    # Check dynamic tables
    print("\n🔄 Checking dynamic tables...")
    
    # Refresh dynamic tables manually (they auto-refresh but this is immediate)
    try:
        session.sql("ALTER DYNAMIC TABLE stock_stats REFRESH").collect()
        session.sql("ALTER DYNAMIC TABLE stock_health REFRESH").collect()
        session.sql("ALTER DYNAMIC TABLE reorder_recommendations REFRESH").collect()
        print("✅ Dynamic tables refreshed")
    except Exception as e:
        print(f"⚠️  Dynamic table refresh: {e}")
        print("   (Tables will auto-refresh based on their lag settings)")
    
    # Check stock_risk view
    risk_count = session.sql("SELECT COUNT(*) as count FROM stock_risk").collect()[0]['COUNT']
    print(f"📊 Rows in STOCK_RISK view: {risk_count}")
    
    print("\n✅ Sample data loaded successfully!")
    print("🚀 You can now run the Streamlit dashboard!")
    
    session.close()

if __name__ == "__main__":
    load_data_to_snowflake()
