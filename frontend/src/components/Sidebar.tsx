import { Link, useLocation } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import { useProfile } from '../hooks/useAuth';
import Badge from './Badge';

const navLinks = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'All Tickets', path: '/tickets' },
  { label: 'Create Ticket', path: '/tickets/create' },
];

const adminLinks = [
  { label: 'User Management', path: '/admin/users' },
  { label: 'Agent Workload', path: '/admin/agent-workload' },
  { label: 'Categories', path: '/admin/categories' },
];

export default function Sidebar() {
  const location = useLocation();
  const { logout } = useAuthContext();
  const { data: profile } = useProfile();

  const isAdmin = profile?.role === 'admin';
  const isAgent = profile?.role === 'agent';

  const roleVariant = profile?.role === 'admin' ? 'danger' : profile?.role === 'agent' ? 'warning' : 'info';

  const linkClass = (path: string) =>
    `block rounded-lg px-4 py-3 mb-1 transition-colors ${
      location.pathname === path
        ? 'bg-white/20 text-white font-medium'
        : 'text-gray-300 hover:bg-white/10 hover:text-white'
    }`;

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen p-4 flex flex-col shrink-0">
      {/* App title */}
      <Link to="/dashboard" className="text-xl font-bold mb-6 block hover:text-gray-200">
        Ticket System
      </Link>

      {/* User info */}
      {profile && (
        <div className="mb-6 pb-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-sm font-bold">
              {profile.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{profile.username}</p>
              <Badge variant={roleVariant}>{profile.role}</Badge>
            </div>
          </div>
        </div>
      )}

      {/* Main navigation */}
      <nav className="flex-1">
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 px-4">Main</p>
        {navLinks.map((link) => (
          <Link key={link.path} to={link.path} className={linkClass(link.path)}>
            {link.label}
          </Link>
        ))}

        {/* Admin section */}
        {isAdmin && (
          <>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 mt-6 px-4">
              Administration
            </p>
            {adminLinks.map((link) => (
              <Link key={link.path} to={link.path} className={linkClass(link.path)}>
                {link.label}
              </Link>
            ))}
          </>
        )}

        {/* Agent quick links */}
        {isAgent && (
          <>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 mt-6 px-4">
              Quick Access
            </p>
            <Link
              to="/tickets?status=OPEN"
              className={linkClass('/tickets?status=OPEN')}
            >
              Open Tickets
            </Link>
          </>
        )}
      </nav>

      {/* Logout */}
      <button
        onClick={logout}
        className="rounded-lg px-4 py-3 text-left text-gray-400 hover:bg-red-600/20 hover:text-red-300 transition-colors text-sm"
      >
        Logout
      </button>
    </aside>
  );
}
