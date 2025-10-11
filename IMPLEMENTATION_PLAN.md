# IndoWater Prepaid Water Meter - Feature Implementation Plan

## Overview
Comprehensive feature addition for prepaid water meter management system including payments, analytics, customer portal, technician features, and AI automation.

---

## PHASE 1: PAYMENTS & BALANCE MANAGEMENT ⭐ (IN PROGRESS)

### Backend Tasks
- [x] Add API keys to .env file
- [ ] Install payment gateway libraries (midtransclient, xendit)
- [ ] Create payment models
  - Transaction model (reference_id, customer_id, amount, status, payment_method, etc.)
  - PaymentSettings model (mode: sandbox/live, active_gateways)
- [ ] Create payment_routes.py
  - POST /api/payments/create-midtrans - Create Midtrans Snap transaction
  - POST /api/payments/create-xendit - Create Xendit payment (VA/QR/E-wallet)
  - GET /api/payments/history - Get purchase history
  - GET /api/payments/:id - Get payment details
  - POST /api/webhooks/midtrans - Handle Midtrans notifications
  - POST /api/webhooks/xendit - Handle Xendit webhooks
- [ ] Create admin_payment_routes.py
  - GET /api/admin/payment-settings - Get payment configuration
  - PUT /api/admin/payment-settings - Update payment mode (sandbox/live)
- [ ] Create payment services
  - midtrans_service.py - Midtrans integration
  - xendit_service.py - Xendit integration
  - receipt_service.py - Generate digital receipts
- [ ] Update User/Customer model to include balance field
- [ ] Create balance update logic on successful payment

### Frontend Tasks
- [ ] Create BalancePurchase page
  - Amount input
  - Payment method selector (Midtrans/Xendit VA/QRIS/E-wallet)
  - Customer information form
- [ ] Create PaymentGateway components
  - MidtransPayment component (Snap integration)
  - XenditPayment component (VA/QR display)
- [ ] Create PurchaseHistory page
  - Transaction list with filters
  - Receipt download
  - Status indicators
- [ ] Create ReceiptViewer component
  - Digital receipt display
  - Download/Print options
- [ ] Create AdminPaymentSettings page (Admin only)
  - Mode switcher (Sandbox/Live)
  - Gateway configuration
  - Transaction dashboard

### Testing
- [ ] Test Midtrans Snap payment flow
- [ ] Test Xendit Virtual Account payment
- [ ] Test Xendit QRIS payment
- [ ] Test webhook processing for both gateways
- [ ] Test admin mode switching
- [ ] Test purchase history
- [ ] Test receipt generation

---

## PHASE 2: ANALYTICS & REPORTING ⭐

### Backend Tasks
- [ ] Create analytics_routes.py
  - GET /api/analytics/usage - Get usage data (day/week/month)
  - GET /api/analytics/trends - Get consumption trends
  - GET /api/analytics/predictions - AI-powered usage predictions
  - GET /api/analytics/comparison - Compare periods
  - POST /api/reports/export-pdf - Generate PDF report
  - POST /api/reports/export-excel - Generate Excel report
- [ ] Create WaterUsage collection seeding
- [ ] Implement consumption calculation logic
- [ ] Create PDF generation service (ReportLab)
- [ ] Create Excel generation service (openpyxl)
- [ ] Admin analytics endpoints with advanced metrics

### Frontend Tasks
- [ ] Create Analytics page
  - Water usage charts (Chart.js + Recharts)
  - Animated water level indicators
  - Period selectors (day/week/month)
- [ ] Create UsageComparison component
  - Side-by-side period comparison
  - Percentage changes
  - Visual indicators
- [ ] Create TrendsChart component
  - Line charts for consumption trends
  - Prediction visualization
- [ ] Create AdminDashboard enhancements
  - System-wide metrics
  - Revenue analytics
  - Customer statistics
  - Device status overview
- [ ] Export functionality (PDF/Excel download)

### Testing
- [ ] Test chart rendering with sample data
- [ ] Test period comparisons
- [ ] Test PDF export
- [ ] Test Excel export
- [ ] Test admin dashboard metrics

---

## PHASE 3: CUSTOMER PORTAL & SUPPORT

### Backend Tasks
- [ ] Create WaterConservationTip model
- [ ] Create SupportTicket model
- [ ] Create conservation_routes.py
  - GET /api/tips - Get water conservation tips
  - POST /api/tips - Create tip (admin)
