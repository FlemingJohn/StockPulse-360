"""
Create Cost Optimization and Stockout Impact Views
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))
from config import get_snowflake_session

def create_views():
    """Create cost optimization and stockout impact views."""
    session = get_snowflake_session()
    
    print("Creating Stockout Impact view...")
    
    # Stockout Impact View - quote lowercase columns
    stockout_query = """
    CREATE OR REPLACE VIEW stockout_impact AS
    SELECT
        h."location",
        h."item",
        h.CURRENT_STOCK,
        h.AVG_DAILY_USAGE,
        h.DAYS_UNTIL_STOCKOUT,
        h.STOCK_STATUS,
        
        -- Patient impact calculations
        ROUND(h.AVG_DAILY_USAGE * h.DAYS_UNTIL_STOCKOUT, 0) AS PATIENTS_AFFECTED_UNTIL_STOCKOUT,
        ROUND(h.AVG_DAILY_USAGE, 0) AS DAILY_PATIENTS_AFFECTED,
        ROUND(h.AVG_DAILY_USAGE * 7, 0) AS WEEKLY_PATIENTS_AFFECTED,
        
        -- Severity based on item criticality and impact
        CASE
            WHEN h."item" = 'Insulin' AND h.STOCK_STATUS IN ('OUT_OF_STOCK', 'CRITICAL') THEN 'LIFE_THREATENING'
            WHEN h."item" IN ('Insulin', 'ORS') AND h.STOCK_STATUS = 'CRITICAL' THEN 'HIGH_SEVERITY'
            WHEN h.STOCK_STATUS = 'CRITICAL' THEN 'MODERATE_SEVERITY'
            WHEN h.STOCK_STATUS = 'WARNING' THEN 'LOW_SEVERITY'
            ELSE 'MINIMAL'
        END AS IMPACT_SEVERITY,
        
        -- ABC category for prioritization
        a.ABC_CATEGORY,
        
        -- Combined priority score (lower = more urgent)
        CASE
            WHEN h.STOCK_STATUS = 'OUT_OF_STOCK' THEN 1
            WHEN h.STOCK_STATUS = 'CRITICAL' AND a.ABC_CATEGORY = 'A' THEN 2
            WHEN h.STOCK_STATUS = 'CRITICAL' AND a.ABC_CATEGORY = 'B' THEN 3
            WHEN h.STOCK_STATUS = 'CRITICAL' THEN 4
            WHEN h.STOCK_STATUS = 'WARNING' AND a.ABC_CATEGORY = 'A' THEN 5
            ELSE 6
        END AS ACTION_PRIORITY
    FROM STOCK_HEALTH h
    LEFT JOIN ABC_ANALYSIS a ON h."item" = a."item"
    WHERE h.STOCK_STATUS IN ('OUT_OF_STOCK', 'CRITICAL', 'WARNING')
    ORDER BY ACTION_PRIORITY, PATIENTS_AFFECTED_UNTIL_STOCKOUT DESC
    """
    
    session.sql(stockout_query).collect()
    print("✅ Stockout Impact view created")
    
    # Budget Tracking View
    print("Creating Budget Tracking view...")
    
    budget_query = """
    CREATE OR REPLACE VIEW budget_tracking AS
    WITH monthly_procurement AS (
        SELECT
            SUM(r.REORDER_QUANTITY * 
                CASE r."item"
                    WHEN 'Insulin' THEN 500
                    WHEN 'ORS' THEN 10
                    WHEN 'Paracetamol' THEN 5
                    ELSE 10
                END
            ) AS ESTIMATED_SPEND
        FROM REORDER_RECOMMENDATIONS r
    )
    SELECT
        100000 AS MONTHLY_BUDGET,
        m.ESTIMATED_SPEND,
        100000 - m.ESTIMATED_SPEND AS REMAINING_BUDGET,
        ROUND((m.ESTIMATED_SPEND / 100000) * 100, 2) AS BUDGET_UTILIZATION_PCT,
        CASE
            WHEN m.ESTIMATED_SPEND > 100000 THEN 'OVER_BUDGET'
            WHEN m.ESTIMATED_SPEND > 90000 THEN 'WARNING'
            WHEN m.ESTIMATED_SPEND > 75000 THEN 'MODERATE'
            ELSE 'HEALTHY'
        END AS BUDGET_STATUS
    FROM monthly_procurement m
    """
    
    session.sql(budget_query).collect()
    print("✅ Budget Tracking view created")
    
    # Verify
    stockout_result = session.sql("SELECT * FROM stockout_impact").to_pandas()
    print(f"\n✅ Stockout Impact has {len(stockout_result)} items")
    if len(stockout_result) > 0:
        print(stockout_result[['location', 'item', 'IMPACT_SEVERITY', 'ACTION_PRIORITY']].head())
    else:
        print("   (No critical/warning items currently)")
    
    budget_result = session.sql("SELECT * FROM budget_tracking").to_pandas()
    print(f"\n✅ Budget Tracking data:")
    print(budget_result)

if __name__ == "__main__":
    create_views()
