# StockPulse 360 - Advanced Analytics Guide

This guide explains the Advanced Analytics features for inventory optimization and impact analysis.

---

## 📊 Feature Overview

The Advanced Analytics module provides two key capabilities:
1. **ABC Analysis** - Classify items by value and importance
2. **Stockout Impact Analysis** - Calculate patient/beneficiary impact

---

## 🔤 ABC Analysis

### What is ABC Analysis?

ABC Analysis is an inventory categorization technique that divides items into three categories:

- **Category A (20%)**: High-value items contributing to ~80% of total value
  - Example: Insulin (₹500/unit)
  - **Management**: Tight control, frequent monitoring, accurate forecasting
  
- **Category B (30%)**: Medium-value items contributing to ~15% of total value
  - Example: ORS (₹10/unit)
  - **Management**: Moderate control, regular monitoring
  
- **Category C (50%)**: Low-value items contributing to ~5% of total value
  - Example: Paracetamol (₹5/unit)
  - **Management**: Simple controls, periodic review

### Views Created

#### 1. **abc_analysis**
Overall ABC classification across all locations:

```sql
SELECT * FROM abc_analysis;
```

**Columns:**
- `item` - Item name
- `total_value` - Total value (quantity × price)
- `total_quantity` - Total quantity issued
- `value_percentage` - % of total value
- `abc_category` - A, B, or C
- `management_priority` - 1 (high), 2 (medium), 3 (low)

#### 2. **abc_analysis_by_location**
ABC classification per location:

```sql
SELECT * FROM abc_analysis_by_location
WHERE location = 'Chennai';
```

**Use Case**: Different locations may have different ABC patterns

#### 3. **abc_summary_statistics**
Summary statistics by category:

```sql
SELECT * FROM abc_summary_statistics;
```

**Shows:**
- Item count per category
- Total value per category
- Pareto principle validation (80-20 rule)

### How to Use ABC Analysis

#### Step 1: View ABC Classification

```sql
-- See all items with their ABC category
SELECT 
    item,
    abc_category,
    category_description,
    total_value,
    value_percentage,
    management_priority
FROM abc_analysis
ORDER BY management_priority, total_value DESC;
```

#### Step 2: Focus on Category A Items

```sql
-- Get all Category A items (critical)
SELECT * FROM abc_analysis
WHERE abc_category = 'A';
```

**Action**: These items need:
- Daily monitoring
- Accurate demand forecasting
- Safety stock maintenance
- Multiple suppliers

#### Step 3: Optimize Category C Items

```sql
-- Get all Category C items (low value)
SELECT * FROM abc_analysis
WHERE abc_category = 'C';
```

**Action**: These items can have:
- Larger order quantities
- Less frequent monitoring
- Simpler forecasting methods

---

## 🏥 Stockout Impact Analysis

### What is Stockout Impact?

Calculates the potential impact on patients/beneficiaries if items run out of stock.

### Views Created

#### 1. **stockout_impact**
Detailed impact analysis for items at risk:

```sql
SELECT * FROM stockout_impact
ORDER BY action_priority;
```

**Key Metrics:**
- `patients_affected_until_stockout` - People affected before stock runs out
- `daily_patients_affected` - Daily impact if stock-out occurs
- `weekly_patients_affected` - Weekly impact projection
- `impact_severity` - LIFE_THREATENING, HIGH_SEVERITY, etc.
- `action_priority` - Priority ranking (1 = most urgent)

#### 2. **critical_items_dashboard**
Combines ABC analysis with stockout impact:

```sql
SELECT * FROM critical_items_dashboard;
```

**Shows:**
- ABC category
- Stock status
- Patient impact
- Recommended action
- Reorder quantity

### Impact Severity Levels

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| **LIFE_THREATENING** | Insulin + (OUT_OF_STOCK or CRITICAL) | Emergency order NOW |
| **HIGH_SEVERITY** | Critical medicines + CRITICAL status | Urgent reorder (24h) |
| **MODERATE_SEVERITY** | Any item + CRITICAL status | Reorder within 48h |
| **LOW_SEVERITY** | WARNING status | Schedule reorder |
| **MINIMAL** | All others | Monitor |

### How to Use Impact Analysis

#### Step 1: Identify Critical Situations

```sql
-- Items with life-threatening impact
SELECT 
    location,
    item,
    current_stock,
    days_until_stockout,
    patients_affected_until_stockout,
    impact_severity
FROM stockout_impact
WHERE impact_severity = 'LIFE_THREATENING';
```

#### Step 2: Calculate Total Impact

```sql
-- Total patients affected across all locations
SELECT
    item,
    SUM(patients_affected_until_stockout) AS total_patients_at_risk,
    SUM(daily_patients_affected) AS total_daily_impact,
    COUNT(DISTINCT location) AS affected_locations
FROM stockout_impact
GROUP BY item
ORDER BY total_patients_at_risk DESC;
```

#### Step 3: Prioritize Actions

```sql
-- Get prioritized action list
SELECT
    location,
    item,
    recommended_action,
    patients_affected_until_stockout,
    recommended_order_qty,
    order_urgency_days
FROM critical_items_dashboard
WHERE recommended_action IN ('EMERGENCY_ORDER_NOW', 'URGENT_REORDER_24H')
ORDER BY action_priority;
```

---

## 🎯 Combined Analysis

### Critical Items Dashboard

The **critical_items_dashboard** view combines ABC analysis with impact analysis:

