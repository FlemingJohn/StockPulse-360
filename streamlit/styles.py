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
    
    /* Alert Cards */
    .critical-alert {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE6E6 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #DC143C;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(220, 20, 60, 0.1);
    }
    
    .warning-alert {
        background: linear-gradient(135deg, #FFFEF5 0%, #FFF4E6 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #FFA500;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(255, 165, 0, 0.1);
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
    
    /* Sidebar - Snowflake Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F0F2F6 100%);
        border-right: 2px solid #29B5E8;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F2F6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #0F4C81;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        color: white;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
    
    /* Navigation Menu */
    .nav-item {
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background-color: #E3F2FD;
        transform: translateX(5px);
    }
    
    .nav-item-selected {
        background: linear-gradient(135deg, #29B5E8 0%, #1E88E5 100%);
        color: white;
        font-weight: 600;
    }
</style>
"""
