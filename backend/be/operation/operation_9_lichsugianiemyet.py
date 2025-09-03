# be/operation/operation_9_lichsugianiemyet.py

import psycopg2
import psycopg2.extras
from datetime import date
import sys
from be.db_connection import get_db_connection, close_db_connection


def add_lichsugianiemyet(id_san_pham: int, gia_niem_yet: int, ngay_ap_dung_str: str, ghi_chu: str = None):
    """
    Thêm một mức giá niêm yết mới cho sản phẩm.
    """
    if gia_niem_yet < 0:
        print("Lỗi: Giá niêm yết không được là số âm.", file=sys.stderr)
        return None

    conn = get_db_connection()
    if not conn:
        return None

    try:
        ngay_ap_dung = date.fromisoformat(ngay_ap_dung_str)
    except (ValueError, TypeError):
        print(f"Lỗi: Định dạng ngày áp dụng '{ngay_ap_dung_str}' không hợp lệ. Vui lòng dùng 'YYYY-MM-DD'.", file=sys.stderr)
        close_db_connection(conn)
        return None

    new_price_history_id = None
    sql = """
        INSERT INTO LichSuGiaNiemYet (id_san_pham, gia_niem_yet, ngay_ap_dung, ghi_chu)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_san_pham, gia_niem_yet, ngay_ap_dung, ghi_chu))
            new_price_history_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi thêm lịch sử giá: {e}", file=sys.stderr)
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_price_history_id


def get_lichsugianiemyet_for_sanpham(id_san_pham: int):
    """
    Lấy toàn bộ lịch sử thay đổi giá của một sản phẩm cụ thể.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = """
        SELECT ls.*, sp.ten_san_pham, sp.ma_san_pham
        FROM LichSuGiaNiemYet ls
        JOIN SanPham sp ON ls.id_san_pham = sp.id
        WHERE ls.id_san_pham = %s
        ORDER BY ls.ngay_ap_dung DESC, ls.id DESC;
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (id_san_pham,))
            price_history = [dict(row) for row in cur.fetchall()]
            return price_history
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi truy vấn lịch sử giá cho sản phẩm ID {id_san_pham}: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def get_lichsugianiemyet_by_id(history_id: int):
    """
    Lấy một bản ghi lịch sử giá theo ID của chính nó.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = """
        SELECT ls.*, sp.ten_san_pham, sp.ma_san_pham
        FROM LichSuGiaNiemYet ls
        JOIN SanPham sp ON ls.id_san_pham = sp.id
        WHERE ls.id = %s;
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (history_id,))
            history_record = cur.fetchone()
            return dict(history_record) if history_record else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy lịch sử giá theo ID: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)

def update_lichsugianiemyet(history_id: int, **kwargs):
    """
    Cập nhật một bản ghi lịch sử giá.
    Chỉ cho phép cập nhật giá và ghi chú để không ảnh hưởng logic trigger.
    """
    conn = get_db_connection()
    if not conn:
        return False

    allowed_fields = ['gia_niem_yet', 'ghi_chu']
    update_fields = []
    params = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            if key == 'gia_niem_yet' and value < 0:
                print("Lỗi: Giá niêm yết không được là số âm.", file=sys.stderr)
                return False
            update_fields.append(f"{key} = %s")
            params.append(value)

    if not update_fields:
        return False

    params.append(history_id)
    sql = f"UPDATE LichSuGiaNiemYet SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi khi cập nhật lịch sử giá: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)
