import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Search, Plus, Minus, Trash2, CheckCircle, Download, Eye, ShoppingCart } from 'lucide-react';
import html2canvas from 'html2canvas';
import { apiService } from '../api';

const CreateOrder = () => {
  const navigate = useNavigate();
  
  // --- STATE QUẢN LÝ DỮ LIỆU ---
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [cart, setCart] = useState([]);
  
  // --- STATE QUẢN LÝ GIAO DIỆN (MODAL) ---
  const [selectedProduct, setSelectedProduct] = useState(null); // Modal chọn số lượng
  const [tempQty, setTempQty] = useState(1);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);  // Modal thanh toán
  const [isSubmitting, setIsSubmitting] = useState(false);      // Loading khi gọi API
  const [invoiceImg, setInvoiceImg] = useState(null);           // Chứa dữ liệu ảnh hóa đơn

  // 1. LẤY DỮ LIỆU SẢN PHẨM TỪ API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await apiService.getPOSProducts(searchTerm);
        setProducts(res.data.data || []);
      } catch (err) {
        console.error("Lỗi tải sản phẩm:", err);
      }
    };
    const timeoutId = setTimeout(() => fetchProducts(), 300);
    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  // 2. LOGIC GIỎ HÀNG
  const openQuantityModal = (product) => {
    const existing = cart.find(i => i.id === product.id);
    setSelectedProduct(product);
    setTempQty(existing ? existing.quantity : 1);
  };

  const confirmAddtoCart = () => {
    setCart(prev => {
      const filtered = prev.filter(i => i.id !== selectedProduct.id);
      return [...filtered, { ...selectedProduct, quantity: tempQty }];
    });
    setSelectedProduct(null);
  };

  const removeFromCart = (id) => {
    setCart(prev => prev.filter(i => i.id !== id));
  };

  const updateCartItemQty = (id, delta) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQty = Math.max(1, item.quantity + delta);
        if (newQty > item.so_luong_ton_kho) {
            alert("Đã vượt quá số lượng tồn kho!");
            return item;
        }
        return { ...item, quantity: newQty };
      }
      return item;
    }));
  };

  // 3. TÍNH TOÁN TÀI CHÍNH (ĐÃ BỎ THUẾ HKD)
  const subtotal = cart.reduce((sum, i) => sum + (i.gia_ban_hien_tai * i.quantity), 0);
  const vat = subtotal * 0.10; // Chỉ giữ lại VAT
  const total = subtotal + vat; // Tổng = Tiền hàng + VAT

  // 4. LOGIC XỬ LÝ ẢNH HÓA ĐƠN
  const handlePreviewInvoice = () => {
    const invoiceElement = document.getElementById('invoice-capture');
    if (!invoiceElement) return;

    html2canvas(invoiceElement, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff'
    }).then((canvas) => {
      const imgData = canvas.toDataURL('image/png');
      setInvoiceImg(imgData);
    }).catch(err => console.error("Lỗi chụp hóa đơn:", err));
  };

  const downloadImage = () => {
    if (!invoiceImg) return;
    const link = document.createElement('a');
    link.download = `HoaDon_${Date.now()}.png`;
    link.href = invoiceImg;
    link.click();
  };

  // 5. GỬI ĐƠN HÀNG LÊN SERVER
  const handleFinalPayment = async () => {
    if (cart.length === 0) return;
    setIsSubmitting(true);
    try {
      const orderRes = await apiService.createOrder({
        id_nhan_vien: 1,
        id_khach_hang: 1,
        dia_chi_giao_hang: "Tại quầy",
        trang_thai_don_hang: 'Hoàn tất',
        trang_thai_thanh_toan: 'Đã thanh toán'
      });
      
      const orderId = orderRes.data.id_don_hang;
      
      const detailPromises = cart.map(item => apiService.addItemToOrder({
          id_don_hang_ban: orderId,
          id_san_pham: item.id,
          so_luong: item.quantity,
          gia_ban_niem_yet_don_vi: item.gia_ban_hien_tai,
          giam_gia: 0
      }));
      
      await Promise.all(detailPromises);

      alert("Thanh toán thành công!");
      navigate('/');
    } catch (err) {
      alert("Lỗi thanh toán: " + (err.response?.data?.detail || err.message));
    } finally { 
      setIsSubmitting(false); 
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white relative overflow-hidden max-w-md mx-auto border-x border-gray-200 shadow-2xl font-sans">
      
      {/* HEADER */}
      <header className="p-4 flex items-center border-b bg-white z-10">
        <button onClick={() => navigate('/')} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <X size={24} className="text-gray-600" />
        </button>
        <h1 className="flex-1 text-center font-bold text-lg text-gray-800">Tạo đơn hàng</h1>
        <div className="w-10"></div>
      </header>

      {/* THANH TÌM KIẾM */}
      <div className="p-4 bg-white z-10">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input 
            className="w-full bg-gray-100 py-3 pl-10 pr-4 rounded-xl outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
            placeholder="Tìm món (VD: Cà phê, Bánh...)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* DANH SÁCH SẢN PHẨM */}
      <div className="flex-1 overflow-y-auto px-4 pb-20">
        {products.length === 0 ? (
            <div className="text-center text-gray-400 mt-10">Không tìm thấy sản phẩm nào</div>
        ) : (
            products.map(p => (
            <div key={p.id} className="flex items-center justify-between py-4 border-b border-gray-100 last:border-0">
                <div className="flex-1 pr-4">
                <h3 className="font-semibold text-gray-800 text-base">{p.ten_san_pham}</h3>
                <div className="flex items-center gap-2 mt-1">
                    <span className="text-blue-600 font-bold">{p.gia_ban_hien_tai.toLocaleString()}đ</span>
                    <span className="text-gray-300">|</span>
                    <span className={`text-xs ${p.so_luong_ton_kho < 10 ? 'text-red-500 font-bold' : 'text-gray-400'}`}>
                    Kho: {p.so_luong_ton_kho} {p.don_vi_tinh}
                    </span>
                </div>
                </div>
                <button 
                onClick={() => openQuantityModal(p)}
                className="bg-blue-600 text-white p-2.5 rounded-xl shadow-md shadow-blue-200 active:scale-95 transition-all hover:bg-blue-700"
                >
                <Plus size={20} />
                </button>
            </div>
            ))
        )}
      </div>

      {/* FOOTER: THANH TRẠNG THÁI GIỎ HÀNG */}
      <footer className="absolute bottom-0 left-0 right-0 p-4 border-t bg-white shadow-[0_-4px_20px_rgba(0,0,0,0.05)] flex items-center justify-between z-20">
        <div>
          <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">Tạm tính ({cart.length} món)</p>
          <p className="text-xl font-black text-gray-900">{subtotal.toLocaleString()}đ</p>
        </div>
        <button 
          onClick={() => setIsCheckoutOpen(true)}
          disabled={cart.length === 0}
          className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold disabled:bg-gray-300 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30 flex items-center gap-2 hover:bg-blue-700 transition-colors"
        >
          <ShoppingCart size={18} />
          Thanh toán
        </button>
      </footer>

      {/* MODAL 1: CHỌN SỐ LƯỢNG */}
      {selectedProduct && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6 z-50 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-xs rounded-3xl p-6 shadow-2xl transform transition-all scale-100">
            <h2 className="text-center font-bold text-gray-800 text-lg mb-1">{selectedProduct.ten_san_pham}</h2>
            <p className="text-center text-blue-600 font-bold text-xl mb-6">{(selectedProduct.gia_ban_hien_tai * tempQty).toLocaleString()}đ</p>
            
            <div className="flex items-center justify-center gap-6 mb-8">
              <button 
                onClick={() => setTempQty(Math.max(1, tempQty - 1))}
                className="w-14 h-14 rounded-full border-2 border-gray-100 flex items-center justify-center text-gray-600 active:bg-gray-50 transition-colors"
              >
                <Minus size={24} />
              </button>
              <span className="text-4xl font-black w-16 text-center text-gray-800">{tempQty}</span>
              <button 
                onClick={() => tempQty < selectedProduct.so_luong_ton_kho && setTempQty(tempQty + 1)}
                className="w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-lg shadow-blue-200 active:bg-blue-700 transition-all"
              >
                <Plus size={24} />
              </button>
            </div>
            
            <p className="text-center text-xs text-gray-400 mb-6 bg-gray-50 py-2 rounded-lg">
                Tồn kho khả dụng: <span className="font-bold text-gray-600">{selectedProduct.so_luong_ton_kho}</span>
            </p>

            <div className="flex gap-3">
              <button onClick={() => setSelectedProduct(null)} className="flex-1 py-3 text-gray-500 font-bold hover:bg-gray-50 rounded-xl transition-colors">Hủy</button>
              <button onClick={confirmAddtoCart} className="flex-1 py-3 bg-blue-600 text-white rounded-xl font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition-colors">Xác nhận</button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: MÀN HÌNH THANH TOÁN (CHECKOUT) */}
      {isCheckoutOpen && (
        <div className="absolute inset-0 bg-white z-[60] flex flex-col animate-in slide-in-from-bottom duration-300">
          <header className="p-4 flex items-center border-b shadow-sm z-20 bg-white">
            <button onClick={() => setIsCheckoutOpen(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors"><X size={24} /></button>
            <h1 className="flex-1 text-center font-bold text-lg">Xác nhận đơn hàng</h1>
            <div className="w-10"></div>
          </header>

          <div className="flex-1 overflow-y-auto bg-gray-50 scrollbar-hide">
            {/* --- VÙNG ID ĐỂ CHỤP ẢNH --- */}
            <div id="invoice-capture" className="bg-white p-6 min-h-full pb-10">
                {/* Header Hóa đơn */}
                <div className="text-center mb-8 pb-6 border-b-2 border-dashed border-gray-200">
                    <div className="flex justify-center mb-2">
                        <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center text-white font-black text-xl">P</div>
                    </div>
                    <h2 className="text-2xl font-black uppercase tracking-tight text-gray-800">Hóa Đơn Bán Lẻ</h2>
                    <p className="text-sm text-gray-500 mt-1">Ngày: {new Date().toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                    <p className="text-sm text-gray-400">Mã đơn: #{Math.floor(Math.random() * 10000)}</p>
                </div>

                {/* List món ăn */}
                <div className="space-y-4">
                {cart.map(item => (
                    <div key={item.id} className="flex justify-between items-start">
                        <div className="flex-1">
                            <p className="font-bold text-gray-800">{item.ten_san_pham}</p>
                            <p className="text-sm text-gray-500 mt-1">
                                <span className="font-medium text-gray-900">{item.quantity}</span> x {item.gia_ban_hien_tai.toLocaleString()}đ
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="font-bold text-gray-800">{(item.gia_ban_hien_tai * item.quantity).toLocaleString()}đ</p>
                            
                            <div data-html2canvas-ignore="true" className="flex items-center justify-end gap-1 mt-2 bg-gray-100 rounded-lg p-1 w-fit ml-auto">
                                <button onClick={() => item.quantity === 1 ? removeFromCart(item.id) : updateCartItemQty(item.id, -1)} className="p-1 hover:bg-white rounded text-gray-600 transition-colors">
                                    {item.quantity === 1 ? <Trash2 size={14} className="text-red-500"/> : <Minus size={14}/>}
                                </button>
                                <button onClick={() => updateCartItemQty(item.id, 1)} className="p-1 hover:bg-white rounded text-gray-600 transition-colors"><Plus size={14}/></button>
                            </div>
                        </div>
                    </div>
                ))}
                </div>

                {/* Phần tổng tiền (Đã xóa HKD) */}
                <div className="mt-8 pt-6 border-t-2 border-dashed border-gray-200 space-y-3">
                    <div className="flex justify-between text-gray-600"><span>Thành tiền</span><span>{subtotal.toLocaleString()}đ</span></div>
                    <div className="flex justify-between text-gray-600"><span>VAT (10%)</span><span>{vat.toLocaleString()}đ</span></div>
                    {/* Đã xóa dòng thuế HKD ở đây */}
                    
                    <div className="flex justify-between items-center pt-4 mt-2 border-t border-gray-100">
                        <span className="font-bold text-lg text-gray-800">TỔNG CỘNG</span>
                        <span className="text-2xl font-black text-blue-600">{total.toLocaleString()}đ</span>
                    </div>
                </div>

                <div className="text-center mt-10 text-xs text-gray-400 italic font-medium">
                    Cảm ơn quý khách đã ủng hộ! <br/> Hẹn gặp lại.
                </div>
            </div>
            {/* --- KẾT THÚC VÙNG CHỤP --- */}
          </div>

          {/* Footer Hành động */}
          <div className="p-4 border-t bg-white shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-20 space-y-3">
            <button 
                onClick={handlePreviewInvoice}
                className="w-full border-2 border-gray-200 text-gray-600 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-gray-50 hover:border-gray-300 transition-all"
            >
                <Eye size={20} /> Xem & Xuất hóa đơn
            </button>
            
            <button 
              onClick={handleFinalPayment}
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-4 rounded-xl font-black flex items-center justify-center gap-2 shadow-lg shadow-blue-500/30 hover:bg-blue-700 transition-all disabled:bg-gray-400"
            >
              {isSubmitting ? (
                 <span className="animate-pulse">ĐANG XỬ LÝ...</span>
              ) : (
                 <><CheckCircle size={20}/> XÁC NHẬN THANH TOÁN</>
              )}
            </button>
          </div>
        </div>
      )}

      {/* MODAL 3: PREVIEW ẢNH HÓA ĐƠN */}
      {invoiceImg && (
        <div className="absolute inset-0 z-[70] bg-black/95 flex flex-col animate-in fade-in duration-300">
            <div className="p-4 flex justify-between items-center text-white/90 border-b border-white/10">
                <h3 className="font-bold text-lg">Hóa đơn điện tử</h3>
                <button onClick={() => setInvoiceImg(null)} className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"><X size={20}/></button>
            </div>

            <div className="flex-1 overflow-auto p-6 flex items-start justify-center">
                <img src={invoiceImg} alt="Hóa đơn preview" className="w-full max-w-sm shadow-2xl rounded-sm ring-1 ring-white/20" />
            </div>

            <div className="p-6 bg-white rounded-t-3xl shadow-2xl">
                <button 
                    onClick={downloadImage}
                    className="w-full bg-blue-600 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-blue-500/30 mb-3 hover:bg-blue-700 transition-all"
                >
                    <Download size={20} /> Lưu ảnh về máy
                </button>
                <button 
                    onClick={() => setInvoiceImg(null)}
                    className="w-full py-3 text-gray-500 font-bold hover:bg-gray-100 rounded-xl transition-colors"
                >
                    Đóng
                </button>
            </div>
        </div>
      )}

    </div>
  );
};

export default CreateOrder;