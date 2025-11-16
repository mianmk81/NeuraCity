import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import PageSkeleton from './components/PageSkeleton'

// Lazy load all page components for better performance
const Home = lazy(() => import('./pages/Home'))
const ReportIssue = lazy(() => import('./pages/ReportIssue'))
const PlanRoute = lazy(() => import('./pages/PlanRoute'))
const MoodMap = lazy(() => import('./pages/MoodMap'))
const Admin = lazy(() => import('./pages/Admin'))
const Analytics = lazy(() => import('./pages/Analytics'))
const CommunityImpact = lazy(() => import('./pages/CommunityImpact'))
const Sustainability = lazy(() => import('./pages/Sustainability'))
const Leaderboard = lazy(() => import('./pages/Leaderboard'))
const RiskIndex = lazy(() => import('./pages/RiskIndex'))

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
        <Suspense fallback={<PageSkeleton />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/report" element={<ReportIssue />} />
            <Route path="/route" element={<PlanRoute />} />
            <Route path="/mood" element={<MoodMap />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/risk" element={<RiskIndex />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/impact" element={<CommunityImpact />} />
            <Route path="/sustainability" element={<Sustainability />} />
          </Routes>
        </Suspense>
      </div>
    </div>
  )
}

export default App
