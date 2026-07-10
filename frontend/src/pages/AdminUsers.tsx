import { useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Input from '../components/Input';
import Select from '../components/Select';
import { useUsers, useUpdateUserRole } from '../hooks/useAuth';
import { useUserRole } from '../hooks/useAuth';

const PAGE_SIZE = 10;

const roleBadgeVariant = (role: string) => {
  switch (role) {
    case 'admin': return 'danger';
    case 'agent': return 'warning';
    default: return 'info';
  }
};

export default function AdminUsers() {
  const currentUserRole = useUserRole();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const { data, isLoading } = useUsers({ page, search: search || undefined, role: roleFilter || undefined });
  const updateRole = useUpdateUserRole();

  if (currentUserRole !== 'admin') {
    return (
      <div className="p-6 text-center text-gray-500">
        Access denied. Admin only.
      </div>
    );
  }

  if (isLoading) return <div className="p-6">Loading users...</div>;

  const users = data?.results ?? [];
  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 0;

  const handleRoleChange = (userId: number, newRole: string) => {
    updateRole.mutate({ id: userId, role: newRole });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">User Management</h1>
        <div className="flex gap-3">
          <Input
            placeholder="Search users..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-60"
          />
          <Select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value);
              setPage(1);
            }}
            options={[
              { value: '', label: 'All Roles' },
              { value: 'customer', label: 'Customer' },
              { value: 'agent', label: 'Agent' },
              { value: 'admin', label: 'Admin' },
            ]}
            className="w-40"
          />
        </div>
      </div>

      <Card>
        {users.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No users found.</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b text-gray-500 text-sm">
                    <th className="pb-3 font-medium">Username</th>
                    <th className="pb-3 font-medium">Email</th>
                    <th className="pb-3 font-medium">Name</th>
                    <th className="pb-3 font-medium">Role</th>
                    <th className="pb-3 font-medium">Joined</th>
                    <th className="pb-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-3 font-medium">{user.username}</td>
                      <td className="py-3 text-gray-600">{user.email}</td>
                      <td className="py-3 text-gray-600">
                        {[user.first_name, user.last_name].filter(Boolean).join(' ') || '—'}
                      </td>
                      <td className="py-3">
                        <Badge variant={roleBadgeVariant(user.role)}>{user.role}</Badge>
                      </td>
                      <td className="py-3 text-sm text-gray-500">
                        {new Date(user.date_joined).toLocaleDateString()}
                      </td>
                      <td className="py-3">
                        <select
                          value={user.role}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          className="border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          disabled={updateRole.isPending}
                        >
                          <option value="customer">Customer</option>
                          <option value="agent">Agent</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-4 pt-4 border-t">
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
          </>
        )}
      </Card>
    </div>
  );
}
