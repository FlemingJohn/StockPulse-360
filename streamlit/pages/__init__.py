"""
StockPulse 360 - Pages Module
Modular page rendering functions for the dashboard
"""

from .overview import render_overview_page
from .alerts import render_alerts_page
from .reorder import render_reorder_page
from .ai_ml import render_ai_ml_page
from .analytics import render_analytics_page
from .supplier import render_supplier_page
from .data_management.page import render_data_management_page

__all__ = [
    'render_overview_page',
    'render_alerts_page',
    'render_reorder_page',
    'render_ai_ml_page',
    'render_analytics_page',
    'render_supplier_page',
    'render_data_management_page'
]
