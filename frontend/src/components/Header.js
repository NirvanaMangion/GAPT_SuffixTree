// src/components/Header.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Header.css';
import Sidebar from './Sidebar';
import ThemeToggle from './ThemeToggle';

const Header = ({ darkMode, setDarkMode }) => {
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  const navigateToHome = () => {
    setSidebarVisible(false);
    navigate('/');
  };

  const navigateToPage = (page) => {
    setSidebarVisible(false);
    if (page === 'allBooks') {
      navigate('/books');
    } else if (page === 'recentSearches') {
      navigate('/recent');
    }
  };

  return (
    <header className="header">
      <div className="circle" />
      <h1 onClick={navigateToHome} style={{ cursor: 'pointer' }}>SuffixSearch</h1>

      <div className="header-right">
        <div className="menu-icon" onClick={toggleSidebar}>
          <div />
          <div />
          <div />
        </div>
        <ThemeToggle darkMode={darkMode} setDarkMode={setDarkMode} />
      </div>

      <Sidebar visible={sidebarVisible} navigateToPage={navigateToPage} />
    </header>
  );
};

export default Header;