```sql
SELECT
    location,
    item,
    abc_category,
    stock_status,
    patients_affected_until_stockout,
    impact_severity,
    recommended_action,
    recommended_order_qty
FROM critical_items_dashboard
ORDER BY action_priority;
```

### Decision Matrix

| ABC Category | Stock Status | Impact Severity | Action |
|--------------|--------------|-----------------|--------|
| A | CRITICAL | LIFE_THREATENING | Emergency order (same day) |
| A | CRITICAL | HIGH_SEVERITY | Urgent reorder (24h) |
| A | WARNING | MODERATE | Schedule reorder (48h) |
| B | CRITICAL | HIGH_SEVERITY | Reorder (48h) |
| B | WARNING | LOW | Schedule reorder (1 week) |
| C | CRITICAL | MODERATE | Reorder (3-5 days) |
| C | WARNING | LOW | Monitor, bulk order |

---

## 📈 Use Cases

### 1. **Budget Allocation**

```sql
-- Allocate budget based on ABC categories
SELECT
    abc_category,
    SUM(total_value) AS category_value,
    ROUND((SUM(total_value) / (SELECT SUM(total_value) FROM abc_analysis)) * 100, 2) AS budget_pct
FROM abc_analysis
GROUP BY abc_category;
```

**Recommended Budget Split:**
- Category A: 70-80% of budget
- Category B: 15-20% of budget
- Category C: 5-10% of budget

### 2. **Supplier Negotiations**

```sql
-- Identify items for bulk purchasing (Category C)
SELECT
    item,
    total_quantity,
    total_value,
    abc_category
FROM abc_analysis
WHERE abc_category = 'C'
ORDER BY total_quantity DESC;
```

**Strategy**: Negotiate bulk discounts for high-quantity, low-value items

### 3. **Safety Stock Calculation**

```sql
-- Calculate safety stock based on ABC category
SELECT
    h.location,
    h.item,
    a.abc_category,
    h.avg_daily_usage,
    h.lead_time_days,
    CASE a.abc_category
        WHEN 'A' THEN h.avg_daily_usage * (h.lead_time_days + 7)  -- 1 week buffer
        WHEN 'B' THEN h.avg_daily_usage * (h.lead_time_days + 3)  -- 3 days buffer
        WHEN 'C' THEN h.avg_daily_usage * (h.lead_time_days + 1)  -- 1 day buffer
    END AS recommended_safety_stock
FROM stock_health h
JOIN abc_analysis a ON h.item = a.item;
```

### 4. **Impact Reporting**

```sql
-- Generate impact report for management
SELECT
    'Total Patients at Risk' AS metric,
    SUM(patients_affected_until_stockout) AS value
FROM stockout_impact
UNION ALL
SELECT
    'Life-Threatening Situations',
    COUNT(*)
FROM stockout_impact
WHERE impact_severity = 'LIFE_THREATENING'
UNION ALL
SELECT
    'Emergency Orders Required',
    COUNT(*)
FROM critical_items_dashboard
WHERE recommended_action = 'EMERGENCY_ORDER_NOW';
```

---

## 🔧 Configuration

### Update Item Prices

Modify the `item_prices` table to reflect actual costs:

```sql
-- Update prices
UPDATE item_prices
SET unit_price = 550.00
WHERE item = 'Insulin';

-- Add new items
INSERT INTO item_prices (item, unit_price, currency, price_category)
VALUES ('Antibiotics', 150.00, 'INR', 'MEDIUM_VALUE');
```

### Adjust ABC Thresholds

Modify the percentile thresholds in `abc_analysis` view:

```sql
-- Current: A=20%, B=30%, C=50%
-- To change to A=15%, B=35%, C=50%:

CASE
    WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.15 THEN 'A'
    WHEN PERCENT_RANK() OVER (ORDER BY total_value DESC) <= 0.50 THEN 'B'
    ELSE 'C'
END AS abc_category
```

---

## 📊 Dashboard Integration

Add to Streamlit dashboard:

```python
# In streamlit/app.py

st.header("📊 Advanced Analytics")

tab1, tab2, tab3 = st.tabs(["ABC Analysis", "Impact Analysis", "Critical Dashboard"])

with tab1:
    st.subheader("ABC Classification")
    abc_data = session.table("abc_analysis").to_pandas()
    
    # Pie chart
    fig = px.pie(abc_data, values='TOTAL_VALUE', names='ABC_CATEGORY',
                 title='Value Distribution by ABC Category')
    st.plotly_chart(fig)
    
    st.dataframe(abc_data)

with tab2:
    st.subheader("Stockout Impact")
    impact_data = session.table("stockout_impact").to_pandas()
    
    # Bar chart
    fig = px.bar(impact_data, x='ITEM', y='PATIENTS_AFFECTED_UNTIL_STOCKOUT',
                 color='IMPACT_SEVERITY', title='Patient Impact by Item')
    st.plotly_chart(fig)

with tab3:
    st.subheader("Critical Items Dashboard")
    critical_data = session.table("critical_items_dashboard").to_pandas()
    st.dataframe(critical_data)
```

---

## 🎓 Best Practices

1. **Review ABC Categories Monthly**: Items may move between categories
2. **Update Prices Regularly**: Ensure accurate value calculations
3. **Monitor Category A Daily**: Critical items need constant attention
4. **Bulk Order Category C**: Reduce ordering costs
5. **Track Impact Metrics**: Report to management regularly
6. **Adjust Safety Stock**: Based on ABC category
7. **Prioritize by Impact**: Not just by value

---

**Your inventory is now optimized with enterprise-grade analytics! 📊**
