# 🍽️ Restaurant Ordering System - Complete Setup Guide

## System Overview

A modern restaurant ordering system with real-time order tracking, dynamic bill popups, and live status updates.

### Features
- ✅ QR Code based table ordering
- ✅ Real-time order status tracking
- ✅ Beautiful animated bill popup
- ✅ Live chef portal with instant notifications
- ✅ Socket.io for real-time updates
- ✅ Mobile-responsive UI with Framer Motion animations
- ✅ MongoDB for data persistence

---

## 🏗️ System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Customer  │ ───► │   Backend    │ ◄─── │    Chef     │
│  (React)    │      │  (Node.js)   │      │   Portal    │
│             │      │  Socket.io   │      │  (React)    │
└─────────────┘      └──────────────┘      └─────────────┘
      │                     │                      │
      │                     ▼                      │
      │              ┌──────────────┐             │
      └─────────────►│   MongoDB    │◄────────────┘
                     └──────────────┘
```

---

## 📁 Project Structure

```
Hotel-Rag-Bot/
├── backend/
│   ├── server.js              # Main server with Socket.io
│   ├── package.json           # Backend dependencies
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── MenuOrderPage.jsx      # Customer menu & ordering
│   ├── OrderStatusTracker.jsx # Live order status tracking
│   ├── ChefPortal.jsx         # Chef dashboard
│   ├── package.json           # Frontend dependencies
│   └── App.jsx                # Main routing component
│
└── RESTAURANT_SETUP.md        # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v18+)
- MongoDB (v6+)
- npm or yarn

### Step 1: Install Backend Dependencies

```bash
cd backend
npm install

# Or install manually:
npm install express mongoose cors socket.io dotenv
npm install -D nodemon
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install

# Or install manually:
npm install react react-dom react-router-dom axios socket.io-client framer-motion
npm install -D vite @vitejs/plugin-react tailwindcss autoprefixer postcss
```

### Step 3: Configure Environment Variables

Create `backend/.env`:

```env
MONGODB_URI=mongodb://localhost:27017/restaurant
PORT=5001
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Step 4: Start MongoDB

```bash
# Windows
mongod

# Linux/Mac
sudo systemctl start mongod
```

### Step 5: Seed Initial Data

```bash
# Seed menu items (optional)
curl -X POST http://localhost:5001/api/seed-menu
```

### Step 6: Start Backend Server

```bash
cd backend
npm run dev

# You should see:
# [OK] Server running on http://localhost:5001
# [OK] MongoDB connected
# [OK] Socket.io enabled
```

### Step 7: Start Frontend

```bash
cd frontend
npm run dev

# You should see:
# Local: http://localhost:5173
```

---

## 🎯 Usage Flow

### Customer Journey

1. **Scan QR Code** → Opens `/menu?table=5`
2. **Browse Menu** → View items by category
3. **Add to Cart** → Select items and quantities
4. **Place Order** → Click "Place Order"
5. **Bill Popup** → Instant bill with order details
6. **Track Status** → Live order status updates
7. **Get Notified** → When order is ready

### Chef Portal

1. **Open Portal** → Navigate to `/chef`
2. **View Orders** → See all incoming orders in real-time
3. **Update Status**:
   - Pending → Confirm
   - Confirmed → Start Preparing
   - Preparing → Mark Ready
   - Ready → Mark Served
4. **Real-time Sync** → Customer sees updates instantly

---

## 🔌 API Endpoints

### Menu Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/menu` | Get all menu items |
| GET | `/api/menu?category=main` | Filter by category |
| GET | `/api/menu/:id` | Get single item |
| POST | `/api/menu` | Add new item (admin) |
| POST | `/api/seed-menu` | Seed sample data |

### Order Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/order` | Create new order |
| GET | `/api/order/:id` | Get order by ID |
| GET | `/api/orders` | Get all orders |
| GET | `/api/orders/table/:tableNo` | Get table's orders |
| PUT | `/api/order/:id/status` | Update order status |
| DELETE | `/api/order/:id` | Cancel order |

---

## 🔔 Socket.io Events

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `joinTable` | `tableNo` | Customer joins table room |
| `joinChef` | - | Chef joins chef portal |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `newOrder` | Order data | New order placed |
| `orderStatusUpdate` | `{orderId, status}` | Status changed |
| `orderConfirmed` | `{orderId, estimatedTime}` | Order confirmed |
| `orderCancelled` | `{orderId}` | Order cancelled |

