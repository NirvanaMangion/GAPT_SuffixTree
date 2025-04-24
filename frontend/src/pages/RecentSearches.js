import React, { useEffect, useState } from 'react';
import './AllBooks.css'; // Reusing styles

const RecentSearches = () => {
  const [recentSearches, setRecentSearches] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/recent')
      .then(res => res.json())
      .then(data => {
        const formatted = data.map((term, index) => ({
          title: `Search: ${term}`,
          author: `Search #${index + 1}`
        }));
        setRecentSearches(formatted);
      })
      .catch(err => {
        console.error('Failed to fetch recent searches:', err);
      });
  }, []);

  return (
    <div className="all-books-container">
      <h1>Recent Searches</h1>
      <div className="books-list">
        {recentSearches.length > 0 ? (
          recentSearches.map((item, index) => (
            <div key={index} className="book-card">
              <span className="book-icon">📚</span>
              <div className="book-details">
                <h3 className="book-title">{item.title}</h3>
                <p className="book-author">{item.author}</p>
              </div>
            </div>
          ))
        ) : (
          <p>No recent searches found.</p>
        )}
      </div>
    </div>
  );
};

export default RecentSearches;
