"""Reorder page components"""

from .simulation_slider import render_simulation_controls
from .strategy_matrix import render_strategy_matrix
from .recommendations_table import render_recommendations_table

__all__ = ['render_simulation_controls', 'render_strategy_matrix', 'render_recommendations_table']
