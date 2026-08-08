import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Report() {
  const [config, setConfig] = useState(null);
  const [chat, setChat] = useState([]);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const savedConfig = localStorage.getItem('interviewConfig');
    const savedChat = localStorage.getItem('interviewChat');
    if (savedConfig) setConfig(JSON.parse(savedConfig));
    if (savedChat) setChat(JSON.parse(savedChat));
  }, []);

  const handleRestart = () => {
    localStorage.removeItem('interviewConfig');
    localStorage.removeItem('interviewChat');
    sessionStorage.removeItem('reportSaved');
    navigate('/');
  };

  const handleRatingSubmit = () => {
    if (rating === 0) {
      alert('Please select a rating first');
      return;
    }
    localStorage.setItem('lastInterviewRating', rating);
    alert('Thanks for your feedback!');
  };

  const answeredCount = chat.filter((msg) => msg.type === 'you').length;
  const overallScore = 60;
  const topicScore = 49;

  return (
    <div className="report-page">
      <div className="terminal-line">$ generate_report --{config?.name?.toLowerCase() || 'candidate'}</div>
      <h1>Interview report</h1>

      <div className="report-card">
        <span className="report-label">OVERALL SCORE</span>
        <div className="score-row">
          <span className="big-score">{overallScore}%</span>
          <div className="score-meta">
            <p>{config?.role} · {config?.experience}</p>
            <p>{config?.difficulty} difficulty · {config?.duration}</p>
          </div>
        </div>
      </div>

      <div className="report-card">
        <span className="report-label">TOPIC-WISE BREAKDOWN</span>
        <div className="breakdown-row">
          <span>General</span>
          <span className="breakdown-percent">{topicScore}%</span>
        </div>
        <div className="breakdown-bar">
          <div className="breakdown-fill" style={{ width: `${topicScore}%` }}></div>
        </div>
      </div>

      <div className="report-card">
        <span className="report-label">STRENGTHS & WEAKNESSES</span>
        <p className="report-text">
          {config?.name || 'Candidate'} answered {answeredCount} questions and showed the strongest command of{' '}
          <span className="highlight-green">the basics</span>, communicating clearly under time pressure.
        </p>
        <p className="report-text">
          Answers touching <span className="highlight-red">General</span> were thinner on detail — worth revisiting
          with concrete examples and tighter explanations of trade-offs.
        </p>
      </div>

      <div className="report-card">
        <span className="report-label">SUGGESTIONS — WHAT TO STUDY NEXT</span>
        <p className="report-text">Review General fundamentals and practice 2-3 timed problems this week.</p>
      </div>

      <div className="report-card">
        <span className="report-label">RATE YOUR INTERVIEW EXPERIENCE</span>
        <div className="star-rating">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              className={`star ${(hoverRating || rating) >= star ? 'filled' : ''}`}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
            >
              ★
            </span>
          ))}
        </div>
        <button className="rating-submit-btn" onClick={handleRatingSubmit}>
          Submit Rating
        </button>
      </div>

      <div className="report-card">
        <span className="report-label">FULL TRANSCRIPT</span>
        {chat.map((msg, idx) => (
          <p key={idx} className="transcript-line">
            <span className="transcript-role">{msg.type}:</span> {msg.text}
          </p>
        ))}
      </div>

      <button className="restart-btn" onClick={handleRestart}>Start a new interview</button>
    </div>
  );
}

export default Report;