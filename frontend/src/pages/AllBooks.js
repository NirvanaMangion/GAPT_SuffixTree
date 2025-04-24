import React, { useEffect, useState } from 'react';
import './AllBooks.css';

const AllBooks = () => {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/books')
      .then(res => res.json())
      .then(data => {
        const formatted = data.map(filename => ({
          title: filename.replace('.txt', ''),
          author: 'Unknown'
        }));
        setBooks(formatted);
      })
      .catch(err => {
        console.error('Failed to fetch books:', err);
      });
  }, []);

  return (
    <div className="all-books-container">
      <h1>All Books</h1>
      <div className="books-list">
        {books.length > 0 ? (
          books.map((book, index) => (
            <div key={index} className="book-card">
              <span className="book-icon">📚</span>
              <div className="book-details">
                <h3 className="book-title">{book.title}</h3>
                <p className="book-author">{book.author}</p>
              </div>
            </div>
          ))
        ) : (
          <p>No books found.</p>
        )}
      </div>
    </div>
  );
};

export default AllBooks;
