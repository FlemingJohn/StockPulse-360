"""
StockPulse 360 - Seasonal Pattern Recognition
Identifies and forecasts based on seasonal patterns (weekly, monthly)
"""

import pandas as pd
import numpy as np
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, dayofweek, month, avg
from datetime import datetime, timedelta
from config import get_snowflake_session


class SeasonalForecaster:
    """
    Identifies seasonal patterns and creates forecasts accounting for seasonality.
    Handles weekly patterns (weekday vs weekend) and monthly patterns.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze_weekly_patterns(self):
        """
        Analyze usage patterns by day of week.
        """
        print("📅 Analyzing weekly patterns...")
        
        weekly_query = """
        SELECT
            "location",
            "item",
            DAYOFWEEK("last_updated_date") as day_of_week,
            CASE DAYOFWEEK("last_updated_date")
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
            END as day_name,
            AVG("issued_qty") as avg_usage,
            STDDEV("issued_qty") as stddev_usage,
            COUNT(*) as data_points,
            CASE
                WHEN DAYOFWEEK("last_updated_date") IN (0, 6) THEN 'Weekend'
                ELSE 'Weekday'
            END as day_type
        FROM RAW_STOCK
        GROUP BY "location", "item", day_of_week, day_name, day_type
        ORDER BY "location", "item", day_of_week
        """
        
        results = self.session.sql(weekly_query).to_pandas()
        
        if not results.empty:
            print(f"✅ Analyzed weekly patterns for {len(results)} combinations")
            
            # Show sample data
            if len(results) > 0:
                print("\n📊 Sample Weekly Patterns:")
                print(results.head(10))
            
            
            return results
        else:
            print("⚠️ No weekly pattern data available")
            return pd.DataFrame()
    
    def analyze_monthly_patterns(self):
        """
        Analyze usage patterns by month.
        """
        print("📆 Analyzing monthly patterns...")
        
        monthly_query = """
        SELECT
            "location",
            "item",
            MONTH("last_updated_date") as month_num,
            CASE MONTH("last_updated_date")
                WHEN 1 THEN 'January'
                WHEN 2 THEN 'February'
                WHEN 3 THEN 'March'
                WHEN 4 THEN 'April'
                WHEN 5 THEN 'May'
                WHEN 6 THEN 'June'
                WHEN 7 THEN 'July'
                WHEN 8 THEN 'August'
                WHEN 9 THEN 'September'
                WHEN 10 THEN 'October'
                WHEN 11 THEN 'November'
                WHEN 12 THEN 'December'
            END as month_name,
            AVG("issued_qty") as avg_usage,
            STDDEV("issued_qty") as stddev_usage,
            COUNT(*) as data_points
        FROM RAW_STOCK
        GROUP BY "location", "item", month_num, month_name
        ORDER BY "location", "item", month_num
        """
        
        results = self.session.sql(monthly_query).to_pandas()
        
        if not results.empty:
            print(f"✅ Analyzed monthly patterns for {len(results)} combinations")
            return results
        else:
            print("⚠️ No monthly pattern data available")
            return pd.DataFrame()
    
    def detect_seasonal_trends(self):
        """
        Detect if items have significant seasonal trends.
        """
        print("🔍 Detecting seasonal trends...")
        
        trend_query = """
        WITH monthly_stats AS (
            SELECT
                "location",
                "item",
                MONTH("last_updated_date") as month_num,
                AVG("issued_qty") as avg_usage
            FROM RAW_STOCK
            GROUP BY "location", "item", month_num
        ),
        overall_stats AS (
            SELECT
                "location",
                "item",
                AVG(avg_usage) as overall_avg,
                STDDEV(avg_usage) as seasonal_variation
            FROM monthly_stats
            GROUP BY "location", "item"
        )
        SELECT
            "location",
            "item",
            overall_avg,
            seasonal_variation,
            CASE
                WHEN seasonal_variation > (overall_avg * 0.3) THEN 'HIGH_SEASONALITY'
                WHEN seasonal_variation > (overall_avg * 0.15) THEN 'MODERATE_SEASONALITY'
                ELSE 'LOW_SEASONALITY'
            END as seasonality_level,
            ROUND((seasonal_variation / NULLIF(overall_avg, 0)) * 100, 2) as coefficient_of_variation
        FROM overall_stats
        WHERE overall_avg > 0
        ORDER BY coefficient_of_variation DESC
        """
        
        results = self.session.sql(trend_query).to_pandas()
        
        if not results.empty:
            print(f"✅ Detected seasonality for {len(results)} items")
            
            # Show items with high seasonality
            high_seasonal = results[results['SEASONALITY_LEVEL'] == 'HIGH_SEASONALITY']
            if not high_seasonal.empty:
                print(f"\n📈 {len(high_seasonal)} items have HIGH seasonality")
            
            return results
        else:
            print("⚠️ No seasonal trend data available")
            return pd.DataFrame()
    
    def create_seasonal_forecast(self, location: str, item: str, forecast_days: int = 7):
        """
        Create forecast incorporating seasonal patterns.
        
        Args:
            location: Location name
            item: Item name
            forecast_days: Number of days to forecast
        """
        print(f"🎯 Creating seasonal forecast for {item} at {location}...")
        
        # Get historical data with day of week
        historical_query = f"""
        SELECT
            "last_updated_date" as record_date,
            "issued_qty" as issued,
            DAYOFWEEK("last_updated_date") as day_of_week,
            MONTH("last_updated_date") as month_num
        FROM RAW_STOCK
        WHERE "location" = '{location}'
        AND "item" = '{item}'
        ORDER BY "last_updated_date"
        """
        
        historical = self.session.sql(historical_query).to_pandas()
        
        if historical.empty:
            print("⚠️ No historical data available")
            return None
        
        # Calculate seasonal factors by day of week
        seasonal_factors = historical.groupby('DAY_OF_WEEK')['ISSUED'].mean()
        overall_avg = historical['ISSUED'].mean()
        
        # Normalize seasonal factors
        seasonal_factors = seasonal_factors / overall_avg
        
        # Create forecast dates
        last_date = historical['RECORD_DATE'].max()
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=forecast_days,
            freq='D'
        )
        
        # Generate forecasts with seasonal adjustment
        forecasts = []
        base_forecast = historical['ISSUED'].tail(7).mean()  # Use recent average
        
        for date in forecast_dates:
            day_of_week = date.dayofweek
            seasonal_factor = seasonal_factors.get(day_of_week, 1.0)
            
            forecasted_value = base_forecast * seasonal_factor
            
            forecasts.append({
                'location': location,
                'item': item,
                'forecast_date': date,
                'forecasted_usage': round(forecasted_value, 2),
                'seasonal_factor': round(seasonal_factor, 2),
                'base_forecast': round(base_forecast, 2)
            })
        
        forecast_df = pd.DataFrame(forecasts)
        print(f"✅ Created {len(forecast_df)}-day seasonal forecast")
        
        return forecast_df
    
    def batch_seasonal_forecast(self, forecast_days: int = 7):
        """
        Create seasonal forecasts for all items.
        """
        print("🚀 Starting batch seasonal forecasting...")
        
        # Get all location-item combinations
        combinations = self.session.sql("""
            SELECT DISTINCT "location", "item"
            FROM RAW_STOCK
        """).collect()
        
        all_forecasts = []
        
        for row in combinations:
            location = row['location']
            item = row['item']
            
            forecast = self.create_seasonal_forecast(location, item, forecast_days)
            if forecast is not None:
                all_forecasts.append(forecast)
        
        if all_forecasts:
            combined = pd.concat(all_forecasts, ignore_index=True)
            print(f"\n✅ Batch seasonal forecasting complete: {len(all_forecasts)} items")
            return combined
        else:
            print("⚠️ No forecasts generated")
            return None
    
    def save_seasonal_forecasts(self, forecasts_df: pd.DataFrame):
        """
        Save seasonal forecasts to Snowflake.
        """
        try:
            # Create table
            self.session.sql("""
                CREATE TABLE IF NOT EXISTS seasonal_forecasts (
                    location STRING,
                    item STRING,
                    forecast_date DATE,
                    forecasted_usage NUMBER(10,2),
                    seasonal_factor NUMBER(5,2),
                    base_forecast NUMBER(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
                )
            """).collect()
            
            # Save forecasts
            self.session.write_pandas(
                forecasts_df,
                "seasonal_forecasts",
                auto_create_table=False,
                overwrite=True
            )
            
            print(f"✅ Saved {len(forecasts_df)} seasonal forecasts to Snowflake")
            
        except Exception as e:
            print(f"❌ Error saving forecasts: {e}")


def run_seasonal_analysis():
    """
    Main function to run seasonal pattern analysis and forecasting.
    """
    print("=" * 60)
    print("StockPulse 360 - Seasonal Pattern Recognition")
    print("=" * 60)
    
    try:
        session = get_snowflake_session()
        forecaster = SeasonalForecaster(session)
        
        # Analyze patterns
        print("\n📊 PATTERN ANALYSIS:")
        weekly_patterns = forecaster.analyze_weekly_patterns()
        monthly_patterns = forecaster.analyze_monthly_patterns()
        seasonal_trends = forecaster.detect_seasonal_trends()
        
        # Create forecasts
        print("\n🎯 SEASONAL FORECASTING:")
        forecasts = forecaster.batch_seasonal_forecast(forecast_days=7)
        
        if forecasts is not None:
            forecaster.save_seasonal_forecasts(forecasts)
            
            # Show sample forecasts
            print("\n📈 Sample Forecasts:")
            print(forecasts.head(10))
        
        session.close()
        print("\n✅ Seasonal analysis completed")
        
    except Exception as e:
        print(f"\n❌ Seasonal analysis failed: {e}")
        raise


if __name__ == "__main__":
    run_seasonal_analysis()
