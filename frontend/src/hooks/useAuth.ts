/**
 * Authentication Hooks
 *
 * Session-based auth hooks using React Query.
 * The authentication state is managed by the AuthContext (session check on mount).
 * These hooks handle profile queries, admin user management, and utility accessors.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthContext } from '../context/AuthContext'
import * as authApi from '../api/authApi'

/* ───── Profile ───── */

/**
 * Hook to get current user profile.
 * Enabled only when the user has an active session.
 */
export const useProfile = () => {
  const { isAuthenticated } = useAuthContext()

  return useQuery({
    queryKey: ['profile'],
    queryFn: authApi.getProfile,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  })
}

/**
 * Hook to update user profile.
 */
export const useUpdateProfile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: authApi.updateProfile,
    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data)
    },
  })
}

/**
 * Hook to change password.
 */
export const useChangePassword = () => {
  return useMutation({
    mutationFn: authApi.changePassword,
  })
}

/* ───── Auth State Accessors ───── */

/**
 * Check if the user is authenticated.
 * Uses context state (set during the session check on app mount).
 */
export const useIsAuthenticated = (): boolean => {
  const { isAuthenticated } = useAuthContext()
  return isAuthenticated
}

/**
 * Get the current user object from context.
 */
export const useUser = () => {
  const { user } = useAuthContext()
  return user
}

/**
 * Get the current user role from context.
 */
export const useUserRole = () => {
  const { user } = useAuthContext()
  return user?.role ?? null
}

/**
 * Get user profile data (alias for useProfile, kept for backward compat).
 */
export const useUserProfile = () => {
  return useProfile()
}

/* ───── Admin: User Management ───── */

/**
 * Hook to list all users (admin only) with pagination and filtering.
 */
export const useUsers = (params?: { page?: number; search?: string; role?: string }) => {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => authApi.getUsers(params),
    staleTime: 30 * 1000,
  })
}

/**
 * Hook to update user role (admin only).
 */
export const useUpdateUserRole = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, role }: { id: number; role: string }) =>
      authApi.updateUserRole(id, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

/**
 * Hook to get available agents sorted by workload (admin only).
 */
export const useAvailableAgents = () => {
  return useQuery({
    queryKey: ['availableAgents'],
    queryFn: authApi.getAvailableAgents,
    staleTime: 30 * 1000,
  })
}
