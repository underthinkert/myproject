import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const dummyQuestions = [
  "Hi! Let's begin. I'll ask medium questions for the next 30 minutes.",
  "Tell me about a project you're proud of and your role in it.",
  "Walk me through how you'd approach debugging a production issue you've never seen before.",
  "How does an AI agent maintain context in a conversation?",
];

function Interview() {
  const [config, setConfig] = useState(null);
  const [chat, setChat] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [timeLeft, setTimeLeft] = useState(30 * 60);
  const navigate = useNavigate();
  const chatEndRef = useRef(null);

  useEffect(() => {
    const savedConfig = localStorage.getItem('interviewConfig');
    const parsedConfig = savedConfig ? JSON.parse(savedConfig) : { name: 'Candidate', role: 'Frontend', difficulty: 'Medium' };
    setConfig(parsedConfig);

    setChat([
      { type: 'interviewer', text: `Hi ${parsedConfig.name}, let's begin. I'll ask ${parsedConfig.difficulty.toLowerCase()} ${parsedConfig.role} questions for the next 30 minutes.` },
      { type: 'interviewer', text: dummyQuestions[1] },
    ]);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const handleSubmit = () => {
    if (answer.trim() === '') return;

    const updatedChat = [...chat, { type: 'you', text: answer }];

    if (currentIndex + 2 < dummyQuestions.length) {
      const nextQuestion = dummyQuestions[currentIndex + 2];
      updatedChat.push({ type: 'interviewer', text: nextQuestion });
      setCurrentIndex(currentIndex + 1);
    } else {
      localStorage.setItem('interviewChat', JSON.stringify(updatedChat));
      navigate('/report');
      return;
    }

    setChat(updatedChat);
    setAnswer('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSubmit();
  };

  const handleEnd = () => {
    localStorage.setItem('interviewChat', JSON.stringify(chat));
    navigate('/report');
  };

  const progress = ((currentIndex + 1) / dummyQuestions.length) * 100;

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="header-left">
          <span className="user-icon">●</span>
          {config?.name} · {config?.role} · {config?.difficulty}
        </div>
        <div className="header-right">
          ⏱ {formatTime(timeLeft)}
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      <div className="chat-window">
        {chat.map((msg, idx) => (
          <div key={idx} className={`chat-row ${msg.type === 'you' ? 'right' : 'left'}`}>
            <div className={`chat-bubble ${msg.type}`}>
              <span className="chat-label">{msg.type}</span>
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Type your answer..."
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="send-btn" onClick={handleSubmit}>➤</button>
      </div>

      <button className="end-btn" onClick={handleEnd}>End interview</button>
    </div>
  );
}

export default Interview;