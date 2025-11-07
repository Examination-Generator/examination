const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const connectDB = require('./config/database');

// Load environment variables
dotenv.config();

// Initialize express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' })); // Support large base64 images
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Request logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Import routes
const authRoutes = require('./routes/auth');
const subjectRoutes = require('./routes/subjects');
const questionRoutes = require('./routes/questions');

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/subjects', subjectRoutes);
app.use('/api/questions', questionRoutes);

// Health check route
app.get('/api/health', (req, res) => {
    res.json({ 
        success: true, 
        message: 'Examination System API is running',
        timestamp: new Date().toISOString()
    });
});

// Root route
app.get('/', (req, res) => {
    res.json({ 
        success: true, 
        message: 'Welcome to Examination System API',
        version: '1.0.0',
        endpoints: {
            health: '/api/health',
            auth: '/api/auth',
            subjects: '/api/subjects',
            questions: '/api/questions'
        }
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ 
        success: false, 
        message: 'Route not found' 
    });
});

// Global error handler
app.use((err, req, res, next) => {
    console.error('Global error handler:', err);
    res.status(err.status || 500).json({ 
        success: false, 
        message: err.message || 'Internal server error' 
    });
});

// Connect to database and start server
const PORT = process.env.PORT || 5000;

const startServer = async () => {
    try {
        // Connect to MongoDB
        await connectDB();

        // Start server
        app.listen(PORT, () => {
            console.log(`\n[SERVER] Server running on port ${PORT}`);
            console.log(`[SERVER] API URL: http://localhost:${PORT}`);
            console.log(`[SERVER] Health check: http://localhost:${PORT}/api/health\n`);
        });

    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
};

startServer();

module.exports = app;
