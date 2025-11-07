const mongoose = require('mongoose');

/**
 * EXAMINATION SYSTEM - MONGODB SCHEMA
 * Phase 1: Data Entry System
 * 
 * Schema Structure:
 * 1. User Registration (Phone/OTP Authentication)
 * 2. Subject Management
 * 3. Syllabus Organization (Subject → Topic → Paper → Section)
 * 4. Question Bank with Rich Content Support
 */

// ==================== USER AUTHENTICATION SCHEMA ====================

/**
 * User Schema
 * Handles registration with phone number, OTP verification, and password management
 */
const userSchema = new mongoose.Schema({
    // Basic Information
    fullName: {
        type: String,
        required: [true, 'Full name is required'],
        trim: true,
        minlength: [2, 'Name must be at least 2 characters'],
        maxlength: [100, 'Name cannot exceed 100 characters']
    },
    
    // Phone Authentication
    phoneNumber: {
        type: String,
        required: [true, 'Phone number is required'],
        unique: true,
        trim: true,
        match: [/^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/, 'Please enter a valid phone number']
    },
    
    // Password (hashed)
    password: {
        type: String,
        required: [true, 'Password is required'],
        minlength: [6, 'Password must be at least 6 characters']
    },
    
    // OTP Management
    otp: {
        code: {
            type: String,
            default: null
        },
        expiresAt: {
            type: Date,
            default: null
        },
        verified: {
            type: Boolean,
            default: false
        }
    },
    
    // Account Status
    isActive: {
        type: Boolean,
        default: true
    },
    
    role: {
        type: String,
        enum: ['admin', 'editor', 'viewer'],
        default: 'editor'
    },
    
    // Metadata
    createdAt: {
        type: Date,
        default: Date.now
    },
    
    lastLogin: {
        type: Date,
        default: null
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Index for faster phone number lookups
userSchema.index({ phoneNumber: 1 });

// ==================== SUBJECT MANAGEMENT SCHEMA ====================

/**
 * Subject Schema
 * Root level - contains papers, which contain topics, which can have sections
 */
const subjectSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Subject name is required'],
        unique: true,
        trim: true
    },
    
    description: {
        type: String,
        trim: true
    },
    
    // Reference to papers under this subject
    papers: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Paper'
    }],
    
    isActive: {
        type: Boolean,
        default: true
    },
    
    // Metadata
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

subjectSchema.index({ name: 1 });

// ==================== PAPER SCHEMA ====================

/**
 * Paper Schema
 * Papers belong to subjects and contain sections (0 or more)
 */
const paperSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Paper name is required'],
        trim: true
    },
    
    // Parent subject reference
    subject: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Subject',
        required: [true, 'Subject reference is required']
    },
    
    // Papers can have 0 or more sections
    sections: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Section'
    }],
    
    // Reference to topics under this paper
    topics: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Topic'
    }],
    
    description: {
        type: String,
        trim: true
    },
    
    isActive: {
        type: Boolean,
        default: true
    },
    
    // Metadata
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Compound index for subject-paper lookup
paperSchema.index({ subject: 1, name: 1 });

// ==================== SECTION SCHEMA ====================

/**
 * Section Schema
 * Sections belong to papers (optional - papers can have 0 or more sections)
 */
const sectionSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Section name is required'],
        trim: true
    },
    
    // Parent paper reference
    paper: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Paper',
        required: [true, 'Paper reference is required']
    },
    
    description: {
        type: String,
        trim: true
    },
    
    // Section order within paper
    order: {
        type: Number,
        default: 0
    },
    
    isActive: {
        type: Boolean,
        default: true
    },
    
    // Metadata
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Compound index for paper-section lookup
sectionSchema.index({ paper: 1, order: 1 });

// ==================== TOPIC SCHEMA ====================

/**
 * Topic Schema
 * Topics belong to papers and can be filtered by paper
 */
const topicSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Topic name is required'],
        trim: true
    },
    
    // Parent paper reference (topics are filtered by paper)
    paper: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Paper',
        required: [true, 'Paper reference is required']
    },
    
    // Optional section reference (if topic belongs to a specific section)
    section: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Section',
        default: null
    },
    
    description: {
        type: String,
        trim: true
    },
    
    isActive: {
        type: Boolean,
        default: true
    },
    
    // Metadata
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Compound index for paper-topic filtering
topicSchema.index({ paper: 1, name: 1 });
topicSchema.index({ paper: 1, section: 1 });

