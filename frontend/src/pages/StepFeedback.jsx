import { useState } from 'react';

function StepFeedback() {
  const sampleScore = 72;
  const sampleTopicScore = 68;
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  const handleRatingSubmit = () => {
    if (rating === 0) {
      alert('Please select a rating first');
      return;
    }
    setSubmitted(true);
  };

  return (
    <div className="report-page">
      <div className="terminal-line">$ sample_report --preview</div>
      <h1>What your feedback report looks like</h1>

      <div className="report-card">
        <span className="report-label">OVERALL SCORE</span>
        <div className="score-row">
          <span className="big-score">{sampleScore}%</span>
          <div className="score-meta">
            <p>Frontend · Junior</p>
            <p>Medium difficulty · 30 min</p>
          </div>
        </div>
      </div>

      <div className="report-card">
        <span className="report-label">TOPIC-WISE BREAKDOWN</span>
        <div className="breakdown-row">
          <span>React & State Management</span>
          <span className="breakdown-percent">{sampleTopicScore}%</span>
        </div>
        <div className="breakdown-bar">
          <div className="breakdown-fill" style={{ width: `${sampleTopicScore}%` }}></div>
        </div>
      </div>

      <div className="report-card">
        <span className="report-label">STRENGTHS & WEAKNESSES</span>
        <p className="report-text">
          Candidates typically show strong command of <span className="highlight-green">core fundamentals</span>{' '}
          and communicate clearly under time pressure.
        </p>
        <p className="report-text">
          Answers touching <span className="highlight-red">system design trade-offs</span> are often thinner on
          detail — worth revisiting with concrete examples.
        </p>
      </div>

      <div className="report-card">
        <span className="report-label">SUGGESTIONS — WHAT TO STUDY NEXT</span>
        <p className="report-text">Review core fundamentals and practice 2-3 timed problems this week.</p>
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

        {submitted ? (
          <p className="report-text" style={{ color: '#6ee7b7' }}>
            Thanks for your feedback! ✓
          </p>
        ) : (
          <button className="rating-submit-btn" onClick={handleRatingSubmit}>
            Submit Rating
          </button>
        )}

        <p className="report-text" style={{ color: '#a39ecb', fontSize: '12px', marginTop: '10px' }}>
          This is a preview — after your real interview, your rating will be saved with your report.
        </p>
      </div>

      <p className="report-text" style={{ textAlign: 'center', marginTop: '10px' }}>
        This is a sample preview. Your real report will be based on your actual answers.
      </p>
    </div>
  );
}

export default StepFeedback;