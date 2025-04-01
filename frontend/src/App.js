import React from 'react';
import { Routes, Route } from 'react-router-dom';

const Home = () => (
  <div style={{ padding: '20px', textAlign: 'center' }}>
    <h1>OCR Application</h1>
    <p>Welcome to the AI Agent OCR Application!</p>
    <p>This is a placeholder home page. The full UI components are still loading.</p>
  </div>
);

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </div>
  );
}

export default App;
