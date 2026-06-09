import { useState } from 'react';
import { Link } from 'react-router-dom';
import Badge, { getStatusBadgeVariant, getPriorityBadgeVariant } from '../components/Badge';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Select from '../components/Select';
import { useTickets } from '../hooks/useTickets';
import { useUserRole } from '../hooks/useAuth';

const PAGE_SIZE = 10;

export default function Tickets() {
  const userRole = useUserRole();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [search, setSearch] = useState('');

  const { data, isLoading } = useTickets({
    page,
    status: statusFilter || undefined,
    priority: priorityFilter || undefined,
    search: search || undefined,
  });

  if (isLoading) return <div className="p-6">Loading tickets...</div>;

  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tickets</h1>
          <p className="text-gray-500 text-sm mt-1">
            {data?.count ?? 0} ticket{data?.count !== 1 ? 's' : ''} total
          </p>
        </div>
        <Link to="/tickets/create">
          <Button>+ Create Ticket</Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Search tickets..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </div>
          <div className="w-40">
            <Select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              options={[
                { value: '', label: 'All Statuses' },
                { value: 'OPEN', label: 'Open' },
                { value: 'IN_PROGRESS', label: 'In Progress' },
                { value: 'RESOLVED', label: 'Resolved' },
                { value: 'CLOSED', label: 'Closed' },
              ]}
            />
          </div>
          <div className="w-40">
            <Select
              value={priorityFilter}
              onChange={(e) => {
                setPriorityFilter(e.target.value);
                setPage(1);
              }}
              options={[
                { value: '', label: 'All Priorities' },
                { value: 'LOW', label: 'Low' },
                { value: 'MEDIUM', label: 'Medium' },
                { value: 'HIGH', label: 'High' },
                { value: 'CRITICAL', label: 'Critical' },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Ticket list */}
      {!data || data.results.length === 0 ? (
        <Card>
          <div className="text-center py-12 text-gray-400">
            <p className="text-lg">No tickets found</p>
            <p className="text-sm mt-1">
              {search || statusFilter || priorityFilter
                ? 'Try adjusting your filters.'
                : 'Create your first ticket to get started.'}
            </p>
            {!search && !statusFilter && !priorityFilter && (
              <Link to="/tickets/create">
                <Button className="mt-4">+ Create Ticket</Button>
              </Link>
            )}
          </div>
        </Card>
      ) : (
        <div className="space-y-3">
          {data.results.map((ticket) => (
            <Link
              key={ticket.id}
              to={`/tickets/${ticket.id}`}
              className="block"
            >
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg truncate">{ticket.title}</h3>
                      {ticket.assigned_agent && (
                        <Badge variant="info" className="shrink-0">
                          {ticket.assigned_agent.username}
                        </Badge>
                      )}
                    </div>
                    <p className="text-gray-500 text-sm mt-1 line-clamp-2">
                      {ticket.description}
                    </p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                      <span>{ticket.user.username}</span>
                      {ticket.category && <span>• {ticket.category.name}</span>}
                      <span>• {new Date(ticket.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex gap-2 shrink-0">
                    <Badge variant={getPriorityBadgeVariant(ticket.priority)}>
                      {ticket.priority}
                    </Badge>
                    <Badge variant={getStatusBadgeVariant(ticket.status)}>
                      {ticket.status}
                    </Badge>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ← Previous
          </Button>
          <span className="text-sm text-gray-500 px-4">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="secondary"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </Button>
        </div>
      )}
    </div>
  );
}
