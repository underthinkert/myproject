import { useState, useEffect } from 'react';

const demoChat = [
  { type: 'interviewer', text: "Tell me about a project you're proud of." },
  { type: 'you', text: "I built a real-time chat app using React and WebSockets." },
  { type: 'interviewer', text: "Nice — how did you handle reconnection when the socket dropped?" },
];

function StepQuestions() {
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    if (visibleCount < demoChat.length) {
      const timer = setTimeout(() => setVisibleCount(visibleCount + 1), 1200);
      return () => clearTimeout(timer);
    }
  }, [visibleCount]);

  return (
    <div className="report-page">
      <div className="terminal-line">$ step_2 --live_questions</div>
      <h1>Answer live questions</h1>

      <div className="report-card demo-chat-card">
        <span className="report-label">LIVE DEMO</span>
        <div className="demo-chat-window">
          {demoChat.slice(0, visibleCount).map((msg, idx) => (
            <div key={idx} className={`chat-row ${msg.type === 'you' ? 'right' : 'left'}`}>
              <div className={`chat-bubble ${msg.type}`}>
                <span className="chat-label">{msg.type}</span>
                <p>{msg.text}</p>
              </div>
            </div>
          ))}
          {visibleCount < demoChat.length && (
            <div className="chat-row left">
              <div className="chat-bubble interviewer typing-bubble">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="report-card">
        <span className="report-label">HOW IT WORKS</span>
        <p className="report-text">
          The AI interviewer asks one question at a time, in a natural chat format —
          just like a real interview.
        </p>
        <p className="report-text">
          Based on your answer, it generates a smart follow-up — digging deeper if your
          answer is vague, or moving on if you've clearly shown understanding.
        </p>
      </div>

      <div className="report-card">
        <span className="report-label">WHAT'S TRACKED</span>
        <p className="report-text">
          Time taken, clarity of explanation, and depth of technical detail — all factored
          into your final score.
        </p>
      </div>
    </div>
  );
}

export default StepQuestions;