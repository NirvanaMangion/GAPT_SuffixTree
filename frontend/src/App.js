import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import SearchResults from './pages/SearchResults';
import AllBooks from './pages/AllBooks';
import RecentSearches from './pages/RecentSearches';
import './App.css';

function App() {
  return (
    <Router>
      <Header />  {/* The Header component with the Sidebar */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/books" element={<AllBooks />} />  {/* Correct route for AllBooks */}
        <Route path="/recent" element={<RecentSearches />} />  {/* Correct route for RecentSearches */}
      </Routes>
    </Router>
  );
}

export default App;
