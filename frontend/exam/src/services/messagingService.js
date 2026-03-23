import { API_URL } from '../config';
import { APIError, handleAPIError } from './errors';

/**
 * Messaging Service
 * Handles both SMS messaging and system messaging (support messages)
 */

// Get auth token
const getAuthHeaders = (includeJsonContentType = true) => {
    // Keep backward compatibility with older key while aligning with authService.
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
    const headers = {
        ...(token && { 'Authorization': `Bearer ${token}` })
    };

    if (includeJsonContentType) {
        headers['Content-Type'] = 'application/json';
    }

    return headers;
};

const buildSystemMessagePayload = (data = {}) => {
    const normalizedData = {
        ...data,
        quoted_text: data.quoted_text ?? data.quotedText
    };

    if (normalizedData.attachment) {
        const formData = new FormData();
        if (normalizedData.subject !== undefined) formData.append('subject', normalizedData.subject || '');
        if (normalizedData.message !== undefined) formData.append('message', normalizedData.message || '');
        if (normalizedData.quoted_text !== undefined) formData.append('quoted_text', normalizedData.quoted_text || '');
        formData.append('attachment', normalizedData.attachment);
        return { body: formData, isMultipart: true };
    }

    return {
        body: JSON.stringify(normalizedData),
        isMultipart: false
    };
};

const normalizeMessageList = (payload) => {
    if (Array.isArray(payload)) {
        return payload;
    }

    if (Array.isArray(payload?.data)) {
        return payload.data;
    }

    if (Array.isArray(payload?.results)) {
        return payload.results;
    }

    return [];
};

const normalizeCount = (payload) => {
    if (typeof payload?.count === 'number') {
        return payload.count;
    }

    if (typeof payload?.data?.count === 'number') {
        return payload.data.count;
    }

    return 0;
};

// ==================== SMS Messaging ====================

/**
 * Search for contacts by name or phone number
 * @param {string} query - Search query (name or phone number)
 * @returns {Promise<Array>} List of matching contacts
 */
export const searchContacts = async (query) => {
    try {
        const response = await fetch(
            `${API_URL}/messaging/contacts/search?q=${encodeURIComponent(query)}`,
            {
                method: 'GET',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to search contacts', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to search contacts');
    }
};

/**
 * Send SMS to one or multiple recipients
 * @param {Object} data - SMS data
 * @param {Array<string>} data.recipients - Array of phone numbers
 * @param {string} data.message - Message content
 * @returns {Promise<Object>} Send result
 */
export const sendSMS = async (data) => {
    try {
        const response = await fetch(`${API_URL}/messaging/sms/send`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new APIError('Failed to send SMS', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to send SMS');
    }
};

/**
 * Get SMS conversation history with a contact
 * @param {string} phoneNumber - Phone number
 * @returns {Promise<Array>} SMS conversation history
 */
export const getSMSConversation = async (phoneNumber) => {
    try {
        const response = await fetch(
            `${API_URL}/messaging/sms/conversation/${encodeURIComponent(phoneNumber)}`,
            {
                method: 'GET',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to fetch SMS conversation', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to fetch SMS conversation');
    }
};

/**
 * Get all SMS conversations
 * @returns {Promise<Array>} List of SMS conversations
 */
export const getAllSMSConversations = async () => {
    try {
        const response = await fetch(`${API_URL}/messaging/sms/conversations`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new APIError('Failed to fetch SMS conversations', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to fetch SMS conversations');
    }
};

// ==================== System Messaging (Support) ====================

/**
 * Send a system message (support message from user to admin)
 * @param {Object} data - Message data
 * @param {string} data.subject - Message subject
 * @param {string} data.message - Message content
 * @returns {Promise<Object>} Created message
 */
export const sendSystemMessage = async (data) => {
    try {
        const payload = buildSystemMessagePayload(data);
        const response = await fetch(`${API_URL}/messaging/system/send`, {
            method: 'POST',
            headers: getAuthHeaders(!payload.isMultipart),
            body: payload.body
        });

        if (!response.ok) {
            throw new APIError('Failed to send message', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to send message');
    }
};

/**
 * Get system messages (inbox)
 * @param {Object} params - Query parameters
 * @param {boolean} params.unreadOnly - Get only unread messages
 * @returns {Promise<Array>} List of system messages
 */
export const getSystemMessages = async (params = {}) => {
    try {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(
            `${API_URL}/messaging/system/messages${queryString ? '?' + queryString : ''}`,
            {
                method: 'GET',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to fetch messages', response.status);
        }

        const data = await response.json();
        return normalizeMessageList(data);
    } catch (error) {
        return handleAPIError(error, 'Failed to fetch messages');
    }
};

/**
 * Get a specific system message conversation
 * @param {string} messageId - Message ID
 * @returns {Promise<Object>} Message with replies
 */
export const getSystemMessageConversation = async (messageId) => {
    try {
        const response = await fetch(
            `${API_URL}/messaging/system/messages/${messageId}/conversation`,
            {
                method: 'GET',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to fetch conversation', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to fetch conversation');
    }
};

/**
 * Reply to a system message
 * @param {string} messageId - Original message ID
 * @param {Object} data - Reply data
 * @param {string} data.message - Reply content
 * @param {string} data.quotedText - Quoted text from original message (optional)
 * @returns {Promise<Object>} Reply message
 */
export const replyToSystemMessage = async (messageId, data) => {
    try {
        const payload = buildSystemMessagePayload(data);
        const response = await fetch(
            `${API_URL}/messaging/system/messages/${messageId}/reply`,
            {
                method: 'POST',
                headers: getAuthHeaders(!payload.isMultipart),
                body: payload.body
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to send reply', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to send reply');
    }
};

/**
 * Mark a system message as read
 * @param {string} messageId - Message ID
 * @returns {Promise<Object>} Updated message
 */
export const markSystemMessageAsRead = async (messageId) => {
    try {
        const response = await fetch(
            `${API_URL}/messaging/system/messages/${messageId}/read`,
            {
                method: 'PUT',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to mark message as read', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to mark message as read');
    }
};

/**
 * Get unread message count
 * @returns {Promise<number>} Count of unread messages
 */
export const getUnreadMessageCount = async () => {
    try {
        const response = await fetch(`${API_URL}/messaging/system/unread-count`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new APIError('Failed to fetch unread count', response.status);
        }

        const data = await response.json();
        return normalizeCount(data);
    } catch (error) {
        console.error('Failed to fetch unread count:', error);
        return 0;
    }
};

/**
 * Delete a system message
 * @param {string} messageId - Message ID
 * @returns {Promise<Object>} Delete result
 */
export const deleteSystemMessage = async (messageId) => {
    try {
        const response = await fetch(
            `${API_URL}/messaging/system/messages/${messageId}`,
            {
                method: 'DELETE',
                headers: getAuthHeaders()
            }
        );

        if (!response.ok) {
            throw new APIError('Failed to delete message', response.status);
        }

        return await response.json();
    } catch (error) {
        return handleAPIError(error, 'Failed to delete message');
    }
};
