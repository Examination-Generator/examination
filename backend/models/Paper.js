const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Paper = sequelize.define('Paper', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    subjectId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'subject_id',
        references: {
            model: 'subjects',
            key: 'id'
        }
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
    tableName: 'papers',
    timestamps: true,
    underscored: true,
    indexes: [
        {
            unique: true,
            fields: ['subject_id', 'name']
        }
    ]
});

module.exports = Paper;
