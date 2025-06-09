# be/operation/operation_4_khachhang.py

import psycopg2
import psycopg2.extras
from datetime import date
from be.db_connection import get_db_connection, close_db_connection


def add_khachhang(ten_khach_hang, so_dien_thoai, email,
                  dia_chi=None, ngay_sinh=None, gioi_tinh=None):
    """
    Thêm một khách hàng mới.
    so_dien_thoai và email phải là duy nhất.
    """
    conn = get_db_connection()
    if not conn:
        return None

    processed_ngay_sinh = None
    if ngay_sinh and isinstance(ngay_sinh, str):
        try:
            processed_ngay_sinh = date.fromisoformat(ngay_sinh)
        except ValueError:
            print(f"Lỗi: Định dạng ngày sinh '{ngay_sinh}' không hợp lệ (YYYY-MM-DD).")
            close_db_connection(conn)
            return None
    elif isinstance(ngay_sinh, date):
        processed_ngay_sinh = ngay_sinh

    new_id = None
    sql = """
        INSERT INTO KhachHang 
            (ten_khach_hang, so_dien_thoai, email, dia_chi, ngay_sinh, gioi_tinh)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (ten_khach_hang, so_dien_thoai, email,
                              dia_chi, processed_ngay_sinh, gioi_tinh))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Đã thêm khách hàng '{ten_khach_hang}' với ID: {new_id}.")
    except psycopg2.Error as e:
        print(f"Lỗi khi thêm khách hàng: {e}")
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_id


def get_khachhang(name_filter=None, phone_filter=None, email_filter=None):
    """
    Lấy danh sách khách hàng, có thể tìm kiếm theo tên, SĐT hoặc email.
    """
    conn = get_db_connection()
    if not conn:
        return None

    base_sql = "SELECT * FROM KhachHang"
    conditions = []
    params = []

    if name_filter:
        conditions.append("ten_khach_hang ILIKE %s")
        params.append(f"%{name_filter}%")
    if phone_filter:
        conditions.append("so_dien_thoai LIKE %s")
        params.append(f"%{phone_filter}%")
    if email_filter:
        conditions.append("email ILIKE %s")
        params.append(f"%{email_filter}%")

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += " ORDER BY ten_khach_hang;"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách khách hàng: {e}")
        return None
    finally:
        close_db_connection(conn)


def get_khachhang_by_id(khachhang_id: int):
    """
    Lấy thông tin một khách hàng theo ID.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = "SELECT * FROM KhachHang WHERE id = %s;"
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (khachhang_id,))
            customer = cur.fetchone()
            return dict(customer) if customer else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy khách hàng theo ID: {e}")
        return None
    finally:
        close_db_connection(conn)


def update_khachhang(khachhang_id, **kwargs):
    """
    Cập nhật thông tin một khách hàng dựa vào ID.
    Không cho phép cập nhật so_lan_mua_hang.
    """
    conn = get_db_connection()
    if not conn:
        return False

    allowed_fields = ['ten_khach_hang', 'so_dien_thoai', 'email',
                      'dia_chi', 'ngay_sinh', 'gioi_tinh']
    update_fields = []
    params = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            if key == 'ngay_sinh' and value is not None and isinstance(value, str):
                try:
                    value = date.fromisoformat(value)
                except ValueError:
                    print(f"Lỗi: Định dạng ngày sinh '{value}' để cập nhật không hợp lệ.")
                    continue
            update_fields.append(f"{key} = %s")
            params.append(value)

    if not update_fields:
        return False

    params.append(khachhang_id)
    sql = f"UPDATE KhachHang SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi khi cập nhật khách hàng: {e}")
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)