import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { LandingPage } from './pages/LandingPage';
import { UploadPage } from './pages/UploadPage';
import { ProcessingPage } from './pages/ProcessingPage';
import { DashboardPage } from './pages/DashboardPage';
import { PaperMetadataPage } from './pages/PaperMetadataPage';
import { ReferencesPage } from './pages/ReferencesPage';
import { CitationsPage } from './pages/CitationsPage';
import { IssuesPage } from './pages/IssuesPage';
import { ReportPage } from './pages/ReportPage';
import { PaperListPage } from './pages/PaperListPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-[#0b0f19] text-slate-100 font-sans subtle-grid-bg">
        <Navbar />

        <div className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/papers" element={<PaperListPage />} />
            
            {/* Paper Dashboard Routes */}
            <Route path="/papers/:id" element={<DashboardPage />} />
            <Route path="/papers/:id/processing" element={<ProcessingPage />} />
            <Route path="/papers/:id/metadata" element={<PaperMetadataPage />} />
            <Route path="/papers/:id/references" element={<ReferencesPage />} />
            <Route path="/papers/:id/citations" element={<CitationsPage />} />
            <Route path="/papers/:id/issues" element={<IssuesPage />} />
            <Route path="/papers/:id/report" element={<ReportPage />} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>

        <Footer />
      </div>
    </Router>
  );
};

export default App;
