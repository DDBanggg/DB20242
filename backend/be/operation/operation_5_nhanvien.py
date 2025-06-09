# be/operation/operation_5_nhanvien.py

import psycopg2
import psycopg2.extras
from be.db_connection import get_db_connection, close_db_connection


def add_nhanvien(ten_nhan_vien, ten_dang_nhap, mat_khau, email, so_dien_thoai,
                 vai_tro='Nhân viên', trang_thai='Đang làm việc'):
    """
    Thêm một nhân viên mới.
    """
    conn = get_db_connection()
    if not conn:
        return None

    new_id = None
    sql = """
        INSERT INTO NhanVien (
            ten_nhan_vien, ten_dang_nhap, mat_khau, email, 
            so_dien_thoai, vai_tro, trang_thai
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            # Trong thực tế, mật khẩu cần được băm trước khi lưu
            # Ví dụ: from passlib.context import CryptContext
            # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            # hashed_password = pwd_context.hash(mat_khau)
            cur.execute(sql, (ten_nhan_vien, ten_dang_nhap, mat_khau, email,
                              so_dien_thoai, vai_tro, trang_thai))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Đã thêm nhân viên '{ten_nhan_vien}' với ID: {new_id}.")
    except psycopg2.Error as e:
        print(f"Lỗi khi thêm nhân viên: {e}")
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_id


def get_all_nhanvien():
    """Lấy tất cả các nhân viên từ database, sắp xếp theo tên."""
    conn = get_db_connection()
    if not conn:
        return None

    sql = "SELECT * FROM NhanVien ORDER BY ten_nhan_vien;"
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách nhân viên: {e}")
        return None
    finally:
        close_db_connection(conn)


def get_nhanvien_by_id(nhanvien_id: int):
    """Lấy thông tin một nhân viên theo ID."""
    conn = get_db_connection()
    if not conn:
        return None

    sql = "SELECT * FROM NhanVien WHERE id = %s;"
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (nhanvien_id,))
            staff = cur.fetchone()
            return dict(staff) if staff else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy nhân viên theo ID: {e}")
        return None
    finally:
        close_db_connection(conn)


def update_nhanvien(nhanvien_id: int, **kwargs):
    """
    Cập nhật thông tin một nhân viên một cách linh hoạt.
    """
    conn = get_db_connection()
    if not conn:
        return False

    allowed_fields = ['ten_nhan_vien', 'email', 'so_dien_thoai',
                      'vai_tro', 'trang_thai', 'mat_khau']
    update_fields = [f"{key} = %s" for key in kwargs if key in allowed_fields]
    params = [value for key, value in kwargs.items() if key in allowed_fields]

    if not update_fields:
        return False

    params.append(nhanvien_id)
    sql = f"UPDATE NhanVien SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi khi cập nhật nhân viên: {e}")
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)

