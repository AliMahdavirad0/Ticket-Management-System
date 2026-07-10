import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Input from '../components/Input'
import Button from '../components/Button'
import Card from '../components/Card'
import { useAuthContext } from '../context/AuthContext'
import * as authApi from '../api/authApi'

export default function Register() {
  const { login } = useAuthContext()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleRegister = async () => {
    setError(null)
    setIsSubmitting(true)

    try {
      // Step 1: Register the user
      await authApi.register(form)

      // Step 2: Auto-login with session auth
      await login(form.username, form.password)

      // Step 3: Navigate to dashboard
      navigate('/dashboard')
    } catch (err: any) {
      const data = err?.response?.data
      if (data) {
        const messages = Object.entries(data)
          .map(([, msgs]) => (Array.isArray(msgs) ? msgs.join(', ') : String(msgs)))
          .join('; ')
        setError(messages || 'Registration failed. Please try again.')
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <Card className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">Create account</h1>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        <Input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <Input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <Input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <Input type="password" placeholder="Confirm Password" value={form.password2} onChange={(e) => setForm({ ...form, password2: e.target.value })} />

        <Button
          className="w-full"
          onClick={handleRegister}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating account...' : 'Register'}
        </Button>

        <Link to="/login" className="text-sm text-blue-600 block text-center">
          Already have an account?
        </Link>
      </Card>
    </div>
  )
}
