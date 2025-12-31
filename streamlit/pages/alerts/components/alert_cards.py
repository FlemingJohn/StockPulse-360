"""
Alerts Page - Alert Cards Component
Renders individual alert cards with enhanced styling
"""

import streamlit as st
from utils import get_svg_icon


def render_alert_cards(filtered_data):
    """Render alert cards with enhanced styling for each alert."""
    
    if filtered_data.empty:
        st.info("No alerts match the selected filters.")
        return
    
    # Alert cards with enhanced styling
    for idx, alert in filtered_data.iterrows():
        status = alert['STOCK_STATUS']
        css_class = "critical-alert" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "warning-alert"
        alert_color = "#DC143C" if status in ['OUT_OF_STOCK', 'CRITICAL'] else "#FFA500"
        alert_svg = get_svg_icon('alert', size=24, color=alert_color)
        
        # Risk Level Badge
        risk_badge = f'<span style="background-color: {alert_color}; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin-left: auto;">{status.replace("_", " ")}</span>'
        
        st.markdown(f"""
        <div class="{css_class}">
            <div style="display: flex; align-items: flex-start; gap: 15px;">
                <div style="background: rgba(255,255,255,0.5); padding: 10px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                    {alert_svg}
                </div>
                <div style="flex-grow: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #0F4C81;">{alert['ITEM']}</span>
                        {risk_badge}
                    </div>
                    <div style="font-size: 0.95rem; color: #333; margin-bottom: 12px; line-height: 1.4;">
                        {alert['ALERT_MESSAGE']}
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; background: rgba(255,255,255,0.3); padding: 8px 12px; border-radius: 8px; font-size: 0.85rem;">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            {get_svg_icon('location', size=14, color="#333")} <span style="font-weight: 600;">{alert['LOCATION']}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 5px;">
                            {get_svg_icon('box', size=14, color="#333")} Stock: <span style="font-weight: 600; color: {alert_color};">{alert['CURRENT_STOCK']:.0f} units</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 5px;">
                            {get_svg_icon('trending', size=14, color="#333")} Usage: <span style="font-weight: 600;">{alert['AVG_DAILY_USAGE']:.1f}/day</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 5px;">
                            {get_svg_icon('hourglass', size=14, color="#333")} Remaining: <span style="font-weight: 600;">{alert['DAYS_UNTIL_STOCKOUT']:.1f} days</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
