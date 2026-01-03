"""Supplier - Comparison Tab - Simplified stub"""
import streamlit as st
from utils import load_supplier_performance
import plotly.express as px

def render_supplier_comparison():
    """Render Supplier Comparison tab."""
    from utils import load_supplier_comparison
    
    st.markdown("### Supplier Benchmarking")
    st.markdown("Compare suppliers based on reliability, lead time, and pricing.")
    
    comparison_data = load_supplier_comparison()
    
    if comparison_data.empty:
        st.info("No comparison data available. Generate some purchase orders first.")
        return

    # Filter by item
    items = sorted(comparison_data['ITEM'].unique())
    selected_item = st.selectbox("Select Item to Benchmark", items)
    
    if selected_item:
        filtered_df = comparison_data[comparison_data['ITEM'] == selected_item].copy()
        
        # UI Diagnostics using SVG instead of Emoji
        from utils import get_svg_icon
        num_suppliers = len(filtered_df)
        
        icon_svg = get_svg_icon("supplier", size=20, color="#29B5E8")
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                {icon_svg}
                <span style="font-size: 0.9em; color: #666;">Found {num_suppliers} suppliers for <b>{selected_item}</b></span>
            </div>
        """, unsafe_allow_html=True)
        
        if num_suppliers == 1:
            st.warning(f"Only one supplier found for {selected_item}. Please run 'py python/init_infra.py' to load more data.")
        
        # Debug View (Collapsible)
        with st.expander("🛠️ Debug Information (Verify Data)"):
            st.write(f"Total rows in view: {len(comparison_data)}")
            st.write(f"Rows for '{selected_item}': {len(filtered_df)}")
            st.dataframe(filtered_df, use_container_width=True)
            if st.button("Force Global Cache Clear"):
                st.cache_data.clear()
                st.rerun()

        # Display top recommendation
        top_supplier = filtered_df.iloc[0]
        st.success(f"🏆 **Top Recommendation:** {top_supplier['SUPPLIER_NAME']} (Score: {top_supplier['OVERALL_SCORE']})")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Multi-metric Scatter/Bubble Chart
            # X: Lead Time (Lower is better)
            # Y: Reliability (Higher is better)
            # Size: Overall Score
            # Color: Supplier Name
            
            fig = px.scatter(
                filtered_df,
                x='AVG_LEAD_TIME_DAYS',
                y='RELIABILITY_SCORE',
                size='OVERALL_SCORE',
                color='SUPPLIER_NAME',
                hover_name='SUPPLIER_NAME',
                hover_data=['UNIT_PRICE', 'OVERALL_SCORE'],
                text='SUPPLIER_NAME',
                title=f"Supplier Performance Matrix: {selected_item}",
                labels={
                    'AVG_LEAD_TIME_DAYS': 'Lead Time (Days)',
                    'RELIABILITY_SCORE': 'Reliability (%)',
                    'SUPPLIER_NAME': 'Supplier'
                },
                template="plotly_white",
                height=500
            )
            
            # Ensure all points are visible and update layout
            fig.update_traces(textposition='top center')
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(autorange=True, zeroline=False),
                yaxis=dict(autorange=True, zeroline=False)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("#### Comparison Details")
            # Show a simplified table
            display_df = filtered_df[['SUPPLIER_NAME', 'UNIT_PRICE', 'AVG_LEAD_TIME_DAYS', 'RELIABILITY_SCORE', 'OVERALL_SCORE']].copy()
            # Ensure numeric columns are numeric for the gradient to work, but cast others to string if needed?
            # Actually, this table contains no Dates, so it is SAFE from the PyArrow Date Bug.
            # I will leave it as is to preserve the styling.
            st.dataframe(
                display_df.style.background_gradient(subset=['OVERALL_SCORE'], cmap="BuGn"),
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Overall Score** is weighted: 50% Reliability, 30% Lead Time, 20% Price.")
