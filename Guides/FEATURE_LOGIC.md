# 🧠 StockPulse 360: Feature Implementation Logic

This document provides a deep-dive into the technical algorithms and logic powering each key feature of StockPulse 360.

---

## 1. 🤖 AI Seasonal Forecasting (`seasonal_forecaster.py`)

**Goal:** Predict future demand by identifying repeating patterns (e.g., higher on Mondays, lower on Sundays).

### ⚙️ The Algorithm
1.  **Weekly Pattern Analysis:** 
    *   Aggregates `RAW_STOCK` data by `DAYOFWEEK(last_updated_date)`.
    *   Calculates `AVG(issued_qty)` for each day (0=Sunday, 6=Saturday).
    *   Identifies if "Weekend" vs. "Weekday" usage differs significantly.
2.  **Seasonality Detection:**
    *   Calculates the **Coefficient of Variation (CV)**: `(Standard Deviation / Mean) * 100`.
    *   **Logic:**
        *   `HIGH_SEASONALITY`: CV > 30%
        *   `MODERATE_SEASONALITY`: CV > 15%
        *   `LOW_SEASONALITY`: CV <= 15%
3.  **Forecast Generation (7-Day Rolling):**
    *   **Base Forecast:** Average of the last 7 days' usage.
    *   **Seasonal Factor:** `(Avg usage for specific Day of Week) / (Overall Avg Usage)`.
    *   **Final Formula:** `Forecast = Base_Forecast * Seasonal_Factor`.

---

## 2. 🚨 Automated Alert System (`alert_sender.py`)

**Goal:** Provide timely warnings without causing "alert fatigue."

### ⚙️ The Strategy: Dual-Mode Execution
We separate alerts into two distinct workflows:

| Mode | Target | Schedule | Logic |
| :--- | :--- | :--- | :--- |
| **Immediate** | ⚡ **Out of Stock** | **Every 5 Mins** | Queries `stock_health` for `status = 'OUT_OF_STOCK'`. Sends instant notification only if critical. |
| **Daily** | 🌅 **Morning Report** | **Daily 8:00 AM** | Queries for **ALL** `CRITICAL` & `WARNING` items. Sends a consolidated summary email. |

### 🛑 Duplicate Prevention
*   **SQL Logic:** The `INSERT INTO alert_log` statement includes a `WHERE NOT EXISTS` clause.
*   **Rule:** It checks if an alert for the same `(location, item, date)` has been generated in the last **24 hours**. This ensures that the 5-minute task doesn't spam stakeholders 12 times an hour for the same ongoing stockout.

---

## 3. 📊 Advanced Analytics: ABC Analysis (`create_abc_view.py`)

**Goal:** Classify inventory by value to prioritize management efforts (Pareto Principle).

### ⚙️ The Logic
1.  **Valuation:**
    *   `Total Value = Total Issued Qty * Unit Price`
    *   *Note: Unit prices are currently standardized (Insulin=500, ORS=10, Paracetamol=5).*
2.  **Ranking:**
    *   Uses Window Function: `PERCENT_RANK() OVER (ORDER BY total_value DESC)`.
3.  **Classification Rules:**
    *   **Class A (High Value):** Top **20%** of items by value. (e.g., Insulin)
    *   **Class B (Medium Value):** Next **30%** of items. (e.g., ORS)
    *   **Class C (Low Value):** Bottom **50%** of items. (e.g., Paracetamol)

---

## 4. 📦 Smart Reorder Recommendations (`dynamic_tables.sql`)

**Goal:** Automatically calculate *when* and *how much* to order.

### ⚙️ The Logic
Calculations happen inside the `reorder_recommendations` Dynamic Table.

1.  **Days Until Stockout:**
    *   `Current Stock / Avg Daily Usage`
2.  **Reorder Point (ROP):**
    *   `Lead Time Demand (3 days) + Safety Stock`.
3.  **Order Quantity:**
    *   `Target Stock Level (30 days) - Current Stock`.
4.  **Priority Assignment:**
    *   **URGENT:** Days Until Stockout < 1
    *   **HIGH:** Days Until Stockout < 3 (Lead Time)
    *   **NORMAL:** Days Until Stockout < 7

---

## 5. 📅 Interactive Delivery Calendar (`delivery_schedule.py`)

**Goal:** Visualize incoming shipments on a timeline.

### ⚙️ The Logic
1.  **Data Loading:** Fetches `delivery_schedule` table.
2.  **Synthetic Injection (Demo Mode):**
    *   Since raw data may be outdated, the script detects the `MAX(date)`.
    *   If `MAX(date) < 2026-01-05`, it generates random "future" orders to populate the calendar view, ensuring a lively demo.
3.  **Type Safety (PyArrow Fix):**
    *   Crucially, `pd.to_datetime()` is strictly applied *after* merging real and synthetic data.
    *   This prevents `ArrowInvalid` errors caused by mixed String/Timestamp columns in Streamlit.
4.  **Component Stability:**
    *   Uses `key="delivery_calendar"` to prevent the component from flickering or resetting state during app re-runs.

---

**File Location:** `Guides/FEATURE_LOGIC.md`
