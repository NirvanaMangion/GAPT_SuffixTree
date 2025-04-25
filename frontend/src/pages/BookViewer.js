import React, { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import './AllBooks.css';
import './BookViewer.css';

const highlightAll = (text, word) => {
  if (!word) return text;
  const regex = new RegExp(`\\b(${word})\\b`, 'gi');
  const parts = text.split(regex);
  return parts.map((part, i) =>
    regex.test(part) ? <mark key={i}>{part}</mark> : part
  );
};

const BookViewer = () => {
  const { title } = useParams();
  const location = useLocation();
  const query = new URLSearchParams(location.search).get("word");

  const [bookText, setBookText] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`http://localhost:5000/api/book/full/${encodeURIComponent(title)}?word=${query}`)
      .then(res => res.json())
      .then(data => {
        if (data.text) {
          setBookText(data.text);
        } else {
          setError("Book not found.");
        }
      })
      .catch(err => {
        console.error(err);
        setError("Failed to load book.");
      });
  }, [title, query]);

  return (
    <div className="all-books-container">
      <h1>{title}</h1>
      {error && <p className="error-message">{error}</p>}
      {!error && (
        <div className="book-text-viewer">
          {highlightAll(bookText, query)}
        </div>
      )}
    </div>
  );
};

export default BookViewer;
