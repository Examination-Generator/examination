const { Sequelize } = require('sequelize');

/**
 * PostgreSQL Database Configuration
 * Handles connection setup using Sequelize ORM
 */

const sequelize = new Sequelize(
    process.env.DB_NAME || 'examination_system',
    process.env.DB_USER || 'postgres',
    process.env.DB_PASSWORD || 'postgres',
    {
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 5432,
        dialect: 'postgres',
        logging: process.env.NODE_ENV === 'development' ? console.log : false,
        pool: {
            max: 5,
            min: 0,
            acquire: 30000,
            idle: 10000
        },
        define: {
            timestamps: true,
            underscored: true,
            createdAt: 'created_at',
            updatedAt: 'updated_at'
        }
    }
);

const connectDB = async () => {
    try {
        console.log('[DB] Attempting to connect to PostgreSQL...');
        console.log(`[DB] Database: ${process.env.DB_NAME || 'examination_system'}`);
        console.log(`[DB] Host: ${process.env.DB_HOST || 'localhost'}:${process.env.DB_PORT || 5432}`);
        
        await sequelize.authenticate();
        console.log('[DB] PostgreSQL Connected Successfully');
        
        // Sync models in development (creates tables if they don't exist)
        if (process.env.NODE_ENV === 'development') {
            await sequelize.sync({ alter: false }); // Set to true to auto-update schema
            console.log('[DB] Database synchronized');
        }

        return sequelize;
    } catch (error) {
        console.error('[DB ERROR] Unable to connect to PostgreSQL:', error.message);
        console.error('[DB ERROR] Details:', error);
        process.exit(1);
    }
};

// Graceful shutdown
process.on('SIGINT', async () => {
    try {
        await sequelize.close();
        console.log('[DB] PostgreSQL connection closed');
        process.exit(0);
    } catch (err) {
        console.error('[DB ERROR] Error closing connection:', err);
        process.exit(1);
    }
});

module.exports = { sequelize, connectDB };
