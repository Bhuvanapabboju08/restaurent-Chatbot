# 🍽️ Modern Restaurant Ordering System

> **Complete end-to-end restaurant ordering solution with real-time bill popups and live order tracking**

![Status](https://img.shields.io/badge/status-production--ready-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-web%20%7C%20mobile-lightgrey)

---

## ✨ What Makes This Special?

### 💳 Instant Bill Popup
Order placed → Beautiful animated bill appears immediately with full breakdown

### 📊 Live Order Status Tracking
Real-time progress bar showing: Pending → Preparing → Ready → Served

### 🔔 Real-time Chef Notifications
Orders appear instantly in chef portal with notification sound

### 🎨 Modern UI/UX
Framer Motion animations, TailwindCSS, responsive design

### ⚡ Socket.io Real-time Sync
No page refresh needed - everything updates live!

---

## 🎬 Demo Flow

### Customer Experience:
1. Scans QR code → `/menu?table=5`
2. Browses menu, adds items to cart
3. Places order → **Bill popup appears instantly**
4. Redirected to live status tracker
5. Watches order progress in real-time
6. Gets notified when ready

### Chef Experience:
1. Opens chef portal → `/chef`
2. Sees new orders appear with notification
3. Updates status with one click
4. Customer sees updates instantly

---

## 🏗️ Tech Stack

### Frontend
- **React 18** - UI framework
- **React Router** - Navigation
- **Framer Motion** - Animations
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **Socket.io Client** - Real-time updates
- **Vite** - Build tool

### Backend
- **Node.js** - Runtime
- **Express** - Web framework
- **MongoDB + Mongoose** - Database
- **Socket.io** - WebSocket server
- **CORS** - Cross-origin support

---

## 📁 Project Structure

```
Hotel-Rag-Bot/
├── backend/
│   ├── server.js              # Main server + Socket.io
│   ├── package.json
│   └── .env
│
├── frontend/
│   ├── MenuOrderPage.jsx      # Customer menu & cart
│   ├── OrderStatusTracker.jsx # Live status with bill popup
│   ├── ChefPortal.jsx         # Kitchen dashboard
│   ├── App.jsx                # Router
│   ├── main.jsx               # Entry point
│   ├── index.css              # Global styles
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── index.html
│   └── package.json
│
├── QUICK_START.md             # 3-minute setup guide
├── RESTAURANT_SETUP.md        # Complete documentation
├── SYSTEM_FLOW.md             # Visual flow diagrams
└── README_RESTAURANT.md       # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- MongoDB
- npm/yarn

### 1. Install Backend
```bash
cd backend
npm install
```

### 2. Install Frontend
```bash
cd frontend
npm install
npx tailwindcss init -p
```

### 3. Setup Environment
Create `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017/restaurant
PORT=5001
```

### 4. Start Everything
```bash
# Terminal 1 - MongoDB
mongod

# Terminal 2 - Backend
cd backend
node server.js

# Terminal 3 - Frontend
cd frontend
npm run dev

# Terminal 4 - Seed Data (optional)
curl -X POST http://localhost:5001/api/seed-menu
```

### 5. Open in Browser
- Customer: http://localhost:5173/menu?table=1
- Chef: http://localhost:5173/chef

---

## 🎯 Key Features

### 1. Bill Popup (Dynamic Island Style)
```jsx
// Auto-appears after order placement
- Order summary with items
- Tax calculation (5%)
- Grand total
- Estimated delivery time
- Action buttons (Track Order, Chat)
- Auto-dismisses after 10 seconds
```

### 2. Order Status Tracker
```jsx
// 5-step progress timeline
Pending → Confirmed → Preparing → Ready → Served

- Real-time Socket.io updates
- Animated progress bar
- Pulse effect on current step
- Order details below
```

### 3. Chef Portal
```jsx
// Kitchen display system
- Stats dashboard (Pending, Preparing, Ready, Served)
- Real-time order cards
- One-click status updates
- Filter by status
- Notification sounds
```

---

## 📡 API Endpoints

### Menu
- `GET /api/menu` - Get all items
- `GET /api/menu?category=main` - Filter by category
- `POST /api/menu` - Add item (admin)
- `POST /api/seed-menu` - Seed sample data

### Orders
- `POST /api/order` - Place new order
- `GET /api/order/:id` - Get order details
- `GET /api/orders` - Get all orders
- `GET /api/orders/table/:tableNo` - Get table's orders
- `PUT /api/order/:id/status` - Update status
- `DELETE /api/order/:id` - Cancel order

---

## 🔌 Socket.io Events

### Events Emitted by Server

| Event | Payload | Description |
|-------|---------|-------------|
| `newOrder` | Order object | New order placed |
| `orderConfirmed` | `{orderId, estimatedTime}` | Order confirmed |
| `orderStatusUpdate` | `{orderId, status}` | Status changed |
| `orderCancelled` | `{orderId}` | Order cancelled |

### Events Emitted by Client

| Event | Payload | Description |
|-------|---------|-------------|
| `joinTable` | `tableNo` | Join table room |
| `joinChef` | - | Join chef portal |

---

## 🎨 Customization

### Colors
Search and replace in frontend files:
- `orange-500` → Your primary color
- `purple-600` → Your accent color
- `green-500` → Success color

### Menu Categories
Edit in `MenuOrderPage.jsx`:
```jsx
const categories = [
  { id: 'appetizer', label: 'Appetizers', icon: '🥗' },
  { id: 'main', label: 'Main Course', icon: '🍕' },
  // Add more...
];
```

### Status Flow
Modify in `server.js`:
```javascript
status: {
  type: String,
  enum: ['pending', 'confirmed', 'preparing', 'ready', 'served'],
  // Add custom statuses
}
```

---

## 📱 QR Code Setup

Generate QR codes for each table:

**URL Format**: `http://yourapp.com/menu?table=X`

**Tools**:
- [QR Code Generator](https://www.qr-code-generator.com/)
- [QR.io](https://qr.io/)
- Chrome Extension: "QR Code Generator"

Print and place on tables!

---

## 🚀 Production Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel deploy
```

### Backend (Railway)
```bash
cd backend
# Push to GitHub
# Connect to Railway
# Set environment variables
# Deploy
```

### Database (MongoDB Atlas)
1. Create cluster
2. Get connection string
3. Update `MONGODB_URI` in env

---

## 📊 Database Schemas

### Order
```javascript
{
  tableNo: Number,
  items: [{
    name: String,
    price: Number,
    quantity: Number,
    category: String
  }],
  total: Number,
  status: String,
  createdAt: Date,
  updatedAt: Date,
  estimatedTime: Number
}
```

### MenuItem
```javascript
{
  name: String,
  description: String,
  price: Number,
  category: String,
  image: String,
  available: Boolean,
  rating: Number,
  prepTime: Number
}
```

---

## 🐛 Troubleshooting

**MongoDB connection error?**
```bash
mongod  # Start MongoDB
mongosh # Test connection
```

**Socket.io not connecting?**
- Check CORS settings
- Verify backend is running
- Check browser console

**Orders not updating?**
- Ensure Socket.io connected
- Check `joinTable` event emitted
- Verify WebSocket in Network tab

---

## 📚 Documentation

- [Quick Start Guide](./QUICK_START.md) - 3-minute setup
- [Complete Setup](./RESTAURANT_SETUP.md) - Full documentation
- [System Flow](./SYSTEM_FLOW.md) - Visual diagrams

---

## 🎯 Use Cases

✅ **Restaurants** - Dine-in ordering
✅ **Cafes** - Quick service
✅ **Food Courts** - Multiple vendors
✅ **Cloud Kitchens** - Order management
✅ **Hotels** - Room service
✅ **Events** - Festival food ordering

---

## 🔮 Future Enhancements

- [ ] Payment gateway integration (Stripe/Razorpay)
- [ ] Customer feedback & ratings
- [ ] Order history & analytics
- [ ] Push notifications (PWA)
- [ ] Multi-language support
- [ ] Table reservation
- [ ] Loyalty program
- [ ] Kitchen display system (KDS)
- [ ] Printer integration
- [ ] Staff management
- [ ] Inventory tracking

---

## 📄 License

MIT License - Free to use for your restaurant!

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

---

## 📞 Support

- 📧 Email: support@yourrestaurant.com
- 📱 WhatsApp: +1234567890
- 🌐 Website: yourrestaurant.com

---

## ⭐ Features Checklist

- [x] Menu browsing with categories
- [x] Shopping cart functionality
- [x] Real-time order placement
- [x] **Instant bill popup after ordering**
- [x] **Live order status tracking**
- [x] Socket.io real-time updates
- [x] Chef dashboard
- [x] One-click status updates
- [x] Notification sounds
- [x] Mobile responsive
- [x] Beautiful animations
- [x] Production ready

---

## 🎉 Success Metrics

- ⚡ **0.5s** - Bill popup appears
- 📡 **Real-time** - Status updates
- 📱 **Mobile-first** - Responsive design
- 🎨 **Modern UI** - Framer Motion
- 🔔 **Instant** - Chef notifications

---

**Built with ❤️ for modern restaurants**

**Star ⭐ this repo if you find it useful!**

---

*Questions? Check out the [Quick Start Guide](./QUICK_START.md) or [Full Documentation](./RESTAURANT_SETUP.md)*
