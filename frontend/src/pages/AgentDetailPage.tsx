import React, { useEffect, useState, useRef } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  getSession, getState, getTrajectory, stepAgent,
  AgentSession, AgentState, TrajectoryStep
} from '../lib/api'
import toast from 'react-hot-toast'
import {
  ArrowLeft, Upload, Play, AlertTriangle,
  CheckCircle, Activity, ChevronDown, ChevronUp, Download
} from 'lucide-react'
import jsPDF from 'jspdf'

const SeverityBar: React.FC<{ value: number }> = ({ value }) => {
  const color = value > 0.7 ? '#ef4444' : value > 0.4 ? '#f59e0b' : '#16a34a'
  return (
    <div className="severity-bar-track">
      <div className="severity-bar-fill" style={{ width: `${value * 100}%`, background: color }} />
    </div>
  )
}

const ConfidencePill: React.FC<{ value: number }> = ({ value }) => {
  const label = value >= 0.75 ? 'HIGH' : value >= 0.5 ? 'MED' : 'LOW'
  return (
    <span className={`confidence-pill ${label.toLowerCase()}`}>
      {label} {(value * 100).toFixed(0)}%
    </span>
  )
}

const StepCard: React.FC<{ step: TrajectoryStep; index: number }> = ({ step, index }) => {
  const [open, setOpen] = useState(false)
  const action = (step.action_proposal as Record<string, unknown>)?.action_type as string
  const result = (step.feedback as Record<string, unknown> | undefined)?.result as string
  return (
    <div className="step-card">
      <button className="step-header" onClick={() => setOpen(v => !v)}>
        <span className="step-num">Step {index + 1}</span>
        <span className="step-action">{action ?? '—'}</span>
        {result && <span className={`step-result ${result.toLowerCase()}`}>{result}</span>}
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      {open && (
        <pre className="step-detail">
          {JSON.stringify({
            action: step.action_proposal,
            validation: step.validation_result,
            feedback: step.feedback,
            timing_ms: step.timing_ms
          }, null, 2)}
        </pre>
      )}
    </div>
  )
}

