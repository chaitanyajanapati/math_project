import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { BarChart3, Target, Gauge } from 'lucide-react';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';

// Lazy load pages for better performance
const QuestionGenerator = lazy(() => import("./pages/QuestionGenerator.tsx"));
const Dashboard = lazy(() => import("./pages/Dashboard.tsx"));
const QuestionQualityDashboard = lazy(() => import("./pages/QuestionQualityDashboard.tsx"));

// Loading component
function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

function Navigation() {
  const location = useLocation();
  
  return (
    <nav className="bg-white shadow-md border-b-2 border-blue-200" aria-label="Main navigation">
      <div className="max-w-7xl mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2" role="banner">
            <Target className="w-8 h-8 text-blue-600" aria-hidden="true" />
            <span className="text-2xl font-bold text-blue-700">Math AI</span>
          </div>
          <div className="flex gap-4" role="navigation" aria-label="Primary">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                location.pathname === '/'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
              aria-label="Go to practice page"
              aria-current={location.pathname === '/' ? 'page' : undefined}
            >
              <Target className="w-5 h-5" aria-hidden="true" />
              Practice
            </Link>
            <Link
              to="/dashboard"
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                location.pathname === '/dashboard'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
              aria-label="Go to dashboard page"
              aria-current={location.pathname === '/dashboard' ? 'page' : undefined}
            >
              <BarChart3 className="w-5 h-5" aria-hidden="true" />
              Dashboard
            </Link>
            <Link
              to="/quality"
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                location.pathname === '/quality'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
              aria-label="Go to quality dashboard page"
              aria-current={location.pathname === '/quality' ? 'page' : undefined}
            >
              <Gauge className="w-5 h-5" aria-hidden="true" />
              Quality
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Navigation />
            <Suspense fallback={<LoadingFallback />}>
              <Routes>
                <Route path="/" element={<QuestionGenerator />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/quality" element={<QuestionQualityDashboard />} />
              </Routes>
            </Suspense>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
