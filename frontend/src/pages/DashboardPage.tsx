import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listSessions, createSession, AgentSession } from '../lib/api'
import toast from 'react-hot-toast'
import { Plus, ChevronRight, Activity, Clock, CheckCircle, AlertTriangle, Leaf, X } from 'lucide-react'

const statusClasses: Record<string, string> = {
  COMPLETED: 'completed',
  ESCALATED: 'escalated',
  FAILED: 'failed',
}

const statusIcon = (s: string) => {
  switch (s) {
    case 'COMPLETED': return <CheckCircle size={12} />
    case 'ESCALATED': return <AlertTriangle size={12} />
    case 'FAILED': return <AlertTriangle size={12} />
    default: return <Activity size={12} />
  }
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [sessions, setSessions] = useState<AgentSession[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [goal, setGoal] = useState('')

  const fetchSessions = async () => {
    try {
      const res = await listSessions()
      setSessions(res.data)
    } catch { /* ignore */ }
    setLoading(false)
  }

  useEffect(() => { fetchSessions() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title || !goal) return
    setCreating(true)
    try {
      const res = await createSession(title, goal)
      toast.success('Agent session created!')
      navigate(`/agents/${res.data._id}`)
    } catch {
      toast.error('Failed to create session.')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="dash-content">
      {/* Page header */}
      <div className="dash-top">
        <div>
          <h1>Agent Sessions</h1>
          <p>Manage your closed-loop agricultural agents</p>
        </div>
        <button
          id="new-session-btn"
          className="btn-primary"
          onClick={() => setShowForm(v => !v)}
        >
          <Plus size={16} />
          New Session
        </button>
      </div>

      {/* Inline create form */}
      {showForm && (
        <form id="new-session-form" className="session-form" onSubmit={handleCreate}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
            <h3 style={{ margin: 0 }}>New Agent Session</h3>
            <button type="button" className="logout-btn" onClick={() => setShowForm(false)}>
              <X size={18} />
            </button>
          </div>
          <div className="form-row">
            <div className="field">
              <label>Session Title</label>
              <input
                id="session-title"
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g. Tomato disease inspection"
                required
              />
            </div>
            <div className="field">
              <label>Agent Goal</label>
              <input
                id="session-goal"
                type="text"
                value={goal}
                onChange={e => setGoal(e.target.value)}
                placeholder="e.g. Diagnose and treat blight"
                required
              />
            </div>
          </div>
          <div className="form-actions">
            <button
              id="cancel-session-btn"
              type="button"
              className="btn-ghost"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
            <button
              id="create-session-btn"
              type="submit"
              className="btn-primary"
              disabled={creating}
            >
              {creating ? <span className="btn-spinner" /> : 'Create Session'}
            </button>
          </div>
        </form>
      )}

      {/* Content */}
      {loading ? (
        <div className="empty-state" style={{ border: 'none', background: 'transparent' }}>
          <div className="spinner" />
        </div>
      ) : sessions.length === 0 ? (
        <div className="empty-state">
          <Leaf size={48} className="empty-icon" />
          <h3>No sessions yet</h3>
          <p>Click "New Session" above to start your first agricultural agent run.</p>
        </div>
      ) : (
        <div className="session-grid">
          {sessions.map(s => (
            <Link
              key={s._id}
              to={`/agents/${s._id}`}
              className="session-card"
              id={`session-${s._id}`}
            >
              <div className="session-card-top">
                <span className={`session-status ${statusClasses[s.status] ?? 'active'}`}>
                  {statusIcon(s.status)} {s.status}
                </span>
                <ChevronRight size={16} />
              </div>
              <h4>{s.title}</h4>
              <p>{s.goal}</p>
              <div className="session-meta">
                <Clock size={12} />
                <span>{new Date(s.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
