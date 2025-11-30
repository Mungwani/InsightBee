import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import MainPage from "./pages/Main";
import ReportPage from "./pages/Report";
import NewsDetailPage from "./pages/NewsDetail";
import MainLoading from "./pages/MainLoading";

function App() {
  return (
    <div className="overflow-x-hidden flex items-center justify-center w-screen h-100% bg-[#FFF7D7]">
      <div
        className="bg-white shadow-xl overflow-y-auto no-scrollbar"
        style={{ width: "430px" }}
      >
        <Router>
          <Routes>
            <Route path="/" element={<Navigate to="/main" />} />
            <Route path="/main" element={<MainPage />} />
            <Route path="/report/:companyName" element={<ReportPage />} />
            <Route path="/news/:id" element={<NewsDetailPage />} />
            <Route path="/main-loading" element={<MainLoading />} />
          </Routes>
        </Router>
      </div>
    </div>
  );
}

export default App;
