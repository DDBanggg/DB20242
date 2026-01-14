import sys
import os
import asyncio
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir)) 
sys.path.append(os.path.join(current_dir, 'backend'))

try:
    from be.db_connection import execute_non_query, execute_query
    from be.routers.routers_10_doanhthuloinhuan import get_bao_cao_nhanh_hom_nay
except ImportError as e:
    print(f"❌ LỖI IMPORT: {e}")
    exit()

def rand_str(): return str(random.randint(10000, 99999))

def setup_data():
    print("\n--- 🛠 TẠO DỮ LIỆU TEST BÁO CÁO (FINAL FIX) ---")
    
    # 1. Tạo dữ liệu nền
    id_kh = execute_non_query("INSERT INTO KhachHang (ten_khach_hang, so_dien_thoai, email) VALUES ('Khach Report', %s, %s) RETURNING id", ("09"+rand_str(), "kh"+rand_str()+"@test.com"), return_id=True)
    id_nv = execute_non_query("INSERT INTO NhanVien (ten_nhan_vien, ten_dang_nhap, mat_khau, email, so_dien_thoai, vai_tro) VALUES ('NV Report', %s, '123', %s, %s, 'Quản lý') RETURNING id", ("user"+rand_str(), "nv"+rand_str()+"@test.com", "08"+rand_str()), return_id=True)
    id_dm = execute_non_query("INSERT INTO DanhMuc (ma_danh_muc, ten_danh_muc) VALUES (%s, 'DM Report') RETURNING id", ("DM"+rand_str(),), return_id=True)
    id_sp = execute_non_query("INSERT INTO SanPham (ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho, don_vi_tinh) VALUES (%s, 'SP Report', %s, 100, 'Cái') RETURNING id", ("SP"+rand_str(), id_dm), return_id=True)
    
    ids_don_hang = []

    # --- KỊCH BẢN TEST ---
    
    # ĐƠN 1: HỢP LỆ (Hôm nay, Hoàn tất)
    # Bán 1 cái, Giá đơn vị 200k, Giá vốn 100k -> Lãi 100k
    sql_dh1 = """
        INSERT INTO DonHangBan (id_khach_hang, id_nhan_vien, ngay_dat_hang, trang_thai_don_hang, dia_chi_giao_hang, phuong_thuc_thanh_toan, trang_thai_thanh_toan) 
        VALUES (%s, %s, CURRENT_DATE, 'Hoàn tất', 'Tại quầy', 'Tiền mặt', 'Đã thanh toán') 
        RETURNING id
    """
    dh1 = execute_non_query(sql_dh1, (id_kh, id_nv), return_id=True)
    
    if dh1:
        # FIX: Thêm cột giam_gia = 0
        sql_ct1 = """
            INSERT INTO ChiTietDonHangBan 
            (id_don_hang_ban, id_san_pham, so_luong, gia_ban_niem_yet_don_vi, gia_ban_cuoi_cung_don_vi, giam_gia, tong_gia_ban, tong_gia_von) 
            VALUES (%s, %s, 1, 200000, 200000, 0, 200000, 100000)
        """
        execute_non_query(sql_ct1, (dh1, id_sp))
        ids_don_hang.append(dh1)

    # ĐƠN 2: SAI NGÀY (Hôm qua) -> Không được tính
    sql_dh2 = """
        INSERT INTO DonHangBan (id_khach_hang, id_nhan_vien, ngay_dat_hang, trang_thai_don_hang, dia_chi_giao_hang, phuong_thuc_thanh_toan, trang_thai_thanh_toan) 
        VALUES (%s, %s, CURRENT_DATE - INTERVAL '1 day', 'Hoàn tất', 'Tại quầy', 'Tiền mặt', 'Đã thanh toán') 
        RETURNING id
    """
    dh2 = execute_non_query(sql_dh2, (id_kh, id_nv), return_id=True)
    
    if dh2:
        sql_ct2 = """
            INSERT INTO ChiTietDonHangBan 
            (id_don_hang_ban, id_san_pham, so_luong, gia_ban_niem_yet_don_vi, gia_ban_cuoi_cung_don_vi, giam_gia, tong_gia_ban, tong_gia_von) 
            VALUES (%s, %s, 1, 500000, 500000, 0, 500000, 200000)
        """
        execute_non_query(sql_ct2, (dh2, id_sp))
        ids_don_hang.append(dh2)

    # ĐƠN 3: SAI TRẠNG THÁI (Đã hủy) -> Không được tính
    # FIX: TrangThaiThanhToan sửa thành 'Chưa thanh toán' (hợp lệ với ENUM)
    sql_dh3 = """
        INSERT INTO DonHangBan (id_khach_hang, id_nhan_vien, ngay_dat_hang, trang_thai_don_hang, dia_chi_giao_hang, phuong_thuc_thanh_toan, trang_thai_thanh_toan) 
        VALUES (%s, %s, CURRENT_DATE, 'Đã hủy', 'Tại quầy', 'Tiền mặt', 'Chưa thanh toán') 
        RETURNING id
    """
    dh3 = execute_non_query(sql_dh3, (id_kh, id_nv), return_id=True)
    
    if dh3:
        sql_ct3 = """
            INSERT INTO ChiTietDonHangBan 
            (id_don_hang_ban, id_san_pham, so_luong, gia_ban_niem_yet_don_vi, gia_ban_cuoi_cung_don_vi, giam_gia, tong_gia_ban, tong_gia_von) 
            VALUES (%s, %s, 1, 100000, 100000, 0, 100000, 50000)
        """
        execute_non_query(sql_ct3, (dh3, id_sp))
        ids_don_hang.append(dh3)

    return id_kh, id_nv, id_sp, id_dm, ids_don_hang

