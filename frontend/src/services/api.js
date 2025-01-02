import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Authentication
export const login = async (email, password) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/login`, { email, password });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const signup = async (email, password) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/signup`, { email, password });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const forgotPassword = async (email) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/forgot-password`, { email });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const resetPassword = async (token, newPassword) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/reset-password`, { token, newPassword });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

// Profile Management
export const getProfile = async (token) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/profile`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const updateProfile = async (token, profileData) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/profile`, profileData, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

// Resume Upload
export const uploadResume = async (token, formData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/resume/upload`, formData, {
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

// Application Tracking
export const getApplications = async (token) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/applications`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const addApplication = async (token, applicationData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/applications`, applicationData, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const updateApplication = async (token, applicationId, applicationData) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/applications/${applicationId}`, applicationData, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const deleteApplication = async (token, applicationId) => {
    try {
        const response = await axios.delete(`${API_BASE_URL}/applications/${applicationId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};
