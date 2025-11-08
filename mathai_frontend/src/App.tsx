import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import QuestionGenerator from "./pages/QuestionGenerator.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import { BarChart3, Target } from 'lucide-react';

function Navigation() {
  const location = useLocation();
  
  return (
    <nav className="bg-white shadow-md border-b-2 border-blue-200">
      <div className="max-w-7xl mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-blue-700">Math AI</span>
          </div>
          <div className="flex gap-4">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                location.pathname === '/'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              <Target className="w-5 h-5" />
              Practice
            </Link>
            <Link
              to="/dashboard"
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                location.pathname === '/dashboard'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-blue-50'
              }`}
            >
              <BarChart3 className="w-5 h-5" />
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          <Route path="/" element={<QuestionGenerator />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
