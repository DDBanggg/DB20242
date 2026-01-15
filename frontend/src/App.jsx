import { BrowserRouter as Router, Routes, Route, useLocation} from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CreateOrder from './pages/CreateOrder';
import OrderHistory from './pages/OrderHistory';
import OrderDetail from './pages/OrderDetail';
import BottomNav from './components/BottomNav';
import Reports from './pages/Reports'; // Đã import
import CategoryManager from './pages/CategoryManager';
import InventoryStats from './pages/InventoryStats';

function AppContent() {
  const location = useLocation();
  // Kiểm tra xem có đang ở trang tạo đơn không
  const isCreateOrderPage = location.pathname === '/create';

  return (
    <div className="flex justify-center bg-gray-100 min-h-screen">
      <div className="w-full max-w-md bg-white min-h-screen relative shadow-2xl flex flex-col">
        {/* pb-24 chỉ áp dụng khi có BottomNav */}
        <main className={`flex-1 overflow-y-auto p-4 ${isCreateOrderPage ? 'pb-0' : 'pb-24'}`}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/categories" element={<CategoryManager />} />
            <Route path="/inventory" element={<InventoryStats />} />
            <Route path="/create" element={<CreateOrder />} />
            <Route path="/history" element={<OrderHistory />} />
            <Route path="/order/:id" element={<OrderDetail />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>

        {/* CHỈ HIỆN BottomNav KHI KHÔNG PHẢI TRANG TẠO ĐƠN */}
        {!isCreateOrderPage && <BottomNav />}
      </div>
    </div>
  );
}

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
              <Route path="/categories" element={<CategoryManager />} />
              <Route path="/inventory" element={<InventoryStats />} />
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