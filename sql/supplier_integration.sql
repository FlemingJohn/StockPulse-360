-- ============================================================================
-- StockPulse 360 - Supplier Integration
-- ============================================================================
-- Supplier management, lead time tracking, and purchase order generation
-- ============================================================================

USE DATABASE stockpulse_db;
USE SCHEMA public;

-- ============================================================================
-- Table 1: Suppliers
-- ============================================================================
-- Track supplier information, lead times, and reliability

CREATE OR REPLACE TABLE suppliers (
    supplier_id STRING PRIMARY KEY,
    supplier_name STRING NOT NULL,
    item STRING NOT NULL,
    avg_lead_time_days NUMBER(5,2) DEFAULT 7,
    reliability_score NUMBER(5,2) DEFAULT 100,  -- 0-100 scale
    unit_price NUMBER(10,2),
    contact_email STRING,
    contact_phone STRING,
    address STRING,
    last_delivery_date DATE,
    total_orders NUMBER DEFAULT 0,
    on_time_deliveries NUMBER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Supplier master data with performance tracking';

-- Insert sample suppliers
-- Insert sample suppliers
INSERT INTO suppliers (supplier_id, supplier_name, item, avg_lead_time_days, reliability_score, unit_price, contact_email, contact_phone, last_delivery_date, total_orders, on_time_deliveries)
VALUES
    -- Insulin Suppliers
    ('SUP001', 'MedSupply Co.', 'Insulin', 3, 95, 500.00, 'orders@medsupply.com', '+91-9876543210', '2024-11-28', 50, 48),
    ('SUP002', 'QuickMeds Ltd', 'Insulin', 1, 85, 520.00, 'sales@quickmeds.com', '+91-9876543211', '2024-11-30', 30, 26),
    ('SUP018', 'Global Insulin Inc', 'Insulin', 2, 92, 490.00, 'support@globalinsulin.com', '+91-9876543227', '2024-11-29', 40, 37),
    ('SUP043', 'Bharat Insulin', 'Insulin', 4, 98, 480.00, 'sales@bharatinsulin.in', '+91-9876543252', '2024-12-01', 15, 14),
    
    -- ORS Suppliers
    ('SUP003', 'PharmaDirect', 'ORS', 2, 98, 10.00, 'info@pharmadirect.com', '+91-9876543212', '2024-11-29', 100, 98),
    ('SUP004', 'HealthPlus Supplies', 'ORS', 4, 92, 9.50, 'orders@healthplus.com', '+91-9876543213', '2024-11-27', 45, 42),
    ('SUP019', 'PureHydrate', 'ORS', 1, 88, 11.00, 'sales@purehydrate.com', '+91-9876543228', '2024-12-01', 20, 18),
    ('SUP044', 'Sanjeevani ORS', 'ORS', 3, 95, 9.80, 'orders@sanjeevani_ors.com', '+91-9876543253', '2024-11-28', 35, 33),
    
    -- Paracetamol Suppliers
    ('SUP005', 'MediCare Distributors', 'Paracetamol', 2, 96, 5.00, 'sales@medicare.com', '+91-9876543214', '2024-11-29', 80, 77),
    ('SUP006', 'FastPharma', 'Paracetamol', 1, 88, 5.20, 'orders@fastpharma.com', '+91-9876543215', '2024-11-30', 25, 22),
    ('SUP020', 'ReliefPills Co', 'Paracetamol', 3, 94, 4.80, 'info@reliefpills.com', '+91-9876543229', '2024-11-28', 60, 56),
    ('SUP045', 'SafePain Ltd', 'Paracetamol', 2, 91, 5.10, 'sales@safepain.com', '+91-9876543254', '2024-11-30', 40, 36),

    -- Antibiotics Suppliers
    ('SUP007', 'AntibioCare', 'Antibiotics', 3, 94, 150.00, 'sales@antibiocare.com', '+91-9876543216', '2024-11-28', 60, 58),
    ('SUP021', 'Global Pharma', 'Antibiotics', 2, 91, 145.00, 'orders@globalpharma.com', '+91-9876543230', '2024-12-01', 30, 27),
    ('SUP022', 'NanoMeds', 'Antibiotics', 1, 85, 160.00, 'sales@nanomeds.com', '+91-9876543231', '2024-11-30', 40, 34),
    ('SUP046', 'Dr Reddy Lab', 'Antibiotics', 2, 97, 155.00, 'info@drreddylab.com', '+91-9876543255', '2024-11-29', 100, 97),

    -- Aspirin Suppliers
    ('SUP008', 'PainRelief Inc', 'Aspirin', 2, 90, 4.50, 'orders@painrelief.com', '+91-9876543217', '2024-11-29', 40, 38),
    ('SUP023', 'AspirinPlus', 'Aspirin', 1, 95, 4.80, 'sales@aspirinplus.com', '+91-9876543232', '2024-11-28', 50, 48),
    ('SUP024', 'ValueMeds', 'Aspirin', 3, 82, 4.20, 'info@valuemeds.com', '+91-9876543233', '2024-11-30', 20, 16),
    ('SUP047', 'CommonHealth', 'Aspirin', 2, 88, 4.90, 'sales@commonhealth.com', '+91-9876543256', '2024-11-29', 30, 26),

    -- BP Monitor Suppliers
    ('SUP009', 'MediTech Devices', 'BP Monitor', 5, 97, 1200.00, 'sales@meditech.com', '+91-9876543218', '2024-11-25', 20, 20),
    ('SUP025', 'HealthTech', 'BP Monitor', 4, 91, 1150.00, 'orders@healthtech.com', '+91-9876543234', '2024-11-26', 15, 13),
    ('SUP026', 'PrecisionCare', 'BP Monitor', 3, 89, 1300.00, 'sales@precisioncare.com', '+91-9876543235', '2024-11-27', 10, 9),
    ('SUP048', 'Omron Pro', 'BP Monitor', 2, 99, 1400.00, 'support@omronpro.in', '+91-9876543257', '2024-12-01', 50, 50),

    -- Bandages Suppliers
    ('SUP010', 'SurgicalNeeds', 'Bandages', 1, 99, 15.00, 'orders@surgicalneeds.com', '+91-9876543219', '2024-11-30', 150, 149),
    ('SUP027', 'QuickWrap', 'Bandages', 2, 94, 14.50, 'sales@quickwrap.com', '+91-9876543236', '2024-11-28', 80, 75),
    ('SUP028', 'SafeCover Co', 'Bandages', 3, 88, 14.00, 'info@safecover.com', '+91-9876543237', '2024-11-29', 50, 44),

    -- Gloves Suppliers
    ('SUP011', 'SafetyFirst', 'Gloves', 2, 93, 8.00, 'sales@safetyfirst.com', '+91-9876543220', '2024-11-28', 200, 190),
    ('SUP029', 'HandGuard', 'Gloves', 3, 96, 8.50, 'orders@handguard.com', '+91-9876543238', '2024-11-27', 150, 144),
    ('SUP030', 'ProTouch', 'Gloves', 1, 85, 9.00, 'sales@protouch.com', '+91-9876543239', '2024-11-30', 100, 85),

    -- Glucose Test Strips Suppliers
    ('SUP012', 'DiabeticCare', 'Glucose Test Strips', 2, 96, 25.00, 'orders@diabeticcare.com', '+91-9876543221', '2024-11-29', 80, 78),
    ('SUP031', 'StripTech', 'Glucose Test Strips', 3, 92, 24.50, 'sales@striptech.com', '+91-9876543240', '2024-12-01', 60, 55),
    ('SUP032', 'SugarMonitor Inc', 'Glucose Test Strips', 1, 87, 26.00, 'info@sugarmonitor.com', '+91-9876543241', '2024-11-30', 40, 35),

    -- IV Fluids Suppliers
    ('SUP013', 'FluidSystems', 'IV Fluids', 3, 91, 45.00, 'sales@fluidsystems.com', '+91-9876543222', '2024-11-27', 70, 65),
    ('SUP033', 'AquaMed', 'IV Fluids', 2, 94, 46.00, 'orders@aquamed.com', '+91-9876543242', '2024-11-28', 50, 47),
    ('SUP034', 'SafeDrop Fluids', 'IV Fluids', 4, 88, 44.00, 'info@safedrop.com', '+91-9876543243', '2024-11-29', 40, 35),

    -- Masks Suppliers
    ('SUP014', 'ProtectMed', 'Masks', 1, 98, 5.00, 'orders@protectmed.com', '+91-9876543223', '2024-11-30', 300, 295),
    ('SUP035', 'BreathSafe', 'Masks', 2, 95, 4.80, 'sales@breathsafe.com', '+91-9876543244', '2024-11-28', 200, 190),
    ('SUP036', 'ClearAir Inc', 'Masks', 3, 85, 4.50, 'info@clearair.com', '+91-9876543245', '2024-11-29', 150, 125),

    -- Oxygen Cylinders Suppliers
    ('SUP015', 'OxyGen', 'Oxygen Cylinders', 1, 99, 4500.00, 'sales@oxygen.com', '+91-9876543224', '2024-11-30', 10, 10),
    ('SUP037', 'PureO2', 'Oxygen Cylinders', 2, 96, 4600.00, 'orders@pureo2.com', '+91-9876543246', '2024-11-29', 8, 7),
    ('SUP038', 'VitalAir Systems', 'Oxygen Cylinders', 3, 91, 4400.00, 'sales@vitalair.com', '+91-9876543247', '2024-11-28', 12, 11),

    -- Syringes Suppliers
    ('SUP016', 'InjectSafe', 'Syringes', 2, 95, 3.00, 'orders@injectsafe.com', '+91-9876543225', '2024-11-29', 120, 115),
    ('SUP039', 'SharpMeds', 'Syringes', 3, 91, 3.20, 'sales@sharpmeds.com', '+91-9876543248', '2024-11-28', 90, 82),
    ('SUP040', 'PrecisionInjections', 'Syringes', 1, 88, 3.50, 'orders@precisioninjections.com', '+91-9876543249', '2024-11-30', 100, 88),

    -- Thermometers Suppliers
    ('SUP017', 'TempCheck', 'Thermometers', 4, 92, 350.00, 'sales@tempcheck.com', '+91-9876543226', '2024-11-26', 30, 28),
    ('SUP041', 'DigiTemp Ltd', 'Thermometers', 3, 95, 370.00, 'orders@digitemp.com', '+91-9876543250', '2024-11-27', 25, 24),
    ('SUP042', 'BodyScanners Co', 'Thermometers', 5, 85, 330.00, 'sales@bodyscanners.com', '+91-9876543251', '2024-11-25', 15, 12);

-- ============================================================================
-- View 1: Purchase Orders
-- ============================================================================
-- Auto-generate purchase orders from reorder recommendations

CREATE OR REPLACE VIEW purchase_orders AS
WITH best_suppliers AS (
    -- Select best supplier for each item based on reliability and lead time
    SELECT
        item,
        supplier_id,
        supplier_name,
        avg_lead_time_days,
        reliability_score,
        unit_price,
        contact_email,
        ROW_NUMBER() OVER (
            PARTITION BY item 
            ORDER BY reliability_score DESC, avg_lead_time_days ASC, unit_price ASC
        ) as supplier_rank
    FROM suppliers
    WHERE is_active = TRUE
)
SELECT
    CONCAT('PO-', TO_CHAR(CURRENT_DATE(), 'YYYYMMDD'), '-', 
           LPAD(ROW_NUMBER() OVER (ORDER BY r.location, r.item), 4, '0')) AS purchase_order_id,
    r.location AS location,
    r.item AS item,
    s.supplier_id,
    s.supplier_name,
    s.contact_email,
    r.reorder_quantity AS order_quantity,
    s.unit_price,
    r.reorder_quantity * s.unit_price AS total_cost,
    s.avg_lead_time_days,
    CURRENT_DATE() AS order_date,
    CURRENT_DATE() + s.avg_lead_time_days AS expected_delivery_date,
    r.days_until_stockout AS order_urgency_days,
    CASE
        WHEN r.days_until_stockout < s.avg_lead_time_days THEN 'URGENT'
        WHEN r.days_until_stockout < (s.avg_lead_time_days * 1.5) THEN 'NORMAL'
        ELSE 'PLANNED'
    END AS order_priority,
    s.reliability_score,
    h.stock_status,
    CURRENT_TIMESTAMP() AS generated_at
FROM reorder_recommendations r
JOIN best_suppliers s ON r.item = s.item AND s.supplier_rank = 1
JOIN stock_health h ON r.location = h.location AND r.item = h.item;

-- ============================================================================
-- View 2: Supplier Performance Dashboard
-- ============================================================================
-- Track supplier reliability and performance metrics

CREATE OR REPLACE VIEW supplier_performance AS
SELECT
    supplier_id,
    supplier_name,
    item,
    avg_lead_time_days,
    reliability_score,
    unit_price,
    total_orders,
    on_time_deliveries,
    ROUND((on_time_deliveries * 100.0 / NULLIF(total_orders, 0)), 2) AS actual_on_time_pct,
    CASE
        WHEN reliability_score >= 95 THEN 'EXCELLENT'
        WHEN reliability_score >= 85 THEN 'GOOD'
        WHEN reliability_score >= 70 THEN 'AVERAGE'
        ELSE 'POOR'
    END AS performance_rating,
    DATEDIFF(day, last_delivery_date, CURRENT_DATE()) AS days_since_last_delivery,
    CASE
        WHEN DATEDIFF(day, last_delivery_date, CURRENT_DATE()) > 30 THEN 'INACTIVE'
        WHEN DATEDIFF(day, last_delivery_date, CURRENT_DATE()) > 14 THEN 'LOW_ACTIVITY'
        ELSE 'ACTIVE'
    END AS activity_status,
    is_active
FROM suppliers
ORDER BY reliability_score DESC, avg_lead_time_days ASC;

-- ============================================================================
-- View 3: Supplier Comparison
-- ============================================================================
-- Compare suppliers for the same item

CREATE OR REPLACE VIEW supplier_comparison AS
WITH supplier_metrics AS (
    SELECT
        item,
        supplier_name,
        unit_price,
        avg_lead_time_days,
        reliability_score,
        MIN(unit_price) OVER (PARTITION BY item) as min_price_per_item
    FROM suppliers
    WHERE is_active = TRUE
)
SELECT
    item,
    supplier_name,
    unit_price,
    avg_lead_time_days,
    reliability_score,
    -- Calculate score (higher is better)
    ROUND(
        (reliability_score * 0.5) +  -- 50% weight on reliability
        ((100 - (avg_lead_time_days * 10)) * 0.3) +  -- 30% weight on speed
        ((100 - ((unit_price / NULLIF(min_price_per_item, 0) - 1) * 100)) * 0.2),  -- 20% weight on price
        2
    ) AS overall_score,
    RANK() OVER (PARTITION BY item ORDER BY 
        (reliability_score * 0.5) + 
        ((100 - (avg_lead_time_days * 10)) * 0.3) + 
        ((100 - ((unit_price / NULLIF(min_price_per_item, 0) - 1) * 100)) * 0.2) DESC
    ) AS supplier_rank
FROM supplier_metrics
ORDER BY item, supplier_rank;

-- ============================================================================
-- View 4: Purchase Order Summary
-- ============================================================================
-- Summarize purchase orders by location and priority

CREATE OR REPLACE VIEW purchase_order_summary AS
SELECT
    location,
    order_priority,
    COUNT(*) AS total_orders,
    SUM(order_quantity) AS total_quantity,
    SUM(total_cost) AS total_cost,
    AVG(avg_lead_time_days) AS avg_delivery_days,
    MIN(expected_delivery_date) AS earliest_delivery,
    MAX(expected_delivery_date) AS latest_delivery,
    COUNT(DISTINCT supplier_id) AS unique_suppliers
FROM purchase_orders
GROUP BY location, order_priority
ORDER BY 
    CASE order_priority
        WHEN 'URGENT' THEN 1
        WHEN 'NORMAL' THEN 2
        WHEN 'PLANNED' THEN 3
    END,
    location;

-- ============================================================================
-- View 5: Supplier Cost Analysis
-- ============================================================================
-- Analyze total spending by supplier

CREATE OR REPLACE VIEW supplier_cost_analysis AS
SELECT
    s.supplier_id,
    s.supplier_name,
    COUNT(DISTINCT p.item) AS items_supplied,
    SUM(p.order_quantity) AS total_units_ordered,
    SUM(p.total_cost) AS total_spend,
    AVG(p.total_cost) AS avg_order_value,
    COUNT(*) AS total_purchase_orders,
    s.reliability_score,
    s.avg_lead_time_days
FROM purchase_orders p
JOIN suppliers s ON p.supplier_id = s.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.reliability_score, s.avg_lead_time_days
ORDER BY total_spend DESC;

-- ============================================================================
-- View 6: Delivery Schedule
-- ============================================================================
-- Track expected deliveries by date

CREATE OR REPLACE VIEW delivery_schedule AS
SELECT
    order_date,
    expected_delivery_date,
    location,
    item,
    supplier_name,
    order_quantity,
    total_cost,
    order_priority,
    stock_status,
    CASE
        WHEN expected_delivery_date = CURRENT_DATE() THEN 'TODAY'
        WHEN expected_delivery_date = CURRENT_DATE() + 1 THEN 'TOMORROW'
        WHEN expected_delivery_date <= CURRENT_DATE() + 7 THEN 'THIS_WEEK'
        ELSE 'LATER'
    END AS delivery_timeframe
FROM purchase_orders
ORDER BY expected_delivery_date, order_priority;
