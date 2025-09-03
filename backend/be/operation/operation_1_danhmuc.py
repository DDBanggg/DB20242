# be/operation/operation_1_danhmuc.py

import psycopg2
import psycopg2.extras
from be.db_connection import get_db_connection, close_db_connection


def add_danhmuc(ma_danh_muc, ten_danh_muc, mo_ta=None):
    """
    Thêm một danh mục mới vào bảng DanhMuc.
    ma_danh_muc phải là duy nhất.
    Trả về ID của danh mục mới nếu thành công, ngược lại trả về None.
    """
    conn = get_db_connection()
    if not conn:
        return None

    new_id = None
    # ngay_tao có DEFAULT trong DB
    sql = """
        INSERT INTO DanhMuc (ma_danh_muc, ten_danh_muc, mo_ta)
        VALUES (%s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (ma_danh_muc, ten_danh_muc, mo_ta))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Đã thêm danh mục '{ten_danh_muc}' với ID: {new_id}.")
    except psycopg2.Error as e:
        print(f"Lỗi khi thêm danh mục: {e}")
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_id


def get_all_danhmuc():
    """Lấy tất cả các danh mục từ database."""
    conn = get_db_connection()
    if not conn:
        return None

    danhmuc_list = []
    sql = "SELECT id, ma_danh_muc, ten_danh_muc, mo_ta, ngay_tao FROM DanhMuc ORDER BY ma_danh_muc;"
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            danhmuc_list = [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách danh mục: {e}")
    finally:
        close_db_connection(conn)
    return danhmuc_list


def get_danhmuc_by_id(danhmuc_id: int):
    """
    Lấy thông tin một danh mục theo ID.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = "SELECT * FROM DanhMuc WHERE id = %s;"
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (danhmuc_id,))
            category = cur.fetchone()
            return dict(category) if category else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh mục theo ID: {e}")
        return None
    finally:
        close_db_connection(conn)


def update_danhmuc(danhmuc_id, **kwargs):
    """
    Cập nhật thông tin một danh mục dựa vào ID.
    kwargs có thể chứa: ten_danh_muc, mo_ta, ma_danh_muc.
    Trả về True nếu thành công, False nếu thất bại.
    """
    conn = get_db_connection()
    if not conn:
        return False

    update_fields = []
    params = []
    allowed_fields = ['ten_danh_muc', 'mo_ta', 'ma_danh_muc']

    for key, value in kwargs.items():
        if key in allowed_fields:
            update_fields.append(f"{key} = %s")
            params.append(value)

    if not update_fields:
        print("Không có trường thông tin hợp lệ nào để cập nhật.")
        return False

    params.append(danhmuc_id)
    sql = f"UPDATE DanhMuc SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                print(f"Không tìm thấy danh mục với ID {danhmuc_id} hoặc dữ liệu không thay đổi.")
                conn.rollback()
                return False
            conn.commit()
            print(f"Đã cập nhật thành công danh mục ID: {danhmuc_id}.")
            return True
    except psycopg2.Error as e:
        print(f"Lỗi khi cập nhật danh mục: {e}")
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)


