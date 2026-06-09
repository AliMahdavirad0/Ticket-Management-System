/**
 * Axios Client Configuration
 *
 * Session-based auth with CSRF protection.
 * - Cookies are sent automatically via `withCredentials: true`
 *   (sessionid cookie set by Django after login)
 * - CSRF token is read from the csrftoken cookie and sent as
 *   X-CSRFToken header on all state-changing requests (POST/PUT/PATCH/DELETE)
 *
 * The Vite dev server proxies /api/* to Django, so all requests
 * are same-origin (localhost:5173) — no CORS issues with cookies.
 */

import axios from 'axios'

/**
 * Read a cookie value by name.
 * The csrftoken cookie is set by Django (CSRF_COOKIE_HTTPONLY = False).
 */
function getCookie(name: string): string {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || ''
  return ''
}

const axiosClient = axios.create({
  baseURL: '/api', // proxied by Vite → Django
  withCredentials: true, // send sessionid + csrftoken cookies
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request interceptor — attach CSRF token to unsafe methods.
 *
 * Django requires the X-CSRFToken header for POST/PUT/PATCH/DELETE
 * when SessionAuthentication is used. The csrftoken cookie is
 * set by Django on every response and is readable by JavaScript.
 */
axiosClient.interceptors.request.use(
  (config) => {
    const unsafeMethods = ['post', 'put', 'patch', 'delete']
    if (config.method && unsafeMethods.includes(config.method.toLowerCase())) {
      const csrfToken = getCookie('csrftoken')
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }
    return config
  },
  (error) => Promise.reject(error),
)

/**
 * Track which requests have already retried CSRF to avoid infinite loops.
 */
const csrfRetrySet = new Set<string>()

/**
 * Response interceptor — handle 401 (session expired) and 403 (CSRF).
 *
 * - 401: Redirect to login if not already there (session expired).
 * - 403 with CSRF failure: Retry once with a fresh CSRF cookie.
 */
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config

    // ── 403 — Possible CSRF failure. Retry once with fresh token.
    if (
      error.response?.status === 403 &&
      config &&
      !csrfRetrySet.has(config.url + config.method)
    ) {
      csrfRetrySet.add(config.url + config.method)
      try {
        // Fetch a fresh CSRF cookie, then retry the original request
        await axios.get('/api/accounts/csrf/', { withCredentials: true })
        const freshToken = getCookie('csrftoken')
        if (freshToken) {
          config.headers['X-CSRFToken'] = freshToken
          return axiosClient(config)
        }
      } catch {
        // CSRF refresh failed — let the original error through
      }
    }

    // ── 401 — Session expired. Redirect to login.
    if (
      error.response?.status === 401 &&
      !window.location.pathname.startsWith('/login')
    ) {
      window.location.href = '/login'
    }

    return Promise.reject(error)
  },
)

export default axiosClient
