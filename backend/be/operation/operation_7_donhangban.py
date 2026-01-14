# be/operation/operation_7_donhangban.py

import psycopg2
import psycopg2.extras
from datetime import date
import sys
from be.db_connection import get_db_connection, close_db_connection

# --- Giữ nguyên các hàm create_donhangban, add_item_to_donhangban như cũ ---
# (Phần code tạo đơn và thêm sản phẩm không cần sửa đổi gì vì Trigger DB vẫn hoạt động tốt)

def create_donhangban(id_nhan_vien, id_khach_hang, dia_chi_giao_hang,
                      ngay_dat_hang_str=None,
                      phuong_thuc_thanh_toan='Tiền mặt',
                      trang_thai_don_hang='Chờ xác nhận',
                      trang_thai_thanh_toan='Chưa thanh toán',
                      ghi_chu_don_hang=None):
    """Tạo một Đơn Hàng Bán mới."""
    conn = get_db_connection()
    if not conn: return None
    ngay_dat_hang = None
    if ngay_dat_hang_str:
        try: ngay_dat_hang = date.fromisoformat(ngay_dat_hang_str)
        except ValueError: return None

    new_order_id = None
    sql = """
        INSERT INTO DonHangBan (
            id_nhan_vien, id_khach_hang, dia_chi_giao_hang, ngay_dat_hang,
            phuong_thuc_thanh_toan, trang_thai_don_hang, trang_thai_thanh_toan,
            ghi_chu_don_hang
        ) VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP), %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_nhan_vien, id_khach_hang, dia_chi_giao_hang, ngay_dat_hang,
                              phuong_thuc_thanh_toan, trang_thai_don_hang, trang_thai_thanh_toan, ghi_chu_don_hang))
            new_order_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL: {e}", file=sys.stderr)
        conn.rollback()
    finally: close_db_connection(conn)
    return new_order_id

def add_item_to_donhangban(id_don_hang_ban, id_san_pham, so_luong, gia_ban_niem_yet_don_vi, giam_gia, ghi_chu_item=None):
    """Thêm sản phẩm vào đơn hàng (Trigger sẽ tự tính giá vốn FIFO)."""
    conn = get_db_connection()
    if not conn: return None
    new_item_id = None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Check tồn kho
            cur.execute("SELECT ten_san_pham, so_luong_ton_kho FROM SanPham WHERE id = %s FOR UPDATE;", (id_san_pham,))
            product = cur.fetchone()
            if not product or product['so_luong_ton_kho'] < so_luong:
                return None # Xử lý lỗi tồn kho ở đây nếu cần

            sql = """
                INSERT INTO ChiTietDonHangBan (id_don_hang_ban, id_san_pham, so_luong, gia_ban_niem_yet_don_vi, giam_gia, ghi_chu)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """
            cur.execute(sql, (id_don_hang_ban, id_san_pham, so_luong, gia_ban_niem_yet_don_vi, giam_gia, ghi_chu_item))
            new_item_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error:
        if conn: conn.rollback()
    finally: close_db_connection(conn)
    return new_item_id

# --- CẬP NHẬT MỚI: Hàm lấy chi tiết đơn hàng CÓ TÍNH THUẾ ---

def get_chitietdonhangban(id_don_hang_ban):
    """
    Lấy thông tin chi tiết đơn hàng và TỰ ĐỘNG TÍNH TOÁN CÁC LOẠI THUẾ
    để hiển thị hóa đơn mà không cần lưu vào DB.
    """
    conn = get_db_connection()
    if not conn: return None

    order_info = None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # 1. Lấy thông tin chung đơn hàng
            sql_order = """
                SELECT dhb.*, kh.ten_khach_hang, nv.ten_nhan_vien
                FROM DonHangBan dhb
                LEFT JOIN KhachHang kh ON dhb.id_khach_hang = kh.id
                JOIN NhanVien nv ON dhb.id_nhan_vien = nv.id
                WHERE dhb.id = %s;
            """
            cur.execute(sql_order, (id_don_hang_ban,))
            row = cur.fetchone()
            if not row: return None
            order_info = dict(row)

            # 2. Lấy danh sách sản phẩm
            sql_items = """
                SELECT ctdhb.*, sp.ten_san_pham, sp.ma_san_pham, sp.don_vi_tinh
                FROM ChiTietDonHangBan ctdhb
                JOIN SanPham sp ON ctdhb.id_san_pham = sp.id
                WHERE ctdhb.id_don_hang_ban = %s ORDER BY ctdhb.id;
            """
            cur.execute(sql_items, (id_don_hang_ban,))
            items = [dict(r) for r in cur.fetchall()]
            order_info['chi_tiet_san_pham'] = items

            # 3. TÍNH TOÁN THUẾ & TỔNG TIỀN (Xử lý Python)
            # Tổng tiền hàng (đã trừ giảm giá từng món, lấy từ DB tính sẵn)
            tong_tien_hang = sum(item['tong_gia_ban'] for item in items)
            
            # Tính thuế theo yêu cầu (VAT 10%, HKD 1.5%)
            # Giả sử thuế được tính thêm trên tổng tiền hàng (Khách phải trả thêm)
            thue_vat = tong_tien_hang * 0.10
            thue_hkd = tong_tien_hang * 0.015
            tong_thanh_toan = tong_tien_hang + thue_vat + thue_hkd

            # Gán thêm các trường calculated vào kết quả trả về
            order_info['financial_calc'] = {
                "tong_tien_hang": float(tong_tien_hang),
                "thue_vat_10_percent": float(thue_vat),
                "thue_hkd_1_5_percent": float(thue_hkd),
                "tong_thanh_toan": float(tong_thanh_toan)
            }

    except psycopg2.Error as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        close_db_connection(conn)
    
    return order_info

# --- CẬP NHẬT MỚI: Hàm lấy danh sách đơn hàng cũng cần hiển thị tổng tiền ---

def get_all_donhangban(customer_id=None, staff_id=None, status=None):
    """
    Lấy danh sách đơn hàng. 
    Lưu ý: Vì không lưu tổng tiền trong DB, ta phải JOIN và SUM để lấy tổng giá trị hiển thị.
    """
    conn = get_db_connection()
    if not conn: return None

    # Query phức tạp hơn xíu để tính tổng tiền on-the-fly
    base_sql = """
        SELECT 
            dhb.*, 
            kh.ten_khach_hang, 
            nv.ten_nhan_vien,
            COALESCE(SUM(ct.tong_gia_ban), 0) as tam_tinh_tien_hang,
            -- Tính luôn tổng thanh toán dự kiến để hiển thị ra list
            (COALESCE(SUM(ct.tong_gia_ban), 0) * 1.115) as tong_thanh_toan_du_kien
        FROM DonHangBan dhb
        JOIN KhachHang kh ON dhb.id_khach_hang = kh.id
        JOIN NhanVien nv ON dhb.id_nhan_vien = nv.id
        LEFT JOIN ChiTietDonHangBan ct ON dhb.id = ct.id_don_hang_ban
    """
    conditions = []
    params = []

    if customer_id:
        conditions.append("dhb.id_khach_hang = %s")
        params.append(customer_id)
    if staff_id:
        conditions.append("dhb.id_nhan_vien = %s")
        params.append(staff_id)
    if status:
        conditions.append("dhb.trang_thai_don_hang = %s")
        params.append(status)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    # Group by để hàm SUM hoạt động đúng
    base_sql += """
        GROUP BY dhb.id, kh.ten_khach_hang, nv.ten_nhan_vien
        ORDER BY dhb.ngay_dat_hang DESC, dhb.id DESC;
    """

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        close_db_connection(conn)

def update_donhangban_status(id_don_hang_ban, new_trang_thai_don_hang,
                             new_trang_thai_thanh_toan=None,
                             ngay_giao_hang_thuc_te_str=None):
    """Cập nhật trạng thái (giữ nguyên logic cũ)."""
    conn = get_db_connection()
    if not conn: return False
    # ... (Giữ nguyên phần update trạng thái như code cũ của bạn)
    # Vì logic trừ kho đã nằm ở Trigger DB nên không cần sửa gì ở đây
    update_fields = ["trang_thai_don_hang = %s"]
    params = [new_trang_thai_don_hang]

    if new_trang_thai_thanh_toan:
        update_fields.append("trang_thai_thanh_toan = %s")
        params.append(new_trang_thai_thanh_toan)

    if ngay_giao_hang_thuc_te_str:
        try:
            ngay_giao_thuc_te = date.fromisoformat(ngay_giao_hang_thuc_te_str)
            update_fields.append("ngay_giao_hang_thuc_te = %s")
            params.append(ngay_giao_thuc_te)
        except ValueError: pass

    params.append(id_don_hang_ban)
    sql = f"UPDATE DonHangBan SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0: return False
            conn.commit()
            return True
    except psycopg2.Error:
        return False
    finally:
        close_db_connection(conn)