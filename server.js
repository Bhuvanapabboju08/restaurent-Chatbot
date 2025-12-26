const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const QRCode = require('qrcode');
const path = require('path');
const fs = require('fs');
require('dotenv').config();
const Groq = require('groq-sdk');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE']
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use('/api/chat', chatRoutes);


// Initialize Groq with error checking
let groq = null;
try {
  if (process.env.GROQ_API_KEY) {
    groq = new Groq({
      apiKey: process.env.GROQ_API_KEY
    });
    console.log('✅ Groq API initialized successfully');
  } else {
    console.log('⚠️  GROQ_API_KEY not found in environment variables');
  }
} catch (error) {
  console.error('❌ Failed to initialize Groq:', error.message);
}

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/restaurant';
mongoose.connect(MONGODB_URI)
  .then(() => {
    console.log('✅ MongoDB connected');
    autoSeedMenu();
  })
  .catch(err => {
    console.log('⚠️  MongoDB not connected (this is OK, using fallback)');
  });

// Order Schema
const orderSchema = new mongoose.Schema({
  tableNo: { type: Number, required: true },
  items: [{
    name: String,
    price: Number,
    quantity: Number,
    category: String,
    image: String
  }],
  total: { type: Number, required: true },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled'],
    default: 'pending'
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
  estimatedTime: { type: Number, default: 20 }
});

const Order = mongoose.model('Order', orderSchema);

// Menu Schema
const menuItemSchema = new mongoose.Schema({
  name: { type: String, required: true },
  description: String,
  price: { type: Number, required: true },
  category: {
    type: String,
    enum: ['appetizer', 'main', 'dessert', 'beverage'],
    required: true
  },
  image: String,
  available: { type: Boolean, default: true },
  rating: { type: Number, default: 4.5 },
  prepTime: Number,
  isVeg: Boolean,
  spiceLevel: Number,
  popular: Boolean,
  chefSpecial: Boolean
});

const MenuItem = mongoose.model('MenuItem', menuItemSchema);

let inMemoryOrders = [];

const autoSeedMenu = async () => {
  try {
    const count = await MenuItem.countDocuments();
    if (count === 0) {
      const menuData = require('./seedData');
      await MenuItem.insertMany(menuData);
      console.log('✅ Auto-seeded ' + menuData.length + ' menu items');
    } else {
      console.log('✅ Found ' + count + ' existing menu items');
    }
  } catch (error) {
    console.log('⚠️  Auto-seed skipped:', error.message);
  }
};

// Socket.IO
io.on('connection', (socket) => {
  console.log('✅ Client connected:', socket.id);

  socket.on('joinTable', (tableNo) => {
    socket.join('table_' + tableNo);
    console.log('✅ Socket joined table_' + tableNo);
  });

  socket.on('joinChef', () => {
    socket.join('chef_portal');
    console.log('✅ Chef portal connected');
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Health Check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    message: 'Restaurant Backend API',
    timestamp: new Date().toISOString()
  });
});

// Get Menu
app.get('/api/menu', async (req, res) => {
  try {
    const { category } = req.query;

    if (mongoose.connection.readyState !== 1) {
      const menuData = require('./seedData');
      let filteredData = category ? menuData.filter(item => item.category === category) : menuData;
      return res.json({ success: true, count: filteredData.length, data: filteredData });
    }

    const filter = category ? { category, available: true } : { available: true };
    const menuItems = await MenuItem.find(filter).sort({ popular: -1, rating: -1 });

    res.json({ success: true, count: menuItems.length, data: menuItems });
  } catch (error) {
    console.error('Error fetching menu:', error);
    try {
      const menuData = require('./seedData');
      res.json({ success: true, count: menuData.length, data: menuData });
    } catch (fallbackError) {
      res.status(500).json({ success: false, error: error.message });
    }
  }
});

