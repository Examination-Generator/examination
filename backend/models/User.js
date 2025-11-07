const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');
const bcrypt = require('bcryptjs');

const User = sequelize.define('User', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    phoneNumber: {
        type: DataTypes.STRING(20),
        allowNull: false,
        unique: true,
        field: 'phone_number'
    },
    fullName: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'full_name'
    },
    password: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    role: {
        type: DataTypes.ENUM('user', 'editor', 'admin'),
        defaultValue: 'user'
    },
    isActive: {
        type: DataTypes.BOOLEAN,
        defaultValue: true,
        field: 'is_active'
    },
    otpVerified: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        field: 'otp_verified'
    },
    lastLogin: {
        type: DataTypes.DATE,
        field: 'last_login'
    }
}, {
    tableName: 'users',
    timestamps: true,
    underscored: true
});

// Instance method to compare password
User.prototype.comparePassword = async function(candidatePassword) {
    return await bcrypt.compare(candidatePassword, this.password);
};

// Hook to hash password before saving
User.beforeCreate(async (user) => {
    if (user.password) {
        const salt = await bcrypt.genSalt(10);
        user.password = await bcrypt.hash(user.password, salt);
    }
});

User.beforeUpdate(async (user) => {
    if (user.changed('password')) {
        const salt = await bcrypt.genSalt(10);
        user.password = await bcrypt.hash(user.password, salt);
    }
});

module.exports = User;
