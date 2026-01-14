import js
from pyodide.http import pyfetch
import json
from datetime import datetime
import asyncio

# --- CẤU HÌNH API ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- BIẾN TOÀN CỤC ---
products_db = [] # Lưu danh sách SP tải từ server
cart = {} # Lưu giỏ hàng: {ma_sp: {info, qty}}

# --- HÀM HỖ TRỢ ĐỊNH DẠNG TIỀN ---
def format_money(amount):
    return "{:,.0f} ₫".format(amount)

# --- 1. LẤY DANH SÁCH SẢN PHẨM ---
async def fetch_products():
    try:
        response = await pyfetch(url=f"{API_BASE_URL}/san-pham/danh-sach", method="GET")
        data = await response.json()
        
        global products_db
        products_db = data.get('data', [])
        render_products(products_db)
        
    except Exception as e:
        js.console.log(f"Lỗi fetch: {e}")
        js.document.getElementById("product-list").innerHTML = f"<div class='alert alert-danger'>Không thể kết nối Backend. Hãy đảm bảo bạn đã chạy main.py ở port 8000!</div>"

def render_products(products):
    container = js.document.getElementById("product-list")
    container.innerHTML = "" # Xóa cũ
    
    if not products:
        container.innerHTML = "<p class='text-center'>Không tìm thấy sản phẩm nào.</p>"
        return

    for p in products:
        # Xử lý cảnh báo tồn kho
        warning_html = ""
        if p.get('canh_bao'):
            warning_html = f"<div class='warning-stock'><i class='fas fa-exclamation-triangle'></i> Chỉ còn {p['so_luong_ton_kho']} {p['don_vi_tinh']}</div>"
        
        # Hình ảnh mặc định nếu null
        img_url = p.get('duong_dan_hinh_anh_chinh')
        if not img_url: img_url = "https://via.placeholder.com/150?text=No+Image"

        html = f"""
        <div class="col-6 col-md-4 col-lg-3">
            <div class="card product-card h-100" id="card-{p['id']}">
                <img src="{img_url}" class="card-img-top product-img" alt="{p['ten_san_pham']}">
                <div class="card-body p-2">
                    <h6 class="card-title text-truncate" title="{p['ten_san_pham']}">{p['ten_san_pham']}</h6>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold text-primary">{format_money(p['gia_ban_hien_tai'])}</span>
                        <small class="text-muted">Kho: {p['so_luong_ton_kho']}</small>
                    </div>
                    {warning_html}
                </div>
            </div>
        </div>
        """
        # Tạo element tạm để gán sự kiện click
        temp_div = js.document.createElement("div")
        temp_div.innerHTML = html
        
        # Gán sự kiện click: Thêm vào giỏ
        card_el = temp_div.firstElementChild.querySelector(".product-card")
        
        # Dùng Closure để giữ biến p
        def add_click_handler(product_info):
            def handler(event):
                add_to_cart(product_info)
            return handler
            
        card_el.onclick = add_click_handler(p)
        
        container.appendChild(temp_div.firstElementChild)

# --- 2. XỬ LÝ GIỎ HÀNG ---
def add_to_cart(product):
    pid = product['id']
    
    # Kiểm tra tồn kho (Client side check)
    current_qty_in_cart = cart[pid]['qty'] if pid in cart else 0
    if current_qty_in_cart + 1 > product['so_luong_ton_kho']:
        js.alert(f"Hết hàng! Chỉ còn {product['so_luong_ton_kho']} trong kho.")
        return

    if pid in cart:
        cart[pid]['qty'] += 1
    else:
        cart[pid] = {
            "info": product,
            "qty": 1
        }
    update_cart_ui()

def remove_from_cart(pid):
    if pid in cart:
        del cart[pid]
        update_cart_ui()

