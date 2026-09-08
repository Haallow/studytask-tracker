// API helper functions
let csrfToken = null;

async function fetchCSRFToken() {
    try {
        const response = await fetch('/csrf-token');
        const data = await response.json();
        csrfToken = data.csrf_token;
        return csrfToken;
    } catch (error) {
        console.error('Error fetching CSRF token:', error);
        return null;
    }
}

async function apiRequest(url, method = 'GET', body = null) {
    // Ensure we have a CSRF token for state-changing operations
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method) && !csrfToken) {
        await fetchCSRFToken();
    }
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (csrfToken && method !== 'GET') {
        headers['X-CSRFToken'] = csrfToken;
    }
    
    const options = {
        method,
        headers,
        credentials: 'same-origin'
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || `HTTP error ${response.status}`);
    }
    
    return data;
}

// Auth functions
async function register(username, email, password, confirmPassword) {
    return await apiRequest('/register', 'POST', {
        username,
        email,
        password,
        confirm_password: confirmPassword
    });
}

async function login(email, password) {
    return await apiRequest('/login', 'POST', { email, password });
}

async function logout() {
    return await apiRequest('/logout', 'POST');
}

async function getCurrentUser() {
    return await apiRequest('/me', 'GET');
}

// Task functions
async function getTasks() {
    return await apiRequest('/tasks', 'GET');
}

async function getTask(taskId) {
    return await apiRequest(`/tasks/${taskId}`, 'GET');
}

async function createTask(taskData) {
    return await apiRequest('/tasks', 'POST', taskData);
}

async function updateTask(taskId, taskData) {
    return await apiRequest(`/tasks/${taskId}`, 'PUT', taskData);
}

async function deleteTask(taskId) {
    return await apiRequest(`/tasks/${taskId}`, 'DELETE');
}

async function toggleTaskComplete(taskId) {
    return await apiRequest(`/tasks/${taskId}/complete`, 'PATCH');
}

// UI helper functions
function showError(message, elementId = 'error-message') {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function hideError(elementId = 'error-message') {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function showSuccess(message, elementId = 'success-message') {
    const successDiv = document.getElementById(elementId);
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }
}

function hideSuccess(elementId = 'success-message') {
    const successDiv = document.getElementById(elementId);
    if (successDiv) {
        successDiv.style.display = 'none';
    }
}

// Initialize CSRF token on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchCSRFToken();
});
