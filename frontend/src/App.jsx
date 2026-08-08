import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Setup from './pages/Setup';
import AiMockInterview from './pages/AiMockInterview';
import SignIn from './pages/SignIn';
import Profile from './pages/Profile';
import Interview from './pages/Interview';
import Report from './pages/Report';
import StepSetup from './pages/StepSetup';
import StepQuestions from './pages/StepQuestions';
import StepFeedback from './pages/StepFeedback';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/setup" element={<Setup />} />
        <Route path="/ai-mock-interview" element={<AiMockInterview />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/interview" element={<Interview />} />
        <Route path="/report" element={<Report />} />
        <Route path="/step-setup" element={<StepSetup />} />
        <Route path="/step-questions" element={<StepQuestions />} />
        <Route path="/step-feedback" element={<StepFeedback />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;