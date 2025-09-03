# be/operation/operation_7_donhangban.py

"""
Module này chứa các hàm nghiệp vụ liên quan đến Đơn Hàng Bán,
bao gồm tạo mới, thêm sản phẩm (với kiểm tra tồn kho an toàn),
xem chi tiết và cập nhật trạng thái.
"""

import psycopg2
import psycopg2.extras
from datetime import date
import sys
from be.db_connection import get_db_connection, close_db_connection


def create_donhangban(id_nhan_vien, id_khach_hang, dia_chi_giao_hang,
                      ngay_dat_hang_str=None,
                      phuong_thuc_thanh_toan='Tiền mặt',
                      trang_thai_don_hang='Chờ xác nhận',
                      trang_thai_thanh_toan='Chưa thanh toán',
                      ghi_chu_don_hang=None):
    """
    Tạo một Đơn Hàng Bán mới.
    """
    conn = get_db_connection()
    if not conn:
        return None

    ngay_dat_hang = None
    if ngay_dat_hang_str:
        try:
            ngay_dat_hang = date.fromisoformat(ngay_dat_hang_str)
        except ValueError:
            print(f"Lỗi: Định dạng ngày đặt hàng '{ngay_dat_hang_str}' không hợp lệ (YYYY-MM-DD).", file=sys.stderr)
            close_db_connection(conn)
            return None

    new_order_id = None
    sql = """
        INSERT INTO DonHangBan (
            id_nhan_vien, id_khach_hang, dia_chi_giao_hang, ngay_dat_hang,
            phuong_thuc_thanh_toan, trang_thai_don_hang, trang_thai_thanh_toan,
            ghi_chu_don_hang
        )
        VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP), %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
                id_nhan_vien, id_khach_hang, dia_chi_giao_hang, ngay_dat_hang,
                phuong_thuc_thanh_toan, trang_thai_don_hang, trang_thai_thanh_toan,
                ghi_chu_don_hang
            ))
            new_order_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo Đơn Hàng Bán mới: {e}", file=sys.stderr)
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_order_id


def add_item_to_donhangban(id_don_hang_ban, id_san_pham, so_luong,
                           gia_ban_niem_yet_don_vi, giam_gia,
                           ghi_chu_item=None):
    """
    Thêm một sản phẩm vào ChiTietDonHangBan.
    """
    if not (0 <= giam_gia <= 1):
        print(f"Lỗi: Tỷ lệ giảm giá '{giam_gia}' không hợp lệ. Phải từ 0.0 đến 1.0.", file=sys.stderr)
        return None

    conn = get_db_connection()
    if not conn:
        return None

    new_item_id = None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT ten_san_pham, so_luong_ton_kho FROM SanPham WHERE id = %s FOR UPDATE;", (id_san_pham,))
            product = cur.fetchone()

            if not product:
                print(f"Lỗi: Sản phẩm với ID {id_san_pham} không tồn tại.", file=sys.stderr)
                conn.rollback()
                return None

            if product['so_luong_ton_kho'] < so_luong:
                print(f"Lỗi: Tồn kho không đủ cho sản phẩm '{product['ten_san_pham']}'. "
                      f"Tồn: {product['so_luong_ton_kho']}, Yêu cầu: {so_luong}.", file=sys.stderr)
                conn.rollback()
                return None

            sql_add_item = """
                INSERT INTO ChiTietDonHangBan (
                    id_don_hang_ban, id_san_pham, so_luong,
                    gia_ban_niem_yet_don_vi, giam_gia, ghi_chu
                )
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """
            cur.execute(sql_add_item, (
                id_don_hang_ban, id_san_pham, so_luong,
                gia_ban_niem_yet_don_vi, giam_gia, ghi_chu_item
            ))
            new_item_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi thêm sản phẩm vào Đơn Hàng Bán: {e}", file=sys.stderr)
        if conn: conn.rollback()
        new_item_id = None
    finally:
        close_db_connection(conn)

    return new_item_id


def get_all_donhangban(customer_id: int = None, staff_id: int = None, status: str = None):
    """
    Lấy danh sách Đơn Hàng Bán, có thể lọc.
    """
    conn = get_db_connection()
    if not conn: return None

    base_sql = """
        SELECT dhb.*, kh.ten_khach_hang, nv.ten_nhan_vien
        FROM DonHangBan dhb
        JOIN KhachHang kh ON dhb.id_khach_hang = kh.id
        JOIN NhanVien nv ON dhb.id_nhan_vien = nv.id
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

    base_sql += " ORDER BY dhb.ngay_dat_hang DESC, dhb.id DESC;"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách đơn hàng bán: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def get_chitietdonhangban(id_don_hang_ban):
    """
    Lấy thông tin chi tiết của một Đơn Hàng Bán.
    """
    conn = get_db_connection()
    if not conn:
        return None

    order_info = None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            sql_order = """
                SELECT dhb.*, kh.ten_khach_hang, nv.ten_nhan_vien
                FROM DonHangBan dhb
                LEFT JOIN KhachHang kh ON dhb.id_khach_hang = kh.id
                JOIN NhanVien nv ON dhb.id_nhan_vien = nv.id
                WHERE dhb.id = %s;
            """
            cur.execute(sql_order, (id_don_hang_ban,))
            order_data = cur.fetchone()

            if not order_data:
                return None

            order_info = dict(order_data)

            sql_items = """
                SELECT ctdhb.*, sp.ten_san_pham, sp.ma_san_pham, sp.don_vi_tinh
                FROM ChiTietDonHangBan ctdhb
                JOIN SanPham sp ON ctdhb.id_san_pham = sp.id
                WHERE ctdhb.id_don_hang_ban = %s ORDER BY ctdhb.id;
            """
            cur.execute(sql_items, (id_don_hang_ban,))
            order_info['chi_tiet_san_pham'] = [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi lấy chi tiết Đơn Hàng Bán ID {id_don_hang_ban}: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)
    return order_info


def update_donhangban_status(id_don_hang_ban, new_trang_thai_don_hang,
                             new_trang_thai_thanh_toan=None,
                             ngay_giao_hang_thuc_te_str=None):
    """
    Cập nhật trạng thái của một Đơn Hàng Bán.
    """
    conn = get_db_connection()
    if not conn:
        return False

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
        except ValueError:
            print(f"Cảnh báo: Định dạng ngày giao hàng thực tế '{ngay_giao_hang_thuc_te_str}' không hợp lệ, bỏ qua.",
                  file=sys.stderr)

    params.append(id_don_hang_ban)
    sql = f"UPDATE DonHangBan SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi cập nhật Đơn Hàng Bán ID {id_don_hang_ban}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return False
    finally:
        close_db_connection(conn)
