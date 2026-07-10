/**
 * Ticket API Service
 * Handles all ticket-related API calls including CRUD operations, status changes, and messages
 */

import axiosClient from './axiosClient';

export interface TicketUser {
  id: number;
  username: string;
  email: string;
}

export interface TicketCategory {
  id: number;
  name: string;
}

export interface TicketMessage {
  id: number;
  ticket: number;
  sender: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
  message: string;
  created_at: string;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  user: TicketUser;
  assigned_agent: TicketUser | null;
  category: TicketCategory | null;
  message_count?: number;
  messages?: TicketMessage[];
  created_at: string;
  updated_at: string;
}

export interface CreateTicketRequest {
  title: string;
  description: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  category?: number;
}

export interface UpdateTicketRequest {
  title?: string;
  description?: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  category?: number;
}

export interface TicketListParams {
  page?: number;
  status?: string;
  priority?: string;
  search?: string;
  ordering?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface TicketStatistics {
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
}

/**
 * Get paginated list of tickets
 */
export const getTickets = async (params?: TicketListParams): Promise<PaginatedResponse<Ticket>> => {
  const response = await axiosClient.get<PaginatedResponse<Ticket>>('/tickets/', { params });
  return response.data;
};

/**
 * Get single ticket by ID
 */
export const getTicket = async (id: number): Promise<Ticket> => {
  const response = await axiosClient.get<Ticket>(`/tickets/${id}/`);
  return response.data;
};

/**
 * Create a new ticket
 */
export const createTicket = async (data: CreateTicketRequest): Promise<Ticket> => {
  const response = await axiosClient.post<Ticket>('/tickets/', data);
  return response.data;
};

/**
 * Update an existing ticket
 */
export const updateTicket = async (id: number, data: UpdateTicketRequest): Promise<Ticket> => {
  const response = await axiosClient.patch<Ticket>(`/tickets/${id}/`, data);
  return response.data;
};

/**
 * Delete a ticket
 */
export const deleteTicket = async (id: number): Promise<void> => {
  await axiosClient.delete(`/tickets/${id}/`);
};

/**
 * Change ticket status
 */
export const changeTicketStatus = async (
  id: number,
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED'
): Promise<Ticket> => {
  const response = await axiosClient.patch(`/tickets/${id}/change_status/`, { status });
  return response.data;
};

/**
 * Change ticket priority
 */
export const changeTicketPriority = async (
  id: number,
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
): Promise<Ticket> => {
  const response = await axiosClient.patch(`/tickets/${id}/change_priority/`, { priority });
  return response.data;
};

/**
 * Assign ticket to an agent (Admin only)
 */
export const assignTicket = async (id: number, agentId: number): Promise<Ticket> => {
  const response = await axiosClient.patch(`/tickets/${id}/assign/`, {
    agent_id: agentId,
  });
  // Backend returns { message, agent, ticket: TicketDetail }
  return response.data.ticket ?? response.data;
};

/**
 * Get ticket statistics
 */
export const getTicketStatistics = async (): Promise<TicketStatistics> => {
  const response = await axiosClient.get<TicketStatistics>('/tickets/statistics/');
  return response.data;
};

/**
 * Get ticket messages
 */
export const getTicketMessages = async (ticketId: number): Promise<TicketMessage[]> => {
  const response = await axiosClient.get('/messages/', {
    params: { ticket: ticketId }
  });
  return response.data.results ?? response.data;
};

/**
 * Add a message to a ticket
 */
export const addTicketMessage = async (
  ticketId: number,
  message: string
): Promise<TicketMessage> => {
  const response = await axiosClient.post('/messages/', {
    ticket: ticketId,
    message,
  });
  return response.data;
};

/**
 * Get all ticket categories
 */
export const getCategories = async (): Promise<TicketCategory[]> => {
  const response = await axiosClient.get('/categories/');
  return response.data.results ?? response.data;
};

/**
 * Create a new category (admin only)
 */
export const createCategory = async (name: string): Promise<TicketCategory> => {
  const response = await axiosClient.post('/categories/', { name });
  return response.data;
};

/**
 * Delete a category (admin only)
 */
export const deleteCategory = async (id: number): Promise<void> => {
  await axiosClient.delete(`/categories/${id}/`);
};