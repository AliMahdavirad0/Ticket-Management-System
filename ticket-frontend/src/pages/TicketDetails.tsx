import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Badge, { getStatusBadgeVariant, getPriorityBadgeVariant } from '../components/Badge';
import Button from '../components/Button';
import Card from '../components/Card';
import Textarea from '../components/Textarea';
import Select from '../components/Select';
import {
  useTicket,
  useTicketMessages,
  useAddTicketMessage,
  useChangeTicketStatus,
  useChangeTicketPriority,
  useAssignTicket,
  useDeleteTicket,
} from '../hooks/useTickets';
import { useUserRole, useUser, useAvailableAgents } from '../hooks/useAuth';

export default function TicketDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const ticketId = Number(id);
  const userRole = useUserRole();

  const [reply, setReply] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<number | ''>('');

  const { data: ticket, isLoading } = useTicket(ticketId);
  const { data: messages } = useTicketMessages(ticketId);
  const addMessage = useAddTicketMessage();
  const changeStatus = useChangeTicketStatus();
  const changePriority = useChangeTicketPriority();
  const assignTicket = useAssignTicket();
  const deleteTicket = useDeleteTicket();
  const { data: availableAgents } = useAvailableAgents();

  const isAgentOrAdmin = userRole === 'agent' || userRole === 'admin';
  const isAdmin = userRole === 'admin';
  const currentUser = useUser();

  if (isLoading) return <div className="p-6">Loading ticket...</div>;
  if (!ticket) return <div className="p-6">Ticket not found.</div>;

  const handleReply = () => {
    if (!reply.trim()) return;
    addMessage.mutate(
      { ticketId, message: reply },
      { onSuccess: () => setReply('') },
    );
  };

  const handleStatusChange = (status: string) => {
    changeStatus.mutate({ id: ticketId, status: status as any });
  };

  const handlePriorityChange = (priority: string) => {
    changePriority.mutate({ id: ticketId, priority: priority as any });
  };

  const handleAssign = () => {
    if (selectedAgent === '') return;
    assignTicket.mutate({ id: ticketId, agentId: Number(selectedAgent) });
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this ticket?')) {
      deleteTicket.mutate(ticketId, {
        onSuccess: () => navigate('/tickets'),
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back link */}
      <button
        onClick={() => navigate('/tickets')}
        className="text-sm text-blue-600 hover:underline"
      >
        ← Back to Tickets
      </button>

      {/* Main ticket card */}
      <Card>
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-3xl font-bold break-words">{ticket.title}</h1>
              <Badge variant={getStatusBadgeVariant(ticket.status)}>{ticket.status}</Badge>
              <Badge variant={getPriorityBadgeVariant(ticket.priority)}>{ticket.priority}</Badge>
            </div>

            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-sm text-gray-500">
              <span>By <strong>{ticket.user.username}</strong></span>
              <span>Created {new Date(ticket.created_at).toLocaleString()}</span>
              <span>Updated {new Date(ticket.updated_at).toLocaleString()}</span>
              {ticket.category && <span>Category: <strong>{ticket.category.name}</strong></span>}
              {ticket.assigned_agent && (
                <span>Assigned to <strong>{ticket.assigned_agent.username}</strong></span>
              )}
              {!ticket.assigned_agent && isAdmin && (
                <span className="text-yellow-600 font-medium">Unassigned</span>
              )}
            </div>
          </div>
        </div>

        <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>

        {/* Action buttons */}
        {(isAgentOrAdmin || isAdmin) && (
          <div className="flex flex-wrap gap-3 mt-6 pt-4 border-t items-end">
            {/* Status change */}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Status</label>
              <select
                value={ticket.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={changeStatus.isPending}
              >
                <option value="OPEN">Open</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </div>

            {/* Priority change */}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Priority</label>
              <select
                value={ticket.priority}
                onChange={(e) => handlePriorityChange(e.target.value)}
                className="border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={changePriority.isPending}
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>

            {/* Agent assignment (admin only) */}
            {isAdmin && (
              <div>
                <label className="block text-xs text-gray-500 mb-1">Assign Agent</label>
                <div className="flex gap-2">
                  <select
                    value={selectedAgent}
                    onChange={(e) => setSelectedAgent(e.target.value ? Number(e.target.value) : '')}
                    className="border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select agent...</option>
                    {(availableAgents || []).map((agent) => (
                      <option key={agent.id} value={agent.id}>
                        {agent.username} ({agent.assigned_count} assigned)
                      </option>
                    ))}
                  </select>
                  <Button
                    size="sm"
                    onClick={handleAssign}
                    disabled={selectedAgent === '' || assignTicket.isPending}
                  >
                    Assign
                  </Button>
                </div>
              </div>
            )}

            {/* Delete (admin or owner) */}
            {(isAdmin || currentUser?.id === ticket.user.id) && (
              <div className="ml-auto">
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleDelete}
                  isLoading={deleteTicket.isPending}
                >
                  Delete Ticket
                </Button>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Messages */}
      <Card title={`Messages (${messages?.length ?? 0})`}>
        {(!messages || messages.length === 0) ? (
          <p className="text-gray-400">No messages yet.</p>
        ) : (
          <div className="space-y-4 max-h-[500px] overflow-y-auto">
            {messages.map((message) => {
              const isOwn = message.sender.role === userRole;
              return (
                <div
                  key={message.id}
                  className={`border rounded-lg p-4 ${isOwn ? 'border-blue-200 bg-blue-50' : ''}`}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-sm">{message.sender.username}</p>
                      <Badge variant={
                        message.sender.role === 'admin' ? 'danger'
                        : message.sender.role === 'agent' ? 'warning'
                        : 'info'
                      }>
                        {message.sender.role}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500">
                      {new Date(message.created_at).toLocaleString()}
                    </p>
                  </div>
                  <p className="mt-2 text-gray-700 whitespace-pre-wrap">{message.message}</p>
                </div>
              );
            })}
          </div>
        )}

        {/* Reply box */}
        <div className="mt-6 border-t pt-4">
          <Textarea
            rows={3}
            placeholder="Type your reply..."
            value={reply}
            onChange={(e) => setReply(e.target.value)}
          />
          <div className="flex justify-between items-center mt-2">
            <p className="text-xs text-gray-400">
              Reply as <strong>{userRole}</strong>
            </p>
            <Button
              onClick={handleReply}
              disabled={addMessage.isPending || !reply.trim()}
            >
              {addMessage.isPending ? 'Sending...' : 'Send Reply'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
