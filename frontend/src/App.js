import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import SearchResults from './pages/SearchResults';
import AllBooks from './pages/AllBooks';
import RecentSearches from './pages/RecentSearches';
import WordDetails from './pages/WordDetails';
import BookDetails from './pages/BookDetails';
import FullBook from './pages/FullBook';

import './App.css';

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/books" element={<AllBooks />} />
        <Route path="/recent" element={<RecentSearches />} />
        <Route path="/word/:word" element={<WordDetails />} />
        <Route path="/book/:title" element={<BookDetails />} />
        <Route path="/read/:title" element={<FullBook />} />
      </Routes>
    </Router>
  );
}

export default App;
