# be/operation/operation_8_chiphi.py

import psycopg2
import psycopg2.extras
from datetime import date
import sys
from be.db_connection import get_db_connection, close_db_connection


def add_chiphi(loai_chi_phi: str, so_tien: int, ngay_chi_phi_str: str = None,
               mo_ta: str = None, id_nhan_vien: int = None):
    """
    Thêm một khoản chi phí mới.
    """
    if so_tien <= 0:
        print("Lỗi: Số tiền chi phí phải là một số dương.", file=sys.stderr)
        return None

    conn = get_db_connection()
    if not conn:
        return None

    ngay_chi_phi = None
    if ngay_chi_phi_str:
        try:
            ngay_chi_phi = date.fromisoformat(ngay_chi_phi_str)
        except (ValueError, TypeError):
            print(f"Lỗi: Định dạng ngày chi phí '{ngay_chi_phi_str}' không hợp lệ. Vui lòng dùng 'YYYY-MM-DD'.",
                  file=sys.stderr)
            close_db_connection(conn)
            return None

    new_chiphi_id = None
    sql = """
        INSERT INTO ChiPhi (loai_chi_phi, so_tien, ngay_chi_phi, mo_ta, id_nhan_vien)
        VALUES (%s, %s, COALESCE(%s, CURRENT_DATE), %s, %s)
        RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (loai_chi_phi, so_tien, ngay_chi_phi, mo_ta, id_nhan_vien))
            new_chiphi_id = cur.fetchone()[0]
            conn.commit()
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi thêm chi phí: {e}", file=sys.stderr)
        conn.rollback()
    finally:
        close_db_connection(conn)
    return new_chiphi_id


def get_chiphi(loai_filter: str = None, date_from_str: str = None, date_to_str: str = None):
    """
    Lấy danh sách các khoản chi phí, có thể lọc.
    """
    conn = get_db_connection()
    if not conn:
        return None

    base_sql = """
        SELECT cp.*, nv.ten_nhan_vien 
        FROM ChiPhi cp
        LEFT JOIN NhanVien nv ON cp.id_nhan_vien = nv.id
    """
    conditions = []
    params = []

    if loai_filter:
        conditions.append("cp.loai_chi_phi ILIKE %s")
        params.append(f"%{loai_filter}%")
    if date_from_str:
        try:
            conditions.append("cp.ngay_chi_phi >= %s")
            params.append(date.fromisoformat(date_from_str))
        except (ValueError, TypeError):
            print(f"Cảnh báo: Ngày bắt đầu '{date_from_str}' sai định dạng, bỏ qua.", file=sys.stderr)
    if date_to_str:
        try:
            conditions.append("cp.ngay_chi_phi <= %s")
            params.append(date.fromisoformat(date_to_str))
        except (ValueError, TypeError):
            print(f"Cảnh báo: Ngày kết thúc '{date_to_str}' sai định dạng, bỏ qua.", file=sys.stderr)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    base_sql += " ORDER BY cp.ngay_chi_phi DESC, cp.id DESC;"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(base_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi truy vấn chi phí: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def get_chiphi_by_id(chiphi_id: int):
    """
    (Hàm mới) Lấy thông tin một khoản chi phí theo ID.
    """
    conn = get_db_connection()
    if not conn:
        return None

    sql = """
        SELECT cp.*, nv.ten_nhan_vien 
        FROM ChiPhi cp
        LEFT JOIN NhanVien nv ON cp.id_nhan_vien = nv.id
        WHERE cp.id = %s;
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (chiphi_id,))
            expense = cur.fetchone()
            return dict(expense) if expense else None
    except psycopg2.Error as e:
        print(f"Lỗi khi lấy chi phí theo ID: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def update_chiphi(chiphi_id: int, **kwargs):
    """
    Cập nhật thông tin của một khoản chi phí.
    """
    conn = get_db_connection()
    if not conn:
        return False

    allowed_fields = ['loai_chi_phi', 'so_tien', 'ngay_chi_phi', 'mo_ta', 'id_nhan_vien']
    update_fields = []
    params = []

    for key, value in kwargs.items():
        if key in allowed_fields:
            if key == 'ngay_chi_phi' and isinstance(value, str):
                try:
                    value = date.fromisoformat(value)
                except (ValueError, TypeError):
                    print(f"Cảnh báo: Ngày chi phí '{value}' sai định dạng, bỏ qua.", file=sys.stderr)
                    continue
            update_fields.append(f"{key} = %s")
            params.append(value)

    if not update_fields:
        return False

    params.append(chiphi_id)
    sql = f"UPDATE ChiPhi SET {', '.join(update_fields)} WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            if cur.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi cập nhật chi phí: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)


def delete_chiphi(chiphi_id: int):
    """
    (Hàm mới) Xóa một khoản chi phí khỏi cơ sở dữ liệu.
    """
    conn = get_db_connection()
    if not conn:
        return False

    sql = "DELETE FROM ChiPhi WHERE id = %s;"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (chiphi_id,))
            if cur.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi xóa chi phí ID {chiphi_id}: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        close_db_connection(conn)
