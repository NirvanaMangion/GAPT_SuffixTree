import React from 'react';
import './Sidebar.css';

const Sidebar = ({ visible, navigateToPage }) => {
  return (
    <div className={`sidebar ${visible ? 'visible' : ''}`}>
      <button onClick={() => navigateToPage('allBooks')}>
        📚 All Books
      </button>
      <button onClick={() => navigateToPage('recentSearches')}>
        🕘 Recent Searches
      </button>
    </div>
  );
};

export default Sidebar;
