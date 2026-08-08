import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  return (
    <div className="hero-page">
      <div className="floating-bg">
        <div className="floating-shape shape-1"></div>
        <div className="floating-shape shape-2"></div>
        <div className="floating-shape shape-3"></div>
      </div>

      <div className="hero-content fade-in">
        <div className="hero-text">
          <span className="hero-tag">✨ AI-Powered Practice</span>
          <h1>
            Ace your next <span className="gradient-text">technical interview</span>
          </h1>
          <p>
            Practice with an AI interviewer that adapts to what you've actually learned —
            real questions, smart follow-ups, and instant feedback.
          </p>
          <button className="ai-cta-btn" onClick={() => navigate('/ai-mock-interview')}>
            USE ME→
          </button>

          <div className="trust-badges">
            <span>✓ Free to use</span>
            <span>✓ No subscription required</span>
            <span>✓ Based on your cohort curriculum</span>
          </div>
          <div className="counter-stats">
  <div className="counter-item">
    <span className="counter-number">31</span>
    <span className="counter-label">Day Program</span>
  </div>
  <div className="counter-item">
    <span className="counter-number">6+</span>
    <span className="counter-label">Roles Supported</span>
  </div>
  <div className="counter-item">
    <span className="counter-number">100%</span>
    <span className="counter-label">Free</span>
  </div>
</div>
        </div>

        <div className="hero-illustration">
          <div className="hero-preview-card">
            <div className="hero-preview-dot"></div>
            <div className="hero-preview-header">
              <span>interviewer</span>
            </div>
            <div className="hero-preview-msg">
              "Tell me about a challenging bug you fixed recently."
            </div>
            <div className="hero-preview-typing">
              <span></span><span></span><span></span>
            </div>
          </div>

          <div className="hero-orb-small">
            <div className="orb-core-small">AI</div>
          </div>
        </div>
      </div>

      <div className="scroll-hint">
        <span>↓</span>
      </div>
    </div>
  );
}

export default Home;