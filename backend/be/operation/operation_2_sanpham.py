# be/operation/operation_2_sanpham.py

import psycopg2
import psycopg2.extras
from be.db_connection import get_db_connection, close_db_connection


def add_sanpham(ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho, don_vi_tinh,
                mo_ta_chi_tiet=None, duong_dan_hinh_anh_chinh=None,
                trang_thai='Đang kinh doanh - Còn hàng'):
    """
    Thêm một sản phẩm mới.
    Trả về ID của sản phẩm mới nếu thành công, ngược lại None.
    """
    conn = get_db_connection()
    if not conn:
        return None
    new_id = None
    sql = """
        INSERT INTO SanPham (
            ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho, don_vi_tinh, 
            mo_ta_chi_tiet, duong_dan_hinh_anh_chinh, trang_thai
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (ma_san_pham, ten_san_pham, id_danh_muc, so_luong_ton_kho,
                              don_vi_tinh, mo_ta_chi_tiet, duong_dan_hinh_anh_chinh, trang_thai))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Sản phẩm '{ten_san_pham}' đã được thêm với ID: {new_id}.")
    except psycopg2.Error as e:
        print(f"Lỗi khi thêm sản phẩm: {e}")
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_id


def get_sanpham(id_danh_muc_filter=None, ten_san_pham_filter=None, low_stock_threshold=None):
    """
    Lấy danh sách sản phẩm, có thể lọc theo danh mục, tên, hoặc tồn kho thấp.
    """
    conn = get_db_connection()
    if not conn:
        return None

    base_sql = """
        SELECT sp.*, dm.ten_danh_muc 
        FROM SanPham sp
        JOIN DanhMuc dm ON sp.id_danh_muc = dm.id
    """
    conditions = []
    params = []

    if id_danh_muc_filter:
        conditions.append("sp.id_danh_muc = %s")
        params.append(id_danh_muc_filter)

    if ten_san_pham_filter:
        conditions.append("sp.ten_san_pham ILIKE %s")
        params.append(f"%{ten_san_pham_filter}%")

    if low_stock_threshold is not None:
        conditions.append("sp.so_luong_ton_kho <= %s")
        params.append(low_stock_threshold)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += " ORDER BY sp.ten_san_pham;"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            products = [dict(row) for row in cur.fetchall()]
            return products
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy danh sách sản phẩm: {e}")
        return None
    finally:
        close_db_connection(conn)


def get_sanpham_by_id(sanpham_id):
    """
    Lấy thông tin chi tiết của một sản phẩm theo ID.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = """
        SELECT sp.*, dm.ten_danh_muc 
        FROM SanPham sp
        JOIN DanhMuc dm ON sp.id_danh_muc = dm.id
        WHERE sp.id = %s;
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (sanpham_id,))
            product = cur.fetchone()
            return dict(product) if product else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy sản phẩm theo ID: {e}")
        return None
    finally:
        close_db_connection(conn)


def update_sanpham(sanpham_id, **kwargs):
    """
    Cập nhật thông tin một sản phẩm.
    """
    conn = get_db_connection()
    if not conn:
        return False

    allowed_fields = ['ma_san_pham', 'ten_san_pham', 'id_danh_muc', 'don_vi_tinh',
                      'mo_ta_chi_tiet', 'duong_dan_hinh_anh_chinh', 'trang_thai']
    update_fields = []
    params = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            update_fields.append(f"{key} = %s")
            params.append(value)

    if not update_fields:
        return False

    params.append(sanpham_id)
    sql = f"UPDATE SanPham SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi khi cập nhật sản phẩm: {e}")
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)
