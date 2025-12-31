"""Supplier - Purchase Orders Tab - Simplified stub"""
import streamlit as st
from utils import load_purchase_orders
import plotly.express as px

def render_purchase_orders():
    """Render Purchase Orders tab."""
    st.markdown("### Purchase Orders by Supplier")
    po_data = load_purchase_orders()
    
    if not po_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total POs", len(po_data))
        with col2:
            total_value = po_data['ORDER_COST'].sum()
            st.metric("Total Value", f"₹{total_value:,.0f}")
        with col3:
            unique_suppliers = po_data['SUPPLIER_NAME'].nunique()
            st.metric("Active Suppliers", unique_suppliers)
        
        st.dataframe(po_data, use_container_width=True, height=400)
    else:
        st.info("No purchase order data available.")
