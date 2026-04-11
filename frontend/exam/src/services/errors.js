// Custom API Error class
export class APIError extends Error {
    constructor(message, statusCode = 500, data = null) {
        super(message);
        this.name = 'APIError';
        this.statusCode = statusCode;
        this.data = data;
    }
}

// User-friendly error helper for services
export const friendlyErrorMessage = (raw, fallback = 'Something went wrong. Please try again or contact support.') => {
    const msg = typeof raw === 'string' ? raw : (raw && raw.message) ? raw.message : '';
    const s = (msg || '').toString();

    if (/insufficient|insufficient questions|insufficient question|not enough questions/i.test(s)) {
        return 'Select more topics';
    }
    if (/encoding|ascii|codec|unicode/i.test(s)) {
        return 'A server encoding error occurred while processing your request. Please try again later.';
    }
    if (/timeout|timed out/i.test(s)) {
        return 'The server took too long to respond. Please try again.';
    }
    if (/unauthorized|401/i.test(s)) {
        return 'You are not authorized. Please login again.';
    }
    if (/forbidden|403/i.test(s)) {
        return 'You do not have permission to perform this action.';
    }
    if (/not found|404/i.test(s)) {
        return 'Requested data was not found.';
    }
    if (/http error|status:\s*\d+/i.test(s)) {
        return 'The server returned an error. Please try again later.';
    }

    return fallback;
};

// Handle API errors with friendly messages
export const handleAPIError = (error, defaultMessage = 'An error occurred') => {
    console.error('API Error:', error);
    
    if (error instanceof APIError) {
        throw error;
    }
    
    const message = friendlyErrorMessage(error, defaultMessage);
    throw new APIError(message, error.statusCode || 500);
};

export default friendlyErrorMessage;
