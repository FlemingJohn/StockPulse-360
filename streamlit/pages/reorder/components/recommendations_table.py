"""
Reorder Page - Recommendations Table Component
Data table with styled reorder recommendations
"""

import streamlit as st
from datetime import datetime


def render_recommendations_table(filtered_data):
    """Render reorder recommendations table with CSV export."""
    
    # Custom highlighting function
    def highlight_risk(row):
        if row['Supplier Reliability (%)'] < 75:
            return ['background-color: #ffebee; border-left: 5px solid #ef5350'] * len(row)
        return [''] * len(row)

    display_df = filtered_data.copy()
    
    # Select and Rename for clarity in display
    display_df = display_df[[
        'LOCATION', 'ITEM', 'CURRENT_STOCK', 'DAYS_UNTIL_STOCKOUT', 
        'SIMULATION_QUANTITY', 'SIMULATION_COST', 'SUPPLIER_NAME', 'RELIABILITY_SCORE'
    ]]
    
    display_df = display_df.rename(columns={
        'LOCATION': 'Location',
        'ITEM': 'Item Name',
        'CURRENT_STOCK': 'Current Stock',
        'DAYS_UNTIL_STOCKOUT': 'Order Within (Days)',
        'SIMULATION_COST': 'Total Cost (₹)',
        'SIMULATION_QUANTITY': 'Order Quantity',
        'SUPPLIER_NAME': 'Supplier',
        'RELIABILITY_SCORE': 'Supplier Reliability (%)'
    })

    st.dataframe(
        display_df.style.apply(highlight_risk, axis=1),
        use_container_width=True,
        height=500,
        column_config={
            "Order Within (Days)": st.column_config.NumberColumn(
                "Order Within (Days)",
                help="Days until stockout",
                format="%d days"
            ),
            "Total Cost (₹)": st.column_config.NumberColumn(
                "Total Cost (₹)",
                help="Estimated procurement cost for selected safety days",
                format="₹%.2f"
            ),
            "Supplier Reliability (%)": st.column_config.ProgressColumn(
                "Supplier Reliability (%)",
                help="Supplier performance score",
                format="%.0f%%",
                min_value=0,
                max_value=100
            )
        }
    )
    
    # CSV download
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download Procurement List (CSV)",
        data=csv,
        file_name=f"procurement_list_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary"
    )
