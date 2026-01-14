import sys
import os
import asyncio
import random
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir)) 
sys.path.append(os.path.join(current_dir, 'backend'))

try:
    from be.db_connection import execute_non_query
    from be.routers.routers_2_sanpham import get_danh_sach_san_pham
except ImportError as e:
    print(f"❌ LỖI IMPORT: {e}")
    exit()

def rand_str(): return str(random.randint(10000, 99999))

def setup_data():
    print("\n--- 🛠 TẠO DỮ LIỆU TEST (SP + GIÁ) ---")
    
    # 1. Danh Mục
    sql_dm = "INSERT INTO DanhMuc (ma_danh_muc, ten_danh_muc) VALUES (%s, %s) RETURNING id"
    id_dm = execute_non_query(sql_dm, ("DM"+rand_str(), "DM Test"), return_id=True)
    
    # 2. SP Tồn ít (<=5)
    sql_low = """
        INSERT INTO SanPham (ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho, don_vi_tinh) 
        VALUES (%s, %s, %s, 3, 'Cái') RETURNING id
    """
    code_low = "SP_LOW_"+rand_str()
    id_low = execute_non_query(sql_low, (code_low, "Iphone 15 (Ton it)", id_dm), return_id=True)
    
    # 3. SP Tồn nhiều (>5)
    sql_high = """
        INSERT INTO SanPham (ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho, don_vi_tinh) 
        VALUES (%s, %s, %s, 20, 'Cái') RETURNING id
    """
    code_high = "SP_HIGH_"+rand_str()
    id_high = execute_non_query(sql_high, (code_high, "Samsung S24 (Ton nhieu)", id_dm), return_id=True)
    
    # 4. QUAN TRỌNG: Tạo giá bán cho 2 SP này (Bảng LichSuGiaNiemYet)
    sql_price = """
        INSERT INTO LichSuGiaNiemYet (id_san_pham, gia_niem_yet, ngay_ap_dung)
        VALUES (%s, %s, CURRENT_DATE)
    """
    execute_non_query(sql_price, (id_low, 25000000))  # Giá Iphone
    execute_non_query(sql_price, (id_high, 18000000)) # Giá Samsung
    
    return id_dm, id_low, id_high, code_low

def cleanup(id_dm, id_low, id_high):
    print("\n--- 🧹 DỌN DẸP ---")
    # Xóa giá trước (do ràng buộc khóa ngoại)
    if id_low: execute_non_query("DELETE FROM LichSuGiaNiemYet WHERE id_san_pham = %s", (id_low,))
    if id_high: execute_non_query("DELETE FROM LichSuGiaNiemYet WHERE id_san_pham = %s", (id_high,))
    
    # Xóa SP
    if id_low: execute_non_query("DELETE FROM SanPham WHERE id = %s", (id_low,))
    if id_high: execute_non_query("DELETE FROM SanPham WHERE id = %s", (id_high,))
    if id_dm: execute_non_query("DELETE FROM DanhMuc WHERE id = %s", (id_dm,))

async def main():
    id_dm = id_low = id_high = None
    try:
        id_dm, id_low, id_high, code_low = setup_data()
        
        print("\n--- 🚀 TEST 1: KIỂM TRA CẢNH BÁO & GIÁ ---")
        # Tìm theo mã sản phẩm vừa tạo
        result = await get_danh_sach_san_pham(tu_khoa=code_low) 
        products = result['data']
        
        found = False
        for p in products:
            if p['id'] == id_low:
                found = True
                print(f"   SP: {p['ten_san_pham']}")
                print(f"   - Tồn kho: {p['so_luong_ton_kho']} -> Cảnh báo: {p['canh_bao']} (Mong đợi: True)")
                print(f"   - Giá bán: {p['gia_ban_hien_tai']:,.0f} (Mong đợi: 25,000,000)")
                
                if p['canh_bao'] == True and p['gia_ban_hien_tai'] == 25000000:
                    print("🌟 KẾT QUẢ: Logic đúng hoàn toàn!")
                else:
                    print("❌ KẾT QUẢ: Sai thông tin cảnh báo hoặc giá!")
        
        if not found:
            print("❌ LỖI: Không tìm thấy sản phẩm vừa tạo.")

    except Exception as e:
        print(f"LỖI: {e}")
    finally:
        cleanup(id_dm, id_low, id_high)

if __name__ == "__main__":
    asyncio.run(main())