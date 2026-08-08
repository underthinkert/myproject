 import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';

function Navbar() {
  const location = useLocation();
  const [isSignedIn, setIsSignedIn] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [location]);

  const checkAuth = () => {
    const user = localStorage.getItem('userProfile');
    setIsSignedIn(!!user);
  };

  return (
    <nav className="navbar">
      <h2 className="nav-logo">AI Interview</h2>
      <div className="nav-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Home</Link>
        <Link to="/ai-mock-interview" className={location.pathname === '/ai-mock-interview' ? 'active' : ''}>
          AI Mock Interview
        </Link>

        {isSignedIn ? (
          <Link to="/profile" className={location.pathname === '/profile' ? 'active' : ''}>
            Profile
          </Link>
        ) : (
          <Link to="/signin" className="signin-btn">
  Sign In
</Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;