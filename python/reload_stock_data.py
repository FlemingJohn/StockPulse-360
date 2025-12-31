"""
StockPulse 360 - Reload Stock Data
Clears and reloads stock_raw table with updated data
"""

import sys
import os
import pandas as pd
from config import get_snowflake_session


def reload_stock_data():
    """
    Clear and reload stock_raw table with fresh data.
    """
    print("=" * 60)
    print("StockPulse 360 - Reloading Stock Data")
    print("=" * 60)
    
    try:
        # Create session
        print("\n🔌 Connecting to Snowflake...")
        session = get_snowflake_session()
        
        # Check if table exists
        print("\n🔍 Checking if RAW_STOCK table exists...")
        try:
            table_check = session.sql("""
                SELECT COUNT(*) as cnt 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'PUBLIC' 
                AND TABLE_NAME = 'RAW_STOCK'
            """).collect()
            
            if table_check[0]['CNT'] == 0:
                print("\n❌ ERROR: RAW_STOCK table does not exist!")
                print("\n📋 Please run the following SQL script first:")
                print("   sql/create_tables.sql")
                print("\nYou can run it using:")
                print("   1. Snowflake Web UI (Worksheets)")
                print("   2. VS Code Snowflake extension")
                print("   3. SnowSQL CLI")
                session.close()
                return
            
            print("✅ Table exists")
            
            # Get actual column names from the table
            print("\n🔍 Checking table structure...")
            try:
                table_desc = session.sql("DESC TABLE RAW_STOCK").collect()
                actual_columns = [row['name'] for row in table_desc]
                print(f"📋 Actual columns in RAW_STOCK: {actual_columns}")
            except Exception as e:
                print(f"⚠️  Could not get table structure: {e}")
                
        except Exception as e:
            print(f"⚠️  Could not verify table existence: {e}")
            print("   Attempting to proceed anyway...")
        
        # Get CSV path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        csv_path = os.path.join(project_dir, 'data', 'stock_data.csv')
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Read CSV
        print(f"\n📂 Reading {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} rows from CSV")
        
        # Check CSV format and map columns accordingly
        # Table expects: location, item, current_stock, issued_qty, received_qty, last_updated_date
        print("\n🔄 Mapping columns to match table structure...")
        
        if 'current_stock' in df.columns:
            # New format - already matches table structure
            print("✅ CSV already matches table structure")
            df_mapped = df[['location', 'item', 'current_stock', 'issued_qty', 'received_qty', 'last_updated_date']].copy()
            df_mapped['last_updated_date'] = pd.to_datetime(df_mapped['last_updated_date']).dt.date
        else:
            # Old format - needs mapping
            print("🔄 Converting from old CSV format...")
            df_mapped = pd.DataFrame({
                'location': df['location'],
                'item': df['item'],
                'current_stock': df['closing_stock'],
                'issued_qty': df['issued'],
                'received_qty': df['received'],
                'last_updated_date': pd.to_datetime(df['record_date']).dt.date
            })
        
        print(f"✅ Mapped {len(df_mapped)} rows")
        
        # Clear existing data
        print("\n🗑️  Clearing existing data from RAW_STOCK...")
        try:
            session.sql("TRUNCATE TABLE RAW_STOCK").collect()
            print("✅ Table cleared")
        except Exception as e:
            print(f"⚠️  Could not truncate table: {e}")
            print("   Table might be empty, continuing...")
        
        # Write to Snowflake using chunked inserts (to avoid PUT command errors)
        print(f"\n📤 Loading {len(df_mapped)} rows into RAW_STOCK using chunked inserts...")
        
        # Function to batch insert data
        def batch_insert(df, table_name, chunk_size=500):
            total_rows = len(df)
            for start in range(0, total_rows, chunk_size):
                end = min(start + chunk_size, total_rows)
                chunk = df.iloc[start:end]
                
                # Convert chunk to values list for SQL
                values_list = []
                for _, row in chunk.iterrows():
                    # Format last_updated_date carefully
                    date_val = row['last_updated_date']
                    date_str = date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val)
                    
                    # Escape single quotes for SQL safely
                    safe_location = str(row['location']).replace("'", "''")
                    safe_item = str(row['item']).replace("'", "''")
                    
                    val = f"('{safe_location}', '{safe_item}', {row['current_stock']}, {row['issued_qty']}, {row['received_qty']}, '{date_str}')"
                    values_list.append(val)
                
                sql = f'INSERT INTO {table_name} (location, item, current_stock, issued_qty, received_qty, last_updated_date) VALUES {", ".join(values_list)}'
                session.sql(sql).collect()
                print(f"   ✅ Processed {end}/{total_rows} rows...")

        batch_insert(df_mapped, 'RAW_STOCK')
        
        print("✅ Data loaded successfully using batch inserts")
        
        # Verify
        count = session.table("RAW_STOCK").count()
        print(f"\n📊 Total rows in RAW_STOCK: {count}")
        
        # Show sample data
        print("\n📋 Sample data:")
        sample = session.table("RAW_STOCK").limit(5).to_pandas()
        print(sample.to_string(index=False))
        
        # Refresh dynamic tables
        print("\n🔄 Refreshing dynamic tables...")
        try:
            session.sql("ALTER DYNAMIC TABLE stock_stats REFRESH").collect()
            print("✅ stock_stats refreshed")
        except Exception as e:
            print(f"⚠️  Note: {e}")
            print("   Dynamic tables will auto-refresh based on TARGET_LAG setting")
        
        # Close session
        session.close()
        print("\n✅ Data reload completed successfully!")
        print("\n💡 Tip: Dynamic tables will auto-refresh within 1 hour")
        print("   Check the dashboard to see updated alerts")
        
    except Exception as e:
        print(f"\n❌ Data reload failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    reload_stock_data()
