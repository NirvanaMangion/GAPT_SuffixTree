import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';  // Import useNavigate for navigation
import './Header.css';
import Sidebar from './Sidebar';

const Header = () => {
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const navigate = useNavigate();  // Initialize the navigate hook

  // Toggle sidebar visibility
  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };

  // Navigate to the main page
  const navigateToHome = () => {
    navigate('/');  // Redirect to the home page (main page)
  };

  // Navigate to other pages from the sidebar
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
      <h1 onClick={navigateToHome} style={{ cursor: 'pointer' }}>SuffixSearch</h1>  {/* Make the text clickable */}
      <div className="menu-icon" onClick={toggleSidebar}>
        <div />
        <div />
        <div />
      </div>

      <Sidebar visible={sidebarVisible} navigateToPage={navigateToPage} />
    </header>
  );
};

export default Header;
