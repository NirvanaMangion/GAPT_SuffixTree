import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './AllBooks.css';
import { highlightMatch } from './highlighting';

const SearchResults = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  const queryParam = params.get("q");
  const mode = params.get("mode");
  const query = mode && queryParam ? `${mode}:${queryParam}` : queryParam;

  const [results, setResults] = useState([]);
  const [searchPattern, setSearchPattern] = useState("");
  const [searchMode, setSearchMode] = useState("");
  const [searchArg, setSearchArg] = useState("");
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
          if (Array.isArray(data.results)) {
            setResults(data.results);
            if (data.regex) setSearchPattern(data.regex);
            if (data.emoji) setSearchMode(data.emoji);
            if (data.query && data.query.includes(":")) {
              const [, arg] = data.query.split(":", 2);
              setSearchArg(arg);
            }
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
  const currentResults = Array.isArray(results) ? results.slice(startIndex, startIndex + resultsPerPage) : [];

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
                    {result.book ? (
                      <a href={`/book/${encodeURIComponent(result.book)}?word=${encodeURIComponent(query)}`}>
                        {result.book}
                      </a>
                    ) : (
                      // If result.book is missing, fallback to book_id or "Unknown"
                      <span>{result.book_id || "Unknown Book"}</span>
                    )}
                  </h3>
                  <p className="book-author">Matches: {result.count}</p>
                  <ul>
                    {(result.snippets || []).map((obj, i) => (
                      <li key={i}>
                        <em>...{highlightMatch(obj.snippet, searchPattern, searchMode, searchArg)}...</em>
                      </li>
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
