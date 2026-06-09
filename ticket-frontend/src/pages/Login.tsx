import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Button from '../components/Button'
import Card from '../components/Card'
import Input from '../components/Input'
import { useAuthContext } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuthContext()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleLogin = async () => {
    setErrorMessage(null)
    setIsSubmitting(true)

    try {
      await login(form.username, form.password)
      navigate('/dashboard')
    } catch (error: any) {
      console.error('Login error:', error)
      setErrorMessage(error?.response?.data?.detail || 'Invalid username or password.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <Card className="w-full max-w-md space-y-4">
        <div>
          <h1 className="text-3xl font-bold">Login</h1>
          <p className="text-gray-500 mt-2">Support ticket management system</p>
        </div>

        {errorMessage && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">
            {errorMessage}
          </div>
        )}

        <Input
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />

        <Input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
        />

        <Button
          className="w-full"
          onClick={handleLogin}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Logging in...' : 'Login'}
        </Button>

        <Link to="/register" className="text-sm text-blue-600 block text-center">
          Create new account
        </Link>
      </Card>
    </div>
  )
}
