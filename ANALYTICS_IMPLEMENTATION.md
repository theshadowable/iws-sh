# Analytics & Reporting Implementation

## Overview
This document tracks the implementation of analytics, reporting, and AI prediction features for the IndoWater prepaid water meter system.

**Implementation Date:** January 2025
**Status:** In Progress

---

## Phase 1: Payment Configuration ✅

### Backend Configuration
- **Payment Gateway Keys:** Configured in `/app/backend/.env`
  - Midtrans Sandbox: Server Key, Client Key, Merchant ID
  - Xendit Sandbox: Secret Key, Public Key, Webhook Token
  - OpenAI API Key: For future AI features
  - Payment Mode: Set to "sandbox"

### Payment Services
- **File:** `midtrans_service.py`
  - Gracefully handles missing API keys
  - Provides `enabled` flag to check if service is available
  
- **File:** `xendit_service.py`
  - Gracefully handles missing API keys
  - Provides `enabled` flag to check if service is available

### Payment Routes
- **File:** `payment_routes.py`
  - POST `/api/payments/create-midtrans` - Midtrans Snap payment
  - POST `/api/payments/create-xendit-va` - Xendit Virtual Account
  - POST `/api/payments/create-xendit-qris` - Xendit QRIS
  - POST `/api/payments/create-xendit-ewallet` - Xendit E-wallet
  - GET `/api/payments/history/list` - Purchase history with pagination
  - GET `/api/payments/{reference_id}` - Payment details

- **File:** `admin_payment_routes.py`
  - GET `/api/admin/payment-settings` - Get payment configuration
  - PUT `/api/admin/payment-settings` - Update settings
  - GET `/api/admin/payment-settings/statistics` - Payment statistics
  - GET `/api/admin/payment-settings/transactions/export` - Export transactions

---

## Phase 2: Analytics & Reporting (Current)

### Database Collections

#### WaterUsage Collection
```javascript
{
  id: string,
  device_id: string,
  customer_id: string,
  property_id: string,
  reading_value: float,  // in cubic meters (m³)
  reading_date: datetime,
  consumption: float,  // consumption since last reading (m³)
  cost: float,  // cost in IDR
  meter_status: string,  // active, inactive, maintenance
  recorded_at: datetime,
  recorded_by: string,  // technician_id or "system"
  notes: string
}
```

### Backend Implementation

#### 1. Analytics Routes (`analytics_routes.py`)

**Endpoints:**
- `GET /api/analytics/usage` - Get usage data with filters
  - Query params: `period` (day/week/month/year), `start_date`, `end_date`, `customer_id`
  - Returns: Daily/weekly/monthly consumption data
  
- `GET /api/analytics/trends` - Get consumption trends
  - Query params: `period`, `customer_id`
  - Returns: Trend data with growth rates
  
- `GET /api/analytics/predictions` - Simple statistical predictions
  - Uses moving average algorithm
  - Query params: `customer_id`, `days_ahead` (default: 7)
  - Returns: Predicted consumption for next N days
  
- `GET /api/analytics/comparison` - Compare periods
  - Query params: `period1_start`, `period1_end`, `period2_start`, `period2_end`, `customer_id`
  - Returns: Side-by-side comparison with percentage changes

- `GET /api/analytics/admin/overview` - Admin system-wide analytics
  - Returns: Total consumption, active devices, revenue, top consumers

#### 2. Report Generation Routes (`report_routes.py`)

**Endpoints:**
- `POST /api/reports/export-pdf` - Generate PDF report
  - Uses ReportLab library
  - Request body: `{customer_id, start_date, end_date, report_type}`
  - Returns: PDF file with charts and tables
  
- `POST /api/reports/export-excel` - Generate Excel report
  - Uses openpyxl library
  - Request body: `{customer_id, start_date, end_date, include_charts}`
  - Returns: Excel file with data and optional charts

