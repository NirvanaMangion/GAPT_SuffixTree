import React from 'react';
import './Sidebar.css';

const Sidebar = ({ visible, navigateToPage }) => (
  <div className={`sidebar ${visible ? 'visible' : ''}`}>
    <button onClick={() => navigateToPage('allBooks')}>View All Books</button>
    <button onClick={() => navigateToPage('recentSearches')}>View Recent Searches</button>
  </div>
);

export default Sidebar;