def update_cart_ui():
    container = js.document.getElementById("cart-items")
    container.innerHTML = ""
    
    total_amount = 0
    count = 0
    
    if not cart:
        container.innerHTML = "<div class='text-center text-muted mt-5'>Giỏ hàng trống</div>"
    
    for pid, item in cart.items():
        p = item['info']
        qty = item['qty']
        sub = p['gia_ban_hien_tai'] * qty
        total_amount += sub
        count += 1
        
        html = f"""
        <div class="d-flex justify-content-between align-items-center border-bottom py-2">
            <div style="width: 60%">
                <div class="fw-bold text-truncate">{p['ten_san_pham']}</div>
                <small class="text-muted">{format_money(p['gia_ban_hien_tai'])} x {qty}</small>
            </div>
            <div class="fw-bold">{format_money(sub)}</div>
            <button class="btn btn-sm btn-outline-danger ms-2 btn-remove" data-id="{pid}"><i class="fas fa-trash"></i></button>
        </div>
        """
        
        temp_div = js.document.createElement("div")
        temp_div.innerHTML = html
        
        # Gán sự kiện xóa
        btn_remove = temp_div.querySelector(".btn-remove")
        def remove_handler(product_id):
            def handler(event):
                remove_from_cart(product_id)
            return handler
        btn_remove.onclick = remove_handler(pid)
        
        container.appendChild(temp_div.firstElementChild)

    # Cập nhật tổng tiền
    vat = total_amount * 0.10
    final = total_amount + vat
    
    js.document.getElementById("cart-count").innerText = str(count)
    js.document.getElementById("sub-total").innerText = format_money(total_amount)
    js.document.getElementById("tax-total").innerText = format_money(vat)
    js.document.getElementById("final-total").innerText = format_money(final)

# --- 3. TÌM KIẾM ---
async def search_product(*args):
    keyword = js.document.getElementById("search-input").value
    try:
        response = await pyfetch(url=f"{API_BASE_URL}/san-pham/danh-sach?tu_khoa={keyword}", method="GET")
        data = await response.json()
        global products_db
        products_db = data.get('data', [])
        render_products(products_db)
    except Exception as e:
        js.console.log(str(e))

# --- 4. THANH TOÁN (CHECKOUT) ---
async def process_checkout(*args):
    if not cart:
        js.alert("Giỏ hàng trống! Vui lòng chọn sản phẩm.")
        return
        
    # Chuẩn bị dữ liệu gửi lên API
    order_details = []
    for pid, item in cart.items():
        order_details.append({
            "MaSP": pid,
            "SoLuong": item['qty'],
            "DonGia": float(item['info']['gia_ban_hien_tai'])
        })
        
    payload = {
        "MaKH": 1, # Hardcode Khách lẻ cho MVP
        "MaNV": 1, # Hardcode Nhân viên ca sáng cho MVP
        "ChiTiet": order_details
    }
    
    try:
        # Gọi API POST
        response = await pyfetch(
            url=f"{API_BASE_URL}/don-hang-ban/tao-moi",
            method="POST",
            body=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            result = await response.json()
            data = result['data']
            
            # 1. In hóa đơn
            print_invoice(data, cart)
            
            # 2. Reset giỏ hàng
            cart.clear()
            update_cart_ui()
            
            # 3. Reload lại danh sách SP (để cập nhật tồn kho mới)
            await fetch_products()
            
            js.alert("Thanh toán thành công! Đang in hóa đơn...")
        else:
            js.alert("Lỗi thanh toán! Vui lòng thử lại.")
            
    except Exception as e:
        js.console.log(str(e))
        js.alert(f"Lỗi hệ thống: {e}")

# --- 5. IN HÓA ĐƠN ---
def print_invoice(order_data, cart_snapshot):
    # Điền dữ liệu vào mẫu in
    js.document.getElementById("inv-id").innerText = f"#{order_data['MaDH']}"
    js.document.getElementById("inv-date").innerText = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    tbody = js.document.getElementById("inv-items")
    tbody.innerHTML = ""
    
    for item in order_data['ChiTiet']:
        # Tìm tên SP trong cart snapshot để hiển thị cho đẹp
        # (Vì API trả về chỉ có MaSP, ta lấy tên từ client cache)
        ma_sp = item['MaSP'] # Lưu ý: API trả về field tên là 'MaSP' trong ChiTiet model
        
        # Trick: tìm tên sản phẩm từ danh sách sản phẩm hiện tại
        name = "Sản phẩm #" + str(ma_sp)
        for db_item in products_db:
             if db_item['id'] == ma_sp:
                 name = db_item['ten_san_pham']
                 break
                 
        row = f"""
            <tr>
                <td>{name}</td>
                <td class="text-center">{item['SoLuong']}</td>
                <td class="text-end">{format_money(item['DonGia'])}</td>
                <td class="text-end">{format_money(item['SoLuong'] * item['DonGia'])}</td>
            </tr>
        """
        tbody.innerHTML += row
        
    js.document.getElementById("inv-subtotal").innerText = format_money(order_data['TongTienHang'])
    js.document.getElementById("inv-tax").innerText = format_money(order_data['ThueVAT'])
    js.document.getElementById("inv-total").innerText = format_money(order_data['TongThanhToan'])
    
    # Gọi lệnh in trình duyệt
    js.window.print()

# --- CHẠY KHI KHỞI ĐỘNG ---
asyncio.ensure_future(fetch_products())