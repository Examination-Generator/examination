// Paper Generation API Service
import { getAuthToken } from './authService';
import { API_URL } from '../config';

const API_BASE_URL = API_URL;

// Helper function to get auth headers
const getAuthHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getAuthToken()}`
});

/**
 * Get topic statistics for a paper
 * Shows how many questions are available for each topic
 * @param {string} paperId - UUID of the paper
 * @returns {Promise} Topic statistics
 */
export const getTopicStatistics = async (paperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/${paperId}/topics/statistics`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching topic statistics:', error);
        throw error;
    }
};

/**
 * Generate a new paper
 * @param {string} paperId - UUID of the paper
 * @param {Array<string>} topicIds - Array of topic UUIDs to include
 * @param {Object} paperData - Optional paper metadata (name, type, etc.)
 * @returns {Promise} Generated paper details
 */
export const generatePaper = async (paperId, topicIds, paperData = null) => {
    try {
        // Determine endpoint based on paper type
        let endpoint = `${API_BASE_URL}/papers/generate`;
        
        // Check if this is Biology Paper 2
        if (paperData) {
            const paperName = paperData.name?.toLowerCase() || '';
            const subjectName = paperData.subject?.toLowerCase() || '';
            
            // Use Biology Paper 2 specific endpoint
            if ((paperName.includes('biology') || subjectName.includes('biology')) && 
                (paperName.includes('paper 2') || paperName.includes('paper two' || paperName.includes('paper II')))) {
                endpoint = `${API_BASE_URL}/papers/biology-paper2/generate`;
                console.log('🧬 Using Biology Paper 2 generation endpoint');
            }
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                paper_id: paperId,
                selected_topics: topicIds
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error generating paper:', error);
        throw error;
    }
};

/**
 * Validate Biology Paper 2 question pool
 * @param {string} paperId - UUID of the paper
 * @param {Array<string>} topicIds - Array of topic UUIDs to validate
 * @returns {Promise} Validation results
 */
export const validateBiologyPaper2Pool = async (paperId, topicIds) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/biology-paper2/validate`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                paper_id: paperId,
                selected_topics: topicIds
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error validating Biology Paper 2 pool:', error);
        throw error;
    }
};

/**
 * Get a specific generated paper with full question details
 * @param {string} generatedPaperId - UUID of the generated paper
 * @returns {Promise} Generated paper with questions
 */
export const getGeneratedPaper = async (generatedPaperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/generated/${generatedPaperId}`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching generated paper:', error);
        throw error;
    }
};

/**
 * View full paper (preview without answers)
 * @param {string} generatedPaperId - UUID of the generated paper
 * @returns {Promise} Paper with questions (no answers)
 */
export const viewFullPaper = async (generatedPaperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/generated/${generatedPaperId}/view`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error viewing full paper:', error);
        throw error;
    }
};

/**
 * Get coverpage data for a generated paper
 * @param {string} generatedPaperId - UUID of the generated paper
 * @returns {Promise} Coverpage data
 */
export const getCoverpageData = async (generatedPaperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/generated/${generatedPaperId}/coverpage/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching coverpage data:', error);
        throw error;
    }
};

/**
 * Update coverpage data for a generated paper
 * @param {string} generatedPaperId - UUID of the generated paper
 * @param {Object} coverpageData - Coverpage information
 * @returns {Promise} Updated coverpage data
 */
export const updateCoverpageData = async (generatedPaperId, coverpageData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/generated/${generatedPaperId}/coverpage/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                coverpage: coverpageData  // Wrap in 'coverpage' key as backend expects
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error updating coverpage data:', error);
        throw error;
    }
};

/**
 * Download paper or marking scheme
 * @param {string} generatedPaperId - UUID of the generated paper
 * @param {Object} options - Download options
 * @param {string} options.format - 'pdf' or 'docx'
 * @param {boolean} options.includeAnswers - Include answers (marking scheme)
 * @param {boolean} options.includeCoverpage - Include coverpage
 * @returns {Promise} Download data
 */
export const downloadPaper = async (generatedPaperId, options = {}) => {
    try {
        const queryParams = new URLSearchParams({
            format: options.format || 'pdf',
            include_answers: options.includeAnswers || false,
            include_coverpage: options.includeCoverpage !== undefined ? options.includeCoverpage : true
        });
        
        const response = await fetch(
            `${API_BASE_URL}/papers/generated/${generatedPaperId}/download?${queryParams.toString()}`,
            {
                method: 'GET',
                headers: getAuthHeaders(),
            }
        );
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error downloading paper:', error);
        throw error;
    }
};

/**
 * Update paper status
 * @param {string} generatedPaperId - UUID of the generated paper
 * @param {string} status - New status (draft/review/published/archived)
 * @returns {Promise} Updated paper
 */
export const updatePaperStatus = async (generatedPaperId, status) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/generated/${generatedPaperId}/status`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify({ status })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error updating paper status:', error);
        throw error;
    }
};

/**
 * List all generated papers with optional filtering
 * @param {Object} filters - Optional filters
 * @param {string} filters.paperId - Filter by paper UUID
 * @param {string} filters.userId - Filter by user UUID
 * @param {string} filters.status - Filter by status
 * @param {boolean} filters.userOnly - Show only current user's papers
 * @returns {Promise} Array of generated papers
 */
export const listGeneratedPapers = async (filters = {}) => {
    try {
        const queryParams = new URLSearchParams();
        
        if (filters.paperId) queryParams.append('paper_id', filters.paperId);
        if (filters.userId) queryParams.append('user_id', filters.userId);
        if (filters.status) queryParams.append('status', filters.status);
        if (filters.userOnly !== undefined) queryParams.append('user_only', filters.userOnly);
        
        const url = `${API_BASE_URL}/papers/generated${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching generated papers:', error);
        throw error;
    }
};

/**
 * Get paper configuration
 * @param {string} paperId - UUID of the paper
 * @returns {Promise} Paper configuration
 */
export const getPaperConfiguration = async (paperId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/${paperId}/configuration`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching paper configuration:', error);
        throw error;
    }
};

/**
 * Update paper configuration (Editor/Admin only)
 * @param {string} paperId - UUID of the paper
 * @param {Object} configData - Configuration updates
 * @returns {Promise} Updated configuration
 */
export const updatePaperConfiguration = async (paperId, configData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/papers/${paperId}/configuration/update`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify(configData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error updating paper configuration:', error);
        throw error;
    }
};

/**
 * Get all subjects with their papers
 * @returns {Promise} List of subjects with papers
 */
export const getAllSubjects = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching subjects:', error);
        throw error;
    }
};

/**
 * Get papers for a specific subject
 * @param {string} subjectId - UUID of the subject
 * @returns {Promise} List of papers for the subject
 */
export const getPapersBySubject = async (subjectId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data?.data?.papers || [];
    } catch (error) {
        console.error('Error fetching papers for subject:', error);
        throw error;
    }
};
