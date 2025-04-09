import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './PageStyles.css'; // Your global styles

const Home = () => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = () => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="home-page">
      <h1 className="title">Search the documents</h1>
      <div className="search-wrapper">
        <input
          type="text"
          placeholder="Search for a word..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
          className="search-input"
        />
        <button className="search-button" onClick={handleSearch}>
          <span role="img" aria-label="search">🔍</span>
        </button>
      </div>
    </div>
  );
};

export default Home;
