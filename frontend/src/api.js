/**
 * api.js — Centralised Axios client for the Django REST backend.
 *
 * Authentication strategy (Phase 1 & 2):
 *   We use pre-seeded token auth. Switching "active user" in the UI
 *   simply swaps the Authorization header on this shared instance.
 */
import axios from 'axios';

// Production tokens from https://ajaia-docs-api-dnt2.onrender.com
export const USER_TOKENS = {
  alice:   'e78901db61434dabfd7b4136953200bd12d9a8e8',
  bob:     'da68fa0d2802641917fb7301f9dadd2997042860',
  charlie: '92d163cd5d70b67bbf3fc8ba62c9aba6fbfa571c',
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
