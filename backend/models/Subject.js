const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Subject = sequelize.define('Subject', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    name: {
        type: DataTypes.STRING(255),
        allowNull: false,
        unique: true
    },
    description: {
        type: DataTypes.TEXT
    },
    isActive: {
        type: DataTypes.BOOLEAN,
        defaultValue: true,
        field: 'is_active'
    },
    createdBy: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'created_by',
        references: {
            model: 'users',
            key: 'id'
        }
    }
}, {
    tableName: 'subjects',
    timestamps: true,
    underscored: true
});

module.exports = Subject;
