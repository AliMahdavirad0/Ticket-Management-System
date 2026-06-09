/**
 * Auth Context
 *
 * Manages authentication state using Django session cookies.
 *
 * Flow:
 *   1. On mount: call /api/accounts/csrf/ to get CSRF cookie, then
 *      call /api/accounts/session/ to check if the user has an active session.
 *   2. On login: POST /api/accounts/session/login/ → session cookie set.
 *   3. On logout: POST /api/accounts/session/logout/ → session cookie cleared.
 *   4. isLoading is true while checking the initial session.
 *      Protected routes should show a spinner during this state.
 */

import { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import * as authApi from '../api/authApi'
import type { UserMinimal } from '../api/authApi'

interface AuthState {
  user: UserMinimal | null
  isLoading: boolean
  isAuthenticated: boolean
}

interface AuthContextType extends AuthState {
  /** Log in with username/password. Throws on failure. */
  login: (username: string, password: string) => Promise<void>
  /** Log out — clears the session. */
  logout: () => Promise<void>
  /** Re-check the session (e.g., after registration). */
  refreshSession: () => Promise<void>
}

const initialState: AuthState = {
  user: null,
  isLoading: true,
  isAuthenticated: false,
}

const AuthContext = createContext<AuthContextType>({
  ...initialState,
  login: async () => {},
  logout: async () => {},
  refreshSession: async () => {},
})

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AuthState>(initialState)
  const queryClient = useQueryClient()

  /**
   * Check if the user has an active session by calling the session endpoint.
   * If authenticated, store the user data. If not, set isAuthenticated = false.
   */
  const checkSession = useCallback(async () => {
    try {
      const data = await authApi.checkSession()
      if (data.authenticated && data.user) {
        setState({
          user: data.user,
          isLoading: false,
          isAuthenticated: true,
        })
      } else {
        setState({ user: null, isLoading: false, isAuthenticated: false })
      }
    } catch {
      // 401 or network error — not authenticated
      setState({ user: null, isLoading: false, isAuthenticated: false })
    }
  }, [])

  /**
   * Initialize auth on mount:
   * 1. Fetch CSRF cookie (needed before any POST/PUT/PATCH/DELETE)
   * 2. Check if an existing session cookie is valid
   */
  useEffect(() => {
    const init = async () => {
      try {
        await authApi.fetchCsrfToken()
      } catch {
        // CSRF fetch failed — continue anyway (will retry on next action)
      }
      await checkSession()
    }
    init()
  }, [checkSession])

  /**
   * Log in — authenticate with the backend.
   * On success, the session cookie is set by Django and stored in state.
   */
  const login = useCallback(async (username: string, password: string) => {
    const response = await authApi.sessionLogin(username, password)
    setState({
      user: response.user,
      isLoading: false,
      isAuthenticated: true,
    })
  }, [])

  /**
   * Log out — clear the session on the server and reset state.
   */
  const logout = useCallback(async () => {
    try {
      await authApi.sessionLogout()
    } catch {
      // Even if the request fails, clear local state
    }
    // Clear React Query cache so stale user/ticket data doesn't persist
    queryClient.clear()
    setState({ user: null, isLoading: false, isAuthenticated: false })
  }, [queryClient])

  /**
   * Refresh the session check (e.g., after registration auto-login).
   */
  const refreshSession = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true }))
    await checkSession()
  }, [checkSession])

  const value = useMemo(
    () => ({ ...state, login, logout, refreshSession }),
    [state, login, logout, refreshSession],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuthContext = () => useContext(AuthContext)
