import React, { useEffect, useState } from 'react';
import './AllBooks.css';

const RecentSearches = () => {
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:5000/api/recent")
      .then(res => res.json())
      .then(data => setRecent(data))
      .catch(err => console.error("Error fetching recent searches:", err))
      .finally(() => setLoading(false));
  }, []);

  const handleClear = () => {
    fetch("http://localhost:5000/api/clear", { method: "POST" })
      .then(() => setRecent([]))
      .catch(err => console.error("Error clearing recent searches:", err));
  };

  return (
    <div className="all-books-container">
      <h1>Recent Searches</h1>
      <button className="back-button" onClick={handleClear}>Clear History</button>

      {loading && <p>Loading...</p>}
      {!loading && recent.length === 0 && <p>No recent searches.</p>}

      <div className="books-list">
        {recent.map((item, index) => (
          <div key={index} className="book-card">
            <span className="book-icon">🕘</span>
            <div className="book-details">
              <h3 className="book-title">Search: {item.query}</h3>
              <p className="book-author">{new Date(item.timestamp).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentSearches;
