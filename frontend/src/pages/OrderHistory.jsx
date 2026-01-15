import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ChevronRight, Filter, Calendar, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { apiService } from '../api';

const OrderHistory = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // DỮ LIỆU FAKE ĐỂ LÀM ĐẸP TRANG LỊCH SỬ (DÀI VÀ ĐA DẠNG)
  const fakeOrders = [
    { id: 1025, time: '10:30 - Hôm nay', total: 450000, status: 'Hoàn tất', customer: 'Nguyễn Văn A' },
    { id: 1024, time: '09:15 - Hôm nay', total: 1200000, status: 'Hoàn tất', customer: 'Khách lẻ' },
    { id: 1023, time: '18:45 - Hôm qua', total: 320000, status: 'Đang giao', customer: 'Trần Thị B' },
    { id: 1022, time: '16:20 - Hôm qua', total: 2100000, status: 'Hoàn tất', customer: 'Lê Văn C' },
    { id: 1021, time: '14:10 - Hôm qua', total: 550000, status: 'Đã hủy', customer: 'Khách lẻ' },
    { id: 1020, time: '08:05 - Hôm qua', total: 890000, status: 'Hoàn tất', customer: 'Phạm Minh M' },
    { id: 1019, time: '21:30 - 2 ngày trước', total: 450000, status: 'Hoàn tất', customer: 'Khách lẻ' },
    { id: 1018, time: '15:20 - 2 ngày trước', total: 1500000, status: 'Hoàn tất', customer: 'Hoàng Anh' },
    { id: 1017, time: '10:00 - 2 ngày trước', total: 95000, status: 'Hoàn tất', customer: 'Khách lẻ' },
    { id: 1016, time: '09:45 - 3 ngày trước', total: 2500000, status: 'Hoàn tất', customer: 'Ngô Gia B' },
    { id: 1015, time: '08:20 - 3 ngày trước', total: 120000, status: 'Đã hủy', customer: 'Khách lẻ' },
    { id: 1014, time: '17:50 - 4 ngày trước', total: 780000, status: 'Hoàn tất', customer: 'Đặng Thu T' },
  ];

  useEffect(() => {
    // Để demo dùng số liệu fake, bạn có thể uncomment để lấy dữ liệu thật sau
    setOrders(fakeOrders);
    // fetchRealOrders();
  }, []);

  const getStatusStyle = (status) => {
    switch (status) {
      case 'Hoàn tất': return 'bg-green-100 text-green-700';
      case 'Đang giao': return 'bg-blue-100 text-blue-700';
      case 'Đã hủy': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const filteredOrders = orders.filter(o => 
    o.id.toString().includes(searchTerm) || o.customer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* HEADER TỐI GIẢN */}
      <div className="flex justify-between items-center mb-6 px-1">
        <h1 className="text-2xl font-black text-gray-900">Lịch sử đơn</h1>
        <div className="p-2 bg-white rounded-xl shadow-sm border border-gray-100">
          <Filter size={20} className="text-primary" />
        </div>
      </div>

      {/* THANH TÌM KIẾM HÓA ĐƠN */}
      <div className="relative mb-6">
        <Search className="absolute left-4 top-3.5 text-gray-400" size={18} />
        <input 
          className="w-full bg-white py-3.5 pl-12 pr-4 rounded-2xl shadow-sm border border-gray-50 outline-none focus:ring-2 focus:ring-primary/20 transition"
          placeholder="Tìm mã đơn hoặc tên khách..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* DANH SÁCH ĐƠN HÀNG (CARD BUBBLE STYLE) */}
      <div className="space-y-4 pb-10">
        {filteredOrders.map((order) => (
          <div 
            key={order.id}
            onClick={() => navigate(`/order/${order.id}`)}
            className="bg-white p-5 rounded-[24px] shadow-sm border border-gray-50 flex justify-between items-center active:scale-[0.98] transition cursor-pointer"
          >
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-black bg-gray-900 text-white px-2 py-0.5 rounded-lg uppercase">
                  #{order.id}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-lg ${getStatusStyle(order.status)}`}>
                  {order.status}
                </span>
              </div>
              <div>
                <h3 className="font-bold text-gray-800">{order.customer}</h3>
                <div className="flex items-center gap-1 text-[10px] text-gray-400 font-medium">
                  <Clock size={12} /> {order.time}
                </div>
              </div>
            </div>

            <div className="text-right flex items-center gap-3">
              <div>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-tighter">Tổng tiền</p>
                <p className="text-lg font-black text-primary">{order.total.toLocaleString()}đ</p>
              </div>
              <ChevronRight size={20} className="text-gray-300" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderHistory;