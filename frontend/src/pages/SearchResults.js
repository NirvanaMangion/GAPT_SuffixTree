import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './AllBooks.css';

const highlightMatch = (text, query) => {
  if (!query) return text;
  try {
    const pattern = query.split(":", 2)[1] || query;
    const regex = new RegExp(`(${pattern})`, "gi");
    return text.split(regex).map((part, i) =>
      regex.test(part) ? <span key={i} className="highlight">{part}</span> : part
    );
  } catch (e) {
    return text;
  }
};

const SearchResults = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  const queryParam = params.get("q");
  const mode = params.get("mode");
  const type = params.get("type");

  const query = mode && queryParam ? `${mode}:${queryParam}` : queryParam;

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 5;

  useEffect(() => {
    setCurrentPage(1);
    if (query) {
      setLoading(true);
      setError("");

      fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          console.log("DEBUG API Response:", data);
          if (data.results) {
            setResults(data.results);
          } else if (data.error) {
            setResults([]);
            setError(data.error);
          } else {
            setResults([]);
            setError("Unexpected response format.");
          }
        })
        .catch(err => {
          setError("Failed to fetch results.");
          setResults([]);
          console.error(err);
        })
        .finally(() => setLoading(false));
    }
  }, [query]);

  const totalPages = Math.ceil(results.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const currentResults = results.slice(startIndex, startIndex + resultsPerPage);

  return (
    <div className="all-books-container">
      <h1>Search Results for "{queryParam}"</h1>
      {loading && <div className="spinner"></div>}
      {error && <p className="error-message">{error}</p>}
      {!loading && results.length === 0 && !error && (
        <p>No results found for "{queryParam}".</p>
      )}

      {!loading && results.length > 0 && (
        <div>
          <h2 className="group-title">Found In Books</h2>
          <div className="books-list">
            {currentResults.map((result, index) => (
              <div key={index} className="book-card">
                <span className="book-icon">📚</span>
                <div className="book-details">
                  <h3 className="book-title">
                    <a href={`/book/${encodeURIComponent(result.book)}?word=${encodeURIComponent(query)}`}>
                      {result.book}
                    </a>
                  </h3>
                  <p className="book-author">Matches: {result.count}</p>
                  <ul>
                    {result.snippets.map((snippet, i) => (
                      <li key={i}><em>...{highlightMatch(snippet, queryParam)}...</em></li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} disabled={currentPage === 1}>
              &laquo; Prev
            </button>
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                className={currentPage === i + 1 ? 'active' : ''}
                onClick={() => setCurrentPage(i + 1)}
              >
                {i + 1}
              </button>
            ))}
            <button onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages}>
              Next &raquo;
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
