import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function SignIn() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSignIn = () => {
    if (email.trim() === '' || password.trim() === '') {
      alert('Please enter email and password');
      return;
    }
    // Abhi ke liye sirf localStorage mein save kar rahe hain (real auth baad me backend se)
    localStorage.setItem('userProfile', JSON.stringify({ email }));
    navigate('/profile');
  };

  return (
    <div className="setup-page">
      <h1>Sign In</h1>
      <div className="setup-card">
        <label className="field-label">EMAIL</label>
        <input
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="field-label">PASSWORD</label>
        <input
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          type="button"
          className={`start-btn ${email && password ? 'active' : ''}`}
          onClick={handleSignIn}
        >
          Sign In →
        </button>
      </div>
    </div>
  );
}

export default SignIn;