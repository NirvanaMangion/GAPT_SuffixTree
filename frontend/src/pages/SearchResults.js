import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './AllBooks.css';
import './SearchResults.css'; // ✅ Create this file for additional styles

const highlightMatch = (word, query) => {
  const index = word.toLowerCase().indexOf(query.toLowerCase());
  if (index === -1) return word;
  const before = word.substring(0, index);
  const match = word.substring(index, index + query.length);
  const after = word.substring(index + query.length);
  return (
    <>
      {before}
      <span className="highlight">{match}</span>
      {after}
    </>
  );
};

const categorizeResults = (results, query) => {
  const lowerQuery = query.toLowerCase();

  return {
    exact: results.filter(w => w.toLowerCase() === lowerQuery),
    startsWith: results.filter(w => w.toLowerCase().startsWith(lowerQuery) && w.toLowerCase() !== lowerQuery),
    endsWith: results.filter(w => w.toLowerCase().endsWith(lowerQuery) && !w.toLowerCase().startsWith(lowerQuery)),
    contains: results.filter(w => w.toLowerCase().includes(lowerQuery)
      && !w.toLowerCase().startsWith(lowerQuery)
      && !w.toLowerCase().endsWith(lowerQuery))
  };
};

const SearchResults = () => {
  const location = useLocation();
  const query = new URLSearchParams(location.search).get("q");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (query) {
      setLoading(true);
      setError("");
      fetch(`http://localhost:5000/api/search?q=${query}`)
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data.matches)) {
            setResults(data.matches);
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

  const grouped = categorizeResults(results, query);

  return (
    <div className="all-books-container">
      <h1>Search Results for "{query}"</h1>

      {loading && <div className="spinner"></div>}
      {error && <p className="error-message">{error}</p>}

      {!loading && results.length === 0 && !error && (
        <p>No results found for "{query}".</p>
      )}

      {!loading && (
        <>
          {Object.entries(grouped).map(([group, groupResults]) => (
            groupResults.length > 0 && (
              <div key={group}>
                <h2 className="group-title">
                  {group === "exact" && "Exact Matches"}
                  {group === "startsWith" && "Starts With"}
                  {group === "endsWith" && "Ends With"}
                  {group === "contains" && "Contains"}
                </h2>
                <div className="books-list">
                  {groupResults.map((result, index) => (
                    <div key={index} className="book-card">
                      <span className="book-icon">📚</span>
                      <div className="book-details">
                        <h3 className="book-title">
                          <a href={`/word/${result}`} className="clickable-word">
                            {highlightMatch(result, query)}
                          </a>
                        </h3>
                        <p className="match-info">Match {index + 1}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          ))}
        </>
      )}
    </div>
  );
};

export default SearchResults;
