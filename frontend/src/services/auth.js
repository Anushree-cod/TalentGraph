const SESSION_KEY = 'talentgraph-session';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

import { roleFromIsRecruiter } from '../utils/roles';

function buildSession({ token, email, isRecruiter }) {
  return {
    token,
    email,
    isRecruiter: Boolean(isRecruiter),
    role: roleFromIsRecruiter(Boolean(isRecruiter)),
  };
}

function parseApiError(errorData, fallback) {
  const detail = errorData?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || String(item)).join(', ');
  }
  if (typeof detail === 'string') {
    return detail;
  }
  return fallback;
}

export async function signUp({ email, password, isRecruiter }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      is_recruiter: Boolean(isRecruiter),
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(parseApiError(errorData, 'Failed to register.'));
  }

  await response.json();
  return signIn({ email, password });
}

export async function signIn({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(parseApiError(errorData, 'Invalid email or password.'));
  }

  const data = await response.json();
  const sessionData = buildSession({
    token: data.access_token,
    email,
    isRecruiter: data.is_recruiter,
  });

  localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
  return sessionData;
}

export function signOut() {
  localStorage.removeItem(SESSION_KEY);
}

export function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
  } catch {
    return null;
  }
}

export function getUserRole() {
  return getSession()?.role ?? null;
}
