import { useNavigate } from 'react-router-dom';

function StepSetup() {
  const navigate = useNavigate();

  return (
    <div className="setup-page">
      <h1>Step 1 · Set up your interview</h1>
      <div className="setup-card">
        <p className="report-text">
          Choose your role (Frontend, Backend, Full Stack, Data Science, DevOps, or AI/ML),
          your experience level, and the topics you've already completed from the cohort.
        </p>
        <p className="report-text">
          This helps the AI interviewer tailor every question to what you actually know —
          instead of asking random or irrelevant topics.
        </p>
        <button className="start-btn active" onClick={() => navigate('/setup')}>
          Go to setup →
        </button>
      </div>
    </div>
  );
}

export default StepSetup;