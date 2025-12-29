"""
StockPulse 360 - Snowflake Cortex AI Integration
Uses Snowflake's native ML capabilities for advanced forecasting
Reference: https://docs.snowflake.com/en/user-guide/ml-functions
"""

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, call_builtin
import pandas as pd
from datetime import datetime, timedelta
from config import get_snowflake_session


class CortexAIForecaster:
    """
    Advanced forecasting using Snowflake Cortex AI.
    Leverages Snowflake's built-in ML functions for time-series prediction.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_forecast_model(self, location: str, item: str, forecast_days: int = 7):
        """
        Create time-series forecast using Snowflake Cortex AI.
        
        Args:
            location: Location name
            item: Item name
            forecast_days: Number of days to forecast
        
        Returns:
            DataFrame with forecasted values
        """
        print(f"🤖 Creating Cortex AI forecast for {item} at {location}...")
        
        try:
            # Use Snowflake's FORECAST function (Cortex AI)
            forecast_query = f"""
            SELECT
                location,
                item,
                last_updated_date as record_date,
                issued_qty as actual_usage,
                SNOWFLAKE.ML.FORECAST(
                    issued_qty,
                    last_updated_date
                ) OVER (
                    PARTITION BY location, item
                    ORDER BY last_updated_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as forecasted_usage
            FROM RAW_STOCK
            WHERE location = '{location}'
            AND item = '{item}'
            ORDER BY last_updated_date
            """
            
            result = self.session.sql(forecast_query).to_pandas()
            
            if not result.empty:
                print(f"✅ Cortex AI forecast created: {len(result)} data points")
                return result
            else:
                print("⚠️ No data available for forecasting")
                return None
                
        except Exception as e:
            print(f"⚠️ Cortex AI not available, using fallback method: {e}")
            return self._fallback_forecast(location, item, forecast_days)
    
    def _fallback_forecast(self, location: str, item: str, forecast_days: int):
        """
        Fallback forecasting method if Cortex AI is not available.
        Uses exponential smoothing.
        """
        print("📊 Using exponential smoothing fallback...")
        
        # Get historical data
        data = self.session.sql(f"""
            SELECT last_updated_date as record_date, issued_qty as issued
            FROM RAW_STOCK
            WHERE location = '{location}'
            AND item = '{item}'
            ORDER BY last_updated_date
        """).to_pandas()
        
        if data.empty:
            return None
        
        # Simple exponential smoothing
        alpha = 0.3  # Smoothing factor
        forecast = []
        
        # Initialize with first value
        s = data['issued'].iloc[0]
        
        for value in data['issued']:
            s = alpha * value + (1 - alpha) * s
            forecast.append(s)
        
        data['forecasted_usage'] = forecast
        data['location'] = location
        data['item'] = item
        
        return data
    
    def batch_forecast_all_items(self, forecast_days: int = 7):
        """
        Create forecasts for all location-item combinations.
        """
        print("🚀 Starting batch Cortex AI forecasting...")
        
        # Get all unique location-item combinations
        combinations = self.session.sql("""
            SELECT DISTINCT location, item
            FROM RAW_STOCK
        """).collect()
        
        all_forecasts = []
        
        for row in combinations:
            location = row['LOCATION']
            item = row['ITEM']
            
            forecast = self.create_forecast_model(location, item, forecast_days)
            if forecast is not None:
                all_forecasts.append(forecast)
        
        if all_forecasts:
            combined = pd.concat(all_forecasts, ignore_index=True)
            print(f"\n✅ Batch forecasting complete: {len(all_forecasts)} items")
            return combined
        else:
            print("⚠️ No forecasts generated")
            return None
    
    def save_cortex_forecasts(self, forecasts_df: pd.DataFrame):
        """
        Save Cortex AI forecasts to Snowflake table.
        """
        try:
            # Create or replace forecast table
            self.session.sql("""
                CREATE TABLE IF NOT EXISTS cortex_forecasts (
                    location STRING,
                    item STRING,
                    forecast_date DATE,
                    forecasted_usage NUMBER(10,2),
                    confidence_interval_lower NUMBER(10,2),
                    confidence_interval_upper NUMBER(10,2),
                    model_type STRING,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
                )
            """).collect()
            
            # Save forecasts
            self.session.write_pandas(
                forecasts_df,
                "cortex_forecasts",
                auto_create_table=False,
                overwrite=True
            )
            
            print(f"✅ Saved {len(forecasts_df)} Cortex AI forecasts to Snowflake")
            
        except Exception as e:
            print(f"❌ Error saving forecasts: {e}")


def run_cortex_forecasting():
    """
    Main function to run Cortex AI forecasting.
    """
    print("=" * 60)
    print("StockPulse 360 - Cortex AI Forecasting")
    print("=" * 60)
    
    try:
        session = get_snowflake_session()
        forecaster = CortexAIForecaster(session)
        
        # Run batch forecasting
        forecasts = forecaster.batch_forecast_all_items(forecast_days=7)
        
        if forecasts is not None:
            # Save to Snowflake
            forecaster.save_cortex_forecasts(forecasts)
            
            # Show summary
            print("\n📊 Forecast Summary:")
            print(forecasts.groupby(['location', 'item'])['forecasted_usage'].mean())
        
        session.close()
        print("\n✅ Cortex AI forecasting completed")
        
    except Exception as e:
        print(f"\n❌ Cortex AI forecasting failed: {e}")
        raise


if __name__ == "__main__":
    run_cortex_forecasting()
