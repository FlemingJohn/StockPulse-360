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
        
        icon_svg = get_svg_icon("supplier", size=18, color="#29B5E8")
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px; background-color: #f8f9fa; padding: 8px 12px; border-radius: 6px; border-left: 3px solid #29B5E8;">
                {icon_svg}
                <span style="font-size: 0.9em; color: #444;">Multiple Benchmarks <b>({num_suppliers})</b> available for {selected_item}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Display top recommendation with SVG instead of emoji
        top_supplier = filtered_df.iloc[0]
        check_svg = get_svg_icon("check", size=20, color="#32CD32")
        st.markdown(f"""
            <div style="padding: 15px; background-color: #ebfaeb; border-radius: 8px; border: 1px solid #c3e6cb; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {check_svg}
                    <strong style="color: #155724;">Top Recommendation:</strong> 
                    <span style="color: #155724;">{top_supplier['SUPPLIER_NAME']} (Score: {top_supplier['OVERALL_SCORE']})</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
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
