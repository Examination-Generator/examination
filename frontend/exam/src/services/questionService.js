// Question Management API Service
import { API_URL } from '../config';

const API_BASE_URL = API_URL;

// Get authentication token from localStorage
const getAuthToken = () => {
    return localStorage.getItem('token');
};

// Create headers with authentication
const getHeaders = () => {
    const token = getAuthToken();
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
};

// Get all questions with filters
export const getAllQuestions = async (filters = {}) => {
    try {
        const params = new URLSearchParams();
        
        if (filters.subject) params.append('subject', filters.subject);
        if (filters.paper) params.append('paper', filters.paper);
        if (filters.topic) params.append('topic', filters.topic);
        if (filters.section) params.append('section', filters.section);
        if (filters.isActive !== undefined) params.append('isActive', filters.isActive);
        if (filters.page) params.append('page', filters.page);
        if (filters.limit) params.append('limit', filters.limit);
        
        const url = `${API_BASE_URL}/questions${params.toString() ? '?' + params.toString() : ''}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, data: { questions: [...], total: X } }
        return result.data?.questions || [];
    } catch (error) {
        console.error('Error fetching questions:', error);
        throw error;
    }
};

// Get question statistics
export const getQuestionStats = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/questions/stats/overview`, {
            method: 'GET',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.data || {};
    } catch (error) {
        console.error('Error fetching question stats:', error);
        throw error;
    }
};

// Get single question by ID
export const getQuestionById = async (questionId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
            method: 'GET',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error fetching question:', error);
        throw error;
    }
};

// Create new question
export const createQuestion = async (questionData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/questions`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(questionData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.data;
    } catch (error) {
        console.error('Error creating question:', error);
        throw error;
    }
};

// Update question
export const updateQuestion = async (questionId, questionData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(questionData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.data;
    } catch (error) {
        console.error('Error updating question:', error);
        throw error;
    }
};

// Delete question
export const deleteQuestion = async (questionId) => {
    try {
        console.log('🗑️ DELETE request - Question ID:', questionId);
        console.log('🗑️ DELETE URL:', `${API_BASE_URL}/questions/hard-delete/${questionId}`);
        
        const response = await fetch(`${API_BASE_URL}/questions/hard-delete/${questionId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        console.log('🗑️ DELETE response status:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('🗑️ DELETE failed:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('🗑️ DELETE result:', result);
        return result;
    } catch (error) {
        console.error('Error deleting question:', error);
        throw error;
    }
};
