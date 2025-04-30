import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Header.css';
import Sidebar from './Sidebar';
import ThemeToggle from './ThemeToggle'; // ✅ Import ThemeToggle

const Header = () => {
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const navigateToHome = () => {
    navigate('/');
  };

  const navigateToPage = (page) => {
    if (page === 'allBooks') {
      navigate('/books');
    } else if (page === 'recentSearches') {
      navigate('/recent');
    }
  };

  return (
    <header className="header">
      <div className="circle" />
      <h1 onClick={navigateToHome} style={{ cursor: 'pointer' }}>VerseSearch</h1>
      
      <div className="header-right"> {/* ✅ New wrapper */}
        <div className="menu-icon" onClick={toggleSidebar}>
          <div />
          <div />
          <div />
        </div>
        <ThemeToggle /> {/* ✅ Moved ThemeToggle inside header-right */}
      </div>

      <Sidebar visible={sidebarVisible} navigateToPage={navigateToPage} />
    </header>
  );
};

export default Header;
