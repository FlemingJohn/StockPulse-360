"""Supplier - Purchase Orders Tab - Simplified stub"""
import streamlit as st
from utils import load_purchase_orders
import plotly.express as px

def render_purchase_orders():
    """Render Purchase Orders tab."""
    st.markdown("### Purchase Orders by Supplier")
    po_data = load_purchase_orders()
    
    if not po_data.empty:
        # Visual Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total POs", len(po_data), delta=None)
        with col2:
            if 'TOTAL_COST' in po_data.columns:
                total_value = po_data['TOTAL_COST'].sum()
                st.metric("Total Value", f"₹{total_value:,.0f}")
        with col3:
            unique_suppliers = po_data['SUPPLIER_NAME'].nunique()
            st.metric("Active Suppliers", unique_suppliers)
        
        # Add Histogram for Order Value Distribution
        st.markdown("#### Order Value Distribution")
        if 'TOTAL_COST' in po_data.columns:
            fig = px.histogram(
                po_data, 
                x="TOTAL_COST", 
                nbins=20,
                title="Distribution of Order Costs",
                labels={'TOTAL_COST': 'Total Cost (₹)'},
                color_discrete_sequence=['#29B5E8']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode="x",
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Table with Status Stylers
        st.markdown("#### Active Purchase Orders Details")
        
        # Define a function to color the priority
        def color_priority(val):
            color = '#DC143C' if val == 'URGENT' else '#29B5E8' if val == 'NORMAL' else '#32CD32'
            return f'color: {color}; font-weight: bold'

        try:
            # Color coding for the priority column
            styled_df = po_data[['PURCHASE_ORDER_ID', 'ITEM', 'SUPPLIER_NAME', 'ORDER_QUANTITY', 'ORDER_PRIORITY', 'EXPECTED_DELIVERY_DATE']]
            
            st.dataframe(
                styled_df.style.applymap(color_priority, subset=['ORDER_PRIORITY']),
                use_container_width=True,
                height=400,
                hide_index=True
            )
        except Exception as e:
            # Fallback to plain dataframe if styling fails
            st.dataframe(po_data.astype(str), use_container_width=True, height=400)
            st.warning(f"Could not apply table styling: {e}")
            
    else:
        st.info("No purchase order data available.")
