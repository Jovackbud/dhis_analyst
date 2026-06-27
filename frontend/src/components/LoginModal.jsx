/**
 * Login modal — standalone JWT authentication flow.
 */
import { useState, useCallback } from 'preact/hooks';
import { login } from '../auth/standaloneAuth.js';

export default function LoginModal({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(username, password);
      onLogin();
    } catch (err) {
      setError(err.message || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  }, [username, password, onLogin]);

  return (
    <div class="login-overlay">
      <form class="login-card" onSubmit={handleSubmit}>
        <h2>DHIS2 AI Analyst</h2>
        <p>Sign in to access the public health intelligence workspace</p>

        <div class="form-group">
          <label for="login-username">Username</label>
          <input
            id="login-username"
            type="text"
            value={username}
            onInput={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            value={password}
            onInput={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            autocomplete="current-password"
          />
        </div>

        {error && <p class="login-error">{error}</p>}

        <button type="submit" class="btn-primary" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}
