"""
StockPulse 360 - Data Loader Utility
Loads CSV data into Snowflake using Snowpark
Reference: https://docs.snowflake.com/en/developer-guide/snowpark/python/working-with-dataframes
"""

import sys
import os
import pandas as pd
from snowflake.snowpark import Session
from config import get_snowflake_session


class DataLoader:
    """
    Utility class to load CSV data into Snowflake tables.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def load_csv_to_snowflake(self, csv_path: str, table_name: str, overwrite: bool = False):
        """
        Load a CSV file into a Snowflake table.
        
        Args:
            csv_path: Path to CSV file
            table_name: Target Snowflake table name
            overwrite: If True, replace existing data; if False, append
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        print(f"📂 Loading {csv_path} into {table_name}...")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} rows from CSV")
        
        # Convert date columns if present
        if 'record_date' in df.columns:
            df['record_date'] = pd.to_datetime(df['record_date'])
        
        # Write to Snowflake
        try:
            self.session.write_pandas(
                df,
                table_name,
                auto_create_table=False,
                overwrite=overwrite
            )
            
            print(f"✅ Successfully loaded {len(df)} rows into {table_name}")
            
            # Verify
            count = self.session.table(table_name).count()
            print(f"📊 Total rows in {table_name}: {count}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def validate_data(self, table_name: str):
        """
        Validate data quality in the table.
        """
        print(f"\n🔍 Validating data in {table_name}...")
        
        # Check for nulls
        null_check = self.session.sql(f"""
            SELECT
                COUNT(*) as total_rows,
                SUM(CASE WHEN location IS NULL THEN 1 ELSE 0 END) as null_location,
                SUM(CASE WHEN item IS NULL THEN 1 ELSE 0 END) as null_item,
                SUM(CASE WHEN closing_stock IS NULL THEN 1 ELSE 0 END) as null_stock
            FROM {table_name}
        """).to_pandas()
        
        print("\n📊 Null Check:")
        print(null_check.to_string(index=False))
        
        # Check for negative values
        negative_check = self.session.sql(f"""
            SELECT
                COUNT(*) as negative_stock_count
            FROM {table_name}
            WHERE closing_stock < 0
        """).to_pandas()
        
        print("\n📊 Negative Stock Check:")
        print(negative_check.to_string(index=False))
        
        # Check date range
        date_range = self.session.sql(f"""
            SELECT
                MIN(record_date) as earliest_date,
                MAX(record_date) as latest_date,
                COUNT(DISTINCT record_date) as unique_dates
            FROM {table_name}
        """).to_pandas()
        
        print("\n📊 Date Range:")
        print(date_range.to_string(index=False))
        
        print("\n✅ Validation complete")


def load_sample_data():
    """
    Load the sample stock_data.csv into Snowflake.
    """
    print("=" * 60)
    print("StockPulse 360 - Data Loading Pipeline")
    print("=" * 60)
    
    try:
        # Create session
        session = get_snowflake_session()
        
        # Initialize loader
        loader = DataLoader(session)
        
        # Get CSV path (relative to this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        csv_path = os.path.join(project_dir, 'data', 'stock_data.csv')
        
        # Load data
        loader.load_csv_to_snowflake(
            csv_path=csv_path,
            table_name='stock_raw',
            overwrite=False  # Append mode
        )
        
        # Validate
        loader.validate_data('stock_raw')
        
        # Close session
        session.close()
        print("\n✅ Data loading completed successfully")
        
    except Exception as e:
        print(f"\n❌ Data loading failed: {e}")
        raise


if __name__ == "__main__":
    load_sample_data()
