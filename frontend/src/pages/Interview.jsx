import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://127.0.0.1:8000/api/interview';

function Interview() {
  const [config, setConfig] = useState(null);
  const [chat, setChat] = useState([]);
  const [answer, setAnswer] = useState('');
  const [timeLeft, setTimeLeft] = useState(30 * 60);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const chatEndRef = useRef(null);

  // ==========================================================
  // SESSION ID
  // ==========================================================

  const getSessionId = () => {
    let sessionId = sessionStorage.getItem(
      'interviewSessionId'
    );

    if (!sessionId) {
      sessionId = `interview-${Date.now()}`;

      sessionStorage.setItem(
        'interviewSessionId',
        sessionId
      );
    }

    return sessionId;
  };

  // ==========================================================
  // START INTERVIEW
  // ==========================================================

  useEffect(() => {
    const startInterview = async () => {
      try {
        setLoading(true);
        setError('');

        const savedConfig =
          localStorage.getItem('interviewConfig');

        if (!savedConfig) {
          setError(
            'Interview configuration not found. Please go back to Setup.'
          );
          setLoading(false);
          return;
        }

        const parsedConfig = JSON.parse(savedConfig);

        setConfig(parsedConfig);

        const sessionId = getSessionId();

        // ------------------------------------------------------
        // Convert Setup.jsx data to backend format
        // ------------------------------------------------------

        const candidate = {
          member: {
            name: parsedConfig.name || 'Candidate',

            jobRole:
              parsedConfig.role ||
              'Software Engineer',

            yearsExperience: 0,

            education: 'Not specified',
          },

          missions: [],
        };

        console.log(
          'Sending candidate to backend:',
          candidate
        );

        // ------------------------------------------------------
        // CALL BACKEND
        // ------------------------------------------------------

        const response = await fetch(
          API_URL,
          {
            method: 'POST',

            headers: {
              'Content-Type': 'application/json',
            },

            body: JSON.stringify({
              sessionId: sessionId,

              candidate: candidate,

              message: null,
            }),
          }
        );

        if (!response.ok) {
          const errorText =
            await response.text();

          throw new Error(
            `Backend error ${response.status}: ${errorText}`
          );
        }

        const data =
          await response.json();

        console.log(
          'Backend response:',
          data
        );

        // ------------------------------------------------------
        // SHOW QUESTION 1
        // ------------------------------------------------------

        setChat([
          {
            type: 'interviewer',
            text: data.reply,
          },
        ]);

      } catch (err) {
        console.error(
          'START INTERVIEW ERROR:',
          err
        );

        setError(
          err.message ||
            'Unable to connect to backend.'
        );

      } finally {
        setLoading(false);
      }
    };

    startInterview();
  }, []);

  // ==========================================================
  // TIMER
  // ==========================================================

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((previous) =>
        previous > 0
          ? previous - 1
          : 0
      );
    }, 1000);

    return () =>
      clearInterval(timer);
  }, []);

  // ==========================================================
  // AUTO SCROLL
  // ==========================================================

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [chat]);

  // ==========================================================
  // FORMAT TIME
  // ==========================================================

  const formatTime = (seconds) => {
    const minutes =
      Math.floor(seconds / 60)
        .toString()
        .padStart(2, '0');

    const secs =
      (seconds % 60)
        .toString()
        .padStart(2, '0');

    return `${minutes}:${secs}`;
  };

  // ==========================================================
  // SUBMIT ANSWER
  // ==========================================================

  const handleSubmit = async () => {
    if (
      !answer.trim() ||
      loading
    ) {
      return;
    }

    const candidateAnswer =
      answer.trim();

    const sessionId =
      getSessionId();

    // Show candidate answer immediately
    setChat((previous) => [
      ...previous,

      {
        type: 'you',
        text: candidateAnswer,
      },
    ]);

    setAnswer('');
    setLoading(true);
    setError('');

    try {
      const response =
        await fetch(
          API_URL,
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify({
              sessionId:
                sessionId,

              candidate: null,

              message:
                candidateAnswer,
            }),
          }
        );

      if (!response.ok) {
        const errorText =
          await response.text();

        throw new Error(
          `Backend error ${response.status}: ${errorText}`
        );
      }

      const data =
        await response.json();

      console.log(
        'Answer response:',
        data
      );

      // ------------------------------------------------------
      // INTERVIEW COMPLETE
      // ------------------------------------------------------

      if (data.done === true) {
        localStorage.setItem(
          'interviewFeedback',
          JSON.stringify(
            data.feedback
          )
        );

        sessionStorage.removeItem(
          'interviewSessionId'
        );

        navigate('/report');

        return;
      }

      // ------------------------------------------------------
      // SHOW NEXT QUESTION
      // ------------------------------------------------------

      setChat((previous) => [
        ...previous,

        {
          type: 'interviewer',
          text: data.reply,
        },
      ]);

    } catch (err) {
      console.error(
        'SUBMIT ANSWER ERROR:',
        err
      );

      setError(
        err.message ||
          'Unable to connect to backend.'
      );

    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // ENTER KEY
  // ==========================================================

  const handleKeyPress = (event) => {
    if (
      event.key === 'Enter' &&
      !event.shiftKey
    ) {
      event.preventDefault();

      handleSubmit();
    }
  };

  // ==========================================================
  // END INTERVIEW
  // ==========================================================

  const handleEnd = () => {
    sessionStorage.removeItem(
      'interviewSessionId'
    );

    navigate('/report');
  };

  // ==========================================================
  // PROGRESS
  // ==========================================================

  const questionCount =
    chat.filter(
      (message) =>
        message.type ===
        'interviewer'
    ).length;

  const progress = Math.min(
    (questionCount / 8) * 100,
    100
  );

  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="interview-page">

      <div className="interview-header">

        <div>
          ●{' '}
          {config?.name ||
            'Candidate'}
          {' · '}
          {config?.role ||
            'Software Engineer'}
          {' · '}
          {config?.difficulty ||
            'Medium'}
        </div>

        <div>
          ⏱{' '}
          {formatTime(
            timeLeft
          )}
        </div>

      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{
            width:
              `${progress}%`,
          }}
        />
      </div>

      {error && (
        <div
          style={{
            margin: '15px 0',
            padding: '12px',
            color: '#ff6b6b',
            border:
              '1px solid #ff6b6b',
            borderRadius: '8px',
          }}
        >
          {error}
        </div>
      )}

      <div className="chat-window">

        {chat.map(
          (message, index) => (
            <div
              key={index}
              className={
                `chat-row ${
                  message.type ===
                  'you'
                    ? 'right'
                    : 'left'
                }`
              }
            >

              <div
                className={
                  `chat-bubble ${
                    message.type
                  }`
                }
              >

                <span className="chat-label">
                  {message.type ===
                  'you'
                    ? 'You'
                    : 'Interviewer'}
                </span>

                <p>
                  {message.text}
                </p>

              </div>

            </div>
          )
        )}

        {loading && (
          <div className="chat-row left">

            <div className="chat-bubble interviewer">

              <span className="chat-label">
                Interviewer
              </span>

              <p>
                Thinking...
              </p>

            </div>

          </div>
        )}

        <div ref={chatEndRef} />

      </div>

      <div className="chat-input-row">

        <input
          type="text"
          placeholder="Type your answer..."
          value={answer}
          disabled={loading}
          onChange={(event) =>
            setAnswer(
              event.target.value
            )
          }
          onKeyDown={
            handleKeyPress
          }
        />

        <button
          className="send-btn"
          onClick={
            handleSubmit
          }
          disabled={
            loading ||
            !answer.trim()
          }
        >
          ➤
        </button>

      </div>

      <button
        className="end-btn"
        onClick={handleEnd}
      >
        End interview
      </button>

    </div>
  );
}

export default Interview;