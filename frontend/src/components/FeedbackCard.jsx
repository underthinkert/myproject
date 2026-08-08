function FeedbackCard({ questionNumber, questionText, answerText }) {
  return (
    <div className="feedback-card">
      <h4>Q{questionNumber}: {questionText}</h4>
      <p><strong>Your Answer:</strong> {answerText}</p>
    </div>
  );
}

export default FeedbackCard;