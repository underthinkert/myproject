import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const allTopics = [
  'Arrays', 'Strings', 'OOP', 'SQL', 'Data Structures', 'Algorithms',
  'System Design', 'REST APIs', 'React', 'Node.js', 'Python',
  'Machine Learning', 'Statistics', 'Databases', 'Git'
];

function Setup() {
  const [name, setName] = useState('');
  const [role, setRole] = useState('Frontend');
  const [experience, setExperience] = useState('Junior');
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [duration, setDuration] = useState('30 min');
  const [difficulty, setDifficulty] = useState('Medium');
  const navigate = useNavigate();

  const toggleTopic = (topic) => {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  };

  const isFormComplete =
    name.trim() !== '' &&
    role !== '' &&
    experience !== '' &&
    selectedTopics.length > 0 &&
    duration !== '' &&
    difficulty !== '';

  const totalFields = 6;
  let filledFields = 0;
  if (name.trim() !== '') filledFields++;
  if (role !== '') filledFields++;
  if (experience !== '') filledFields++;
  if (selectedTopics.length > 0) filledFields++;
  if (duration !== '') filledFields++;
  if (difficulty !== '') filledFields++;

  const progressPercent = Math.round((filledFields / totalFields) * 100);

  const handleStart = () => {
    if (!isFormComplete) {
      alert('Please fill all details and select at least one topic');
      return;
    }
    const config = { name, role, experience, selectedTopics, duration, difficulty };
    localStorage.setItem('interviewConfig', JSON.stringify(config));
    navigate('/interview');
  };

  return (
    <div className="setup-page-wrapper">
      <div className="floating-bg">
        <div className="floating-shape shape-1"></div>
        <div className="floating-shape shape-2"></div>
        <div className="floating-shape shape-3"></div>
      </div>

      <div className="setup-page">
        <div className="progress-indicator">
          <div className="progress-indicator-bar">
            <div
              className="progress-indicator-fill"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
          <span className="progress-indicator-text">{progressPercent}% complete</span>
        </div>

        <h1>Set up your mock interview</h1>

        <div className="setup-card">
          <label className="field-label">YOUR NAME</label>
          <input
            type="text"
            placeholder="e.g. Priya Sharma"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <div className="row">
            <div className="col">
              <label className="field-label">ROLE APPLYING FOR</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option>Frontend</option>
                <option>Backend</option>
                <option>Full Stack</option>
                <option>Data Science</option>
                <option>DevOps</option>
                <option>AI/ML Engineer</option>
              </select>
            </div>
            <div className="col">
              <label className="field-label">EXPERIENCE LEVEL</label>
              <select value={experience} onChange={(e) => setExperience(e.target.value)}>
                <option>Junior</option>
                <option>Mid</option>
                <option>Senior</option>
              </select>
            </div>
          </div>

          <label className="field-label">TOPICS YOU'VE COMPLETED</label>
          <div className="topics-grid">
            {allTopics.map((topic) => (
              <button
                key={topic}
                type="button"
                className={`topic-chip ${selectedTopics.includes(topic) ? 'active' : ''}`}
                onClick={() => toggleTopic(topic)}
              >
                {topic}
              </button>
            ))}
          </div>

          <div className="row">
            <div className="col">
              <label className="field-label">INTERVIEW LENGTH</label>
              <select value={duration} onChange={(e) => setDuration(e.target.value)}>
                <option>15 min</option>
                <option>30 min</option>
                <option>45 min</option>
                <option>60 min</option>
              </select>
            </div>
            <div className="col">
              <label className="field-label">DIFFICULTY</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option>Easy</option>
                <option>Medium</option>
                <option>Hard</option>
              </select>
            </div>
          </div>

          <button
            type="button"
            className={`start-btn ${isFormComplete ? 'active' : ''}`}
            onClick={handleStart}
            disabled={!isFormComplete}
          >
            Start interview →
          </button>
        </div>
      </div>
    </div>
  );
}

export default Setup;