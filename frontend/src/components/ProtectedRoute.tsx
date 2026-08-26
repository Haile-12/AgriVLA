import React from 'react'
import { Navigate, Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Sprout, LayoutDashboard, LogOut } from 'lucide-react'

export const ProtectedRoute: React.FC = () => {
  const { user, isLoading, logout } = useAuth()
  const location = useLocation()

  if (isLoading) return (
    <div className="loading-screen">
      <div className="spinner" />
      <span>Authenticating…</span>
    </div>
  )

  if (!user) return <Navigate to="/login" replace />

  const initials = user.display_name
    ? user.display_name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
    : '?'

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="app-sidebar">
        {/* Brand */}
        <div className="sidebar-brand">
          <Sprout size={26} />
          <span>AgriVLA</span>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <Link
            to="/dashboard"
            className={`nav-item ${location.pathname === '/dashboard' ? 'active' : ''}`}
          >
            <LayoutDashboard size={20} />
            Dashboard
          </Link>
        </nav>

        {/* User Profile — anchored to bottom */}
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">{initials}</div>
            <div className="user-info">
              <span className="user-name">{user.display_name}</span>
              <span className="user-role">Agronomist</span>
            </div>
          </div>
          <button id="logout-btn" className="logout-btn" onClick={logout} title="Sign out">
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