// Create Order
app.post('/api/order', async (req, res) => {
  try {
    const { tableNo, items, total } = req.body;

    if (!tableNo || !items || !items.length || !total) {
      return res.status(400).json({ success: false, error: 'Missing required fields' });
    }

    const estimatedTime = Math.max(...items.map(item => item.prepTime || 15)) + 5;

    if (mongoose.connection.readyState !== 1) {
      const order = {
        _id: Date.now().toString(),
        tableNo,
        items,
        total,
        estimatedTime,
        status: 'pending',
        createdAt: new Date()
      };

      inMemoryOrders.push(order);
      io.to('chef_portal').emit('newOrder', order);
      io.to('table_' + tableNo).emit('orderConfirmed', order);

      return res.status(201).json({ success: true, data: order });
    }

    const order = new Order({ tableNo, items, total, estimatedTime });
    await order.save();

    io.to('chef_portal').emit('newOrder', order);
    io.to('table_' + tableNo).emit('orderConfirmed', order);

    res.status(201).json({ success: true, data: order });
  } catch (error) {
    console.error('Error creating order:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get Order by ID
app.get('/api/order/:id', async (req, res) => {
  try {
    if (mongoose.connection.readyState !== 1) {
      const order = inMemoryOrders.find(o => o._id === req.params.id);
      if (!order) return res.status(404).json({ success: false, error: 'Order not found' });
      return res.json({ success: true, data: order });
    }

    const order = await Order.findById(req.params.id);
    if (!order) return res.status(404).json({ success: false, error: 'Order not found' });

    res.json({ success: true, data: order });
  } catch (error) {
    console.error('Error fetching order:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get All Orders
app.get('/api/orders', async (req, res) => {
  try {
    const { status } = req.query;
    const filter = status ? { status } : {};
    const orders = await Order.find(filter).sort({ createdAt: -1 });
    res.json({ success: true, count: orders.length, data: orders });
  } catch (error) {
    console.error('Error fetching orders:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Update Order Status
app.put('/api/order/:id/status', async (req, res) => {
  try {
    const { status } = req.body;
    const validStatuses = ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled'];
    
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ success: false, error: 'Invalid status' });
    }

    const order = await Order.findByIdAndUpdate(
      req.params.id,
      { status, updatedAt: Date.now() },
      { new: true }
    );

    if (!order) return res.status(404).json({ success: false, error: 'Order not found' });

    io.to('table_' + order.tableNo).emit('orderStatusUpdate', {
      orderId: order._id,
      status: order.status
    });

    io.to('chef_portal').emit('orderStatusUpdated', {
      orderId: order._id,
      status: order.status
    });

    res.json({ success: true, data: order });
  } catch (error) {
    console.error('Error updating order:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Seed Menu (Manual)
app.post('/api/seed-menu', async (req, res) => {
  try {
    await MenuItem.deleteMany({});
    const menuData = require('./seedData');
    await MenuItem.insertMany(menuData);
    res.json({ success: true, message: 'Menu seeded', count: menuData.length });
  } catch (error) {
    console.error('Error seeding menu:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Generate QR Codes
app.post('/api/generate-qr-codes', async (req, res) => {
  try {
    const totalTables = 20;
    const qrCodesDir = path.join(__dirname, 'qr-codes');
    const frontendURL = 'http://localhost:5173';

    if (!fs.existsSync(qrCodesDir)) {
      fs.mkdirSync(qrCodesDir, { recursive: true });
    }

    const generatedQRCodes = [];

    for (let tableNo = 1; tableNo <= totalTables; tableNo++) {
      const url = frontendURL + '/menu?table=' + tableNo;
      const fileName = 'table-' + tableNo + '.png';
      const filePath = path.join(qrCodesDir, fileName);

      await QRCode.toFile(filePath, url, {
        width: 300,
        margin: 2,
        color: { dark: '#000000', light: '#FFFFFF' }
      });

      generatedQRCodes.push({
        tableNo,
        url,
        fileName,
        filePath: '/api/qr-codes/table-' + tableNo + '.png'
      });
    }

    console.log('✅ Generated ' + totalTables + ' QR codes');
    res.json({ success: true, message: 'Generated QR codes', data: generatedQRCodes });
  } catch (error) {
    console.error('Error generating QR codes:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Serve QR Codes
app.use('/api/qr-codes', express.static(path.join(__dirname, 'qr-codes')));

// List QR Codes
app.get('/api/qr-codes-list', (req, res) => {
  try {
    const qrCodesDir = path.join(__dirname, 'qr-codes');

    if (!fs.existsSync(qrCodesDir)) {
      return res.json({ success: true, message: 'No QR codes yet', data: [] });
    }

    const files = fs.readdirSync(qrCodesDir);
    const qrCodesList = files
      .filter(file => file.endsWith('.png'))
      .map(file => {
        const tableNo = parseInt(file.match(/table-(\d+)\.png/)[1]);
        return {
          tableNo,
          fileName: file,
          url: '/api/qr-codes/' + file,
          menuUrl: 'http://localhost:5173/menu?table=' + tableNo
        };
      })
      .sort((a, b) => a.tableNo - b.tableNo);

    res.json({ success: true, count: qrCodesList.length, data: qrCodesList });
  } catch (error) {
    console.error('Error listing QR codes:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// ========================================
// CHATBOT WITH GROQ AI - SIMPLIFIED VERSION
// ========================================

const restaurantContext = {
  name: "Our Restaurant",
  hours: "10:00 AM - 11:00 PM daily",
  location: "Downtown, City Center",
  specialties: ["Italian Pizza", "Indian Curries", "Desserts", "Fresh Beverages"]
};

const personalityPrompts = {
  family: 'Answer like Technical way',
  friends: 'Answer like Technical way',
  couples: 'Answer like Technical way.',
  lovies: 'Answer like Technical way',
  single: 'Answer like Technical way'
};

// CHATBOT TEST ENDPOINT
app.get('/api/chatbot-test', (req, res) => {
  res.json({
    success: true,
    message: 'Chatbot endpoint is available',
    groqConfigured: !!groq,
    groqApiKeyExists: !!process.env.GROQ_API_KEY,
    groqApiKeyLength: process.env.GROQ_API_KEY ? process.env.GROQ_API_KEY.length : 0,
    personalities: Object.keys(personalityPrompts)
  });
});

// MAIN CHATBOT ENDPOINT
app.post('/api/chatbot', async (req, res) => {
  console.log('\n' + '='.repeat(60));
  console.log('🤖 CHATBOT REQUEST RECEIVED');
  console.log('='.repeat(60));

  try {
    const { message, conversationHistory, tableNo, personality, orderId } = req.body;

    // Log request details
    console.log('📝 Request Details:');
    console.log('   Table:', tableNo);
    console.log('   Personality:', personality);
    console.log('   Message:', message);
    console.log('   Order ID:', orderId || 'none');

    // Validate inputs
    if (!message) {
      console.log('❌ ERROR: Message is missing');
      return res.status(400).json({
        success: false,
        error: 'Message is required'
      });
    }

    if (!personality) {
      console.log('❌ ERROR: Personality is missing');
      return res.status(400).json({
        success: false,
        error: 'Personality is required'
      });
    }

    // Check if Groq is initialized
    if (!groq) {
      console.log('❌ ERROR: Groq not initialized');
      console.log('   GROQ_API_KEY exists:', !!process.env.GROQ_API_KEY);
      console.log('   GROQ_API_KEY value:', process.env.GROQ_API_KEY ? 'SET' : 'NOT SET');
      
      return res.status(500).json({
        success: false,
        error: 'Chatbot not configured properly',
        details: 'GROQ_API_KEY not found or invalid'
      });
    }

    // Get system prompt
    const systemPrompt = personalityPrompts[personality] || personalityPrompts.family;
    console.log('✅ System prompt selected:', personality);

    // Build menu context
    let menuContext = '';
    try {
      let menuItems = [];
      
      if (mongoose.connection.readyState === 1) {
        menuItems = await MenuItem.find({ available: true }).limit(15);
        console.log('✅ Fetched', menuItems.length, 'menu items from database');
      } else {
        const seedData = require('./seedData');
        menuItems = seedData.slice(0, 15);
        console.log('✅ Using', menuItems.length, 'menu items from seedData');
      }

      const menuList = menuItems.map(item => 
        item.name + ' (₹' + item.price + ')'
      ).join(', ');

      menuContext = '\n\nMenu: ' + menuList;
    } catch (err) {
      console.log('⚠️  Could not fetch menu:', err.message);
      menuContext = '\n\nPopular Items: Margherita Pizza (₹349), Chicken Tikka (₹389), Lava Cake (₹199)';
    }

    // Build context
    let contextInfo = 
      'Restaurant: ' + restaurantContext.name + '\n' +
      'Hours: ' + restaurantContext.hours + '\n' +
      'Table: ' + tableNo + 
      menuContext;

    // Prepare messages for Groq
    const messages = [{
      role: 'system',
      content: systemPrompt + '\n\n' + contextInfo + '\n\nBe helpful and concise!'
    }];

    // Add conversation history
    if (conversationHistory && conversationHistory.length > 0) {
      const recentHistory = conversationHistory.slice(-8);
      messages.push(...recentHistory);
    }

    console.log('📡 Calling Groq API...');
    console.log('   Model: llama-3.1-70b-versatile');
    console.log('   Messages count:', messages.length);

    // Call Groq API
    const completion = await groq.chat.completions.create({
      messages: messages,
      model: 'llama-3.1-70b-versatile',
      temperature: 0.7,
      max_tokens: 250,
      top_p: 1,
      stream: false
    });

    const reply = completion.choices[0]?.message?.content || 
                  "I'm here to help! What would you like to know?";

    console.log('✅ SUCCESS! Response generated');
    console.log('   Tokens used:', completion.usage?.total_tokens || 0);
    console.log('   Reply length:', reply.length, 'characters');
    console.log('   Reply preview:', reply.substring(0, 80) + '...');
    console.log('='.repeat(60) + '\n');

    res.json({
      success: true,
      reply: reply,
      personality: personality,
      tokensUsed: completion.usage?.total_tokens || 0
    });

  } catch (error) {
    console.log('❌ CHATBOT ERROR');
    console.log('   Error type:', error.constructor.name);
    console.log('   Error message:', error.message);
    
    if (error.stack) {
      console.log('   Stack trace:', error.stack.split('\n').slice(0, 3).join('\n'));
    }
    
    if (error.response) {
      console.log('   API Response:', error.response);
    }
    
    console.log('='.repeat(60) + '\n');

    res.status(500).json({
      success: false,
      error: 'Failed to generate response',
      details: error.message,
      errorType: error.constructor.name
    });
  }
});

// Restaurant Info
app.get('/api/restaurant-info', (req, res) => {
  res.json({
    success: true,
    restaurant: restaurantContext
  });
});

// Start Server
const PORT = process.env.PORT || 5001;

server.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 RESTAURANT BACKEND SERVER');
  console.log('='.repeat(60));
  console.log('✅ Server running: http://localhost:' + PORT);
  console.log('✅ Socket.IO enabled');
  console.log('✅ MongoDB:', MONGODB_URI);
  console.log('✅ GROQ_API_KEY:', process.env.GROQ_API_KEY ? 'CONFIGURED' : 'MISSING');
  console.log('✅ Groq instance:', groq ? 'INITIALIZED' : 'NOT INITIALIZED');
  console.log('='.repeat(60));
  console.log('\n📝 Test endpoints:');
  console.log('   Health: http://localhost:' + PORT + '/health');
  console.log('   Chatbot Test: http://localhost:' + PORT + '/api/chatbot-test');
  console.log('='.repeat(60) + '\n');
});

module.exports = { app, io };