export const AgentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [session, setSession] = useState<AgentSession | null>(null)
  const [state, setState] = useState<AgentState | null>(null)
  const [trajectory, setTrajectory] = useState<TrajectoryStep[]>([])
  const [image, setImage] = useState<File | null>(null)
  const [stepping, setStepping] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const isTerminal = state?.status === 'COMPLETED' || state?.status === 'FAILED' || state?.status === 'ESCALATED'

  const refresh = async () => {
    if (!id) return
    try {
      const [s, st, tr] = await Promise.all([getSession(id), getState(id), getTrajectory(id)])
      setSession(s.data)
      setState(st.data)
      setTrajectory(tr.data)
    } catch { /* ignore */ }
  }

  useEffect(() => { refresh() }, [id])

  const handleStep = async () => {
    if (!id) return
    setStepping(true)
    try {
      const res = await stepAgent(id, image ?? undefined)
      setState(res.data)
      toast.success(`Step ${res.data.step_number} complete — ${res.data.status}`)
      await refresh()
      setImage(null)
      if (fileRef.current) fileRef.current.value = ''
    } catch {
      toast.error('Agent step failed.')
    } finally {
      setStepping(false)
    }
  }

  const exportToPDF = () => {
    try {
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pw = pdf.internal.pageSize.getWidth()
      const now = new Date().toLocaleString()

      // ── Header banner ──────────────────────────────────────────
      pdf.setFillColor(22, 101, 52)
      pdf.rect(0, 0, pw, 28, 'F')
      pdf.setTextColor(255, 255, 255)
      pdf.setFontSize(20)
      pdf.setFont('helvetica', 'bold')
      pdf.text('AgriVLA Diagnostic Report', 14, 12)
      pdf.setFontSize(9)
      pdf.setFont('helvetica', 'normal')
      pdf.text(`Generated: ${now}`, 14, 20)

      // ── Session info ────────────────────────────────────────────
      pdf.setTextColor(30, 30, 30)
      pdf.setFontSize(13)
      pdf.setFont('helvetica', 'bold')
      pdf.text('Session Overview', 14, 38)
      pdf.setDrawColor(22, 101, 52)
      pdf.line(14, 40, pw - 14, 40)

      const rows = [
        ['Session Title', session?.title ?? '—'],
        ['Goal', session?.goal ?? '—'],
        ['Status', state?.status ?? '—'],
        ['Steps Completed', String(state?.step_number ?? 0)],
        ['Trend', state?.trend ?? '—'],
        ['Consecutive Failures', String(state?.failure_count ?? 0)],
      ]
      pdf.setFontSize(10)
      let y = 48
      rows.forEach(([label, value]) => {
        pdf.setFont('helvetica', 'bold')
        pdf.setTextColor(80, 80, 80)
        pdf.text(label + ':', 14, y)
        pdf.setFont('helvetica', 'normal')
        pdf.setTextColor(30, 30, 30)
        pdf.text(String(value), 65, y)
        y += 7
      })

      // ── Diagnosis ───────────────────────────────────────────────
      y += 4
      pdf.setFontSize(13)
      pdf.setFont('helvetica', 'bold')
      pdf.setTextColor(30, 30, 30)
      pdf.text('Diagnosis', 14, y)
      pdf.setDrawColor(22, 101, 52)
      pdf.line(14, y + 2, pw - 14, y + 2)
      y += 10

      const diagRows = [
        ['Crop Detected', state?.crop ?? '—'],
        ['Condition', state?.condition ?? '—'],
        ['Severity', state?.severity != null ? `${(state.severity * 100).toFixed(0)}%` : '—'],
        ['Confidence', state?.confidence != null ? `${(state.confidence * 100).toFixed(0)}%` : '—'],
        ['Image Quality', state?.observation_quality ? `${state.observation_quality.quality_level} (${(state.observation_quality.quality_score * 100).toFixed(0)}%)` : '—'],
      ]
      pdf.setFontSize(10)
      diagRows.forEach(([label, value]) => {
        pdf.setFont('helvetica', 'bold')
        pdf.setTextColor(80, 80, 80)
        pdf.text(label + ':', 14, y)
        pdf.setFont('helvetica', 'normal')
        pdf.setTextColor(30, 30, 30)
        pdf.text(String(value), 65, y)
        y += 7
      })

      // ── Trajectory ──────────────────────────────────────────────
      y += 4
      pdf.setFontSize(13)
      pdf.setFont('helvetica', 'bold')
      pdf.setTextColor(30, 30, 30)
      pdf.text(`Trajectory (${trajectory.length} steps)`, 14, y)
      pdf.setDrawColor(22, 101, 52)
      pdf.line(14, y + 2, pw - 14, y + 2)
      y += 10

      trajectory.forEach((step, idx) => {
        if (y > 260) { pdf.addPage(); y = 20 }
        const ap = step.action_proposal as Record<string, unknown>
        const fb = step.feedback as Record<string, unknown> | undefined
        const actionType = ap?.action_type as string ?? '—'
        const result = fb?.result as string ?? '—'
        const explanation = fb?.explanation as string ?? ''

        pdf.setFontSize(10)
        pdf.setFont('helvetica', 'bold')
        pdf.setTextColor(22, 101, 52)
        pdf.text(`Step ${idx + 1}: ${actionType}`, 14, y)
        pdf.setFont('helvetica', 'normal')
        pdf.setTextColor(30, 30, 30)
        pdf.text(`Result: ${result}`, 80, y)
        y += 6
        if (explanation) {
          const lines = pdf.splitTextToSize(explanation, pw - 28)
          pdf.setFontSize(9)
          pdf.setTextColor(80, 80, 80)
          pdf.text(lines, 14, y)
          y += lines.length * 5 + 4
        }
      })

      // ── Footer ──────────────────────────────────────────────────
      const pageCount = pdf.getNumberOfPages()
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i)
        pdf.setFontSize(8)
        pdf.setTextColor(150, 150, 150)
        pdf.text('AgriVLA — AI-Powered Agricultural Diagnostics', 14, 290)
        pdf.text(`Page ${i} of ${pageCount}`, pw - 30, 290)
      }

      pdf.save(`agrivla-report-${session?.title?.replace(/\s+/g, '-') || 'session'}.pdf`)
      toast.success('PDF report downloaded!')
    } catch (err) {
      toast.error('Failed to generate PDF')
      console.error(err)
    }
  }

  return (
    <div className="detail-content">
      {/* Back navigation */}
      <div className="detail-top-nav" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Link to="/dashboard" className="detail-back-btn">
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        {isTerminal && (
          <button onClick={exportToPDF} className="btn-secondary" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <Download size={16} /> Download PDF Report
          </button>
        )}
      </div>

      <div className="detail-main" id="report-content">
        {/* Left Column: State Panel */}
        <div className="state-panel">
          <div className="panel-head">
            <h2>{session?.title ?? '…'}</h2>
            <p className="goal-text">{session?.goal}</p>
          </div>

          {state && (
            <>
              <div className="state-grid">
                <div className="stat-card">
                  <label>Step</label>
                  <span>{state.step_number}</span>
                </div>
                <div className="stat-card">
                  <label>Status</label>
                  <span className={`state-status ${state.status.toLowerCase()}`}>
                    {state.status === 'COMPLETED'
                      ? <CheckCircle size={12} />
                      : state.status === 'ESCALATED'
                      ? <AlertTriangle size={12} />
                      : <Activity size={12} />}
                    {state.status}
                  </span>
                </div>
                <div className="stat-card">
                  <label>Trend</label>
                  <span>{state.trend}</span>
                </div>
                <div className="stat-card">
                  <label>Failures</label>
                  <span>{state.failure_count}</span>
                </div>
              </div>

              <div className="diagnosis-block">
                <h3>Diagnosis</h3>
                <div className="diag-row"><label>Crop</label><span>{state.crop ?? '—'}</span></div>
                <div className="diag-row"><label>Condition</label><span>{state.condition ?? '—'}</span></div>
                <div className="diag-row"><label>Confidence</label><ConfidencePill value={state.confidence} /></div>
                <div className="diag-row"><label>Severity</label></div>
                <SeverityBar value={state.severity} />
                {state.observation_quality && (
                  <div className="diag-row">
                    <label>Image Quality</label>
                    <span>
                      {state.observation_quality.quality_level} ({(state.observation_quality.quality_score * 100).toFixed(0)}%)
                    </span>
                  </div>
                )}
              </div>

              {!isTerminal && (
                <div className="step-panel">
                  <h3>Trigger Step</h3>
                  <p>Upload a plant image then click Run Step</p>
                  <div
                    className="upload-zone"
                    id="image-upload-zone"
                    onClick={() => fileRef.current?.click()}
                  >
                    <Upload size={24} />
                    <span>{image ? image.name : 'Click to upload image'}</span>
                  </div>
                  <input
                    ref={fileRef}
                    id="image-file-input"
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={e => setImage(e.target.files?.[0] ?? null)}
                  />
                  <button
                    id="run-step-btn"
                    className="btn-primary full-width"
                    onClick={handleStep}
                    disabled={stepping}
                  >
                    {stepping ? <span className="btn-spinner" /> : <><Play size={14} /> Run Step</>}
                  </button>
                </div>
              )}

              {isTerminal && (
                <div className="terminal-banner">
                  <CheckCircle size={20} />
                  <span>Session ended: {state.termination_reason}</span>
                </div>
              )}
            </>
          )}
        </div>

        {/* Right Column: Trajectory */}
        <div className="trajectory-panel">
          <h3>
            Trajectory{' '}
            <span className="traj-count">({trajectory.length} steps)</span>
          </h3>
          {trajectory.length === 0 ? (
            <div className="empty-state small">
              <p>No steps yet. Upload an image and click Run Step.</p>
            </div>
          ) : (
            <div className="trajectory-list">
              {[...trajectory].reverse().map((step, i) => (
                <StepCard key={i} step={step} index={trajectory.length - 1 - i} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
