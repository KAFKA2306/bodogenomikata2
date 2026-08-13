import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { HomePage } from './pages/HomePage';
import { PlayModePage } from './pages/PlayModePage';
import { ComparisonPage } from './pages/ComparisonPage';
import { GameDetailPage } from './pages/GameDetailPage';
import { PalworldCardSearchPage } from './pages/PalworldCardSearchPage';
import { ProductShell } from './components/ProductShell';
import { KafkaSignalRuntime } from './components/KafkaSignalRuntime';
import './index.css';
import './workflow.css';
import './kafka-signal.css';
import './detail-layout.css';

function App() {
  return (
    <HelmetProvider>
      <BrowserRouter>
        <KafkaSignalRuntime />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/play" element={<PlayModePage intent="play" />} />
          <Route path="/install" element={<PlayModePage intent="install" />} />
          <Route path="/research" element={<ProductShell><ComparisonPage /></ProductShell>} />
          <Route path="/cards/palworld" element={<ProductShell><PalworldCardSearchPage /></ProductShell>} />
          <Route path="/game/:slug" element={<ProductShell><GameDetailPage /></ProductShell>} />
        </Routes>
      </BrowserRouter>
    </HelmetProvider>
  );
}

export default App;
