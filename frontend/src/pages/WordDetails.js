import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import './AllBooks.css';

const WordDetails = () => {
  const { word } = useParams();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/word/${word}`)
      .then(res => res.json())
      .then(data => setBooks(data.books || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [word]);

  return (
    <div className="all-books-container">
      <h1>Books containing "{word}"</h1>
      {loading ? (
        <div className="spinner"></div>
      ) : books.length > 0 ? (
        <div className="books-list">
          {books.map((book, index) => (
            <div key={index} className="book-card">
              <span className="book-icon">📘</span>
              <div className="book-details">
                <h3 className="book-title">
                  <a href={`/book/${book.title}?word=${word}`} className="clickable-word">
                    {book.title}
                  </a>
                </h3>
                <p className="book-author">Frequency: {book.frequency}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>No books found with this word.</p>
      )}
    </div>
  );
};

export default WordDetails;
