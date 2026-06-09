import { Link } from 'react-router-dom';
import Card from '../components/Card';
import Badge from '../components/Badge';
import { getStatusBadgeVariant, getPriorityBadgeVariant } from '../components/Badge';
import { useDashboardOverview } from '../hooks/useDashboard';
import { useUserRole } from '../hooks/useAuth';

export default function Dashboard() {
  const { data, isLoading } = useDashboardOverview();
  const userRole = useUserRole();

  if (isLoading) return <div className="p-6">Loading dashboard...</div>;
  if (!data) return <div className="p-6">No data available.</div>;

  const { tickets, customer, agent: agentMetrics, admin: adminMetrics, user } = data;

  const roleVariant = user.role === 'admin' ? 'danger' : user.role === 'agent' ? 'warning' : 'info';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-500 mt-1">
            Welcome back, <span className="font-semibold">{user.username}</span>
          </p>
        </div>
        <Badge variant={roleVariant} className="text-sm px-3 py-1">
          {user.role}
        </Badge>
      </div>

      {/* Ticket stats — every role */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Ticket Overview</h2>
          <Link to="/tickets" className="text-sm text-blue-600 hover:underline">
            View All Tickets →
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <p className="text-gray-500 text-sm">Total</p>
            <p className="text-3xl font-bold mt-1">{tickets.total}</p>
          </Card>
          <Card>
            <p className="text-gray-500 text-sm">Open</p>
            <p className="text-3xl font-bold mt-1 text-blue-600">{tickets.open}</p>
          </Card>
          <Card>
            <p className="text-gray-500 text-sm">In Progress</p>
            <p className="text-3xl font-bold mt-1 text-yellow-600">{tickets.in_progress}</p>
          </Card>
          <Card>
            <p className="text-gray-500 text-sm">Resolved</p>
            <p className="text-3xl font-bold mt-1 text-green-600">{tickets.resolved}</p>
          </Card>
        </div>
      </div>

      {/* Priority breakdown */}
      <Card title="By Priority">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-gray-500 text-sm">Low</p>
            <p className="text-xl font-bold text-gray-600">{tickets.by_priority.low}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Medium</p>
            <p className="text-xl font-bold text-blue-600">{tickets.by_priority.medium}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">High</p>
            <p className="text-xl font-bold text-yellow-600">{tickets.by_priority.high}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Critical</p>
            <p className="text-xl font-bold text-red-600">{tickets.by_priority.critical}</p>
          </div>
        </div>
      </Card>

      {/* Customer-specific metrics */}
      {customer && (
        <div>
          <h2 className="text-lg font-semibold mb-3">My Tickets</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-l-4 border-blue-500">
              <p className="text-gray-500 text-sm">Open Tickets</p>
              <p className="text-3xl font-bold mt-1">{customer.open_tickets}</p>
            </Card>
            <Card className="border-l-4 border-yellow-500">
              <p className="text-gray-500 text-sm">Awaiting Response</p>
              <p className="text-3xl font-bold mt-1">{customer.awaiting_response}</p>
            </Card>
            <Card className="border-l-4 border-green-500">
              <p className="text-gray-500 text-sm">Resolved / Closed</p>
              <p className="text-3xl font-bold mt-1">{customer.resolved_or_closed}</p>
            </Card>
          </div>
        </div>
      )}

      {/* Agent-specific metrics */}
      {agentMetrics && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Agent Overview</h2>
            <Link to="/tickets" className="text-sm text-blue-600 hover:underline">
              View My Tickets →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-l-4 border-blue-500">
              <p className="text-gray-500 text-sm">Assigned to Me</p>
              <p className="text-3xl font-bold mt-1">{agentMetrics.assigned_to_me}</p>
            </Card>
            <Card className="border-l-4 border-purple-500">
              <p className="text-gray-500 text-sm">Unassigned Pool</p>
              <p className="text-3xl font-bold mt-1">{agentMetrics.unassigned_pool}</p>
            </Card>
            <Card className="border-l-4 border-red-500">
              <p className="text-gray-500 text-sm">Needs Attention</p>
              <p className="text-3xl font-bold mt-1">{agentMetrics.needs_attention}</p>
            </Card>
          </div>

          {/* Agent status breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <Card>
              <p className="text-gray-500 text-sm">Open</p>
              <p className="text-2xl font-bold text-blue-600">{agentMetrics.by_status.open}</p>
            </Card>
            <Card>
              <p className="text-gray-500 text-sm">In Progress</p>
              <p className="text-2xl font-bold text-yellow-600">{agentMetrics.by_status.in_progress}</p>
            </Card>
            <Card>
              <p className="text-gray-500 text-sm">Resolved</p>
              <p className="text-2xl font-bold text-green-600">{agentMetrics.by_status.resolved}</p>
            </Card>
            <Card>
              <p className="text-gray-500 text-sm">Closed</p>
              <p className="text-2xl font-bold text-gray-600">{agentMetrics.by_status.closed}</p>
            </Card>
          </div>
        </div>
      )}

      {/* Admin-specific metrics */}
      {adminMetrics && (
        <>
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">System Overview</h2>
              <div className="flex gap-3">
                <Link to="/admin/users" className="text-sm text-blue-600 hover:underline">
                  Manage Users →
                </Link>
                <Link to="/admin/agent-workload" className="text-sm text-blue-600 hover:underline">
                  Agent Workload →
                </Link>
              </div>
            </div>

            {/* Users summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <Card className="border-l-4 border-gray-500">
                <p className="text-gray-500 text-sm">Total Users</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.users.total}</p>
              </Card>
              <Card className="border-l-4 border-blue-500">
                <p className="text-gray-500 text-sm">Customers</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.users.customers}</p>
              </Card>
              <Card className="border-l-4 border-yellow-500">
                <p className="text-gray-500 text-sm">Agents</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.users.agents}</p>
              </Card>
              <Card className="border-l-4 border-red-500">
                <p className="text-gray-500 text-sm">Admins</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.users.admins}</p>
              </Card>
            </div>

            {/* Ticket status breakdown */}
            <Card title="Ticket Status Breakdown" className="mb-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-gray-500 text-sm">Open</p>
                  <p className="text-2xl font-bold text-blue-600">{adminMetrics.tickets.by_status.open}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">In Progress</p>
                  <p className="text-2xl font-bold text-yellow-600">{adminMetrics.tickets.by_status.in_progress}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Resolved</p>
                  <p className="text-2xl font-bold text-green-600">{adminMetrics.tickets.by_status.resolved}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Closed</p>
                  <p className="text-2xl font-bold text-gray-600">{adminMetrics.tickets.by_status.closed}</p>
                </div>
              </div>
            </Card>

            {/* Quick numbers */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <p className="text-gray-500 text-sm">Unassigned Tickets</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.tickets.unassigned}</p>
              </Card>
              <Card>
                <p className="text-gray-500 text-sm">Created (Last 7 Days)</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.tickets.created_last_7_days}</p>
              </Card>
              <Card>
                <p className="text-gray-500 text-sm">Total Messages</p>
                <p className="text-3xl font-bold mt-1">{adminMetrics.messages.total}</p>
              </Card>
            </div>
          </div>

          {/* Categories breakdown */}
          {adminMetrics.by_category.length > 0 && (
            <Card title="Tickets by Category">
              <div className="space-y-3">
                {adminMetrics.by_category.map((cat) => (
                  <div key={cat.id} className="flex items-center justify-between">
                    <span className="text-gray-700">{cat.name}</span>
                    <Badge>{cat.ticket_count} tickets</Badge>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}

      {/* Recent tickets — every role */}
      <Card title="Recent Tickets">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-500">Latest 5 tickets</p>
          <Link to="/tickets" className="text-sm text-blue-600 hover:underline">
            View all →
          </Link>
        </div>
        {data.recent_tickets.length === 0 ? (
          <p className="text-gray-400">No tickets yet.</p>
        ) : (
          <div className="space-y-2">
            {data.recent_tickets.map((ticket) => (
              <Link
                key={ticket.id}
                to={`/tickets/${ticket.id}`}
                className="block border rounded-lg p-3 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold truncate">{ticket.title}</p>
                    <div className="flex gap-2 mt-1 text-sm text-gray-500">
                      <span>{ticket.user?.username}</span>
                      {ticket.assigned_agent && (
                        <span>→ {ticket.assigned_agent.username}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4 shrink-0">
                    <Badge variant={getPriorityBadgeVariant(ticket.priority)}>
                      {ticket.priority}
                    </Badge>
                    <Badge variant={getStatusBadgeVariant(ticket.status)}>
                      {ticket.status}
                    </Badge>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </Card>

      {/* Recent messages — every role */}
      {data.recent_messages.length > 0 && (
        <Card title="Recent Messages">
          <div className="space-y-3">
            {data.recent_messages.slice(0, 5).map((msg) => (
              <Link
                key={`msg-${msg.ticket_id}-${msg.id}`}
                to={`/tickets/${msg.ticket_id}`}
                className="block border rounded-lg p-3 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between text-sm">
                  <p className="font-semibold">{msg.sender}</p>
                  <p className="text-gray-500">{new Date(msg.created_at).toLocaleString()}</p>
                </div>
                <p className="text-sm text-gray-600 mt-1 truncate">{msg.message}</p>
                <p className="text-xs text-blue-500 mt-1">Ticket: {msg.ticket_title}</p>
              </Link>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
