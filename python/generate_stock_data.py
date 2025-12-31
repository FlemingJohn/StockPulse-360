"""
Data Generator for StockPulse 360
Generates realistic stock data with multiple locations and items
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Configuration
LOCATIONS = [
    'Chennai', 'Mumbai', 'Delhi', 'Bangalore', 'Kolkata', 
    'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
]

ITEMS = [
    'Paracetamol', 'ORS', 'Insulin', 'Aspirin', 'Antibiotics',
    'Bandages', 'Syringes', 'Gloves', 'Masks', 'Thermometers',
    'BP Monitor', 'Glucose Test Strips', 'IV Fluids', 'Oxygen Cylinders'
]

# Date range for historical data (last 60 days)
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=60)

def generate_realistic_stock_data(num_days=60):
    """Generate realistic stock movement data."""
    
    data = []
    
    # Initialize starting stock for each location-item combination
    stock_levels = {}
    for location in LOCATIONS:
        for item in ITEMS:
            # Starting stock: lower range to trigger alerts
            stock_levels[(location, item)] = random.randint(50, 250)
    
    # Generate daily records
    for day in range(num_days):
        current_date = START_DATE + timedelta(days=day)
        for location in LOCATIONS:
            for item in ITEMS:
                key = (location, item)
                current_stock = stock_levels[key]
                
                # Simulate daily movements
                # Issued (consumption): 5-30% of current stock
                issued = int(current_stock * np.random.uniform(0.05, 0.30))
                issued = min(issued, current_stock)  # Can't issue more than available
                
                # Received (replenishment): Occasional replenishment (15% chance)
                received = 0
                if random.random() < 0.15: # Lowered frequency to allow stock levels to drop
                    received = random.randint(50, 150)
                
                # Update stock
                new_stock = current_stock - issued + received
                new_stock = max(0, new_stock)  # Stock can't go negative
                
                # Record the day's data
                data.append({
                    'location': location,
                    'item': item,
                    'current_stock': new_stock,
                    'issued_qty': issued,
                    'received_qty': received,
                    'last_updated_date': current_date.strftime('%Y-%m-%d')
                })
                
                # Update stock level for next day
                stock_levels[key] = new_stock
    
    return pd.DataFrame(data)


def main():
    """Generate and save stock data."""
    print("=" * 60)
    print("StockPulse 360 - Data Generator")
    print("=" * 60)
    
    print(f"\n📊 Generating data for:")
    print(f"   - {len(LOCATIONS)} locations")
    print(f"   - {len(ITEMS)} items")
    print(f"   - 60 days of history")
    print(f"   - Total records: {len(LOCATIONS) * len(ITEMS) * 60:,}")
    
    # Generate data
    print("\n⚙️  Generating realistic stock movements...")
    df = generate_realistic_stock_data(num_days=60)
    
    # Sort by date and location
    df = df.sort_values(['last_updated_date', 'location', 'item'])
    
    # Save to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(project_dir, 'data', 'stock_data.csv')
    
    print(f"\n💾 Saving to: {output_path}")
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {len(df):,} records")
    
    # Show summary
    print("\n📊 Summary:")
    print(f"   Date range: {df['last_updated_date'].min()} to {df['last_updated_date'].max()}")
    print(f"   Locations: {', '.join(sorted(df['location'].unique()))}")
    print(f"   Items: {', '.join(sorted(df['item'].unique()))}")
    print(f"   Avg stock level: {df['current_stock'].mean():.0f}")
    print(f"   Items with zero stock: {len(df[df['current_stock'] == 0])}")
    
    # Show sample
    print("\n📋 Sample data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    print("\n✅ Data generation complete!")
    print("\n💡 Next steps:")
    print("   1. Review the generated data in data/stock_data.csv")
    print("   2. Run: python python/reload_stock_data.py")
    print("   3. Check the Streamlit dashboard")


if __name__ == "__main__":
    main()
