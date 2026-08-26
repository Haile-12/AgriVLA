import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { getMe, login as apiLogin, register as apiRegister, User } from '../lib/api'

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, display_name: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('agrivla_token'))
  const [isLoading, setIsLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    try {
      const res = await getMe()
      setUser(res.data)
    } catch {
      localStorage.removeItem('agrivla_token')
      setToken(null)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (token) fetchUser()
    else setIsLoading(false)
  }, [token, fetchUser])

  const login = async (email: string, password: string) => {
    const res = await apiLogin(email, password)
    const t = res.data.access_token
    localStorage.setItem('agrivla_token', t)
    setToken(t)
    const me = await getMe()
    setUser(me.data)
  }

  const register = async (email: string, password: string, display_name: string) => {
    const res = await apiRegister(email, password, display_name)
    const t = res.data.access_token
    localStorage.setItem('agrivla_token', t)
    setToken(t)
    const me = await getMe()
    setUser(me.data)
  }

  const logout = () => {
    localStorage.removeItem('agrivla_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
