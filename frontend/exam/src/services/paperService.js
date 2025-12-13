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
        console.log('📤 ========== PAPER GENERATION REQUEST ==========');
        console.log('📄 Paper ID:', paperId);
        console.log('📚 Selected Topic IDs:', topicIds);
        console.log('🗂️ Paper Data (FULL OBJECT):', JSON.stringify(paperData, null, 2));
        
        // Determine endpoint based on paper type
        let endpoint = `${API_BASE_URL}/papers/generate`;
        let paperType = 'standard';
        
        // Check if this is Biology Paper 2
        if (paperData) {
            console.log('🔍 Checking paper type using database fields...');
            console.log('   Available fields:', Object.keys(paperData));
            console.log('   Paper object:', paperData);
            
            // Get paper metadata from database object
            const paperNumber = paperData.paper_number || paperData.number || null;
            const paperName = paperData.name?.toLowerCase() || '';
            const subjectId = paperData.subject_id || paperData.subject?.id || null;
            const subjectName = paperData.subject?.name?.toLowerCase() || paperData.subject_name?.toLowerCase() || '';
            
            console.log('   Paper Number (from DB):', paperNumber);
            console.log('   Paper Name:', paperName);
            console.log('   Subject ID:', subjectId);
            console.log('   Subject Name:', subjectName);
            
            // Check for Biology Paper 2
            const isBiology = paperName.includes('biology') || subjectName.includes('biology');
            const isPaper2 = paperNumber === 2 || 
                           paperNumber === '2' || 
                           paperName.includes('paper 2') || 
                           paperName.includes('paper two') || 
                           paperName.includes('paper ii');
            
            // Check for Physics Paper 1
            const isPhysics = paperName.includes('physics') || subjectName.includes('physics');
            const isPaper1 = paperNumber === 1 || 
                           paperNumber === '1' || 
                           paperName.includes('paper 1') || 
                           paperName.includes('paper one') || 
                           paperName.includes('paper i');
            
            console.log('   Is Biology?', isBiology);
            console.log('   Is Paper 2?', isPaper2);
            console.log('   Is Physics?', isPhysics);
            console.log('   Is Paper 1?', isPaper1);
            
            if (isBiology && isPaper2) {
                endpoint = `${API_BASE_URL}/papers/biology-paper2/generate`;
                paperType = 'biology-paper2';
                console.log('🧬 ✅ DETECTED: Biology Paper 2 (using dedicated endpoint)');
            } else if (isPhysics && isPaper1) {
                endpoint = `${API_BASE_URL}/papers/physics-paper1/generate`;
                paperType = 'physics-paper1';
                console.log('⚛️ ✅ DETECTED: Physics Paper 1 (using dedicated endpoint)');
            } else {
                console.log('📝 DETECTED: Standard Paper (using general endpoint)');
            }
        }
        
        const requestBody = {
            paper_id: paperId,
            topic_ids: topicIds
        };
        
        console.log('Target Endpoint:', endpoint);
        console.log('Request Body:', JSON.stringify(requestBody, null, 2));
        console.log('Headers:', getAuthHeaders());
        console.log('=================================================');
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(requestBody)
        });
        
        console.log('📡 Response Status:', response.status, response.statusText);
        
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
                console.error(' Error Response Data:', errorData);
            } catch (e) {
                const errorText = await response.text();
                console.error(' Error Response Text:', errorText);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            throw new Error(errorData.error || errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Generation Success! Result:', result);
        return result;
    } catch (error) {
        console.error('========== GENERATION ERROR ==========');
        console.error('Error Type:', error.name);
        console.error('Error Message:', error.message);
        console.error('Error Stack:', error.stack);
        console.error('=========================================');
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
        const endpoint = `${API_BASE_URL}/papers/biology-paper2/validate`;
        const requestBody = {
            paper_id: paperId,
            topic_ids: topicIds
        };
        
        console.log(' ========== BIOLOGY PAPER 2 VALIDATION ==========');
        console.log('Endpoint:', endpoint);
        console.log('Request Body:', JSON.stringify(requestBody, null, 2));
        console.log('==================================================');
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(requestBody)
        });
        
        console.log('📡 Validation Response Status:', response.status, response.statusText);
        
        if (!response.ok) {
            // Read the response body as text first (can only read once!)
            const errorText = await response.text();
            console.error('Validation Error Response:', errorText);
            
            // Try to parse as JSON
            let errorMessage;
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.error || errorData.message || `HTTP error! status: ${response.status}`;
            } catch (e) {
                // If not JSON, use the text directly
                errorMessage = errorText || `HTTP error! status: ${response.status}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        console.log(' Validation Result:', result);
        return result;
    } catch (error) {
        console.error(' Validation Error:', error);
        throw error;
    }
};

/**
 * Validate Physics Paper 1 question pool
 * @param {string} paperId - UUID of the paper
 * @param {Array<string>} topicIds - Array of topic UUIDs to validate
 * @returns {Promise} Validation results
 */
export const validatePhysicsPaper1Pool = async (paperId, topicIds) => {
    try {
        const endpoint = `${API_BASE_URL}/papers/physics-paper1/validate`;
        const requestBody = {
            paper_id: paperId,
            topic_ids: topicIds  
        };
        
        console.log(' ========== PHYSICS PAPER 1 VALIDATION ==========');
        console.log('Endpoint:', endpoint);
        console.log('Request Body:', JSON.stringify(requestBody, null, 2));
        console.log('==================================================');
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(requestBody)
        });
        
        console.log('Validation Response Status:', response.status, response.statusText);
        
        if (!response.ok) {
            // Read the response body as text first (can only read once!)
            const errorText = await response.text();
            console.error('Validation Error Response:', errorText);
            
            // Try to parse as JSON
            let errorMessage;
            try {
                const errorData = JSON.parse(errorText);
                console.error('Validation Error Data:', errorData);
                errorMessage = errorData.error || errorData.message || `HTTP error! status: ${response.status}`;
            } catch (e) {
                // If not JSON, use the text directly
                errorMessage = errorText || `HTTP error! status: ${response.status}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        console.log('Validation Result:', result);
        return result;
    } catch (error) {
        console.error(' Validation Error:', error);
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
