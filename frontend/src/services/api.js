const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

import { getSession } from './auth';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const session = getSession();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (session && session.token) {
    headers['Authorization'] = `Bearer ${session.token}`;
  }

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  health: () => request('/'),

  uploadResume: (formData) => {
    const session = getSession();
    return fetch(`${API_BASE_URL}/candidates/resume`, {
      method: 'POST',
      headers: session?.token ? { Authorization: `Bearer ${session.token}` } : {},
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        const detail = error.detail;
        const message = Array.isArray(detail)
          ? detail.map((item) => item.msg || item).join(', ')
          : detail || error.message || 'Failed to upload resume';
        throw new Error(message);
      }
      return res.json();
    });
  },

  getRecruiterJobs: () => request('/jobs/'),

  getJobs: () => request('/jobs/'),

  getJob: (jobId) => request(`/jobs/${jobId}`),

  createJob: (payload) => request('/jobs/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  submitApplication: (jobId, formData) => {
    const session = getSession();
    return fetch(`${API_BASE_URL}/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: session?.token ? { Authorization: `Bearer ${session.token}` } : {},
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        const detail = error.detail;
        const message = Array.isArray(detail)
          ? detail.map((item) => item.msg || item).join(', ')
          : detail || error.message || 'Failed to submit application';
        throw new Error(message);
      }
      return res.json();
    });
  },
  
  getRecruiterDashboard: (jobId) => request(`/dashboards/recruiter/jobs/${jobId}/candidates`),

  getRecruiterMetrics: () => request('/dashboards/recruiter/metrics'),

  getApplicationDetail: (applicationId) =>
    request(`/dashboards/recruiter/applications/${applicationId}`),

  updateApplicationStatus: (applicationId, status) =>
    request(`/dashboards/recruiter/applications/${applicationId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  
  getApplicantDashboard: () => request('/dashboards/applicant/status'),
  
  analyzeGithub: (githubUrl) => request('/candidates/github', {
    method: 'POST',
    body: JSON.stringify({ github_url: githubUrl })
  }),
};

export default api;
