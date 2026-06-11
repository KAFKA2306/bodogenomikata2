import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ComparisonPage } from './pages/ComparisonPage';
import { GameDetailPage } from "./pages/GameDetailPage";

function App() {
  return (<Router><Routes><Route path='/' element={<ComparisonPage />} /><Route path="/game/:slug" element={<GameDetailPage />} /></Routes></Router>);
}

export default App;
