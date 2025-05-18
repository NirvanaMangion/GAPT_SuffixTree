import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './AllBooks.css';


const getQueryParam = (location, name) => {
  return new URLSearchParams(location.search).get(name);
};

const highlight = (text, query) => {
  if (typeof text !== "string") return text;
  const regex = new RegExp(`(${query})`, 'gi');
  return text.split(regex).map((part, i) =>
    part.toLowerCase() === query.toLowerCase() ? (
      <span key={i} className="highlight">{part}</span>
    ) : (
      <span key={i}>{part}</span>
    )
  );
};

const BookDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const word = getQueryParam(location, "word");

  // Extract the book name from the full path after "/book/"
  const book = decodeURIComponent(location.pathname.replace("/book/", ""));

  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!book || !word) {
      setError("Missing book or word in URL.");
      setLoading(false);
      return;
    }

    fetch(`http://localhost:5000/api/book/${encodeURIComponent(book)}?word=${word}`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data.matches)) {
          setMatches(data.matches);
        } else {
          setMatches([]);
          setError("No matches found.");
        }
      })
      .catch(err => {
        console.error(err);
        setError("Failed to fetch book details.");
      })
      .finally(() => setLoading(false));
  }, [book, word]);

  return (
    <div className="all-books-container">
      <h1>Matches for "{word}" in {book}</h1>

      <button onClick={() => navigate(-1)} className="back-button">← Back</button>

      {loading && <div className="spinner"></div>}
      {error && <p className="error-message">{error}</p>}

      {!loading && matches.length > 0 && (
        <ul className="matches-list">
          {matches.map((match, index) => (
            <li key={index} className="match-entry">
              <p><strong>Offset:</strong> {match.offset}</p>
              <p><strong>Context:</strong> {highlight(match.context, word)}</p>
            </li>
          ))}
        </ul>
      )}

      {!loading && matches.length === 0 && !error && (
        <p>No matches found in this book.</p>
      )}
    </div>
  );
};

export default BookDetails;