// ==================== QUESTION SCHEMA ====================

/**
 * Question Schema
 * Supports rich content with inline images, drawings, and graph paper
 */
const questionSchema = new mongoose.Schema({
    // Classification
    subject: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Subject',
        required: [true, 'Subject is required']
    },
    
    paper: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Paper',
        required: [true, 'Paper is required']
    },
    
    topic: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Topic',
        required: [true, 'Topic is required']
    },
    
    // Optional section (since not all papers have sections)
    section: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Section',
        default: null
    },
    
    // Question Content
    questionText: {
        type: String,
        required: [true, 'Question text is required']
    },
    
    // Inline images for question (from editor)
    questionInlineImages: [{
        id: {
            type: Number,
            required: true
        },
        url: {
            type: String,
            required: true
        },
        width: {
            type: Number,
            default: 300
        },
        height: {
            type: Number,
            default: 200
        },
        type: {
            type: String,
            enum: ['upload', 'drawing', 'graph'],
            default: 'upload'
        }
    }],
    
    // Answer Content
    answerText: {
        type: String,
        required: [true, 'Answer text is required']
    },
    
    // Inline images for answer
    answerInlineImages: [{
        id: {
            type: Number,
            required: true
        },
        url: {
            type: String,
            required: true
        },
        width: {
            type: Number,
            default: 300
        },
        height: {
            type: Number,
            default: 200
        },
        type: {
            type: String,
            enum: ['upload', 'drawing', 'graph'],
            default: 'upload'
        }
    }],
    
    // Marks allocation
    marks: {
        type: Number,
        required: [true, 'Marks are required'],
        min: [0, 'Marks cannot be negative']
    },
    
    // Question Status
    isActive: {
        type: Boolean,
        default: true
    },
    
    // Usage tracking
    timesUsed: {
        type: Number,
        default: 0
    },
    
    lastUsed: {
        type: Date,
        default: null
    },
    
    // Metadata
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

// Indexes for efficient querying
questionSchema.index({ subject: 1, paper: 1, topic: 1 });
questionSchema.index({ subject: 1, paper: 1, section: 1 });
questionSchema.index({ isActive: 1 });
questionSchema.index({ createdBy: 1 });

// ==================== OTP LOG SCHEMA ====================

/**
 * OTP Log Schema
 * Track OTP generation and verification for security
 */
const otpLogSchema = new mongoose.Schema({
    phoneNumber: {
        type: String,
        required: true
    },
    
    otp: {
        type: String,
        required: true
    },
    
    purpose: {
        type: String,
        enum: ['registration', 'password_reset', 'login'],
        required: true
    },
    
    status: {
        type: String,
        enum: ['sent', 'verified', 'expired', 'failed'],
        default: 'sent'
    },
    
    expiresAt: {
        type: Date,
        required: true
    },
    
    verifiedAt: {
        type: Date,
        default: null
    },
    
    attempts: {
        type: Number,
        default: 0
    },
    
    ipAddress: {
        type: String
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    }
});

// Index for cleanup of expired OTPs
otpLogSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// ==================== SESSION SCHEMA ====================

/**
 * Session Schema
 * Track user sessions for security
 */
const sessionSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    
    token: {
        type: String,
        required: true,
        unique: true
    },
    
    ipAddress: {
        type: String
    },
    
    userAgent: {
        type: String
    },
    
    expiresAt: {
        type: Date,
        required: true
    },
    
    createdAt: {
        type: Date,
        default: Date.now
    }
});

// Index for token lookup and automatic session cleanup
sessionSchema.index({ token: 1 });
sessionSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// ==================== EXPORT MODELS ====================

const User = mongoose.model('User', userSchema);
const Subject = mongoose.model('Subject', subjectSchema);
const Paper = mongoose.model('Paper', paperSchema);
const Section = mongoose.model('Section', sectionSchema);
const Topic = mongoose.model('Topic', topicSchema);
const Question = mongoose.model('Question', questionSchema);
const OTPLog = mongoose.model('OTPLog', otpLogSchema);
const Session = mongoose.model('Session', sessionSchema);

module.exports = {
    User,
    Subject,
    Paper,
    Section,
    Topic,
    Question,
    OTPLog,
    Session
};
