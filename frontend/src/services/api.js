import axios from 'axios';

const API_BASE_URL = 'https://localhost/api'; // Replace with actual API URL

// Axios instance for base configuration
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * User Authentication Services
 */
export const loginUser = async (email, password) => {
    try {
        const response = await apiClient.post('/auth/login', { email, password });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const signupUser = async (email, password) => {
    try {
        const response = await apiClient.post('/auth/signup', { email, password });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const forgotPassword = async (email) => {
    try {
        const response = await apiClient.post('/auth/forgot-password', { email });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const resetPassword = async (token, newPassword) => {
    try {
        const response = await apiClient.post(`/auth/reset-password/${token}`, { newPassword });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

/**
 * Profile Services
 */
export const fetchUserProfile = async (userId) => {
    try {
        const response = await apiClient.get(`/profile/${userId}`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const updateUserProfile = async (userId, profileData) => {
    try {
        const response = await apiClient.put(`/profile/${userId}`, profileData);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

/**
 * Resume Upload Services
 */
export const uploadResume = async (userId, resumeFile) => {
    try {
        const formData = new FormData();
        formData.append('file', resumeFile);

        const response = await apiClient.post(`/resume/upload/${userId}`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

/**
 * Application Tracking Services
 */
export const fetchApplications = async (userId) => {
    try {
        const response = await apiClient.get(`/applications/${userId}`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const addApplication = async (userId, applicationData) => {
    try {
        const response = await apiClient.post(`/applications/${userId}`, applicationData);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const deleteApplication = async (userId, applicationId) => {
    try {
        const response = await apiClient.delete(`/applications/${userId}/${applicationId}`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export default apiClient;
