"""
StockPulse 360 - Demand Forecast Model
Uses Snowpark Python to build demand forecasting models
Reference: https://docs.snowflake.com/en/developer-guide/snowpark/python/working-with-dataframes
"""

import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, avg, sum as sum_, count, max as max_
from config import get_snowflake_session, APP_CONFIG


class DemandForecaster:
    """
    Simple demand forecasting using moving averages and trend analysis.
    For production, consider using Snowflake's ML capabilities or external models.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.forecast_horizons = APP_CONFIG["forecast_days"]
        self.min_data_points = APP_CONFIG["min_data_points"]
    
    def calculate_forecasts(self):
        """
        Calculate demand forecasts for all location-item combinations.
        Uses simple moving average with trend adjustment.
        """
        print("📊 Starting demand forecast calculation...")
        
        # Get historical data from Snowflake
        stock_df = self.session.table("stock_raw").select(
            col("location"),
            col("item"),
            col("issued"),
            col("record_date"),
            col("lead_time_days")
        ).to_pandas()
        
        if stock_df.empty:
            print("⚠️ No data available for forecasting")
            return None
        
        print(f"📈 Processing {len(stock_df)} records...")
        
        # Group by location and item
        forecasts = []
        
        for (location, item), group in stock_df.groupby(['location', 'item']):
            if len(group) < self.min_data_points:
                print(f"⚠️ Skipping {location}-{item}: insufficient data ({len(group)} days)")
                continue
            
            # Sort by date
            group = group.sort_values('record_date')
            
            # Calculate forecasts
            forecast = self._forecast_item(location, item, group)
            if forecast:
                forecasts.append(forecast)
        
        if not forecasts:
            print("⚠️ No forecasts generated")
            return None
        
        # Convert to DataFrame
        forecast_df = pd.DataFrame(forecasts)
        
        # Write to Snowflake
        self._save_forecasts(forecast_df)
        
        print(f"✅ Generated {len(forecasts)} forecasts")
        return forecast_df
    
    def _forecast_item(self, location: str, item: str, data: pd.DataFrame) -> dict:
        """
        Forecast demand for a single location-item combination.
        
        Methods used:
        1. Simple Moving Average (SMA)
        2. Weighted Moving Average (WMA) - recent days weighted more
        3. Trend adjustment
        """
        issued = data['issued'].values
        
        # Calculate simple moving average
        sma = np.mean(issued)
        
        # Calculate weighted moving average (more weight to recent days)
        weights = np.arange(1, len(issued) + 1)
        wma = np.average(issued, weights=weights)
        
        # Calculate trend (linear regression slope)
        if len(issued) > 1:
            x = np.arange(len(issued))
            slope = np.polyfit(x, issued, 1)[0]
        else:
            slope = 0
        
        # Forecast for different horizons
        forecast_7_days = max(0, wma * 7 + slope * 7)
        forecast_14_days = max(0, wma * 14 + slope * 14)
        
        # Calculate confidence score based on data consistency
        std_dev = np.std(issued)
        mean_val = np.mean(issued)
        coefficient_of_variation = std_dev / mean_val if mean_val > 0 else 1
        confidence = max(0, min(1, 1 - coefficient_of_variation))
        
        return {
            'location': location,
            'item': item,
            'forecast_date': datetime.now().date(),
            'demand_next_7_days': round(forecast_7_days, 2),
            'demand_next_14_days': round(forecast_14_days, 2),
            'confidence_score': round(confidence, 2),
            'avg_daily_demand': round(sma, 2),
            'trend_slope': round(slope, 2),
            'data_points': len(issued)
        }
    
    def _save_forecasts(self, forecast_df: pd.DataFrame):
        """
        Save forecasts to Snowflake table.
        """
        try:
            # Select only columns that match the table schema
            output_df = forecast_df[[
                'location',
                'item',
                'forecast_date',
                'demand_next_7_days',
                'demand_next_14_days',
                'confidence_score'
            ]]
            
            # Write to Snowflake
            self.session.write_pandas(
                output_df,
                "forecast_output",
                auto_create_table=False,
                overwrite=True
            )
            
            print(f"✅ Saved {len(output_df)} forecasts to Snowflake")
            
        except Exception as e:
            print(f"❌ Error saving forecasts: {e}")
            raise
    
    def get_forecast_summary(self):
        """
        Get summary of forecasts from Snowflake.
        """
        summary_df = self.session.sql("""
            SELECT
                COUNT(*) as total_forecasts,
                AVG(confidence_score) as avg_confidence,
                MIN(forecast_date) as earliest_forecast,
                MAX(forecast_date) as latest_forecast
            FROM forecast_output
        """).to_pandas()
        
        return summary_df


def run_forecast_pipeline():
    """
    Main function to run the forecast pipeline.
    Can be called from Snowflake Task or run manually.
    """
    print("=" * 60)
    print("StockPulse 360 - Demand Forecasting Pipeline")
    print("=" * 60)
    
    try:
        # Create session
        session = get_snowflake_session()
        
        # Initialize forecaster
        forecaster = DemandForecaster(session)
        
        # Calculate forecasts
        forecasts = forecaster.calculate_forecasts()
        
        if forecasts is not None:
            # Show summary
            print("\n📊 Forecast Summary:")
            print(forecasts.describe())
            
            # Get summary from Snowflake
            summary = forecaster.get_forecast_summary()
            print("\n📈 Snowflake Summary:")
            print(summary)
        
        # Close session
        session.close()
        print("\n✅ Forecast pipeline completed successfully")
        
    except Exception as e:
        print(f"\n❌ Forecast pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_forecast_pipeline()
