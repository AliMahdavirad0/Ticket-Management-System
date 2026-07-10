/**
 * Dashboard API Service
 * Handles dashboard-related API calls for statistics and metrics
 */

import axiosClient from './axiosClient';

export interface DashboardOverview {
  user: {
    id: number;
    username: string;
    email: string;
    role: 'customer' | 'agent' | 'admin';
  };
  tickets: {
    total: number;
    open: number;
    in_progress: number;
    resolved: number;
    closed: number;
    by_priority: {
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  };
  messages: {
    total: number;
  };
  recent_tickets: Array<{
    id: number;
    title: string;
    status: string;
    priority: string;
    user: {
      id: number;
      username: string;
      email: string;
    };
    assigned_agent: {
      id: number;
      username: string;
      email: string;
    } | null;
    created_at: string;
    updated_at: string;
  }>;
  recent_messages: Array<{
    id: number;
    ticket_id: number;
    ticket_title: string;
    sender: string;
    message: string;
    created_at: string;
  }>;
  customer?: {
    open_tickets: number;
    awaiting_response: number;
    resolved_or_closed: number;
  };
  agent?: {
    assigned_to_me: number;
    unassigned_pool: number;
    needs_attention: number;
    by_status: {
      open: number;
      in_progress: number;
      resolved: number;
      closed: number;
    };
  };
  admin?: {
    users: {
      total: number;
      customers: number;
      agents: number;
      admins: number;
    };
    tickets: {
      total: number;
      unassigned: number;
      created_last_7_days: number;
      by_status: {
        open: number;
        in_progress: number;
        resolved: number;
        closed: number;
      };
      by_priority: {
        low: number;
        medium: number;
        high: number;
        critical: number;
      };
    };
    by_category: Array<{
      id: number;
      name: string;
      ticket_count: number;
    }>;
    messages: {
      total: number;
    };
  };
}

export interface AgentWorkload {
  id: number;
  username: string;
  email: string;
  assigned_total: number;
  open: number;
  in_progress: number;
  resolved: number;
  closed: number;
}

/**
 * Get dashboard overview based on user role
 */
export const getDashboardOverview = async (): Promise<DashboardOverview> => {
  const response = await axiosClient.get<DashboardOverview>('/dashboard/');
  return response.data;
};

/**
 * Get agent workload breakdown (admin only)
 */
export const getAgentWorkload = async (): Promise<AgentWorkload[]> => {
  const response = await axiosClient.get<AgentWorkload[]>('/dashboard/agents/');
  return response.data;
};
