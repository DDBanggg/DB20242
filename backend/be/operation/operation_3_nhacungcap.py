# be/operation/operation_3_nhacungcap.py

import psycopg2
import psycopg2.extras
from be.db_connection import get_db_connection, close_db_connection


def add_nhacungcap(ten_nha_cung_cap, email, dia_chi, ma_so_thue=None,
                   so_dien_thoai=None, nguoi_lien_he_chinh=None):
    """
    Thêm một nhà cung cấp mới.
    """
    conn = get_db_connection()
    if not conn:
        return None

    new_id = None
    sql = """
        INSERT INTO NhaCungCap (
            ten_nha_cung_cap, ma_so_thue, so_dien_thoai, 
            email, dia_chi, nguoi_lien_he_chinh
        )
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (ten_nha_cung_cap, ma_so_thue, so_dien_thoai,
                              email, dia_chi, nguoi_lien_he_chinh))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Đã thêm nhà cung cấp '{ten_nha_cung_cap}' với ID: {new_id}.")
    except psycopg2.Error as e:
        print(f"Lỗi khi thêm nhà cung cấp: {e}")
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_id


def get_nhacungcap(name_filter=None, phone_filter=None, email_filter=None):
    """
    Lấy danh sách nhà cung cấp, có thể lọc theo nhiều tiêu chí.
    """
    conn = get_db_connection()
    if not conn:
        return None

    base_sql = "SELECT * FROM NhaCungCap"
    conditions = []
    params = []

    if name_filter:
        conditions.append("ten_nha_cung_cap ILIKE %s")
        params.append(f"%{name_filter}%")
    if phone_filter:
        conditions.append("so_dien_thoai LIKE %s")
        params.append(f"%{phone_filter}%")
    if email_filter:
        conditions.append("email ILIKE %s")
        params.append(f"%{email_filter}%")

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += " ORDER BY ten_nha_cung_cap;"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách nhà cung cấp: {e}")
        return None
    finally:
        close_db_connection(conn)


def get_nhacungcap_by_id(nhacungcap_id: int):
    """
    Lấy thông tin một nhà cung cấp theo ID.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = "SELECT * FROM NhaCungCap WHERE id = %s;"
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (nhacungcap_id,))
            supplier = cur.fetchone()
            return dict(supplier) if supplier else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy nhà cung cấp theo ID: {e}")
        return None
    finally:
        close_db_connection(conn)


def update_nhacungcap(nhacungcap_id, **kwargs):
    """
    Cập nhật thông tin một nhà cung cấp dựa vào ID.
    """
    conn = get_db_connection()
    if not conn:
        return False

    allowed_fields = ['ten_nha_cung_cap', 'ma_so_thue', 'so_dien_thoai',
                      'email', 'dia_chi', 'nguoi_lien_he_chinh']
    update_fields = [f"{key} = %s" for key in kwargs if key in allowed_fields]
    params = [value for key, value in kwargs.items() if key in allowed_fields]

    if not update_fields:
        return False

    params.append(nhacungcap_id)
    sql = f"UPDATE NhaCungCap SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi khi cập nhật nhà cung cấp: {e}")
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)

