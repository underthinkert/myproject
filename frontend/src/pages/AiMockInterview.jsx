import { useNavigate } from 'react-router-dom';

function AiMockInterview() {
  const navigate = useNavigate();

  return (
    <div className="ai-landing">
      <div className="ai-animation">
        <div className="ai-orb">
          <div className="pulse-ring"></div>
          <div className="pulse-ring delay-1"></div>
          <div className="pulse-ring delay-2"></div>
          <div className="orb-core">AI</div>
        </div>
        <div className="sound-bars">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <h1>Practice with your AI Interviewer</h1>
      <p>
        Get a realistic, adaptive technical interview based on what you've actually
        learned — with intelligent follow-up questions and instant feedback.
      </p>

      <button className="ai-cta-btn" onClick={() => navigate('/setup')}>
        Try a Mock Interview →
      </button>

      <div className="how-it-works">
        <div className="hiw-card" onClick={() => navigate('/step-setup')}>
          <span className="hiw-number">1</span>
          <h4>Set up your interview</h4>
          <p>Pick your role, experience level, and the topics you've completed.</p>
          <span className="hiw-click">Click me →</span>
        </div>

        <div className="hiw-card" onClick={() => navigate('/step-questions')}>
          <span className="hiw-number">2</span>
          <h4>Answer live questions</h4>
          <p>Get adaptive, intelligent follow-ups based on your actual answers.</p>
          <span className="hiw-click">Click me →</span>
        </div>

        <div className="hiw-card" onClick={() => navigate('/step-feedback')}>
          <span className="hiw-number">3</span>
          <h4>Get instant feedback</h4>
          <p>Receive a detailed report with your score, strengths, and next steps.</p>
          <span className="hiw-click">Click me →</span>
        </div>
      </div>

      <div className="feature-strip">
        <div className="feature-item">
          <span className="feature-icon">⚡</span>
          <p>Adaptive follow-ups</p>
        </div>
        <div className="feature-item">
          <span className="feature-icon">📊</span>
          <p>Instant scoring</p>
        </div>
        <div className="feature-item">
          <span className="feature-icon">🎯</span>
          <p>Topic-based questions</p>
        </div>
        <div className="feature-item">
          <span className="feature-icon">📝</span>
          <p>Full transcript</p>
        </div>
      </div>
    </div>
  );
}

export default AiMockInterview;