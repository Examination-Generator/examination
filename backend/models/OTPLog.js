const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const OTPLog = sequelize.define('OTPLog', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    phoneNumber: {
        type: DataTypes.STRING(20),
        allowNull: false,
        field: 'phone_number'
    },
    otp: {
        type: DataTypes.STRING(10),
        allowNull: false
    },
    purpose: {
        type: DataTypes.ENUM('registration', 'login', 'password_reset'),
        allowNull: false
    },
    status: {
        type: DataTypes.ENUM('pending', 'verified', 'expired', 'failed'),
        defaultValue: 'pending'
    },
    expiresAt: {
        type: DataTypes.DATE,
        allowNull: false,
        field: 'expires_at'
    },
    verifiedAt: {
        type: DataTypes.DATE,
        field: 'verified_at'
    }
}, {
    tableName: 'otp_logs',
    timestamps: true,
    underscored: true,
    updatedAt: false
});

module.exports = OTPLog;
