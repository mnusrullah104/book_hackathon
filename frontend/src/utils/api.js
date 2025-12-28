// Backend API URL
const API_URL = process.env.API_URL || 'http://localhost:7860/api';

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Critical for cookie transmission
  });

  return response;
}

export default apiRequest;