- [ ] Create support_routes.py
  - POST /api/tickets - Create support ticket
  - GET /api/tickets - Get user tickets
  - PUT /api/tickets/:id - Update ticket
  - POST /api/tickets/:id/messages - Add message
  - GET /api/admin/tickets - Get all tickets (admin)
  - PUT /api/admin/tickets/:id/status - Update ticket status (admin)

### Frontend Tasks
- [ ] Create WaterTips component
  - Tip cards with categories
  - Savings calculator
- [ ] Create SupportTickets page
  - Create ticket form
  - Ticket list with status
  - Ticket detail view
  - Message thread
- [ ] Create AdminTickets page
  - All tickets dashboard
  - Status management
  - Quick responses
  - Analytics

### Testing
- [ ] Test tip display
- [ ] Test ticket creation
- [ ] Test ticket messaging
- [ ] Test admin ticket management

---

## PHASE 4: TECHNICIAN ENHANCEMENTS

### Backend Tasks
- [ ] Create route_optimization_service.py
  - Calculate optimal routes for field visits
  - Integration with mapping service
- [ ] Create offline_sync_routes.py
  - POST /api/offline/sync - Sync offline meter readings
  - POST /api/offline/queue - Queue offline data
- [ ] Create digital_signature_routes.py
  - POST /api/signatures/upload - Upload signature image
  - GET /api/signatures/:workOrderId - Get signature
- [ ] Update WorkOrder model to include signature field

### Frontend Tasks
- [ ] Create RouteOptimizer component
  - Daily task list
  - Optimized route display
  - Map integration
- [ ] Implement offline mode
  - Service worker for PWA
  - IndexedDB for local storage
  - Sync queue management
- [ ] Create SignaturePad component
  - Canvas-based signature capture
  - Save and attach to work orders
- [ ] Update MeterReading page with offline support
- [ ] Update TechnicianTasks with route optimization

### Testing
- [ ] Test route optimization
- [ ] Test offline data storage
- [ ] Test sync when back online
- [ ] Test signature capture and storage

---

## PHASE 5: AI & MOBILE (PWA)

### Backend Tasks
- [ ] Create ai_service.py
  - Usage prediction using OpenAI
  - Anomaly detection logic
  - Pattern recognition
- [ ] Create chatbot_routes.py
  - POST /api/chatbot/message - Send message to AI
  - GET /api/chatbot/history - Get chat history
- [ ] Create ai_analytics_routes.py
  - GET /api/ai/predict-usage - Predict future usage
  - GET /api/ai/detect-anomalies - Detect unusual patterns
  - POST /api/ai/analyze-pattern - Analyze usage patterns

### Frontend Tasks
- [ ] Create PWA configuration
  - manifest.json with app details
  - Service worker for offline support
  - Install prompt
- [ ] Create Chatbot component
  - Chat interface
  - OpenAI integration
  - Context-aware responses
- [ ] Create AIPredictions component
  - Usage forecast charts
  - Anomaly alerts
  - Recommendations
- [ ] Mobile optimizations
  - Responsive layouts
  - Touch-friendly interactions
  - Reduced data usage mode
- [ ] Camera improvements
  - Better OCR preprocessing
  - Multiple photo capture
  - Gallery preview

### Testing
- [ ] Test PWA installation
- [ ] Test offline functionality
- [ ] Test chatbot responses
- [ ] Test AI predictions accuracy
- [ ] Test anomaly detection
- [ ] Test mobile responsiveness

---

## Technical Stack Additions

### Backend Libraries
- midtransclient - Midtrans payment gateway
- xendit - Xendit payment gateway
- reportlab - PDF generation
- openpyxl - Excel generation
- openai - AI features
- Pillow - Image processing enhancements

### Frontend Libraries
- chart.js - Charts and graphs
- recharts - React charts
- react-chartjs-2 - Chart.js React wrapper
- signature_pad - Digital signatures
- workbox - PWA service worker
- react-pdf - PDF viewer
- xlsx - Excel export

---

## Implementation Strategy

1. **Incremental Development**: Complete each phase fully before moving to the next
2. **Testing First**: Test backend thoroughly before building frontend
3. **User Feedback**: Get feedback after each phase
4. **Documentation**: Update docs as features are added
5. **Performance**: Monitor and optimize as we go

---

## Current Status
**Phase 1: IN PROGRESS**
- API keys configured
- Starting backend payment integration
