"""
Shared Page Components - Filters
Common filter functionality used across multiple pages
"""

import streamlit as st


def render_page_sidebar_filters(df, page_name=""):
    """Render common sidebar filters (Location/Item) for a specific page."""
    if df is None or df.empty:
        return df
        
    # Get the container from session state or fallback to sidebar
    container = st.session_state.get('filter_container', st.sidebar)
    
    container.markdown(f'<div class="sidebar-filter-header">{page_name} Filters</div>', unsafe_allow_html=True)
    
    # Selection logic
    filtered_df = df.copy()
    
    # Location Filter
    if 'LOCATION' in df.columns:
        loc_options = ['All'] + sorted(df['LOCATION'].unique().tolist())
        selected_loc = container.selectbox("Select Location", loc_options, key=f"filter_loc_{page_name}")
        if selected_loc != 'All':
            filtered_df = filtered_df[filtered_df['LOCATION'] == selected_loc]
            
    # Item Filter
    if 'ITEM' in df.columns:
        item_options = ['All'] + sorted(filtered_df['ITEM'].unique().tolist())
        selected_item = container.selectbox("Select Item", item_options, key=f"filter_item_{page_name}")
        if selected_item != 'All':
            filtered_df = filtered_df[filtered_df['ITEM'] == selected_item]
            
    return filtered_df


def apply_sidebar_logic_to_performance(perf_df, filtered_po_df):
    """Filter performance data to match the suppliers in the filtered PO data."""
    if perf_df is None or perf_df.empty or filtered_po_df is None or filtered_po_df.empty:
        return perf_df
    
    # Get unique suppliers from filtered POs
    valid_suppliers = filtered_po_df['SUPPLIER_NAME'].unique()
    return perf_df[perf_df['SUPPLIER_NAME'].isin(valid_suppliers)]
