import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CreateOrder from './pages/CreateOrder';
import OrderHistory from './pages/OrderHistory';
import OrderDetail from './pages/OrderDetail';
import BottomNav from './components/BottomNav';
import Reports from './pages/Reports'; // Đã import

function App() {
  return (
    <Router>
      {/* Khung giả lập Mobile: Căn giữa màn hình, giới hạn chiều rộng  */}
      <div className="flex justify-center bg-gray-100 min-h-screen">
        <div className="w-full max-w-md bg-white min-h-screen relative shadow-2xl flex flex-col">
          
          {/* Nội dung chính: pb-24 để không bị thanh Nav che khuất  */}
          <main className="flex-1 overflow-y-auto pb-24 p-4">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/create" element={<CreateOrder />} />
              <Route path="/history" element={<OrderHistory />} />
              <Route path="/order/:id" element={<OrderDetail />} />
              {/* BỔ SUNG DÒNG NÀY ĐỂ KÍCH HOẠT TRANG BÁO CÁO */}
              <Route path="/reports" element={<Reports />} /> 
            </Routes>
          </main>

          {/* Thanh điều hướng cố định dưới cùng với nút (+) Royal Blue [cite: 15, 16] */}
          <BottomNav />
          
        </div>
      </div>
    </Router>
  );
}

export default App;