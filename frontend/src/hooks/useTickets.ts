/**
 * Ticket Hooks
 * Custom React hooks for ticket operations using React Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as ticketApi from '../api/ticketApi';

/**
 * Hook to get paginated tickets list
 */
export const useTickets = (params?: ticketApi.TicketListParams) => {
  return useQuery({
    queryKey: ['tickets', params],
    queryFn: () => ticketApi.getTickets(params),
    staleTime: 30 * 1000, // 30 seconds
  });
};

/**
 * Hook to get single ticket by ID
 */
export const useTicket = (id: number) => {
  return useQuery({
    queryKey: ['ticket', id],
    queryFn: () => ticketApi.getTicket(id),
    enabled: !!id,
  });
};

/**
 * Hook to create a new ticket
 */
export const useCreateTicket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ticketApi.createTicket,
    onSuccess: () => {
      // Invalidate tickets list to refetch
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['ticketStatistics'] });
    },
  });
};

/**
 * Hook to update a ticket
 */
export const useUpdateTicket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ticketApi.UpdateTicketRequest }) =>
      ticketApi.updateTicket(id, data),
    onSuccess: (_, variables) => {
      // Invalidate specific ticket and list
      queryClient.invalidateQueries({ queryKey: ['ticket', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

/**
 * Hook to delete a ticket
 */
export const useDeleteTicket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ticketApi.deleteTicket,
    onSuccess: () => {
      // Invalidate tickets list
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['ticketStatistics'] });
    },
  });
};

/**
 * Hook to change ticket status
 */
export const useChangeTicketStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: ticketApi.Ticket['status'] }) =>
      ticketApi.changeTicketStatus(id, status),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ticket', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['ticketStatistics'] });
    },
  });
};

/**
 * Hook to change ticket priority
 */
export const useChangeTicketPriority = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, priority }: { id: number; priority: ticketApi.Ticket['priority'] }) =>
      ticketApi.changeTicketPriority(id, priority),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ticket', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

/**
 * Hook to assign ticket to agent
 */
export const useAssignTicket = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, agentId }: { id: number; agentId: number }) =>
      ticketApi.assignTicket(id, agentId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ticket', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });
};

/**
 * Hook to get ticket statistics
 */
export const useTicketStatistics = () => {
  return useQuery({
    queryKey: ['ticketStatistics'],
    queryFn: ticketApi.getTicketStatistics,
    staleTime: 60 * 1000, // 1 minute
  });
};

/**
 * Hook to get ticket messages
 */
export const useTicketMessages = (ticketId: number) => {
  return useQuery({
    queryKey: ['ticketMessages', ticketId],
    queryFn: () => ticketApi.getTicketMessages(ticketId),
    enabled: !!ticketId,
  });
};

/**
 * Hook to add a message to a ticket
 */
export const useAddTicketMessage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ticketId, message }: { ticketId: number; message: string }) =>
      ticketApi.addTicketMessage(ticketId, message),
    onSuccess: (_, variables) => {
      // Invalidate messages for this ticket
      queryClient.invalidateQueries({ queryKey: ['ticketMessages', variables.ticketId] });
    },
  });
};

/**
 * Hook to get all categories
 */
export const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: ticketApi.getCategories,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to create a category
 */
export const useCreateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ticketApi.createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    },
  });
};

/**
 * Hook to delete a category
 */
export const useDeleteCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ticketApi.deleteCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    },
  });
};
