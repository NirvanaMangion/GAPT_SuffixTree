import React from 'react';
import './AllBooks.css'; // Using the same CSS

const RecentSearches = () => {
  const recentSearches = [
    { title: 'Recently Viewed Book 1', author: 'User A' },
    { title: 'Recently Viewed Book 2', author: 'User B' },
    { title: 'Recently Viewed Book 3', author: 'User C' },
  ];

  return (
    <div className="all-books-container">
      <h1>Recent Searches</h1>
      <div className="books-list">
        {recentSearches.map((item, index) => (
          <div key={index} className="book-card">
            <span className="book-icon">📚</span>
            <div className="book-details">
              <h3 className="book-title">{item.title}</h3>
              <p className="book-author">{item.author}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentSearches;
