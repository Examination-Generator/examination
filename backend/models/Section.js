const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Section = sequelize.define('Section', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    paperId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'paper_id',
        references: {
            model: 'papers',
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
    tableName: 'sections',
    timestamps: true,
    underscored: true,
    indexes: [
        {
            unique: true,
            fields: ['paper_id', 'name']
        }
    ]
});

module.exports = Section;
