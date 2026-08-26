import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'
import { Leaf, Mail, Lock, User, ArrowLeft, Eye, EyeOff } from 'lucide-react'

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch {
      toast.error('Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-back-btn">
          <ArrowLeft size={16} /> Home
        </Link>
        <div className="auth-brand">
          <div className="brand-icon"><Leaf size={28} /></div>
          <h1>AgriVLA</h1>
          <p>Vision-Language Agricultural Agent</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Sign In</h2>
          <div className="field">
            <label htmlFor="login-email"><Mail size={14} /> Email</label>
            <input id="login-email" type="email" value={email}
              onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>
          <div className="field">
            <label htmlFor="login-password"><Lock size={14} /> Password</label>
            <input id="login-password" type={showPassword ? 'text' : 'password'} value={password}
              onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
            <button 
              type="button" 
              className="password-toggle" 
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          <button id="login-submit" type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <span className="btn-spinner" /> : 'Sign In'}
          </button>
        </form>
        <p className="auth-switch">Don't have an account? <Link to="/register">Register</Link></p>
      </div>
    </div>
  )
}

export const RegisterPage: React.FC = () => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register(email, password, name)
      toast.success('Account created! Welcome.')
      navigate('/dashboard')
    } catch {
      toast.error('Registration failed. Email may already be in use.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-back-btn">
          <ArrowLeft size={16} /> Home
        </Link>
        <div className="auth-brand">
          <div className="brand-icon"><Leaf size={28} /></div>
          <h1>AgriVLA</h1>
          <p>Vision-Language Agricultural Agent</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Create Account</h2>
          <div className="field">
            <label htmlFor="reg-name"><User size={14} /> Display Name</label>
            <input id="reg-name" type="text" value={name}
              onChange={e => setName(e.target.value)} placeholder="Dr. Jane Smith" required />
          </div>
          <div className="field">
            <label htmlFor="reg-email"><Mail size={14} /> Email</label>
            <input id="reg-email" type="email" value={email}
              onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>
          <div className="field">
            <label htmlFor="reg-password"><Lock size={14} /> Password</label>
            <input id="reg-password" type={showPassword ? 'text' : 'password'} value={password}
              onChange={e => setPassword(e.target.value)} placeholder="••••••••" minLength={8} required />
            <button 
              type="button" 
              className="password-toggle" 
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          <button id="reg-submit" type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <span className="btn-spinner" /> : 'Create Account'}
          </button>
        </form>
        <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  )
}
