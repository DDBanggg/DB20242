import { ArrowLeft, Printer, Share2 } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

const OrderDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  return (
    <div className="space-y-4 pb-10">
      <button onClick={() => navigate(-1)} className="flex items-center text-gray-500 gap-1">
        <ArrowLeft size={20} /> <span className="text-sm">Quay lại</span>
      </button>

      <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 relative overflow-hidden">
        {/* Giả lập hiệu ứng răng cưa của hóa đơn ở dưới */}
        <div className="text-center border-b border-dashed pb-4 mb-4">
          <h1 className="font-black text-xl text-primary">OMNIPOCKET</h1>
          <p className="text-[10px] text-gray-400">Mã đơn: {id}</p>
          <p className="text-[10px] text-gray-400">Ngày: 12/01/2026 14:30</p>
        </div>

        {/* Danh sách sản phẩm */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-xs font-bold text-gray-400 uppercase">
            <span>Sản phẩm</span>
            <span>T.Tiền</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>2x Sữa tươi Vinamilk</span>
            <span className="font-medium">50,000</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>1x Bánh mì Oishi</span>
            <span className="font-medium">5,000</span>
          </div>
        </div>

        {/* Phần tính thuế & Tổng tiền theo nghiệp vụ bạn yêu cầu */}
        <div className="border-t pt-4 space-y-2 text-sm">
          <div className="flex justify-between text-gray-500">
            <span>Tiền hàng</span>
            <span>55,000 ₫</span>
          </div>
          <div className="flex justify-between text-gray-500">
            <span>Thuế VAT (10%)</span>
            <span>5,500 ₫</span>
          </div>
          <div className="flex justify-between text-gray-500">
            <span>Thuế HKD (1.5%)</span>
            <span>825 ₫</span>
          </div>
          <div className="flex justify-between font-black text-lg text-gray-800 pt-2">
            <span>TỔNG CỘNG</span>
            <span className="text-primary">61,325 ₫</span>
          </div>
        </div>
      </div>

      {/* Nút thao tác nhanh */}
      <div className="grid grid-cols-2 gap-3">
        <button className="flex items-center justify-center gap-2 bg-gray-100 text-gray-600 py-3 rounded-2xl font-bold">
          <Share2 size={18} /> Chia sẻ
        </button>
        <button className="flex items-center justify-center gap-2 bg-primary text-white py-3 rounded-2xl font-bold">
          <Printer size={18} /> In hóa đơn
        </button>
      </div>
    </div>
  );
};

export default OrderDetail;