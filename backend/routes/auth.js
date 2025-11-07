const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { User, OTPLog } = require('../models/schema');

/**
 * USER AUTHENTICATION ROUTES
 * 
 * Routes:
 * - POST /api/auth/send-otp - Send OTP to phone number
 * - POST /api/auth/verify-otp - Verify OTP code
 * - POST /api/auth/register - Complete registration with password
 * - POST /api/auth/login - Login with phone and password
 * - POST /api/auth/logout - Logout user
 * - POST /api/auth/forgot-password - Initiate password reset
 * - POST /api/auth/reset-password - Reset password with OTP
 */

// JWT Secret (should be in environment variable)
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

// ==================== HELPER FUNCTIONS ====================

/**
 * Generate random 6-digit OTP
 */
const generateOTP = () => {
    return Math.floor(100000 + Math.random() * 900000).toString();
};

/**
 * Send OTP via SMS (Mock implementation - integrate with SMS provider)
 */
const sendSMS = async (phoneNumber, message) => {
    // TODO: Integrate with SMS provider (Twilio, Africa's Talking, etc.)
    console.log(`📱 Sending SMS to ${phoneNumber}: ${message}`);
    
    // Mock implementation - always succeeds
    return { success: true };
};

/**
 * Generate JWT token
 */
const generateToken = (userId) => {
    return jwt.sign({ userId }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
};

// ==================== ROUTES ====================

/**
 * @route   POST /api/auth/send-otp
 * @desc    Send OTP to phone number for registration or login
 * @access  Public
 */
router.post('/send-otp', async (req, res) => {
    try {
        const { phoneNumber, purpose = 'registration' } = req.body;

        // Validate phone number
        if (!phoneNumber) {
            return res.status(400).json({ 
                success: false, 
                message: 'Phone number is required' 
            });
        }

        // Check if user exists
        const existingUser = await User.findOne({ phoneNumber });

        if (purpose === 'registration' && existingUser) {
            return res.status(400).json({ 
                success: false, 
                message: 'Phone number already registered. Please login.' 
            });
        }

        if (purpose === 'login' && !existingUser) {
            return res.status(404).json({ 
                success: false, 
                message: 'Phone number not registered. Please register first.' 
            });
        }

        // Generate OTP
        const otp = generateOTP();
        const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

        // Save OTP to log
        await OTPLog.create({
            phoneNumber,
            otp,
            purpose,
            expiresAt,
            ipAddress: req.ip
        });

        // If user exists, update their OTP
        if (existingUser) {
            existingUser.otp = {
                code: otp,
                expiresAt,
                verified: false
            };
            await existingUser.save();
        }

        // Send OTP via SMS
        const smsResult = await sendSMS(
            phoneNumber, 
            `Your verification code is: ${otp}. Valid for 10 minutes.`
        );

        if (!smsResult.success) {
            return res.status(500).json({ 
                success: false, 
                message: 'Failed to send OTP. Please try again.' 
            });
        }

        res.json({ 
            success: true, 
            message: 'OTP sent successfully',
            expiresIn: 600 // seconds
        });

    } catch (error) {
        console.error('Send OTP error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   POST /api/auth/verify-otp
 * @desc    Verify OTP code
 * @access  Public
 */
router.post('/verify-otp', async (req, res) => {
    try {
        const { phoneNumber, otp } = req.body;

        // Validate input
        if (!phoneNumber || !otp) {
            return res.status(400).json({ 
                success: false, 
                message: 'Phone number and OTP are required' 
            });
        }

        // Find OTP log
        const otpLog = await OTPLog.findOne({
            phoneNumber,
            otp,
            status: 'sent',
            expiresAt: { $gt: new Date() }
        }).sort({ createdAt: -1 });

        if (!otpLog) {
            return res.status(400).json({ 
                success: false, 
                message: 'Invalid or expired OTP' 
            });
        }

        // Check attempts (max 5)
        if (otpLog.attempts >= 5) {
            return res.status(400).json({ 
                success: false, 
                message: 'Too many attempts. Please request a new OTP.' 
            });
        }

        // Update OTP log
        otpLog.status = 'verified';
        otpLog.verifiedAt = new Date();
        await otpLog.save();

        // Check if user exists
        let user = await User.findOne({ phoneNumber });

        if (user) {
            user.otp.verified = true;
            await user.save();
        }

        res.json({ 
            success: true, 
            message: 'OTP verified successfully',
            userExists: !!user
        });

    } catch (error) {
        console.error('Verify OTP error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   POST /api/auth/register
 * @desc    Complete registration after OTP verification
 * @access  Public
 */
router.post('/register', async (req, res) => {
    try {
        const { phoneNumber, fullName, password } = req.body;
        console.log('[AUTH] Registration attempt for:', phoneNumber);

        // Validate input
        if (!phoneNumber || !fullName || !password) {
            console.log('[AUTH] Missing required fields');
            return res.status(400).json({ 
                success: false, 
                message: 'All fields are required' 
            });
        }

        // Validate password length
        if (password.length < 6) {
            console.log('[AUTH] Password too short');
            return res.status(400).json({ 
                success: false, 
                message: 'Password must be at least 6 characters' 
            });
        }

        // Check if user already exists
        const existingUser = await User.findOne({ phoneNumber });
        if (existingUser) {
            console.log('[AUTH] User already exists:', phoneNumber);
            return res.status(400).json({ 
                success: false, 
                message: 'Phone number already registered' 
            });
        }

        // Verify that OTP was verified
        const otpLog = await OTPLog.findOne({
            phoneNumber,
            status: 'verified',
            purpose: 'registration'
        }).sort({ createdAt: -1 });

        if (!otpLog) {
            console.log('[AUTH] OTP not verified for:', phoneNumber);
            return res.status(400).json({ 
                success: false, 
                message: 'Please verify OTP first' 
            });
        }

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Create user
        const user = await User.create({
            phoneNumber,
            fullName,
            password: hashedPassword,
            otp: {
                verified: true
            }
        });

        // Generate token
        const token = generateToken(user._id);

        console.log('[AUTH] User registered successfully:', phoneNumber);

        res.status(201).json({ 
            success: true, 
            message: 'Registration successful',
            token,
            user: {
                id: user._id,
                fullName: user.fullName,
                phoneNumber: user.phoneNumber,
                role: user.role
            }
        });

    } catch (error) {
        console.error('[AUTH ERROR] Registration error:', error.message);
        console.error(error.stack);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.',
            error: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

/**
 * @route   POST /api/auth/login
 * @desc    Login with phone number and password
 * @access  Public
 */
router.post('/login', async (req, res) => {
    try {
        const { phoneNumber, password } = req.body;
        console.log('[AUTH] Login attempt for:', phoneNumber);

        // Validate input
        if (!phoneNumber || !password) {
            console.log('[AUTH] Missing credentials');
            return res.status(400).json({ 
                success: false, 
                message: 'Phone number and password are required' 
            });
        }

        // Find user
        const user = await User.findOne({ phoneNumber });
        if (!user) {
            console.log('[AUTH] User not found:', phoneNumber);
            return res.status(401).json({ 
                success: false, 
                message: 'Invalid credentials' 
            });
        }

        // Check if account is active
        if (!user.isActive) {
            console.log('[AUTH] Account deactivated:', phoneNumber);
            return res.status(403).json({ 
                success: false, 
                message: 'Account is deactivated. Please contact support.' 
            });
        }

        // Verify password
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            console.log('[AUTH] Invalid password for:', phoneNumber);
            return res.status(401).json({ 
                success: false, 
                message: 'Invalid credentials' 
            });
        }

        // Update last login
        user.lastLogin = new Date();
        await user.save();

        // Generate token
        const token = generateToken(user._id);

        console.log('[AUTH] Login successful:', phoneNumber, 'Role:', user.role);
        res.json({ 
            success: true, 
            message: 'Login successful',
            token,
            user: {
                id: user._id,
                fullName: user.fullName,
                phoneNumber: user.phoneNumber,
                role: user.role
            }
        });

    } catch (error) {
        console.error('[AUTH ERROR] Login error:', error.message);
        console.error(error.stack);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.',
            error: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

/**
 * @route   POST /api/auth/forgot-password
 * @desc    Initiate password reset with OTP
 * @access  Public
 */
router.post('/forgot-password', async (req, res) => {
    try {
        const { phoneNumber } = req.body;

        // Validate input
        if (!phoneNumber) {
            return res.status(400).json({ 
                success: false, 
                message: 'Phone number is required' 
            });
        }

        // Find user
        const user = await User.findOne({ phoneNumber });
        if (!user) {
            return res.status(404).json({ 
                success: false, 
                message: 'Phone number not registered' 
            });
        }

        // Generate OTP
        const otp = generateOTP();
        const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

        // Save OTP
        await OTPLog.create({
            phoneNumber,
            otp,
            purpose: 'password_reset',
            expiresAt,
            ipAddress: req.ip
        });

        // Update user OTP
        user.otp = {
            code: otp,
            expiresAt,
            verified: false
        };
        await user.save();

        // Send OTP via SMS
        await sendSMS(
            phoneNumber, 
            `Your password reset code is: ${otp}. Valid for 10 minutes.`
        );

        res.json({ 
            success: true, 
            message: 'Password reset OTP sent successfully' 
        });

    } catch (error) {
        console.error('Forgot password error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   POST /api/auth/reset-password
 * @desc    Reset password with verified OTP
 * @access  Public
 */
router.post('/reset-password', async (req, res) => {
    try {
        const { phoneNumber, otp, newPassword } = req.body;

        // Validate input
        if (!phoneNumber || !otp || !newPassword) {
            return res.status(400).json({ 
                success: false, 
                message: 'All fields are required' 
            });
        }

        // Validate password length
        if (newPassword.length < 6) {
            return res.status(400).json({ 
                success: false, 
                message: 'Password must be at least 6 characters' 
            });
        }

        // Verify OTP
        const otpLog = await OTPLog.findOne({
            phoneNumber,
            otp,
            purpose: 'password_reset',
            status: 'sent',
            expiresAt: { $gt: new Date() }
        }).sort({ createdAt: -1 });

        if (!otpLog) {
            return res.status(400).json({ 
                success: false, 
                message: 'Invalid or expired OTP' 
            });
        }

        // Find user
        const user = await User.findOne({ phoneNumber });
        if (!user) {
            return res.status(404).json({ 
                success: false, 
                message: 'User not found' 
            });
        }

        // Hash new password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(newPassword, salt);

        // Update password
        user.password = hashedPassword;
        user.otp.verified = true;
        await user.save();

        // Update OTP log
        otpLog.status = 'verified';
        otpLog.verifiedAt = new Date();
        await otpLog.save();

        res.json({ 
            success: true, 
            message: 'Password reset successful. Please login with your new password.' 
        });

    } catch (error) {
        console.error('Reset password error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

module.exports = router;
