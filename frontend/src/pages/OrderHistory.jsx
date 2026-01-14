import { Search, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const OrderHistory = () => {
  const navigate = useNavigate();
  
  // Dữ liệu mẫu (Thực tế sẽ gọi hàm get_all_donhangban từ operation_7)
  const orders = [
    { id: 'DH00004', customer: 'Nguyễn Văn A', date: '12/01/2026', total: 1250000, status: 'Hoàn tất' },
    { id: 'DH00003', customer: 'Khách lẻ', date: '11/01/2026', total: 450000, status: 'Hoàn tất' },
    { id: 'DH00002', customer: 'Trần Thị B', date: '10/01/2026', total: 2100000, status: 'Đã hủy' },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Lịch sử hóa đơn</h2>
      
      {/* Thanh tìm kiếm */}
      <div className="relative">
        <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
          <Search size={18} />
        </span>
        <input
          type="text"
          placeholder="Tìm mã đơn, tên khách..."
          className="w-full pl-10 pr-4 py-3 bg-white border border-gray-100 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
        />
      </div>

      {/* Danh sách Order Cards */}
      <div className="space-y-3">
        {orders.map((order) => (
          <div 
            key={order.id} 
            onClick={() => navigate(`/order/${order.id}`)}
            className="bg-white p-4 rounded-2xl border border-gray-50 shadow-sm active:bg-gray-50 flex justify-between items-center"
          >
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${order.status === 'Hoàn tất' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                  {order.status}
                </span>
                <span className="text-xs text-gray-400">{order.date}</span>
              </div>
              <p className="font-bold text-gray-800">{order.id} - {order.customer}</p>
              <p className="text-primary font-bold">{order.total.toLocaleString()} ₫</p>
            </div>
            <ChevronRight size={20} className="text-gray-300" />
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderHistory;