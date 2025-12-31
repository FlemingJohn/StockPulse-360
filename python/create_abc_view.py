"""
Create Advanced Analytics Views for StockPulse 360
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
from config import get_snowflake_session

def create_abc_analysis_view():
    """Create ABC Analysis view."""
    session = get_snowflake_session()
    
    print("Creating ABC Analysis view...")
    
    # ABC Analysis View
    abc_query = """
    CREATE OR REPLACE VIEW abc_analysis AS
    WITH item_value AS (
        SELECT
            item,
            location,
            SUM(issued_qty) AS total_issued,
            CASE item
                WHEN 'Insulin' THEN 500
                WHEN 'ORS' THEN 10
                WHEN 'Paracetamol' THEN 5
                ELSE 10
            END AS unit_price
        FROM raw_stock
        GROUP BY item, location
    ),
    item_total_value AS (
        SELECT
            item,
            SUM(total_issued * unit_price) AS total_value,
            SUM(total_issued) AS total_quantity,
            COUNT(DISTINCT location) AS locations_count
        FROM item_value
        GROUP BY item
    )
    SELECT
        item,
        total_value,
        total_quantity,
        locations_count,
        ROUND((total_value / SUM(total_value) OVER ()) * 100, 2) AS value_percentage,
        ROUND((total_quantity / SUM(total_quantity) OVER ()) * 100, 2) AS quantity_percentage,
        CASE
            WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.2 THEN 'A'
            WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.5 THEN 'B'
            ELSE 'C'
        END AS abc_category,
        CASE
            WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.2 THEN 'HIGH_VALUE_CRITICAL'
            WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.5 THEN 'MEDIUM_VALUE'
            ELSE 'LOW_VALUE'
        END AS category_description
    FROM item_total_value
    ORDER BY total_value DESC
    """
    
    session.sql(abc_query).collect()
    print("✅ ABC Analysis view created")
    
    # Verify
    result = session.sql("SELECT * FROM abc_analysis").to_pandas()
    if len(result) > 0:
        print(result[['ITEM', 'TOTAL_VALUE', 'ABC_CATEGORY', 'CATEGORY_DESCRIPTION']].head())
    else:
        print("   (No ABC analysis data available)")

if __name__ == "__main__":
    create_abc_analysis_view()
