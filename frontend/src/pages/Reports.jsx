import { useState, useEffect } from 'react';
import { DollarSign, PieChart, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { apiService } from '../api'; // Đảm bảo đường dẫn import đúng với project của bạn

const Reports = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Gọi API lấy báo cáo
    const fetchReport = async () => {
      try {
        const res = await apiService.getFinancialReport('last_month');
        // Giả sử res.data.summary trả về object: { tong_doanh_thu, chi_phi_von, thue_phi, loi_nhuan, ... }
        setData(res.data.summary);
      } catch (err) {
        console.error("Lỗi khi tải báo cáo:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReport();
  }, []);

  // Hiển thị loading state hoặc lỗi nếu chưa có data
  if (isLoading) {
    return <div className="p-6 text-center text-gray-500 animate-pulse">Đang tải báo cáo tài chính...</div>;
  }

  if (!data) {
    return <div className="p-6 text-center text-red-500">Không thể tải dữ liệu báo cáo.</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-800">Báo cáo tài chính</h2>

      {/* --- Thẻ Lợi nhuận ròng (Main Card) --- */}
      <div className="bg-primary p-6 rounded-3xl text-white shadow-lg relative overflow-hidden transition-transform hover:scale-[1.01]">
        <div className="relative z-10">
          <p className="opacity-80 text-sm">Lợi nhuận ròng (Sau thuế 11.5%)</p>
          <h1 className="text-3xl font-black mt-1">
            {data.loi_nhuan?.toLocaleString('vi-VN')} ₫
          </h1>
          
          {/* Badge tăng trưởng - Có thể làm động nếu API trả về % tăng trưởng */}
          <div className="mt-4 flex items-center gap-2 bg-white/20 w-fit px-3 py-1 rounded-full text-xs backdrop-blur-sm">
            <ArrowUpRight size={14} /> 
            {/* Nếu API có trường tang_truong thì thay số 12 bằng data.tang_truong */}
            <span>+12% so với tháng trước</span> 
          </div>
        </div>
        {/* Decorative Icon */}
        <PieChart size={120} className="absolute -right-8 -bottom-8 opacity-10" />
      </div>

      {/* --- Chi tiết tài chính (List) --- */}
      <div className="bg-white rounded-3xl p-4 shadow-sm space-y-4">
        
        {/* Dòng 1: Tổng doanh thu */}
        <div className="flex justify-between items-center border-b border-gray-100 pb-3">
          <div className="flex items-center gap-3">
            <div className="bg-blue-50 p-2 rounded-xl text-blue-600">
              <DollarSign size={20}/>
            </div>
            <span className="text-sm font-medium text-gray-600">Tổng doanh thu</span>
          </div>
          <span className="font-bold text-gray-800">
            {data.tong_doanh_thu?.toLocaleString('vi-VN')}
          </span>
        </div>

        {/* Dòng 2: Giá vốn (COGS) */}
        <div className="flex justify-between items-center border-b border-gray-100 pb-3">
          <div className="flex items-center gap-3">
            <div className="bg-orange-50 p-2 rounded-xl text-orange-600">
              <ArrowDownRight size={20}/>
            </div>
            <span className="text-sm font-medium text-gray-600">Giá vốn (COGS)</span>
          </div>
          <span className="font-bold text-orange-600">
            {/* Lưu ý: Kiểm tra key API trả về là 'chi_phi_von' hay 'gia_von' */}
            {data.chi_phi_von?.toLocaleString('vi-VN') || 0}
          </span>
        </div>

        {/* Dòng 3: Thuế & Phí vận hành */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-red-50 p-2 rounded-xl text-red-600">
              <ArrowDownRight size={20}/>
            </div>
            <span className="text-sm font-medium text-gray-600">Thuế & Phí vận hành</span>
          </div>
          <span className="font-bold text-red-600">
            {/* Lưu ý: Kiểm tra key API trả về là 'thue_phi' hay tên khác */}
            {data.thue_phi?.toLocaleString('vi-VN') || 0}
          </span>
        </div>

      </div>
    </div>
  );
};

export default Reports;