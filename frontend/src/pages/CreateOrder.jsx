import { useState, useEffect } from 'react';
import { ShoppingCart, Plus, Minus, Trash2, Search, Package } from 'lucide-react';
import { apiService } from '../api'; // Đảm bảo đường dẫn đúng

const CreateOrder = () => {
  // --- STATE ---
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // --- EFFECT: Lấy danh sách sản phẩm ---
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await apiService.getProducts();
        // Giả sử res.data là mảng: [{ id: 1, name: 'Cà phê', price: 25000, ... }]
        setProducts(res.data || []);
      } catch (error) {
        console.error("Lỗi lấy sản phẩm:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProducts();
  }, []);

  // --- LOGIC GIỎ HÀNG ---
  
  // 1. Thêm sản phẩm vào giỏ
  const addToCart = (product) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === product.id);
      if (existingItem) {
        // Nếu đã có -> Tăng số lượng
        return prevCart.map((item) =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      // Nếu chưa có -> Thêm mới với quantity = 1
      return [...prevCart, { ...product, quantity: 1 }];
    });
  };

  // 2. Giảm số lượng
  const decreaseQuantity = (productId) => {
    setCart((prevCart) => {
      return prevCart.map((item) => {
        if (item.id === productId) {
          return { ...item, quantity: item.quantity - 1 };
        }
        return item;
      }).filter((item) => item.quantity > 0); // Xóa nếu số lượng về 0
    });
  };

  // 3. Xóa hẳn khỏi giỏ
  const removeFromCart = (productId) => {
    setCart((prevCart) => prevCart.filter((item) => item.id !== productId));
  };

  // 4. Tính tổng tiền
  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  // --- LOGIC TẠO ĐƠN (SUBMIT) ---
  const handleCreateOrder = async () => {
    if (cart.length === 0) return alert("Giỏ hàng đang trống!");
    
    setIsSubmitting(true);
    try {
      // Format dữ liệu theo backend yêu cầu
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        total_price: totalAmount,
        created_at: new Date().toISOString()
      };

      await apiService.createOrder(orderData); // Gọi API tạo đơn
      
      alert("Tạo đơn hàng thành công!");
      setCart([]); // Reset giỏ hàng
    } catch (error) {
      console.error("Lỗi tạo đơn:", error);
      alert("Có lỗi xảy ra, vui lòng thử lại.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Lọc sản phẩm theo tìm kiếm
  const filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-[calc(100vh-100px)] gap-6">
      
      {/* --- CỘT TRÁI: DANH SÁCH SẢN PHẨM --- */}
      <div className="flex-1 flex flex-col bg-white rounded-3xl shadow-sm overflow-hidden">
        {/* Header Tìm kiếm */}
        <div className="p-4 border-b flex items-center gap-3">
          <Search className="text-gray-400" size={20} />
          <input 
            type="text"
            placeholder="Tìm món..."
            className="flex-1 outline-none text-gray-700"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Grid Sản phẩm */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          {isLoading ? (
            <div className="text-center py-10 text-gray-400">Đang tải menu...</div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-10 text-gray-400">Không tìm thấy sản phẩm.</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {filteredProducts.map((product) => (
                <div 
                  key={product.id} 
                  onClick={() => addToCart(product)}
                  className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md cursor-pointer transition border border-transparent hover:border-blue-500 group"
                >
                  <div className="h-24 w-full bg-gray-100 rounded-lg mb-3 flex items-center justify-center text-gray-300">
                     {/* Nếu có ảnh thật thì dùng thẻ <img src={product.image} ... /> */}
                     <Package size={40} />
                  </div>
                  <h3 className="font-semibold text-gray-800 line-clamp-1">{product.name}</h3>
                  <p className="text-blue-600 font-bold mt-1">
                    {product.price.toLocaleString('vi-VN')} ₫
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* --- CỘT PHẢI: GIỎ HÀNG (CART) --- */}
      <div className="w-[350px] bg-white rounded-3xl shadow-lg flex flex-col border border-gray-100">
        <div className="p-5 border-b bg-gray-50 rounded-t-3xl">
          <h2 className="text-lg font-bold flex items-center gap-2 text-gray-800">
            <ShoppingCart size={20} /> Đơn hàng hiện tại
          </h2>
        </div>

        {/* List Items */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
              <ShoppingBagIcon size={48} />
              <p className="mt-2 text-sm">Chưa có món nào</p>
            </div>
          ) : (
            cart.map((item) => (
              <div key={item.id} className="flex justify-between items-center group">
                <div>
                  <h4 className="font-medium text-gray-800 text-sm">{item.name}</h4>
                  <p className="text-xs text-gray-500">
                    {(item.price * item.quantity).toLocaleString('vi-VN')} ₫
                  </p>
                </div>
                
                <div className="flex items-center gap-3 bg-gray-50 px-2 py-1 rounded-lg">
                  <button 
                    onClick={() => decreaseQuantity(item.id)}
                    className="w-6 h-6 flex items-center justify-center bg-white rounded shadow-sm hover:text-red-500"
                  >
                    {item.quantity === 1 ? <Trash2 size={14} /> : <Minus size={14} />}
                  </button>
                  <span className="text-sm font-bold w-4 text-center">{item.quantity}</span>
                  <button 
                    onClick={() => addToCart(item)}
                    className="w-6 h-6 flex items-center justify-center bg-blue-500 text-white rounded shadow-sm hover:bg-blue-600"
                  >
                    <Plus size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer: Tổng tiền & Nút Pay */}
        <div className="p-5 bg-gray-50 rounded-b-3xl border-t space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Tổng cộng</span>
            <span className="text-2xl font-black text-blue-600">
              {totalAmount.toLocaleString('vi-VN')} ₫
            </span>
          </div>

          <button 
            onClick={handleCreateOrder}
            disabled={cart.length === 0 || isSubmitting}
            className={`w-full py-3 rounded-xl font-bold text-white transition-all transform active:scale-95
              ${cart.length === 0 || isSubmitting 
                ? 'bg-gray-300 cursor-not-allowed' 
                : 'bg-primary hover:shadow-lg hover:shadow-blue-200'}`}
          >
            {isSubmitting ? 'Đang xử lý...' : 'Thanh toán ngay'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Component icon phụ trợ nếu cần
const ShoppingBagIcon = ({ size }) => (
  <svg 
    width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" 
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
  >
    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <path d="M16 10a4 4 0 0 1-8 0"></path>
  </svg>
);

export default CreateOrder;