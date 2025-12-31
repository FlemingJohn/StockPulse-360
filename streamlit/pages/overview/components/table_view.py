"""
Overview Page - Table View Component
Displays stock data in table format
"""

import streamlit as st


def render_table_view(filtered_data):
    """Render stock data as a table."""
    
    if not filtered_data.empty:
        # Display table
        st.dataframe(
            filtered_data[[
                'LOCATION', 'ITEM', 'CURRENT_STOCK', 'AVG_DAILY_USAGE',
                'DAYS_UNTIL_STOCKOUT', 'STOCK_STATUS', 'HEALTH_SCORE'
            ]],
            use_container_width=True,
            height=400
        )
    else:
        st.warning("No data available for the selected filters.")
