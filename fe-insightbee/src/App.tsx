import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import MainPage from "./pages/Main"
import ReportPage from "./pages/Report"
import NewsDetailPage from "./pages/NewsDetail"

function App() {
  return (
    <div className="flex items-center justify-center w-screen h-screen bg-[#FFF7D7]">
      {/* iPhone 14 Pro 화면 비율 고정 */}
      <div
        className="bg-white shadow-xl overflow-hidden rounded-xl"
        style={{ width: "430px", height: "932px" }}
      >
        <Router>
          <Routes>
            <Route path="/" element={<Navigate to="/main" />} />
            <Route path="/main" element={<MainPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/report/keyword/news-detail" element={<NewsDetailPage />} />
          </Routes>
        </Router>
      </div>
    </div>
  )
}

export default App
