# 🍽️ Restaurant System - Complete Flow Diagram

## 🎯 Customer Journey with Bill Popup & Status Tracking

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CUSTOMER FLOW                               │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ Customer Scans QR Code
   ↓
   📱 Opens: /menu?table=5

2️⃣ Menu Page Loads (MenuOrderPage.jsx)
   ↓
   - Browse by category (Appetizers, Main, Desserts, Beverages)
   - View items with images, ratings, prep time
   - Click "Add +" to add items to cart
   - Cart badge shows item count

3️⃣ Customer Clicks Cart Button
   ↓
   - Sidebar slides in from right (Framer Motion)
   - Shows all selected items
   - Quantity controls (+ / -)
   - Subtotal + Tax + Total displayed

4️⃣ Customer Clicks "Place Order 🎉"
   ↓
   - POST /api/order
   - Backend creates order in MongoDB
   - Backend emits Socket.io event: "newOrder"
   - Navigates to: /order-status?table=5&orderId=xxx

5️⃣ 💳 BILL POPUP APPEARS (Instant!)
   ├─────────────────────────────────────┐
   │  🎉 Order Confirmed!                │
   │  Table 5 • Order #abc123            │
   │  ┌─────────────────────────────┐   │
   │  │ 2x Margherita Pizza   ₹598  │   │
   │  │ 1x Caesar Salad      ₹199  │   │
   │  │ ─────────────────────────── │   │
   │  │ Subtotal            ₹797   │   │
   │  │ Tax (5%)            ₹39.85 │   │
   │  │ Total               ₹836.85│   │
   │  └─────────────────────────────┘   │
   │                                     │
   │  ⏱️ Estimated Time: 15-20 min      │
   │                                     │
   │  [Track Order]  [Chat with Us]     │
   └─────────────────────────────────────┘
   ↓
   - Auto-hides after 10 seconds
   - Can be dismissed manually
   - Click "Track Order" to see status

6️⃣ 📊 ORDER STATUS TRACKER (OrderStatusTracker.jsx)
   ├─────────────────────────────────────┐
   │  Table 5 • Order #abc123            │
   │                                     │
   │  Order Status:                      │
   │  ● ✅ Order Placed                  │
   │  │                                  │
   │  ● ⏳ Confirmed (waiting...)        │
   │  │                                  │
   │  ● ⏳ Being Prepared (waiting...)   │
   │  │                                  │
   │  ● ⏳ Ready to Serve (waiting...)   │
   │  │                                  │
   │  ● ⏳ Served (waiting...)           │
   │                                     │
   │  Your Order:                        │
   │  2x Margherita Pizza   ₹598        │
   │  1x Caesar Salad      ₹199         │
   │  ─────────────────────────────────  │
   │  Total: ₹836.85                    │
   └─────────────────────────────────────┘
   ↓
   - Real-time updates via Socket.io
   - Progress bar animates as status changes
   - Current step has pulse animation
   - Shows order details below

7️⃣ 🔔 CHEF UPDATES STATUS
   ↓
   - Chef clicks "Confirm" in portal
   - Backend: PUT /api/order/:id/status
   - Backend emits: "orderStatusUpdate"
   - Customer screen updates INSTANTLY
   - Progress bar moves to next step

