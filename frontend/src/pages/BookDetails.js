// src/pages/BookDetails.js
import React, { useEffect, useState } from 'react';
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

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const query = queryParams.get("word") || "";
    if (!query) {
      setLoading(false);
      return;
    }

    setLoading(true);

    // 1. Fetch matches (snippets) for this book/query
    fetch(`http://localhost:5000/api/book/${encodeURIComponent(title)}?word=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        setMatches(data.matches || []);
      })
      .catch(err => {
        setError("Failed to fetch matches.");
        setMatches([]);
      });

    // 2. Fetch search metadata for highlighting
    fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        if (data.regex) setPattern(data.regex);
        if (data.emoji) setEmoji(data.emoji);
        // Parse queryArg from the part after ':'
        if (data.query && data.query.includes(":")) {
          const [, arg] = data.query.split(":", 2);
          setQueryArg(arg);
        } else {
          setQueryArg("");
        }
      })
      .catch(err => {
        setPattern('');
        setEmoji('');
        setQueryArg('');
      })
      .finally(() => setLoading(false));
  }, [title]);

  return (
    <div className="all-books-container">
      <button onClick={() => window.history.back()} className="sort-button">← Back</button>
      <h2>{decodeURIComponent(title)}</h2>

      {loading && <p>Loading...</p>}
      {error && <p className="error-message">{error}</p>}

      {!loading && !error && matches.length > 0 && matches.map((match, index) => (
        <div key={index} className="book-card">
          <div>
            <p><strong>Offset:</strong> {Array.isArray(match.offset) ? match.offset[1] : match.offset}</p>
          </div>
          <br/>
          <div>
            <p>
              <strong>Context:</strong> {
                highlightMatch(match.snippet || '', pattern, emoji, queryArg)
              }
            </p>
          </div>
        </div>
      ))}

      {!loading && !error && matches.length === 0 && (
        <p>No matches found in this book.</p>
      )}
    </div>
  );
};

export default BookDetails;
