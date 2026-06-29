const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  health: () => request('/health'),

  uploadResume: (formData) =>
    fetch(`${API_BASE_URL}/resumes/upload`, {
      method: 'POST',
      body: formData,
    }).then((res) => {
      if (!res.ok) throw new Error('Failed to upload resume');
      return res.json();
    }),

  getAnalysisStatus: (jobId) => request(`/resumes/${jobId}/status`),

  getAnalysisResults: (jobId) => request(`/resumes/${jobId}/results`),

  getRecruiterDashboard: () => request('/recruiter/dashboard'),
};

export default api;
