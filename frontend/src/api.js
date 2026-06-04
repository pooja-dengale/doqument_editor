/**
 * api.js — Centralised Axios client for the Django REST backend.
 *
 * Authentication strategy (Phase 1 & 2):
 *   We use pre-seeded token auth. Switching "active user" in the UI
 *   simply swaps the Authorization header on this shared instance.
 */
import axios from 'axios';

// Tokens for the three seeded users. In a real app these would come
// from a login flow; here we hard-code them so the mock-auth switcher works.
export const USER_TOKENS = {
  alice:   '646f7dbdfc3cb48a102d334b0e3a2720da1874ae',
  bob:     'd0b33cbb7f67e35610285ccf029b5559d81d9782',
  charlie: 'eac75e2a6ef2a39ad42db994b4958bd430414880',
};

// In development: Vite proxies /api → http://localhost:8000 (no CORS issues).
// In production (Vercel): VITE_API_URL is set to the Render backend URL.
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

/** Swap the active user token on the shared instance. */
export function setActiveUser(username) {
  const token = USER_TOKENS[username];
  if (!token) throw new Error(`No token found for user "${username}"`);
  api.defaults.headers.common['Authorization'] = `Token ${token}`;
}

// --- Documents ---

export const getDocuments = () => api.get('/documents/');

export const getDocument = (id) => api.get(`/documents/${id}/`);

export const createDocument = (data) => api.post('/documents/', data);

export const updateDocument = (id, data) => api.patch(`/documents/${id}/`, data);

export const deleteDocument = (id) => api.delete(`/documents/${id}/`);

// --- Sharing ---

export const shareDocument = (id, username, permission) =>
  api.post(`/documents/${id}/share/`, { username, permission });

export const revokeShare = (id, username) =>
  api.delete(`/documents/${id}/share/${username}/`);

// --- Users ---

export const getUsers = () => api.get('/users/');

export default api;
