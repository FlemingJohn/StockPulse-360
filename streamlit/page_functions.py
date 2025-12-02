"""
Page Rendering Functions for StockPulse 360 Dashboard
These functions render each navigation page section.
"""

def render_alerts_page_content(filtered_data):
    """Render Critical Alerts page content."""
    import streamlit as st
    from datetime import datetime
    
    st.markdown(section_header("Critical Alerts", "alert"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    alerts_data = load_critical_alerts()
    
    if not alerts_data.empty:
        critical_alerts = alerts_data[alerts_data['STOCK_STATUS'].isin(['OUT_OF_STOCK', 'CRITICAL'])]
        warning_alerts = alerts_data[alerts_data['STOCK_STATUS'] == 'WARNING']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Critical Alerts", len(critical_alerts))
        with col2:
            st.metric("Warning Alerts", len(warning_alerts))
        with col3:
            st.metric("Total Alerts", len(alerts_data))
        
        st.divider()
        
        for idx, alert in alerts_data.iterrows():
            status = alert['STOCK_STATUS']
            css_class = "critical-alert" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "warning-alert"
            alert_svg = get_svg_icon('alert', size=20, color="#DC143C" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "#FFA500")
            
            st.markdown(f"""
            <div class="{css_class}">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {alert_svg}
                    <strong>{alert['ALERT_MESSAGE']}</strong>
                </div>
                <div style="margin-top: 8px;">
                    Location: {alert['LOCATION']} | Item: {alert['ITEM']}<br>
                    Current Stock: {alert['CURRENT_STOCK']:.0f} | Avg Daily Usage: {alert['AVG_DAILY_USAGE']:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No critical alerts - all stock levels are healthy!")


def render_reorder_page_content(filtered_data):
    """Render Reorder Recommendations page content."""
    import streamlit as st
    from datetime import datetime
    
    st.markdown(section_header("Reorder Recommendations", "cart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    procurement_data = load_procurement_export()
    
    if not procurement_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Items to Reorder", len(procurement_data))
        with col2:
            total_cost = procurement_data['Estimated Cost (₹)'].sum()
            st.metric("Total Estimated Cost", f"₹{total_cost:,.0f}")
        with col3:
            urgent_count = len(procurement_data[procurement_data['Order Within (Days)'] <= 1])
            st.metric("Urgent Orders", urgent_count)
        
        st.divider()
        
        st.dataframe(procurement_data, use_container_width=True, height=500)
        
        csv = procurement_data.to_csv(index=False)
        st.download_button(
            label="Download Procurement List (CSV)",
            data=csv,
            file_name=f"procurement_list_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No reorder recommendations at this time.")


def render_ai_ml_page_content(filtered_data):
    """Render AI/ML Insights page content."""
    import streamlit as st
    
    st.markdown(section_header("AI/ML Insights", "trending"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("AI/ML features including Cortex AI forecasting, anomaly detection, and seasonal analysis.")
    
    st.markdown("### Features")
    st.markdown("""
    - **Cortex AI Demand Forecasting**: Predict future demand using Snowflake's native ML
    - **Anomaly Detection**: Identify unusual usage patterns
    - **Seasonal Trend Analysis**: Recognize holiday spikes and patterns
    - **Predictive Analytics**: Forecast stockouts before they happen
    """)


def render_analytics_page_content(filtered_data):
    """Render Advanced Analytics page content."""
    import streamlit as st
    
    st.markdown(section_header("Advanced Analytics", "chart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Advanced analytics including ABC analysis, cost optimization, and stockout impact analysis.")
    
    st.markdown("### Features")
    st.markdown("""
    - **ABC Analysis**: Classify inventory by value (High/Medium/Low)
    - **Cost Optimization Dashboard**: Track budget and ROI
    - **Stockout Impact Analysis**: Quantify patient/beneficiary impact
    - **Budget Tracking**: Monitor spending and identify savings
    """)


def render_supplier_page_content():
    """Render Supplier Management page content."""
    import streamlit as st
    
    st.markdown(section_header("Supplier Management", "box"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Supplier integration features including purchase orders, performance tracking, and delivery schedules.")
    
    st.markdown("### Features")
    st.markdown("""
    - **Auto-Generated Purchase Orders**: Smart procurement based on reorder recommendations
    - **Supplier Performance Dashboard**: Track reliability and lead times
    - **Delivery Schedule Tracking**: Monitor expected arrivals
    - **Cost Analysis by Supplier**: Optimize supplier selection
    """)
