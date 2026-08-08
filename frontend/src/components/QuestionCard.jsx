function QuestionCard({ questionNumber, questionText }) {
  return (
    <div className="question-card">
      <h3>Question {questionNumber}</h3>
      <p>{questionText}</p>
    </div>
  );
}

export default QuestionCard;