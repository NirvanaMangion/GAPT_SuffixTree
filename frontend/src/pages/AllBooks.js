// AllBooks.js
import React from 'react';
import './AllBooks.css';  // Import the updated styles for AllBooks

const AllBooks = () => {
  const books = [
    { title: 'Book Title 1', author: 'Author Name' },
    { title: 'Book Title 2', author: 'Author Name' },
    { title: 'Book Title 3', author: 'Author Name' }
  ];

  return (
    <div className="all-books-container">
      <h1>All Books</h1>
      <div className="books-list">
        {books.map((book, index) => (
          <div key={index} className="book-card">
            <span className="book-icon">📚</span> {/* Book icon */}
            <div className="book-details">
              <h3 className="book-title">{book.title}</h3>
              <p className="book-author">{book.author}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AllBooks;
