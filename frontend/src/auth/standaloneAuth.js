/**
 * Standalone JWT auth — login, token storage, identity access.
 * Tokens are stored in sessionStorage (cleared on tab close).
 */

const TOKEN_KEY = 'dhis2_analyst_token';
const IDENTITY_KEY = 'dhis2_analyst_identity';

/**
 * Login with username + password. Stores JWT in sessionStorage.
 * @param {string} username
 * @param {string} password
 * @returns {Promise<{token: string, identity: object}>}
 */
export async function login(username, password) {
  const res = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Login failed (${res.status})`);
  }

  const data = await res.json();
  sessionStorage.setItem(TOKEN_KEY, data.access_token);
  sessionStorage.setItem(IDENTITY_KEY, JSON.stringify(data.identity || {}));

  return { token: data.access_token, identity: data.identity };
}

/**
 * Get the stored auth state.
 * @returns {{ token: string, identity: object } | null}
 */
export function getAuth() {
  const token = sessionStorage.getItem(TOKEN_KEY);
  if (!token) return null;

  let identity = {};
  try {
    identity = JSON.parse(sessionStorage.getItem(IDENTITY_KEY) || '{}');
  } catch { /* ignore */ }

  return { token, identity };
}

/**
 * Check if the user is currently authenticated.
 * @returns {boolean}
 */
export function isAuthenticated() {
  return !!sessionStorage.getItem(TOKEN_KEY);
}

/**
 * Clear stored auth state (logout).
 */
export function clearAuth() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(IDENTITY_KEY);
}
