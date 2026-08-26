import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('agrivla_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- Types ---
export interface TokenResponse { access_token: string }
export interface User { id: string; email: string; display_name: string; is_active: boolean }
export interface AgentSession {
  _id: string; user_id: string; title: string; goal: string
  status: string; scenario_id?: string; created_at: string
}
export interface ObservationQuality { quality_score: number; quality_level: string; issues: string[] }
export interface AgentState {
  agent_id: string; goal: string; step_number: number; crop?: string
  condition?: string; severity: number; confidence: number
  observation_quality?: ObservationQuality; action_history: object[]
  feedback_history: object[]; trend: string; status: string
  failure_count: number; termination_reason?: string
}
export interface TrajectoryStep {
  step_number: number; state_before: object; action_proposal?: object
  validation_result?: object; environment_result?: object; feedback?: object
  state_after: object; timing_ms: Record<string, number>; created_at: string
}

// --- Auth ---
export const register = (email: string, password: string, display_name: string) =>
  api.post<TokenResponse>('/auth/register', { email, password, display_name })
export const login = (email: string, password: string) =>
  api.post<TokenResponse>('/auth/login', { email, password })
export const getMe = () => api.get<User>('/auth/me')

// --- Agent Sessions ---
export const createSession = (title: string, goal: string) =>
  api.post<AgentSession>('/agents', { title, goal })
export const listSessions = () => api.get<AgentSession[]>('/agents')
export const getSession = (id: string) => api.get<AgentSession>(`/agents/${id}`)
export const getState = (id: string) => api.get<AgentState>(`/agents/${id}/state`)
export const getTrajectory = (id: string) => api.get<TrajectoryStep[]>(`/agents/${id}/trajectory`)
export const stepAgent = (id: string, image?: File, observationRef?: string) => {
  const form = new FormData()
  if (image) form.append('image', image)
  if (observationRef) form.append('observation_ref', observationRef)
  return api.post<AgentState>(`/agents/${id}/step`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export default api
