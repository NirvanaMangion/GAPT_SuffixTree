import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './AllBooks.css';

const SearchResults = () => {
  const location = useLocation();
  const query = new URLSearchParams(location.search).get("q");
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (query) {
      fetch(`http://localhost:5000/search?q=${query}`)
        .then(res => res.json())
        .then(data => setResults(data));
    }
  }, [query]);

  return (
    <div className="all-books-container">
      <h1>Search Results for "{query}"</h1>
      <div className="books-list">
        {results.map((result, index) => (
          <div key={index} className="book-card">
            <span className="book-icon">📚</span>
            <div className="book-details">
              <h3 className="book-title">{result.title}</h3>
              <p className="book-author">Matches: {result.matches}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
