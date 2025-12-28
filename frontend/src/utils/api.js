// Backend API URL - Production HuggingFace endpoint
const API_URL = 'https://mnusrulah104-robotics-rag-backend.hf.space/api';

/**
 * Generic API request helper with error handling
 * @param {string} endpoint - API endpoint (e.g., '/chat/message')
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  });

  return response;
}

/**
 * Send a chat message to the RAG backend
 * @param {string} message - User message
 * @returns {Promise<{success: boolean, data?: object, error?: string, status?: number}>}
 */
export async function sendChatMessage(message) {
  try {
    const response = await apiRequest('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });

    if (response.status === 401) {
      return { success: false, error: 'Session expired. Please sign in again.', status: 401 };
    }
    if (response.status === 429) {
      return { success: false, error: 'Rate limit exceeded. Please wait a moment.', status: 429 };
    }
    if (response.status === 503) {
      return { success: false, error: 'Chat service unavailable. Try again later.', status: 503 };
    }
    if (!response.ok) {
      return { success: false, error: 'Failed to send message. Please try again.', status: response.status };
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error('Chat API error:', error);
    return { success: false, error: 'Network error. Please check your connection.' };
  }
}

export default apiRequest;
