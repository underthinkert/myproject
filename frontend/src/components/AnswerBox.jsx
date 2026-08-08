import { useState } from 'react';

function AnswerBox({ onSubmit }) {
  const [answer, setAnswer] = useState('');

  const handleSubmit = () => {
    if (answer.trim() === '') {
      alert('Please write an answer');
      return;
    }
    onSubmit(answer);
    setAnswer('');
  };

  return (
    <div className="answer-box">
      <textarea
        placeholder="Type your answer here..."
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        rows={5}
      />
      <button onClick={handleSubmit}>Submit Answer</button>
    </div>
  );
}

export default AnswerBox;