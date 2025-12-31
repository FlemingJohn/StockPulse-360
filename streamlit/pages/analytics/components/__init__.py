"""Analytics page components"""

from .abc_analysis import render_abc_analysis
from .cost_optimization import render_cost_optimization
from .stockout_impact import render_stockout_impact

__all__ = ['render_abc_analysis', 'render_cost_optimization', 'render_stockout_impact']
