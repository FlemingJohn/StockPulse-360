# Streamlit Dashboard - Modular Structure

## 📁 File Organization

```
streamlit/
├── app_modular.py      # Main application (clean, ~130 lines)
├── styles.py           # All CSS styling
├── utils.py            # SVG icons, helpers, data loaders
├── pages.py            # All page rendering functions
├── app.py              # Original monolithic version (backup)
└── page_functions.py   # Old helper file (can be deleted)
```

## 🎯 Benefits of Modular Structure

### 1. **Easy to Edit**
- **Styles**: Edit `styles.py` to change colors, fonts, spacing
- **Icons**: Add/modify SVG icons in `utils.py`
- **Pages**: Edit individual page functions in `pages.py`
- **Navigation**: Modify routing in `app_modular.py`

### 2. **Better Organization**
- Each file has a single responsibility
- No need to scroll through 1000+ lines
- Clear separation of concerns

### 3. **Easier Testing**
- Test individual page functions independently
- Mock data loaders from `utils.py`
- Isolate CSS changes

### 4. **Team Collaboration**
- Multiple developers can work on different pages
- Fewer merge conflicts
- Clear ownership of components

## 🚀 Usage

### Run the Modular Version
```bash
py -m streamlit run streamlit/app_modular.py
```

### Run the Original Version
```bash
py -m streamlit run streamlit/app.py
```

## 📝 Quick Edit Guide

### Change Colors
**File**: `styles.py`
```python
# Edit the color palette
:root {
    --snowflake-blue: #29B5E8;      # Change this
    --snowflake-dark-blue: #1E88E5; # And this
    ...
}
```

### Add a New SVG Icon
**File**: `utils.py`
```python
def get_svg_icon(icon_name, size=24, color="#29B5E8"):
    icons = {
        'your_icon': f'''<svg>...</svg>''',  # Add here
        ...
    }
```

### Modify a Page
**File**: `pages.py`
```python
def render_overview_page(filtered_data):
    # Edit this function to change the Overview page
    ...
```

### Add a New Navigation Page
1. **Add function in `pages.py`**:
   ```python
   def render_new_page(filtered_data):
       st.markdown(section_header("New Page", "icon_name"))
       # Your content here
   ```

2. **Import in `app_modular.py`**:
   ```python
   from pages import (..., render_new_page)
   ```

3. **Add to navigation menu**:
   ```python
   nav_options = [
       "Overview & Heatmap",
       "New Page",  # Add here
       ...
   ]
   ```

4. **Add routing**:
   ```python
   elif selected_page == "New Page":
       render_new_page(filtered_data)
   ```

## 🔄 Migration Path

### Option 1: Use Modular Version (Recommended)
```bash
# Rename files
mv streamlit/app.py streamlit/app_old.py
mv streamlit/app_modular.py streamlit/app.py
```

### Option 2: Keep Both Versions
- Use `app_modular.py` for development
- Keep `app.py` as fallback
- Test thoroughly before switching

## 📦 Module Details

### `styles.py` (200 lines)
- All CSS in one place
- Snowflake color palette
- Component styles (cards, buttons, alerts)
- Layout styles (filter container, navigation)

### `utils.py` (180 lines)
- 12 SVG icons (chart, box, alert, location, etc.)
- `section_header()` helper
- Data loading functions with caching
- `get_status_color()` helper

### `pages.py` (350 lines)
- `render_filters()` - Filter component
- `render_overview_page()` - Heatmap & metrics
- `render_alerts_page()` - Critical alerts
- `render_reorder_page()` - Procurement
- `render_ai_ml_page()` - AI/ML features
- `render_analytics_page()` - Advanced analytics
- `render_supplier_page()` - Supplier management

### `app_modular.py` (130 lines)
- Page configuration
- Header rendering
- Sidebar navigation
- Page routing
- Footer

## 🎨 Customization Examples

### Change Button Style
**File**: `styles.py`
```css
.stButton>button {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); /* New gradient */
    border-radius: 20px; /* More rounded */
}
```

### Add Custom Metric Card
**File**: `pages.py`
```python
def render_custom_metric(title, value, icon):
    st.markdown(f'''
    <div class="metric-card">
        {get_svg_icon(icon, size=32)}
        <h3>{title}</h3>
        <p style="font-size: 2rem; font-weight: bold;">{value}</p>
    </div>
    ''', unsafe_allow_html=True)
```

### Modify Filter Layout
**File**: `pages.py` → `render_filters()`
```python
# Change from 4 columns to 3 columns
col1, col2, col3 = st.columns(3)  # Instead of [2,2,2,1]
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the streamlit directory
cd streamlit
py -m streamlit run app_modular.py
```

### Module Not Found
```python
# Add parent directory to path (already in app_modular.py)
import sys, os
sys.path.append(os.path.dirname(__file__))
```

### Session State Issues
```python
# Session is stored in st.session_state['session']
# Access it in utils.py data loaders
session = st.session_state.get('session')
```

## ✅ Next Steps

1. **Test the modular version**: `py -m streamlit run streamlit/app_modular.py`
2. **Make small edits**: Try changing a color in `styles.py`
3. **Add content**: Populate AI/ML and Analytics pages
4. **Switch to modular**: Rename `app_modular.py` to `app.py`
5. **Clean up**: Delete old `page_functions.py` if not needed

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Snowflake Streamlit Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
