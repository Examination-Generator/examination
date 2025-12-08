/**
 * Environment-aware configuration for the frontend
 * Automatically detects the environment and uses the appropriate backend URL
 */

// Detect the current environment
const getEnvironment = () => {
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'local';
  } else if (hostname.includes('vercel.app')) {
    return 'staging';
  } else if (hostname.includes('speedstarexams.co.ke')) {
    return 'production';
  }
  
  // Default to local if unknown
  return 'local';
};

// Environment-specific configuration
const environments = {
  local: {
    API_URL: process.env.REACT_APP_API_URL || 'https://speedstarexams.co.ke/api',
    ENVIRONMENT: 'development'
  },
  staging: {
    API_URL: process.env.REACT_APP_API_URL || 'https://speedstarexams.co.ke/api',
    ENVIRONMENT: 'staging'
  },
  production: {
    API_URL: process.env.REACT_APP_API_URL || 'https://speedstarexams.co.ke/api',
    ENVIRONMENT: 'production'
  }
};

// Get current environment configuration
const currentEnv = getEnvironment();
const config = environments[currentEnv];

// Export configuration
export const API_URL = config.API_URL;
export const ENVIRONMENT = config.ENVIRONMENT;
export const IS_PRODUCTION = currentEnv === 'production';
export const IS_STAGING = currentEnv === 'staging';
export const IS_LOCAL = currentEnv === 'local';

// Log configuration in development
if (!IS_PRODUCTION) {
  console.log('🔧 Frontend Configuration:', {
    environment: currentEnv,
    apiUrl: API_URL,
    hostname: window.location.hostname
  });
}

export default config;
