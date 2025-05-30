import React, { useEffect, useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import './AllBooks.css';
import { highlightMatch } from './highlighting';

const SearchResults = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("q");

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

            // Set global pattern/mode/arg from API
            if (data.regex) setSearchPattern(data.regex);
            if (data.emoji) setSearchMode(data.emoji);

            // Extract queryArg from query, e.g. for 📄:ing, arg is 'ing'
            if (data.query && data.query.includes(":")) {
              const [, arg] = data.query.split(":", 2);
              setSearchArg(arg.trim());
            } else {
              setSearchArg(""); // fallback
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

  // Group results by book
  const groupedResults = useMemo(() => {
    const grouped = results.reduce((acc, curr) => {
      const book = curr.book || "Unknown Book";
      if (!acc[book]) acc[book] = [];
      acc[book].push(curr);
      return acc;
    }, {});
    return Object.entries(grouped);
  }, [results]);

  const totalPages = Math.ceil(groupedResults.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const paginatedBooks = groupedResults.slice(startIndex, startIndex + resultsPerPage);

  return (
    <div className="all-books-container">
      <h1>Search Results for "{query}"</h1>

      {loading && <div className="spinner"></div>}
      {error && <p className="error-message">{error}</p>}
      {!loading && groupedResults.length === 0 && !error && (
        <p>No results found for "{query}".</p>
      )}

      {!loading && groupedResults.length > 0 && (
        <>
          <h2 className="group-title">Found In Books</h2>
          <div className="books-list">
            {paginatedBooks.map(([bookName, entries], index) => (
              <div key={index} className="book-card">
                <span className="book-icon">📚</span>
                <div className="book-details">
                  <h3 className="book-title">
                    <a href={`/book/${encodeURIComponent(bookName)}?word=${encodeURIComponent(query)}`}>
                      {bookName}
                    </a>
                  </h3>
                  <ul>
                    {entries.slice(0, 3).map((entry, i) => {
                      // Try to use pattern/emoji/arg per entry (if backend sends them), otherwise fallback to global
                      const pattern = entry.pattern || searchPattern || searchArg;
                      const emoji = entry.emoji || searchMode;
                      const arg = entry.arg || searchArg;
                      return (
                        <li key={i}>
                          <span>
                            {highlightMatch(entry.snippet || '', pattern, emoji, arg)}
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
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
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              Next &raquo;
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default SearchResults;