8️⃣ 🍳 Status Progression
   ↓
   Pending → Confirmed → Preparing → Ready → Served
   (Each update reflects in real-time on customer's screen)

9️⃣ ✅ Order Ready!
   ↓
   - Chef marks "Ready"
   - Customer sees "Ready to Serve" ✅
   - Bill popup appears AGAIN (optional)
   - Notification shown
```

---

## 👨‍🍳 Chef Portal Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CHEF PORTAL FLOW                            │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ Chef Opens Portal
   ↓
   📱 Opens: /chef

2️⃣ Chef Portal Loads (ChefPortal.jsx)
   ↓
   - Connects to Socket.io
   - Emits: "joinChef"
   - Fetches existing orders: GET /api/orders

3️⃣ 📊 Dashboard Shows Stats
   ├────────────────────────────────────┐
   │  ⏳ Pending    | 👨‍🍳 Preparing       │
   │     3          |     5             │
   │                                    │
   │  ✅ Ready      | ✨ Served         │
   │     2          |     12            │
   └────────────────────────────────────┘

4️⃣ 🔔 NEW ORDER ARRIVES (Socket.io: "newOrder")
   ↓
   - Notification sound plays
   - Order card appears at top
   - Shows: Table, Items, Total, Status
   - Timestamp displayed

5️⃣ 📋 Order Card Details
   ├────────────────────────────────────┐
   │  🟡 PENDING                        │
   │  Table 5             ₹836.85      │
   │  Order #abc123       ⏱️ 20 min     │
   │                                    │
   │  Items:                            │
   │  • 2x Margherita Pizza   ₹598     │
   │  • 1x Caesar Salad      ₹199      │
   │                                    │
   │  Ordered: 14:30:25                 │
   │                                    │
   │  [Confirm Order]                   │
   │  [Cancel Order]                    │
   └────────────────────────────────────┘

6️⃣ 👨‍🍳 Chef Takes Action
   ↓
   - Clicks "Confirm Order"
   - PUT /api/order/:id/status
   - Backend updates MongoDB
   - Backend emits: "orderStatusUpdate"
   - Customer's screen updates
   - Button changes to "Start Preparing"

7️⃣ 🔄 Status Updates Continue
   ↓
   Confirm → Start Preparing → Mark Ready → Mark Served

   Each click:
   - Updates database
   - Emits Socket.io event
   - Updates customer's view
   - Changes button text

8️⃣ 🎯 Filter & Manage
   ├────────────────────────────────────┐
   │  [All] [Pending] [Preparing] [Ready]│
   │                                    │
   │  (Click to filter orders by status)│
   └────────────────────────────────────┘

9️⃣ 🔄 Auto-Refresh
   ↓
   - Real-time via Socket.io
   - Manual refresh button available
   - Stats update automatically
```

---

## 🔌 Backend & Socket.io Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │   Express    │
                        │   Server     │
                        │  (Port 5001) │
                        └──────┬───────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
            ┌───────▼────────┐    ┌──────▼────────┐
            │   REST API     │    │  Socket.io    │
            │   Endpoints    │    │   Server      │
            └───────┬────────┘    └──────┬────────┘
                    │                    │
                    │                    │
            ┌───────▼────────┐    ┌──────▼────────┐
            │   MongoDB      │    │  WebSocket    │
            │  (Mongoose)    │    │  Connections  │
            └────────────────┘    └───────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       SOCKET.IO ROOMS                                │
└─────────────────────────────────────────────────────────────────────┘

Customer Joins:
socket.emit('joinTable', 5)  →  Joins room: "table_5"

Chef Joins:
socket.emit('joinChef')  →  Joins room: "chef_portal"

Events Flow:

1. Order Placed (Customer):
   POST /api/order
   ↓
   io.to('chef_portal').emit('newOrder', orderData)
   io.to('table_5').emit('orderConfirmed', orderData)

2. Status Updated (Chef):
   PUT /api/order/:id/status
   ↓
   io.to('table_5').emit('orderStatusUpdate', statusData)
   io.to('chef_portal').emit('orderStatusUpdated', statusData)

3. Order Cancelled:
   DELETE /api/order/:id
   ↓
   io.to('table_5').emit('orderCancelled', orderId)
   io.to('chef_portal').emit('orderCancelled', orderId)
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      COMPLETE DATA FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

[Customer Phone] ──────┐
                       │
[Chef Tablet] ─────────┤
                       │
                       ▼
                ┌──────────────┐
                │  Socket.io   │◄──── Real-time bidirectional
                │   Server     │      communication
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   Express    │
                │   REST API   │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   MongoDB    │
                │  (Persistent │
                │    Storage)  │
                └──────────────┘

Data Objects:

Order Document:
{
  _id: "abc123",
  tableNo: 5,
  items: [
    { name: "Pizza", price: 299, quantity: 2 }
  ],
  total: 598,
  status: "preparing",
  createdAt: "2025-01-20T14:30:00Z",
  estimatedTime: 20
}

Menu Item Document:
{
  _id: "xyz789",
  name: "Margherita Pizza",
  description: "Classic tomato and mozzarella",
  price: 299,
  category: "main",
  image: "https://...",
  prepTime: 15,
  rating: 4.5,
  available: true
}
```

---

## 🎨 UI Components Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND COMPONENTS                               │
└─────────────────────────────────────────────────────────────────────┘

App.jsx (Router)
│
├── /menu → MenuOrderPage.jsx
│   ├── Category Filter
│   ├── Menu Items Grid
│   │   └── Item Card
│   │       ├── Image
│   │       ├── Name, Description
│   │       ├── Price, Rating
│   │       └── "Add +" Button
│   └── Cart Sidebar (AnimatePresence)
│       ├── Cart Items List
│       │   └── Quantity Controls
│       ├── Subtotal/Tax/Total
│       └── "Place Order" Button
│
├── /order-status → OrderStatusTracker.jsx
│   ├── Header (Table, Order ID)
│   ├── Status Progress Bar
│   │   ├── 5 Status Steps
│   │   ├── Timeline Animation
│   │   └── Active Step Pulse
│   ├── Order Items Summary
│   ├── Total Amount
│   └── Bill Popup (AnimatePresence)
│       ├── Confetti Header
│       ├── Order Summary
│       ├── Tax Breakdown
│       ├── Estimated Time
│       └── Action Buttons
│
└── /chef → ChefPortal.jsx
    ├── Stats Dashboard
    │   ├── Pending Count
    │   ├── Preparing Count
    │   ├── Ready Count
    │   └── Served Count
    ├── Filter Tabs
    └── Orders Grid (AnimatePresence)
        └── Order Card
            ├── Status Badge
            ├── Table & Order ID
            ├── Items List
            ├── Total Amount
            ├── Timestamp
            └── Action Buttons
```

---

## 🔄 State Management

```
┌─────────────────────────────────────────────────────────────────────┐
│                       STATE FLOW                                     │
└─────────────────────────────────────────────────────────────────────┘

MenuOrderPage.jsx:
├── menuItems (from API)
├── cart (local state)
├── selectedCategory (filter)
└── showCart (sidebar toggle)

OrderStatusTracker.jsx:
├── status (from Socket.io)
├── orderDetails (from props/API)
├── socket (WebSocket connection)
└── showBill (popup toggle)

ChefPortal.jsx:
├── orders (from API + Socket.io)
├── filter (status filter)
├── stats (calculated from orders)
└── socket (WebSocket connection)

Flow:
1. Initial: Fetch from API
2. Subscribe: Socket.io listeners
3. Update: setState on events
4. Render: React re-renders
```

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                                  │
└─────────────────────────────────────────────────────────────────────┘

Frontend (Vercel/Netlify):
├── Build: npm run build
├── Deploy: dist/ folder
└── Environment: VITE_API_URL=https://api.restaurant.com

Backend (Railway/Render):
├── MongoDB Atlas (Cloud)
├── Socket.io with CORS
├── Environment Variables:
│   ├── MONGODB_URI
│   ├── PORT
│   └── CORS_ORIGINS
└── WebSocket Support: Enable

Database (MongoDB Atlas):
├── Cluster Setup
├── Network Access: Allow All
└── User: Create DB user

CDN (Cloudflare/CloudFront):
└── Cache static assets
```

---

**Complete Restaurant System with Real-time Features! 🎉**
