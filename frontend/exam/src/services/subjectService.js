// Subject Management API Service
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

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

// Get all subjects with populated data
export const getAllSubjects = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects`, {
            method: 'GET',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, count: X, data: [...] }
        // Return just the data array
        return result.data || [];
    } catch (error) {
        console.error('Error fetching subjects:', error);
        throw error;
    }
};

// Get single subject by ID
export const getSubjectById = async (subjectId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}`, {
            method: 'GET',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, data: {...} }
        return result.data || null;
    } catch (error) {
        console.error('Error fetching subject:', error);
        throw error;
    }
};

// Create new subject
export const createSubject = async (subjectData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(subjectData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, message: '...', data: {...} }
        return result.data;
    } catch (error) {
        console.error('Error creating subject:', error);
        throw error;
    }
};

// Update subject
export const updateSubject = async (subjectId, subjectData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}`, {
            method: 'PATCH',  // Use PATCH for partial updates
            headers: getHeaders(),
            body: JSON.stringify(subjectData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, message: '...', data: {...} }
        return result.data;
    } catch (error) {
        console.error('Error updating subject:', error);
        throw error;
    }
};

// Delete subject (soft delete)
export const deleteSubject = async (subjectId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, message: '...' }
        return result;
    } catch (error) {
        console.error('Error deleting subject:', error);
        throw error;
    }
};

// Get topics filtered by paper
export const getTopicsByPaper = async (subjectId, paperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/papers/${paperId}/topics`, {
            method: 'GET',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        // Backend returns { success: true, count: X, data: [...] }
        return result.data || [];
    } catch (error) {
        console.error('Error fetching topics by paper:', error);
        throw error;
    }
};

// Update paper
export const updatePaper = async (subjectId, paperId, paperData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/papers/${paperId}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(paperData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.data;
    } catch (error) {
        console.error('Error updating paper:', error);
        throw error;
    }
};

// Delete paper
export const deletePaper = async (subjectId, paperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/papers/${paperId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error deleting paper:', error);
        throw error;
    }
};

// Update topic
export const updateTopic = async (topicId, topicData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/topics/${topicId}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(topicData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error updating topic:', error);
        throw error;
    }
};

// Delete topic
export const deleteTopic = async (topicId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/topics/${topicId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error deleting topic:', error);
        throw error;
    }
};

// Update section
export const updateSection = async (sectionId, sectionData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/sections/${sectionId}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(sectionData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error updating section:', error);
        throw error;
    }
};

// Delete section
export const deleteSection = async (sectionId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/sections/${sectionId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error deleting section:', error);
        throw error;
    }
};
