"""Supplier page components"""

from .purchase_orders import render_purchase_orders
from .performance_metrics import render_performance_metrics
from .supplier_comparison import render_supplier_comparison
from .delivery_schedule import render_delivery_schedule

__all__ = [
    'render_purchase_orders',
    'render_performance_metrics', 
    'render_supplier_comparison',
    'render_delivery_schedule'
]
