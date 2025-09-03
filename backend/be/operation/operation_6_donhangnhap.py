# be/operation/operation_6_donhangnhap.py

import psycopg2
import psycopg2.extras
from datetime import date
import sys
from be.db_connection import get_db_connection, close_db_connection


def create_donhangnhap(id_nha_cung_cap, id_nhan_vien,
                       ngay_dat_hang_str=None, ngay_du_kien_nhan_hang_str=None,
                       trang_thai='Chờ xác nhận', ghi_chu=None):
    """
    Tạo một Đơn Hàng Nhập mới trong bảng DonHangNhap.
    """
    conn = get_db_connection()
    if not conn:
        return None

    processed_ngay_dat_hang = None
    if ngay_dat_hang_str:
        try:
            processed_ngay_dat_hang = date.fromisoformat(ngay_dat_hang_str)
        except (ValueError, TypeError):
            print(f"Lỗi: Định dạng ngày đặt hàng '{ngay_dat_hang_str}' không hợp lệ (YYYY-MM-DD).", file=sys.stderr)
            close_db_connection(conn)
            return None

    processed_ngay_du_kien = None
    if ngay_du_kien_nhan_hang_str:
        try:
            processed_ngay_du_kien = date.fromisoformat(ngay_du_kien_nhan_hang_str)
        except (ValueError, TypeError):
            print(f"Lỗi: Định dạng ngày dự kiến nhận hàng '{ngay_du_kien_nhan_hang_str}' không hợp lệ (YYYY-MM-DD).",
                  file=sys.stderr)
            close_db_connection(conn)
            return None

    new_order_id = None
    sql = """
        INSERT INTO DonHangNhap (id_nha_cung_cap, id_nhan_vien, ngay_dat_hang, ngay_du_kien_nhan_hang, trang_thai, ghi_chu)
        VALUES (%s, %s, COALESCE(%s, CURRENT_DATE), %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
            id_nha_cung_cap, id_nhan_vien, processed_ngay_dat_hang, processed_ngay_du_kien, trang_thai, ghi_chu))
            new_order_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo đơn hàng nhập: {e}", file=sys.stderr)
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_order_id


def add_item_to_donhangnhap(id_don_hang_nhap, id_san_pham, so_luong, gia_nhap_don_vi, ghi_chu_item=None):
    """
    Thêm một sản phẩm vào một Đơn Hàng Nhập.
    """
    conn = get_db_connection()
    if not conn:
        return None

    new_item_id = None
    sql = """
        INSERT INTO ChiTietDonHangNhap (id_don_hang_nhap, id_san_pham, so_luong, gia_nhap_don_vi, ghi_chu)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_don_hang_nhap, id_san_pham, so_luong, gia_nhap_don_vi, ghi_chu_item))
            new_item_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi thêm sản phẩm vào đơn hàng nhập: {e}", file=sys.stderr)
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_item_id


def get_all_donhangnhap(supplier_id: int = None, status: str = None):
    """
    Lấy danh sách Đơn Hàng Nhập, có thể lọc.
    """
    conn = get_db_connection()
    if not conn: return None

    base_sql = """
        SELECT dhn.*, ncc.ten_nha_cung_cap, nv.ten_nhan_vien
        FROM DonHangNhap dhn
        JOIN NhaCungCap ncc ON dhn.id_nha_cung_cap = ncc.id
        JOIN NhanVien nv ON dhn.id_nhan_vien = nv.id
    """
    conditions = []
    params = []

    if supplier_id:
        conditions.append("dhn.id_nha_cung_cap = %s")
        params.append(supplier_id)
    if status:
        conditions.append("dhn.trang_thai = %s")
        params.append(status)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += " ORDER BY dhn.ngay_dat_hang DESC, dhn.id DESC;"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách đơn hàng nhập: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def get_chitietdonhangnhap(id_don_hang_nhap):
    """
    Lấy thông tin chi tiết của một Đơn Hàng Nhập.
    """
    conn = get_db_connection()
    if not conn:
        return None

    order_info = None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            sql_order = """
                SELECT dhn.*, ncc.ten_nha_cung_cap, nv.ten_nhan_vien
                FROM DonHangNhap dhn
                LEFT JOIN NhaCungCap ncc ON dhn.id_nha_cung_cap = ncc.id
                LEFT JOIN NhanVien nv ON dhn.id_nhan_vien = nv.id 
                WHERE dhn.id = %s;
            """
            cur.execute(sql_order, (id_don_hang_nhap,))
            order_data = cur.fetchone()
            if not order_data: return None
            order_info = dict(order_data)

            sql_items = """
                SELECT ctdhn.*, sp.ten_san_pham, sp.don_vi_tinh, sp.ma_san_pham
                FROM ChiTietDonHangNhap ctdhn
                JOIN SanPham sp ON ctdhn.id_san_pham = sp.id
                WHERE ctdhn.id_don_hang_nhap = %s ORDER BY sp.ten_san_pham;
            """
            cur.execute(sql_items, (id_don_hang_nhap,))
            order_info['chi_tiet_san_pham'] = [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi lấy chi tiết Đơn Hàng Nhập: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)
    return order_info


def update_donhangnhap_status(id_don_hang_nhap, new_status, ngay_nhan_hang_thuc_te_str=None):
    """
    Cập nhật trạng thái của một Đơn Hàng Nhập.
    """
    conn = get_db_connection()
    if not conn:
        return False

    update_fields = ["trang_thai = %s"]
    params = [new_status]

    if ngay_nhan_hang_thuc_te_str:
        try:
            ngay_nhan_thuc_te = date.fromisoformat(ngay_nhan_hang_thuc_te_str)
            update_fields.append("ngay_nhan_hang_thuc_te = %s")
            params.append(ngay_nhan_thuc_te)
        except ValueError:
            print(f"Cảnh báo: Định dạng ngày nhận hàng thực tế '{ngay_nhan_hang_thuc_te_str}' không hợp lệ, bỏ qua.",
                  file=sys.stderr)

    params.append(id_don_hang_nhap)
    sql = f"UPDATE DonHangNhap SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi cập nhật trạng thái Đơn Hàng Nhập: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)

