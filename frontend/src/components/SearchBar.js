import React from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch }) => (
  <div className="search-container">
    <input type="text" placeholder="Search for a word..." />
    <button className="search-btn" onClick={onSearch}>🔍</button>
  </div>
);

export default SearchBar;
