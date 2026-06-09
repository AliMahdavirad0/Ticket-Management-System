import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import { AuthProvider, useAuthContext } from './context/AuthContext'
import AdminAgentWorkload from './pages/AdminAgentWorkload'
import AdminUsers from './pages/AdminUsers'
import CreateTicket from './pages/CreateTicket'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import NotFound from './pages/NotFound'
import Profile from './pages/Profile'
import Register from './pages/Register'
import TicketDetails from './pages/TicketDetails'
import Tickets from './pages/Tickets'

function Protected({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthContext()

  // Show a loading spinner while the session is being checked on mount
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto" />
          <p className="mt-4 text-gray-500">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <AppLayout>{children}</AppLayout>
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes with layout */}
        <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
        <Route path="/profile" element={<Protected><Profile /></Protected>} />
        <Route path="/tickets" element={<Protected><Tickets /></Protected>} />
        <Route path="/tickets/create" element={<Protected><CreateTicket /></Protected>} />
        <Route path="/tickets/:id" element={<Protected><TicketDetails /></Protected>} />

        {/* Admin-only routes */}
        <Route path="/admin/users" element={<Protected><AdminUsers /></Protected>} />
        <Route path="/admin/agent-workload" element={<Protected><AdminAgentWorkload /></Protected>} />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  )
}
