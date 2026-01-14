import sys
import os
import asyncio
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir)) 
sys.path.append(os.path.join(current_dir, 'backend'))

try:
    from be.db_connection import execute_non_query
    from be.routers.routers_7_donhangban import create_don_hang_ban, DonHangInput, ChiTietDonHangInput
except ImportError as e:
    print(f"❌ LỖI IMPORT: {e}")
    exit()

# Hàm random để tạo email/mã duy nhất tránh lỗi Duplicate
def rand_str():
    return str(random.randint(10000, 99999))

def setup_dummy_data():
    print("\n--- 🛠 ĐANG TẠO DỮ LIỆU GIẢ (FIXED SCHEMA) ---")
    
    # 1. KhachHang (Yêu cầu: ten_khach_hang, so_dien_thoai, email UNIQUE)
    sql_kh = """
        INSERT INTO KhachHang (ten_khach_hang, so_dien_thoai, email) 
        VALUES ('Khach Test POS', %s, %s) RETURNING id
    """
    sdt_kh = "09" + rand_str()
    email_kh = "khach" + rand_str() + "@test.com"
    ma_kh = execute_non_query(sql_kh, (sdt_kh, email_kh), return_id=True)
    
    # 2. NhanVien (Yêu cầu: ten_nhan_vien, ten_dang_nhap, mat_khau, email, so_dien_thoai)
    sql_nv = """
        INSERT INTO NhanVien (ten_nhan_vien, ten_dang_nhap, mat_khau, email, so_dien_thoai, vai_tro) 
        VALUES ('NV Test', %s, '123456', %s, %s, 'Nhân viên') RETURNING id
    """
    user_nv = "user" + rand_str()
    email_nv = "nv" + rand_str() + "@test.com"
    sdt_nv = "08" + rand_str()
    ma_nv = execute_non_query(sql_nv, (user_nv, email_nv, sdt_nv), return_id=True)
    
    # 3. DanhMuc (Yêu cầu: ma_danh_muc, ten_danh_muc)
    sql_dm = "INSERT INTO DanhMuc (ma_danh_muc, ten_danh_muc) VALUES (%s, %s) RETURNING id"
    ma_dm_code = "DM" + rand_str()
    ten_dm = "Danh Muc " + rand_str()
    id_dm = execute_non_query(sql_dm, (ma_dm_code, ten_dm), return_id=True)

    # 4. SanPham (Yêu cầu: ma_san_pham, ten_san_pham, don_vi_tinh, id_danh_muc)
    # Lưu ý: Schema SanPham KHÔNG có cột gia_ban, ta chỉ quan tâm SoLuongTonKho
    sql_sp = """
        INSERT INTO SanPham (ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho, don_vi_tinh) 
        VALUES (%s, %s, %s, 100, 'Cái') 
        RETURNING id
    """
    ma_sp_code = "SP" + rand_str()
    ten_sp = "San Pham " + rand_str()
    id_sp = execute_non_query(sql_sp, (ma_sp_code, ten_sp, id_dm), return_id=True)
    
    print(f"   -> Đã tạo: KH={ma_kh}, NV={ma_nv}, SP={id_sp}")
    return ma_kh, ma_nv, id_sp, id_dm

def cleanup_data(ma_kh, ma_nv, id_sp, id_dm, ma_dh):
    print("\n--- 🧹 ĐANG DỌN DẸP DỮ LIỆU ---")
    if ma_dh:
        execute_non_query("DELETE FROM ChiTietDonHangBan WHERE id_don_hang_ban = %s", (ma_dh,))
        execute_non_query("DELETE FROM DonHangBan WHERE id = %s", (ma_dh,))
    if id_sp: execute_non_query("DELETE FROM SanPham WHERE id = %s", (id_sp,))
    if id_dm: execute_non_query("DELETE FROM DanhMuc WHERE id = %s", (id_dm,))
    if ma_nv: execute_non_query("DELETE FROM NhanVien WHERE id = %s", (ma_nv,))
    if ma_kh: execute_non_query("DELETE FROM KhachHang WHERE id = %s", (ma_kh,))
    print("   -> Đã xóa sạch.")

async def main():
    ma_kh = ma_nv = id_sp = id_dm = ma_dh = None
    try:
        ma_kh, ma_nv, id_sp, id_dm = setup_dummy_data()
        
        # Test Input
        input_data = DonHangInput(
            MaKH=ma_kh,
            MaNV=ma_nv,
            ChiTiet=[ChiTietDonHangInput(MaSP=id_sp, SoLuong=2, DonGia=100000)]
        )
        
        print("\n--- 🚀 ĐANG GỌI API 'TẠO ĐƠN HÀNG' ---")
        result = await create_don_hang_ban(input_data)
        
        data = result['data']
        ma_dh = data['MaDH']
        
        print(f"✅ THÀNH CÔNG! Mã ĐH: {ma_dh}")
        print(f"   Tổng tiền: {data['TongThanhToan']:,.0f} (Đã +10% Thuế)")
            
    except Exception as e:
        print(f"❌ LỖI: {e}")
    finally:
        cleanup_data(ma_kh, ma_nv, id_sp, id_dm, ma_dh)

if __name__ == "__main__":
    asyncio.run(main())