def cleanup(id_kh, id_nv, id_sp, id_dm, ids_don_hang):
    print("\n--- 🧹 DỌN DẸP ---")
    for dh in ids_don_hang:
        if dh:
            execute_non_query("DELETE FROM ChiTietDonHangBan WHERE id_don_hang_ban = %s", (dh,))
            execute_non_query("DELETE FROM DonHangBan WHERE id = %s", (dh,))
    if id_sp: execute_non_query("DELETE FROM SanPham WHERE id = %s", (id_sp,))
    if id_dm: execute_non_query("DELETE FROM DanhMuc WHERE id = %s", (id_dm,))
    if id_nv: execute_non_query("DELETE FROM NhanVien WHERE id = %s", (id_nv,))
    if id_kh: execute_non_query("DELETE FROM KhachHang WHERE id = %s", (id_kh,))
    print("   -> Đã xóa sạch dữ liệu test.")

async def main():
    id_kh = id_nv = id_sp = id_dm = None
    ids_don_hang = []
    try:
        id_kh, id_nv, id_sp, id_dm, ids_don_hang = setup_data()
        
        print("\n--- 🚀 CHẠY API BÁO CÁO ---")
        
        result = await get_bao_cao_nhanh_hom_nay()
        data = result['data']
        
        print(f"📊 Kết quả trả về:")
        print(f"   - Số đơn hàng: {data['so_don_hang']}")
        print(f"   - Doanh thu: {data['doanh_thu']:,.0f}")
        print(f"   - Lợi nhuận: {data['loi_nhuan']:,.0f}")

        # Mong đợi: Ít nhất phải có 1 đơn 200k lãi 100k
        if data['doanh_thu'] >= 200000 and data['loi_nhuan'] >= 100000:
             print("🌟 KẾT QUẢ: Logic báo cáo hoạt động chính xác!")
        else:
             print("❌ KẾT QUẢ: Vẫn sai số liệu!")

    except Exception as e:
        print(f"LỖI: {e}")
    finally:
        cleanup(id_kh, id_nv, id_sp, id_dm, ids_don_hang)

if __name__ == "__main__":
    asyncio.run(main())