#### 3. Data Generation Script (`seed_water_usage.py`)
- Generates 6 months of realistic water usage data
- Multiple customers with varying consumption patterns
- Includes seasonal variations
- Adds some anomalies for testing

### Frontend Implementation

#### 1. Analytics Page (`/analytics`)

**Components:**
- **UsageChart** - Line/bar chart showing consumption over time
- **UsageStatistics** - KPI cards (total usage, average, cost)
- **PeriodSelector** - Date range picker and preset periods
- **TrendIndicator** - Shows growth/decline with percentage
- **PredictionChart** - Visualization of predicted usage
- **ComparisonView** - Side-by-side period comparison

**Features:**
- Interactive charts using Recharts
- Period filters (day, week, month, year)
- Export buttons (PDF, Excel)
- Real-time data updates
- Responsive design

#### 2. Admin Analytics Dashboard (`/admin/analytics`)

**Components:**
- **SystemOverview** - System-wide metrics
- **RevenueChart** - Revenue trends
- **CustomerAnalytics** - Top consumers, inactive customers
- **DeviceStatus** - Device health and status
- **PaymentAnalytics** - Payment method breakdown
- **ExportTools** - Bulk export functionality

### Prediction Algorithm

**Moving Average Prediction:**
```python
def predict_usage(historical_data, days_ahead=7):
    """
    Simple moving average prediction
    - Uses last 30 days of data
    - Calculates 7-day moving average
    - Projects forward based on trend
    """
    # Calculate moving average
    # Identify trend (increasing/decreasing)
    # Apply seasonal factors if detected
    # Generate predictions for N days ahead
    return predictions
```

---

## Phase 3: Testing

### Backend Testing
- [ ] Test all analytics endpoints with sample data
- [ ] Verify prediction accuracy
- [ ] Test PDF generation
- [ ] Test Excel export
- [ ] Test admin analytics endpoints
- [ ] Verify date range filtering
- [ ] Test pagination and limits

### Frontend Testing
- [ ] Chart rendering with various data ranges
- [ ] Period selector functionality
- [ ] Export button functionality
- [ ] Responsive design on mobile
- [ ] Loading states
- [ ] Error handling
- [ ] Empty state displays

---

## Implementation Progress

### Completed ✅
- Payment gateway configuration
- Payment services with graceful error handling
- Backend restart with new API keys

### In Progress 🔄
- Generating water usage sample data
- Creating analytics backend routes
- Building analytics frontend components

### Pending ⏳
- PDF report generation
- Excel report export
- Admin analytics dashboard
- Prediction algorithm refinement
- Documentation updates

---

## Files Created/Modified

### Backend
- `/app/backend/.env` - Added payment gateway keys ✅
- `/app/backend/midtrans_service.py` - Added graceful error handling ✅
- `/app/backend/xendit_service.py` - Added graceful error handling ✅
- `/app/backend/analytics_routes.py` - To be created
- `/app/backend/report_routes.py` - To be created
- `/app/backend/seed_water_usage.py` - To be created
- `/app/backend/analytics_models.py` - To be created

### Frontend
- `/app/frontend/src/pages/Analytics.js` - To be created
- `/app/frontend/src/pages/AdminAnalytics.js` - To be created
- `/app/frontend/src/components/UsageChart.js` - To be created
- `/app/frontend/src/components/PredictionChart.js` - To be created
- `/app/frontend/src/components/ComparisonView.js` - To be created

### Documentation
- `/app/ANALYTICS_IMPLEMENTATION.md` - This file ✅

---

## Next Steps

1. Create water usage sample data script
2. Implement analytics backend routes
3. Create analytics models
4. Build frontend analytics components
5. Integrate charts and visualizations
6. Add export functionality
7. Test end-to-end
8. Update test_result.md

---

## Notes

- All analytics use the existing WaterUsage collection
- Predictions use simple statistical methods (moving averages)
- Reports are generated on-demand (not cached)
- Admin can view system-wide analytics
- Customers can only view their own data
- All dates are in UTC, displayed in local timezone on frontend
