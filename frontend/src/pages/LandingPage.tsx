import React from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout, BrainCircuit, Activity, ChevronRight, Eye, Upload, Zap, ShieldCheck, Github, Twitter, Linkedin } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const LandingPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="landing-logo">
          <Sprout size={28} />
          AgriVLA
        </div>
        <div className="landing-nav-links">
          {user ? (
            <Link to="/dashboard" className="btn-primary" style={{ padding: '8px 24px' }}>
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">Log in</Link>
              <Link to="/register" className="btn-primary" style={{ padding: '8px 24px' }}>Sign up</Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">


        <motion.h1
          className="hero-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
        >
          Adaptive Agricultural <span>Intelligence</span>
        </motion.h1>

        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
        >
          Diagnose crop diseases, optimize yield, and execute autonomous farming actions in real-time.
          A production-ready platform designed for modern agriculture.
        </motion.p>

        <motion.div
          className="hero-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
        >
          <button
            className="btn-large"
            onClick={() => navigate(user ? '/dashboard' : '/register')}
          >
            Start Analyzing <ChevronRight size={18} />
          </button>
          <a href="#how-it-works" className="btn-secondary">
            Learn More
          </a>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <h2 className="section-title">Enterprise-Grade AI Capabilities</h2>
        <div className="features-grid">
          <motion.div
            className="clean-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
          >
            <div className="clean-card-icon">
              <Eye size={28} />
            </div>
            <h3>Multimodal Perception</h3>
            <p>Upload field images and let our fine-tuned models instantly detect blights, pests, and nutrient deficiencies with pinpoint accuracy.</p>
          </motion.div>

          <motion.div
            className="clean-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="clean-card-icon">
              <BrainCircuit size={28} />
            </div>
            <h3>Agentic Reasoning</h3>
            <p>Our closed-loop architecture evaluates confidence, cross-references RAG knowledge bases, and automatically escalates highly uncertain cases.</p>
          </motion.div>

          <motion.div
            className="clean-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="clean-card-icon">
              <Zap size={28} />
            </div>
            <h3>Real-time Execution</h3>
            <p>Generate step-by-step, actionable treatment plans formatted instantly for modern automated farming infrastructure and robotics.</p>
          </motion.div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="how-it-works">
        <h2 className="section-title">How AgriVLA Works</h2>
        <div className="steps-container">
          <motion.div
            className="step-row"
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
          >
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Upload & Observe</h3>
              <p>Initiate a new agent session on your dashboard. Upload imagery directly from your drones, IoT cameras, or smartphones. AgriVLA's perception engine will process the visual data using optimized multimodal models.</p>
            </div>
          </motion.div>

          <motion.div
            className="step-row"
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Retrieve & Reason</h3>
              <p>The system queries a Qdrant-backed vector database containing extensive agricultural research. It combines visual findings with verified knowledge to formulate a high-confidence diagnosis and treatment plan.</p>
            </div>
          </motion.div>

          <motion.div
            className="step-row"
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Execute & Monitor</h3>
              <p>AgriVLA executes the planned steps, adjusting environmental parameters or alerting staff. If the condition is too complex, the system gracefully halts and requests human intervention, ensuring safety.</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <Sprout size={28} />
            AgriVLA
          </div>
          <div className="footer-links">
            <a href="#">Documentation</a>
            <a href="#">API Reference</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
          <div className="footer-links" style={{ gap: '16px' }}>
            <a href="#"><Github size={20} /></a>
            <a href="#"><Twitter size={20} /></a>
            <a href="#"><Linkedin size={20} /></a>
          </div>
        </div>
        <div className="footer-bottom">
          &copy; {new Date().getFullYear()} AgriVLA Systems. All rights reserved. Built for precision agriculture.
        </div>
      </footer>
    </div>
  );
};
