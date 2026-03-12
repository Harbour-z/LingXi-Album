import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { UnifiedHomePage } from './pages/UnifiedHomePage';
import { GalleryPage } from './pages/GalleryPage';
import { UploadPage } from './pages/UploadPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { ConversationListPage } from './pages/ConversationListPage';
import { ChatPage } from './pages/ChatPage';
import MainLayout from './components/layout/MainLayout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<UnifiedHomePage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="conversations" element={<ConversationListPage />} />
          <Route path="gallery" element={<GalleryPage />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="architecture" element={<ArchitecturePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
