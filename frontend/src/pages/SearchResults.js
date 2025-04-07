import React from 'react';
import './AllBooks.css'; // Using the same CSS

const SearchResults = () => {
  const results = [
    { title: 'Matched Result 1', author: 'Author A' },
    { title: 'Matched Result 2', author: 'Author B' },
    { title: 'Matched Result 3', author: 'Author C' },
  ];

  return (
    <div className="all-books-container">
      <h1>Search Results</h1>
      <div className="books-list">
        {results.map((result, index) => (
          <div key={index} className="book-card">
            <span className="book-icon">📚</span>
            <div className="book-details">
              <h3 className="book-title">{result.title}</h3>
              <p className="book-author">{result.author}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
