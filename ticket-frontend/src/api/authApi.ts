/**
 * Authentication API Service
 *
 * Session-based auth API calls.
 * All state-changing requests include the X-CSRFToken header
 * automatically via the axiosClient request interceptor.
 */

import axiosClient from './axiosClient'

/* ───── Types ───── */

export interface UserMinimal {
  id: number
  username: string
  email: string
  role: 'customer' | 'agent' | 'admin'
  first_name: string
  last_name: string
}

export interface SessionCheckResponse {
  authenticated: boolean
  user?: UserMinimal
}

export interface LoginResponse {
  detail: string
  user: UserMinimal
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  password2: string
}

export interface RegisterResponse {
  id: number
  username: string
  email: string
  role: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
  role: 'customer' | 'agent' | 'admin'
  first_name: string
  last_name: string
  date_joined: string
  statistics: {
    total_tickets: number
    open_tickets: number
    resolved_tickets: number
    assigned_tickets?: number
  }
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
  new_password2: string
}

/* ───── Session Auth ───── */

/**
 * Initialize CSRF cookie.
 * Must be called once before any state-changing request.
 */
export const fetchCsrfToken = async (): Promise<void> => {
  await axiosClient.get('/accounts/csrf/')
}

/**
 * Check if the user has an active session.
 * Returns user data if authenticated, throws 401 if not.
 */
export const checkSession = async (): Promise<SessionCheckResponse> => {
  const response = await axiosClient.get<SessionCheckResponse>('/accounts/session/')
  return response.data
}

/**
 * Log in with username/password.
 * On success, Django sets the sessionid cookie (HttpOnly).
 */
export const sessionLogin = async (username: string, password: string): Promise<LoginResponse> => {
  const response = await axiosClient.post<LoginResponse>('/accounts/session/login/', {
    username,
    password,
  })
  return response.data
}

/**
 * Log out — clear the session on the server.
 * The sessionid cookie is cleared by Django.
 */
export const sessionLogout = async (): Promise<void> => {
  await axiosClient.post('/accounts/session/logout/')
}

/* ───── Registration ───── */

/**
 * Register a new user account.
 */
export const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await axiosClient.post<RegisterResponse>('/accounts/register/', data)
  return response.data
}

/* ───── Profile ───── */

/**
 * Get current user profile with ticket statistics.
 */
export const getProfile = async (): Promise<UserProfile> => {
  const response = await axiosClient.get<UserProfile>('/accounts/profile/')
  return response.data
}

/**
 * Update user profile (email, first_name, last_name).
 */
export const updateProfile = async (data: Partial<UserProfile>): Promise<UserProfile> => {
  const response = await axiosClient.patch<UserProfile>('/accounts/profile/update/', data)
  return response.data
}

/**
 * Change password.
 */
export const changePassword = async (data: ChangePasswordRequest): Promise<{ message: string }> => {
  const response = await axiosClient.post<{ message: string }>('/accounts/change-password/', data)
  return response.data
}

/* ───── Admin: User Management ───── */

export interface UserAdmin {
  id: number
  username: string
  email: string
  role: 'customer' | 'agent' | 'admin'
  first_name: string
  last_name: string
  date_joined: string
}

export interface AvailableAgent {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  assigned_count: number
}

/**
 * List all users (admin only).
 */
export const getUsers = async (): Promise<UserAdmin[]> => {
  const response = await axiosClient.get<UserAdmin[]>('/accounts/users/')
  return response.data
}

/**
 * Get single user detail (admin only).
 */
export const getUserDetail = async (id: number): Promise<UserAdmin> => {
  const response = await axiosClient.get<UserAdmin>(`/accounts/users/${id}/`)
  return response.data
}

/**
 * Update user role (admin only).
 */
export const updateUserRole = async (id: number, role: string): Promise<UserAdmin> => {
  const response = await axiosClient.patch<UserAdmin>(`/accounts/users/${id}/role/`, { role })
  return response.data
}

/**
 * Get available agents sorted by workload (admin only).
 */
export const getAvailableAgents = async (): Promise<AvailableAgent[]> => {
  const response = await axiosClient.get<AvailableAgent[]>('/accounts/agents/available/')
  return response.data
}
