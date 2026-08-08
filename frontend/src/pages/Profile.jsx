import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Profile() {
  const [user, setUser] = useState(null);
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const savedUser = localStorage.getItem('userProfile');
    const savedHistory = localStorage.getItem('interviewHistory');
    if (savedUser) setUser(JSON.parse(savedUser));
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, []);
  const handleSignOut = () => {
  localStorage.removeItem('userProfile');
  navigate('/');
};

  const avgScore = history.length
    ? Math.round(history.reduce((sum, item) => sum + item.score, 0) / history.length)
    : 0;

  return (
    <div className="report-page">
      <h1>Your Profile</h1>

      <div className="report-card">
        <span className="report-label">ACCOUNT</span>
        <p style={{ color: '#f5f3ff', fontSize: '15px' }}>
          {user?.email || 'Not signed in'}
        </p>
      </div>

      <div className="report-card">
        <span className="report-label">AVERAGE SCORE (LAST {history.length} INTERVIEWS)</span>
        <span className="big-score">{avgScore}%</span>
      </div>

      <div className="report-card">
        <span className="report-label">RECENT MOCK INTERVIEWS</span>

        {history.length === 0 ? (
          <p className="report-text">No interviews yet. Take your first mock interview!</p>
        ) : (
          history.map((item, idx) => (
            <div key={idx} className="history-row">
              <div>
                <p className="history-role">{item.role} · {item.experience}</p>
                <p className="history-meta">{item.difficulty} · {item.duration} · {item.date}</p>
              </div>
              <span className="history-score">{item.score}%</span>
            </div>
          ))
        )}
      </div>

      <button
  className="start-btn"
  style={{ marginTop: '10px', backgroundColor: 'transparent', border: '1px solid #38335a', color: '#f5f3ff' }}
  onClick={handleSignOut}
>
  Sign Out
</button>
    </div>
  );
}

export default Profile;