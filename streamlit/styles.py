"""
StockPulse 360 - CSS Styles
All custom CSS styling for the Streamlit dashboard
"""

CUSTOM_CSS = """
<style>
    /* Snowflake Color Palette */
    :root {
        --snowflake-blue: #29B5E8;
        --snowflake-dark-blue: #1E88E5;
        --snowflake-light-blue: #E3F2FD;
        --snowflake-navy: #0F4C81;
        --snowflake-gray: #F0F2F6;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .subtitle {
        text-align: center;
        color: #0F4C81;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* SVG Icons */
    .icon-container {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
    
    .section-header-icon {
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F2F6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #29B5E8;
        box-shadow: 0 2px 8px rgba(41, 181, 232, 0.1);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.2);
    }
    
    /* Alert Cards - Premium Glassmorphism */
    .critical-alert {
        background: rgba(220, 20, 60, 0.05);
        backdrop-filter: blur(8px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(220, 20, 60, 0.2);
        border-left: 8px solid #DC143C;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(220, 20, 60, 0.08);
        transition: all 0.3s ease;
    }
    
    .critical-alert:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 20px rgba(220, 20, 60, 0.15);
        background: rgba(220, 20, 60, 0.08);
    }
    
    .warning-alert {
        background: rgba(255, 165, 0, 0.05);
        backdrop-filter: blur(8px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 165, 0, 0.2);
        border-left: 8px solid #FFA500;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(255, 165, 0, 0.08);
        transition: all 0.3s ease;
    }

    .warning-alert:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 20px rgba(255, 165, 0, 0.15);
        background: rgba(255, 165, 0, 0.08);
    }
    
    /* Buttons - Snowflake Style */
    .stButton>button {
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 2px 6px rgba(41, 181, 232, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.4);
        transform: translateY(-1px);
    }
    
    /* Premium Side Nav - Image Matched */
    [data-testid="stSidebar"] {
        background-color: #0B1727 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0F4C81;
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #29B5E8;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Divider */
    hr {
        border-color: #29B5E8;
        opacity: 0.3;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #E3F2FD;
        border-left: 5px solid #29B5E8;
        border-radius: 8px;
    }
    
    .stSuccess {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #FFF4E6;
        border-left: 5px solid #FFA500;
        border-radius: 8px;
    }
    
    /* Filter Container */
    .filter-container {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F2F6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #29B5E8;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(41, 181, 232, 0.1);
    }

    /* PREMIUM SIDEBAR ENHANCEMENTS */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #E3F2FD;
    }

    /* Target the radio options specifically */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 8px !important;
    }

    /* Style for the radio items to look like nav links */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: transparent !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
        color: rgba(255, 255, 255, 0.7) !important;
        width: 100% !important;
        margin-bottom: 4px !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background-color: rgba(41, 181, 232, 0.15) !important;
        color: #29B5E8 !important;
        border: 1px solid rgba(41, 181, 232, 0.3) !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stRadio"] label p {
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* Sidebar Divider */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Sidebar Header Branding */
    .sidebar-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .sidebar-logo-text {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }

    /* Input/Select boxes in Sidebar */
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* Sidebar Fixed Bottom Footer */
    .sidebar-footer {
        margin-top: auto;
        padding: 2rem 0 1rem 0;
    }
    
    .sidebar-footer-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #FFFFFF;
        transition: all 0.3s;
    }
</style>
"""
