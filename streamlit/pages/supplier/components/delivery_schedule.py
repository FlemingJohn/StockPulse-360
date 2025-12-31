"""Supplier - Delivery Schedule Tab - Simplified stub"""
import streamlit as st
from utils import load_purchase_orders

def render_delivery_schedule():
    """Render Delivery Schedule tab."""
    st.markdown("### Delivery Schedule")
    po_data = load_purchase_orders()
    
    if not po_data.empty and 'DELIVERY_DATE' in po_data.columns:
        st.dataframe(po_data[['SUPPLIER_NAME', 'ITEM', 'DELIVERY_DATE', 'ORDER_QUANTITY', 'ORDER_COST']],
                    use_container_width=True, height=400)
    else:
        st.info("No delivery schedule data available.")
