import sys
import os

# --- CẤU HÌNH ĐƯỜNG DẪN IMPORT ---
# Tự động tìm đường dẫn để import được folder 'be'
current_dir = os.path.dirname(os.path.abspath(__file__))
# Nếu file test nằm trong thư mục con, cần trỏ ngược ra ngoài để thấy folder 'be'
sys.path.append(current_dir) 
sys.path.append(os.path.dirname(current_dir)) 
sys.path.append(os.path.join(current_dir, 'backend')) # Dự phòng

try:
    # Import các hàm mới vừa viết
    from be.db_connection import get_db_connection, execute_query, execute_non_query
    
    print("\n--- 1. TEST KẾT NỐI DATABASE ---")
    conn = get_db_connection()
    if conn:
        print("✅ KẾT NỐI THÀNH CÔNG!")
        conn.close()
    else:
        print("❌ KẾT NỐI THẤT BẠI. Dừng kiểm tra.")
        exit()

    print("\n--- 2. TEST HÀM 'SELECT' (execute_query) ---")
    # Test query đơn giản, không ảnh hưởng dữ liệu thật
    sql_select = "SELECT version() as phien_ban, current_date as hom_nay"
    result = execute_query(sql_select)
    
    if result and isinstance(result, list) and len(result) > 0:
        print(f"✅ Query thành công. Dữ liệu trả về (Dictionary):")
        print(f"   -> Phiên bản: {result[0]['phien_ban']}")
        print(f"   -> Ngày: {result[0]['hom_nay']}")
    else:
        print("❌ Lỗi: Không lấy được dữ liệu hoặc định dạng sai.")

    print("\n--- 3. TEST HÀM 'INSERT' LẤY ID (execute_non_query) ---")
    
    # 1. Tạo bảng THẬT (Thay vì Temporary) để nó tồn tại qua các lần ngắt kết nối
    table_name = "Test_KiemTra_ID_Xoa_Ngay"
    setup_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, noi_dung TEXT);"
    execute_non_query(setup_sql)
    
    try:
        # 2. Test Insert và yêu cầu trả về ID
        insert_sql = f"INSERT INTO {table_name} (noi_dung) VALUES (%s) RETURNING id"
        new_id = execute_non_query(insert_sql, ('Test chức năng lấy ID',), return_id=True)
        
        if new_id and isinstance(new_id, int):
            print(f"✅ Insert thành công!")
            print(f"   -> ID vừa tạo là: {new_id} (Tuyệt vời! Hàm đã trả về ID chuẩn)")
        else:
            print(f"❌ Lỗi: Không lấy được ID. Kết quả trả về: {new_id}")
            
    finally:
        # 3. DỌN DẸP: Xóa bảng test đi dù chạy thành công hay thất bại
        cleanup_sql = f"DROP TABLE IF EXISTS {table_name};"
        execute_non_query(cleanup_sql)
        print("   -> Đã dọn dẹp (xóa) bảng test.")

    print("\n------------------------------------------------")
    print("🎉 CHÚC MỪNG: DATABASE HELPER ĐÃ SẴN SÀNG CHO MVP!")

except ImportError as e:
    print("❌ LỖI IMPORT: Không tìm thấy module 'be'. Hãy đảm bảo bạn chạy file từ thư mục gốc backend.")
    print(f"Chi tiết: {e}")
except Exception as e:
    print(f"❌ LỖI KHÁC: {e}")