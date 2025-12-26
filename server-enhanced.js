const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: ['http://localhost:3000', 'http://localhost:5173'],
    methods: ['GET', 'POST', 'PUT', 'DELETE']
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/restaurant';
mongoose.connect(MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => {
  console.log('[OK] MongoDB connected');
  // Auto-seed menu on startup if empty
  autoSeedMenu();
})
.catch(err => console.error('[ERROR] MongoDB connection error:', err));

// Order Schema
const orderSchema = new mongoose.Schema({
  tableNo: {
    type: Number,
    required: true
  },
  items: [{
    name: String,
    price: Number,
    quantity: Number,
    category: String,
    image: String
  }],
  total: {
    type: Number,
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled'],
    default: 'pending'
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
  estimatedTime: {
    type: Number, // in minutes
    default: 20
  }
});

const Order = mongoose.model('Order', orderSchema);

// Menu Schema
const menuItemSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  description: String,
  price: {
    type: Number,
    required: true
  },
  category: {
    type: String,
    enum: ['appetizer', 'main', 'dessert', 'beverage'],
    required: true
  },
  image: String,
  available: {
    type: Boolean,
    default: true
  },
  rating: {
    type: Number,
    default: 4.5
  },
  prepTime: Number,
  isVeg: Boolean,
  spiceLevel: Number,
  popular: Boolean,
  chefSpecial: Boolean
});

const MenuItem = mongoose.model('MenuItem', menuItemSchema);

// Auto-seed function
const autoSeedMenu = async () => {
  try {
    const count = await MenuItem.countDocuments();
    if (count === 0) {
      const menuData = require('./seedData');
      await MenuItem.insertMany(menuData);
      console.log(`[OK] Auto-seeded ${menuData.length} menu items`);
    } else {
      console.log(`[OK] Found ${count} existing menu items`);
    }
  } catch (error) {
    console.log('[WARN] Auto-seed failed:', error.message);
  }
};

// ==================== SOCKET.IO EVENTS ====================

io.on('connection', (socket) => {
  console.log('[OK] Client connected:', socket.id);

  socket.on('joinTable', (tableNo) => {
    socket.join(`table_${tableNo}`);
    console.log(`[OK] Socket ${socket.id} joined table_${tableNo}`);
  });

  socket.on('joinChef', () => {
    socket.join('chef_portal');
    console.log(`[OK] Chef portal connected: ${socket.id}`);
  });

  socket.on('disconnect', () => {
    console.log('[OK] Client disconnected:', socket.id);
  });
});

// ==================== API ROUTES ====================

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    message: 'Restaurant Backend API',
    timestamp: new Date().toISOString()
  });
});

// Get all menu items
app.get('/api/menu', async (req, res) => {
  try {
    const { category } = req.query;
    const filter = category ? { category, available: true } : { available: true };

    const menuItems = await MenuItem.find(filter).sort({ popular: -1, rating: -1, name: 1 });

    res.json({
      success: true,
      count: menuItems.length,
      data: menuItems
    });
  } catch (error) {
    console.error('[ERROR] Get menu error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Create new order
app.post('/api/order', async (req, res) => {
  try {
    const { tableNo, items, total } = req.body;

    if (!tableNo || !items || !items.length || !total) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: tableNo, items, total'
      });
    }

    const estimatedTime = Math.max(...items.map(item => item.prepTime || 15)) + 5;

    const order = new Order({
      tableNo,
      items,
      total,
      estimatedTime,
      status: 'pending'
    });

    await order.save();

    // Emit to chef portal
    io.to('chef_portal').emit('newOrder', {
      orderId: order._id,
      tableNo: order.tableNo,
      items: order.items,
      total: order.total,
      status: order.status,
      createdAt: order.createdAt,
      estimatedTime: order.estimatedTime
    });

    // Emit to customer's table
    io.to(`table_${tableNo}`).emit('orderConfirmed', {
      orderId: order._id,
      status: order.status,
      estimatedTime: order.estimatedTime
    });

    res.status(201).json({
      success: true,
      message: 'Order placed successfully',
      data: order
    });
  } catch (error) {
    console.error('[ERROR] Create order error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get order by ID
app.get('/api/order/:id', async (req, res) => {
  try {
    const order = await Order.findById(req.params.id);

    if (!order) {
      return res.status(404).json({
        success: false,
        error: 'Order not found'
      });
    }

    res.json({
      success: true,
      data: order
    });
  } catch (error) {
    console.error('[ERROR] Get order error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all orders
app.get('/api/orders', async (req, res) => {
  try {
    const { status } = req.query;
    const filter = status ? { status } : {};

    const orders = await Order.find(filter).sort({ createdAt: -1 });

    res.json({
      success: true,
      count: orders.length,
      data: orders
    });
  } catch (error) {
    console.error('[ERROR] Get all orders error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Update order status
app.put('/api/order/:id/status', async (req, res) => {
  try {
    const { status } = req.body;

    const validStatuses = ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid status'
      });
    }

    const order = await Order.findByIdAndUpdate(
      req.params.id,
      { status, updatedAt: Date.now() },
      { new: true }
    );

    if (!order) {
      return res.status(404).json({
        success: false,
        error: 'Order not found'
      });
    }

    // Emit to customer
    io.to(`table_${order.tableNo}`).emit('orderStatusUpdate', {
      orderId: order._id,
      status: order.status,
      updatedAt: order.updatedAt
    });

    // Emit to chef portal
    io.to('chef_portal').emit('orderStatusUpdated', {
      orderId: order._id,
      status: order.status
    });

    res.json({
      success: true,
      message: 'Order status updated',
      data: order
    });
  } catch (error) {
    console.error('[ERROR] Update order status error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Seed menu endpoint
app.post('/api/seed-menu', async (req, res) => {
  try {
    await MenuItem.deleteMany({});
    const menuData = require('./seedData');
    await MenuItem.insertMany(menuData);

    res.json({
      success: true,
      message: 'Menu seeded successfully',
      count: menuData.length
    });
  } catch (error) {
    console.error('[ERROR] Seed menu error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ==================== START SERVER ====================

const PORT = process.env.PORT || 5001;

server.listen(PORT, () => {
  console.log('\n============================================================');
  console.log('[APP] Restaurant Backend Server');
  console.log('============================================================');
  console.log(`[OK] Server running on http://localhost:${PORT}`);
  console.log(`[OK] Socket.io enabled for real-time updates`);
  console.log(`[OK] MongoDB: ${MONGODB_URI}`);
  console.log('============================================================\n');
});

module.exports = { app, io };
