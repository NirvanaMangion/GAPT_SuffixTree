// src/pages/BookDetails.js
import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import './AllBooks.css';
import { highlightMatch } from './highlighting';

const BookDetails = () => {
  const { title } = useParams();
  const [matches, setMatches] = useState([]);
  const [pattern, setPattern] = useState('');
  const [emoji, setEmoji] = useState('');
  const [queryArg, setQueryArg] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [rawQuery, setRawQuery] = useState('');

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const query = queryParams.get("word") || "";
    setRawQuery(query);
    if (!query) return;

    fetch(`http://localhost:5000/api/book/${encodeURIComponent(title)}?word=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        if (data.matches) {
          setMatches(data.matches);
        }
      })
      .catch(err => {
        console.error(err);
        setError("Failed to fetch matches.");
      });

    fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        if (data.regex) setPattern(data.regex);
        if (data.emoji) setEmoji(data.emoji);
        if (data.query && data.query.includes(":")) {
          const [, arg] = data.query.split(":", 2);
          setQueryArg(arg);
        }
      })
      .catch(err => console.error("Failed to load regex pattern:", err))
      .finally(() => setLoading(false));
  }, [title]);

  const highlightedMatches = useMemo(() => {
    if (!pattern) return matches;
    return matches.map(m => ({
      ...m,
      context: <>{highlightMatch(m.context, pattern, emoji, queryArg)}</>
    }));
  }, [matches, pattern, emoji, queryArg]);

  return (
    <div className="all-books-container">
      <button onClick={() => window.history.back()} className="sort-button">← Back</button>
      <h2>{decodeURIComponent(title)}</h2>

      {loading && <p>Loading...</p>}
      {error && <p className="error-message">{error}</p>}

      {!loading && !error && highlightedMatches.map((match, index) => (
        <div key={index} className="book-card">
          <p><strong>Offset:</strong> {match.offset}</p>
          <p><strong>Context:</strong> {match.context}</p>
        </div>
      ))}
    </div>
  );
};

export default BookDetails;
