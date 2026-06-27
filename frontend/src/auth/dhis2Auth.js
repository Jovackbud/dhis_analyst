/**
 * DHIS2 embedded auth — detects window.d2 presence and extracts token.
 *
 * When running as a DHIS2 app (embedded in the DHIS2 platform), the d2
 * library is injected globally. This module detects that and extracts
 * the session token for API calls.
 *
 * Falls back to standalone auth when d2 is unavailable.
 */

/**
 * Detect if we're running inside the DHIS2 platform.
 * @returns {boolean}
 */
export function detectDhis2() {
  return !!(
    typeof window !== 'undefined' &&
    (window.d2 || window.dhis2 || window.DHIS_CONFIG)
  );
}

/**
 * Get the DHIS2 session token from the d2 library.
 * @returns {string|null}
 */
export function getDhis2Token() {
  try {
    // d2 library stores the current user context
    if (window.d2?.currentUser) {
      return window.d2.Api?.getApi()?.defaultHeaders?.Authorization?.replace('Bearer ', '') || null;
    }

    // DHIS2 app-platform runtime
    if (window.DHIS_CONFIG?.baseUrl) {
      // In DHIS2 app-platform, cookies handle auth — no explicit token needed
      // Return a marker so the auth layer knows to use cookie-based auth
      return '__dhis2_cookie_auth__';
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * Get the DHIS2 base URL from the environment.
 * @returns {string}
 */
export function getDhis2BaseUrl() {
  if (window.DHIS_CONFIG?.baseUrl) return window.DHIS_CONFIG.baseUrl;
  if (window.d2?.system?.systemInfo?.contextPath) return window.d2.system.systemInfo.contextPath;
  return '';
}