---

## 🎨 Component Details

### 1. MenuOrderPage.jsx

**Purpose**: Customer menu browsing and ordering

**Features**:
- Category filtering (Appetizers, Main, Desserts, Beverages)
- Add to cart functionality
- Quantity management
- Cart sidebar with animations
- Place order button

**Key Props**:
- `tableNo` - From URL parameter `?table=5`

### 2. OrderStatusTracker.jsx

**Purpose**: Real-time order status tracking for customers

**Features**:
- Live progress timeline
- Status badges with animations
- Dynamic bill popup (auto-shows after order)
- Order items summary
- Socket.io real-time updates

**Status Flow**:
```
Pending → Confirmed → Preparing → Ready → Served
```

### 3. ChefPortal.jsx

**Purpose**: Chef dashboard for managing orders

**Features**:
- Real-time order notifications
- Stats dashboard (Pending, Preparing, Ready, Served)
- Filter orders by status
- One-click status updates
- Order cancellation
- Auto-refresh

---

## 💾 Database Schema

### Order Schema

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
  status: String, // pending, confirmed, preparing, ready, served
  createdAt: Date,
  updatedAt: Date,
  estimatedTime: Number // in minutes
}
```

### MenuItem Schema

```javascript
{
  name: String,
  description: String,
  price: Number,
  category: String, // appetizer, main, dessert, beverage
  image: String,
  available: Boolean,
  rating: Number,
  prepTime: Number // in minutes
}
```

---

## 🎨 UI Components & Animations

### Bill Popup (Dynamic Island Style)

- **Trigger**: Automatically shows after order placement
- **Animation**: Slides from top with scale effect
- **Auto-hide**: Dismisses after 10 seconds
- **Features**:
  - Order summary
  - Tax calculation
  - Estimated time
  - Action buttons (Track Order, Chat)

### Order Status Timeline

- **Design**: Vertical progress bar
- **States**: 5 status levels with icons
- **Active State**: Pulse animation
- **Colors**: Dynamic based on status

---

## 🔧 Customization

### Add New Menu Items

```bash
POST http://localhost:5001/api/menu
Content-Type: application/json

{
  "name": "Chicken Biryani",
  "description": "Aromatic rice with tender chicken",
  "price": 349,
  "category": "main",
  "prepTime": 20,
  "rating": 4.7,
  "available": true
}
```

### Modify Status Flow

Edit `server.js` to add custom statuses or workflows.

### Change Color Scheme

Modify Tailwind classes in components:
- Primary: `orange-500` / `purple-600`
- Success: `green-500`
- Warning: `yellow-500`

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
mongosh

# Start MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # Mac
```

### Socket.io Connection Issues
- Ensure backend is running on port 5001
- Check CORS configuration in `server.js`
- Verify firewall settings

### Orders Not Updating in Real-time
- Check Socket.io connection in browser console
- Verify `joinTable` or `joinChef` events are emitted
- Check network tab for WebSocket connection

---

## 📱 QR Code Generation

Use a QR code generator to create codes for each table:

**URL Format**:
```
http://localhost:5173/menu?table=1
http://localhost:5173/menu?table=2
http://localhost:5173/menu?table=3
```

**Free QR Generators**:
- https://www.qr-code-generator.com/
- https://qr.io/
- Chrome extension: "QR Code Generator"

---

## 🚀 Production Deployment

### Backend (Railway / Render / Heroku)

1. Set environment variables
2. Update MongoDB URI to cloud instance (MongoDB Atlas)
3. Configure CORS for production domain

### Frontend (Vercel / Netlify)

1. Build: `npm run build`
2. Deploy `dist/` folder
3. Update API_URL to production backend

---

## 📈 Future Enhancements

- [ ] Payment gateway integration
- [ ] Customer feedback system
- [ ] Order history & analytics
- [ ] Push notifications
- [ ] Multi-language support
- [ ] Table reservation system
- [ ] Loyalty points program
- [ ] Kitchen display system (KDS)

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review console logs
3. Verify all dependencies are installed
4. Ensure MongoDB is running

---

## 📄 License

MIT License - Feel free to use for your restaurant!

---

**Built with ❤️ for modern restaurants**
