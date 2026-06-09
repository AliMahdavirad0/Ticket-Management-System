import Card from '../components/Card';
import Badge from '../components/Badge';
import { useAgentWorkload } from '../hooks/useDashboard';
import { useUserRole } from '../hooks/useAuth';

export default function AdminAgentWorkload() {
  const currentUserRole = useUserRole();
  const { data: workloads, isLoading } = useAgentWorkload();

  if (currentUserRole !== 'admin') {
    return (
      <div className="p-6 text-center text-gray-500">
        Access denied. Admin only.
      </div>
    );
  }

  if (isLoading) return <div className="p-6">Loading agent workload...</div>;

  const totalAssigned = workloads?.reduce((sum, w) => sum + w.assigned_tickets, 0) ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Agent Workload</h1>
        <div className="text-sm text-gray-500">
          Total assigned tickets: <span className="font-bold text-lg">{totalAssigned}</span>
        </div>
      </div>

      {(!workloads || workloads.length === 0) ? (
        <Card>
          <p className="text-gray-400 text-center py-8">No agents found.</p>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b text-gray-500 text-sm">
                  <th className="pb-3 font-medium">Agent</th>
                  <th className="pb-3 font-medium">Email</th>
                  <th className="pb-3 font-medium text-center">Open</th>
                  <th className="pb-3 font-medium text-center">In Progress</th>
                  <th className="pb-3 font-medium text-center">Resolved</th>
                  <th className="pb-3 font-medium text-center">Closed</th>
                  <th className="pb-3 font-medium text-center">Total Assigned</th>
                </tr>
              </thead>
              <tbody>
                {workloads.map((w) => (
                  <tr key={w.agent.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-3 font-medium">{w.agent.username}</td>
                    <td className="py-3 text-gray-600">{w.agent.email}</td>
                    <td className="py-3 text-center">
                      <Badge variant="info">{w.open_tickets}</Badge>
                    </td>
                    <td className="py-3 text-center">
                      <Badge variant="warning">{w.in_progress_tickets}</Badge>
                    </td>
                    <td className="py-3 text-center text-green-600 font-medium">
                      {w.assigned_tickets - w.open_tickets - w.in_progress_tickets >= 0
                        ? w.assigned_tickets - w.open_tickets - w.in_progress_tickets
                        : '—'}
                    </td>
                    <td className="py-3 text-center text-gray-500">
                      {/* closed count not available from API directly; show dash */}
                      —
                    </td>
                    <td className="py-3 text-center font-bold">{w.assigned_tickets}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <p className="text-gray-500">Total Agents</p>
          <p className="text-3xl font-bold mt-2">{workloads?.length ?? 0}</p>
        </Card>
        <Card>
          <p className="text-gray-500">Total Assigned Tickets</p>
          <p className="text-3xl font-bold mt-2">{totalAssigned}</p>
        </Card>
        <Card>
          <p className="text-gray-500">Avg per Agent</p>
          <p className="text-3xl font-bold mt-2">
            {workloads && workloads.length > 0
              ? Math.round(totalAssigned / workloads.length)
              : 0}
          </p>
        </Card>
      </div>
    </div>
  );
}
