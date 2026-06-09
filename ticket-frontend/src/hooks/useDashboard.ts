/**
 * Dashboard Hooks
 * Custom React hooks for dashboard operations using React Query
 */

import { useQuery } from '@tanstack/react-query';
import * as dashboardApi from '../api/dashboardApi';

/**
 * Hook to get dashboard overview
 */
export const useDashboardOverview = () => {
  return useQuery({
    queryKey: ['dashboardOverview'],
    queryFn: dashboardApi.getDashboardOverview,
    staleTime: 60 * 1000, // 1 minute
  });
};

/**
 * Hook to get agent workload (admin only)
 */
export const useAgentWorkload = () => {
  return useQuery({
    queryKey: ['agentWorkload'],
    queryFn: dashboardApi.getAgentWorkload,
    staleTime: 60 * 1000, // 1 minute
  });
};
