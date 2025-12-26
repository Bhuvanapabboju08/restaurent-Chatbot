# 🚀 Quick Start Guide - Restaurant Ordering System

## ⚡ 3-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
# Terminal 1 - Backend
cd backend
npm install express mongoose cors socket.io dotenv
npm install -D nodemon

# Terminal 2 - Frontend
cd frontend
npm install react react-dom react-router-dom axios socket.io-client framer-motion
npm install -D vite @vitejs/plugin-react tailwindcss autoprefixer postcss
npx tailwindcss init -p
```

### Step 2: Setup Environment

Create `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017/restaurant
PORT=5001
```

### Step 3: Start MongoDB

```bash
# Make sure MongoDB is running
mongod
```

### Step 4: Run Everything (1 minute)

```bash
# Terminal 1 - Backend
cd backend
node server.js

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Seed Data (optional)
curl -X POST http://localhost:5001/api/seed-menu
```

## 🎉 You're Ready!

Open your browser:

- **Customer Menu**: http://localhost:5173/menu?table=1
- **Chef Portal**: http://localhost:5173/chef

---

## 📱 Test Flow

### As Customer:

1. Open: `http://localhost:5173/menu?table=5`
2. Click "Add +" on items
3. Click "Cart" button (top right)
4. Click "Place Order"
5. See **beautiful bill popup** 💳
6. Watch **live order status** update in real-time ⏱️

### As Chef:

1. Open: `http://localhost:5173/chef`
2. See new orders appear instantly 🔔
3. Click "Confirm" → "Start Preparing" → "Mark Ready"
4. Watch customer's screen update automatically ✨

---

## 🎨 Key Features You'll See

### 1. Dynamic Bill Popup (After Ordering)
- Auto-shows with beautiful animation
- Displays order summary, tax, total
- Estimated time
- Action buttons

### 2. Live Order Status Tracker
- 5-step progress bar (Pending → Confirmed → Preparing → Ready → Served)
- Real-time updates via Socket.io
- Pulse animations on current step
- Order items with quantities and prices

### 3. Chef Portal Dashboard
- Real-time notifications
- Stats cards (Pending, Preparing, Ready, Served)
- Filter by status
- One-click status updates
- Order cards with all details

---

## 🧪 Test Scenarios

### Scenario 1: Single Table Order
```
1. Customer (Table 1) places order
2. Bill popup appears
3. Order shows in chef portal
4. Chef confirms → Customer sees "Confirmed"
5. Chef starts preparing → Customer sees "Preparing"
6. Chef marks ready → Customer sees "Ready"
```

### Scenario 2: Multiple Tables
```
1. Open Table 1: /menu?table=1
2. Open Table 2: /menu?table=2
3. Place orders from both
4. Chef sees both orders
5. Updates propagate to correct tables only
```

### Scenario 3: Real-time Sync
```
1. Open customer view: /menu?table=3
2. Place order
3. Open chef portal in another tab
4. Change status in chef portal
5. Watch customer view update automatically!
```

---

## 🎯 URLs to Bookmark

| Page | URL | Purpose |
|------|-----|---------|
| Table 1 | http://localhost:5173/menu?table=1 | Customer menu |
| Table 2 | http://localhost:5173/menu?table=2 | Another table |
| Chef | http://localhost:5173/chef | Kitchen dashboard |
| API Docs | http://localhost:5001/health | Server health |

---

## 📊 Sample API Calls

### Get Menu
```bash
curl http://localhost:5001/api/menu
```

### Place Order
```bash
curl -X POST http://localhost:5001/api/order \
  -H "Content-Type: application/json" \
  -d '{
    "tableNo": 5,
    "items": [
      {"name": "Pizza", "price": 299, "quantity": 2, "category": "main"}
    ],
    "total": 598
  }'
```

### Update Status
```bash
curl -X PUT http://localhost:5001/api/order/ORDER_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status": "preparing"}'
```

---

## 🐛 Common Issues

### MongoDB Connection Failed
```bash
# Start MongoDB
mongod

# Or check if it's running
mongosh
```

### Port Already in Use
```bash
# Change port in backend/.env
PORT=5002

# Update API_URL in frontend components
const API_URL = 'http://localhost:5002';
```

### Socket.io Not Connecting
- Check console for errors
- Verify CORS settings in server.js
- Ensure backend is running

---

## 🎨 Customization Quick Tips

### Change Colors
**Frontend components** - Search and replace:
- `orange-500` → Your primary color
- `purple-600` → Your accent color

### Add Menu Items
```bash
curl -X POST http://localhost:5001/api/menu \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Dish",
    "price": 199,
    "category": "main",
    "description": "Delicious food",
    "prepTime": 15
  }'
```

### Modify Status Flow
Edit `server.js` and `OrderStatusTracker.jsx`:
- Add new status to enum
- Update statusConfig object
- Add transitions in getStatusActions()

---

## 📖 Full Documentation

See [RESTAURANT_SETUP.md](./RESTAURANT_SETUP.md) for:
- Complete API reference
- Socket.io events
- Database schemas
- Component details
- Production deployment
- Troubleshooting

---

## 🎬 What Makes This Special?

✅ **Instant Bill Popup** - Beautiful animated popup appears right after order
✅ **Live Status Updates** - No refresh needed, Socket.io magic
✅ **Modern UI** - Framer Motion animations, TailwindCSS
✅ **Real-time Chef Portal** - Orders appear instantly with sound
✅ **Mobile Responsive** - Works on all devices
✅ **Production Ready** - MongoDB, proper error handling

---

## 🚀 Next Steps

1. ✅ Get it running (you're here!)
2. 📱 Generate QR codes for tables
3. 🎨 Customize colors and branding
4. 📊 Add your real menu items
5. 🚀 Deploy to production
6. 💰 Integrate payment gateway

---

**Enjoy your modern restaurant system! 🍽️✨**
