const jwt = require('jsonwebtoken');
const { User } = require('../models/schema');

/**
 * Authentication Middleware
 * Verifies JWT token and attaches user info to request
 */

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

const authMiddleware = async (req, res, next) => {
    try {
        // Get token from header
        const token = req.header('Authorization')?.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({ 
                success: false, 
                message: 'No token provided. Authentication required.' 
            });
        }

        // Verify token
        const decoded = jwt.verify(token, JWT_SECRET);

        // Find user
        const user = await User.findById(decoded.userId);

        if (!user) {
            return res.status(401).json({ 
                success: false, 
                message: 'Invalid token. User not found.' 
            });
        }

        // Check if user is active
        if (!user.isActive) {
            return res.status(403).json({ 
                success: false, 
                message: 'Account is deactivated. Please contact support.' 
            });
        }

        // Attach user info to request
        req.user = {
            userId: user._id,
            fullName: user.fullName,
            phoneNumber: user.phoneNumber,
            role: user.role
        };

        next();

    } catch (error) {
        if (error.name === 'JsonWebTokenError') {
            return res.status(401).json({ 
                success: false, 
                message: 'Invalid token.' 
            });
        }

        if (error.name === 'TokenExpiredError') {
            return res.status(401).json({ 
                success: false, 
                message: 'Token expired. Please login again.' 
            });
        }

        console.error('Auth middleware error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
};

/**
 * Role-based authorization middleware
 */
const authorize = (...roles) => {
    return (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ 
                success: false, 
                message: 'Authentication required.' 
            });
        }

        if (!roles.includes(req.user.role)) {
            return res.status(403).json({ 
                success: false, 
                message: 'You do not have permission to perform this action.' 
            });
        }

        next();
    };
};

module.exports = {
    authMiddleware,
    authorize
};
