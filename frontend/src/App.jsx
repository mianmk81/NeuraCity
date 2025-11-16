import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import ReportIssue from './pages/ReportIssue'
import PlanRoute from './pages/PlanRoute'
import MoodMap from './pages/MoodMap'
import Admin from './pages/Admin'
import Analytics from './pages/Analytics'
import ContractorPortal from './pages/ContractorPortal'
import MyIssues from './pages/MyIssues'

function App() {
  return (
    <div className="min-h-screen relative">
      {/* Animated Background Particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-screen opacity-20 blur-3xl animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full mix-blend-screen opacity-20 blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-1/4 left-1/2 w-96 h-96 bg-cyan-500 rounded-full mix-blend-screen opacity-20 blur-3xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>
      
      <div className="relative z-10">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report" element={<ReportIssue />} />
          <Route path="/route" element={<PlanRoute />} />
          <Route path="/mood" element={<MoodMap />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/contractor" element={<ContractorPortal />} />
          <Route path="/my-issues" element={<MyIssues />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
