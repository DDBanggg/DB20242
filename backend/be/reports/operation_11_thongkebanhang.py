# be/reports/operation_11_thongkebanhang.py

"""
Module này chứa các hàm để tạo báo cáo thống kê bán hàng,
bao gồm số lượng đơn hàng, sản phẩm bán chạy và tình hình tồn kho.
"""

import psycopg2
import psycopg2.extras
from datetime import date, timedelta
import sys
from be.db_connection import get_db_connection, close_db_connection


def _get_date_range(period: str, start_date_str: str = None, end_date_str: str = None):
    """
    Hàm nội bộ để tính toán và trả về khoảng ngày dựa trên kỳ báo cáo.
    Tránh lặp lại code trong nhiều hàm báo cáo.
    """
    allowed_periods = ['yesterday', 'last_week', 'last_month', 'custom']
    if period not in allowed_periods:
        raise ValueError(f"Kỳ báo cáo '{period}' không hợp lệ.")

    today = date.today()
    start_date, end_date = None, None

    if period == 'yesterday':
        start_date = end_date = today - timedelta(days=1)
    elif period == 'last_week':
        end_date = today - timedelta(days=today.weekday() + 1)
        start_date = end_date - timedelta(days=6)
    elif period == 'last_month':
        end_date = today.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif period == 'custom':
        if not start_date_str or not end_date_str:
            raise ValueError("Với period='custom', cần cung cấp ngày bắt đầu và kết thúc.")
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
        if start_date > end_date:
            raise ValueError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")

    return start_date, end_date


def get_order_count_report(period: str, start_date_str: str = None, end_date_str: str = None):
    """
    Tạo báo cáo thống kê số lượng đơn hàng đã bán theo từng ngày.

    Args:
        period (str): Kỳ báo cáo ('yesterday', 'last_week', 'last_month', 'custom').
        start_date_str (str, optional): Ngày bắt đầu cho 'custom'.
        end_date_str (str, optional): Ngày kết thúc cho 'custom'.

    Returns:
        list or None: Một danh sách chi tiết theo ngày, hoặc None nếu có lỗi.
    """
    try:
        start_date, end_date = _get_date_range(period, start_date_str, end_date_str)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return None

    # FIX: Đổi bí danh từ "do" thành "d_orders" để tránh xung đột với từ khóa của SQL.
    sql = """
        WITH daily_orders AS (
            -- Đếm số lượng đơn hàng (phân biệt) đã 'Hoàn tất' mỗi ngày
            SELECT
                DATE_TRUNC('day', ngay_dat_hang)::date AS report_date,
                COUNT(DISTINCT id) AS order_count
            FROM DonHangBan
            WHERE trang_thai_don_hang = 'Hoàn tất' AND ngay_dat_hang::date BETWEEN %s AND %s
            GROUP BY report_date
        ), all_dates AS (
            -- Tạo chuỗi ngày đầy đủ để đảm bảo không ngày nào bị thiếu
            SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date AS report_date
        )
        -- Kết hợp để có báo cáo hoàn chỉnh, ngày không có đơn hàng sẽ có giá trị 0
        SELECT
            ad.report_date AS ky_bao_cao,
            COALESCE(d_orders.order_count, 0) AS so_luong_don_hang
        FROM all_dates ad
        LEFT JOIN daily_orders d_orders ON ad.report_date = d_orders.report_date
        ORDER BY ad.report_date ASC;
    """

    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (start_date, end_date, start_date, end_date))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo báo cáo số lượng đơn hàng: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def get_best_selling_products_report(period: str, sort_by: str, top_n: int,
                                     start_date_str: str = None, end_date_str: str = None):
    """
    Tạo báo cáo về các sản phẩm bán chạy nhất.

    Args:
        period (str): Kỳ báo cáo ('yesterday', 'last_week', 'last_month', 'custom').
        sort_by (str): Tiêu chí sắp xếp ('quantity' hoặc 'revenue').
        top_n (int): Số lượng sản phẩm hàng đầu cần hiển thị (3, 5, hoặc 10).
        start_date_str (str, optional): Ngày bắt đầu cho 'custom'.
        end_date_str (str, optional): Ngày kết thúc cho 'custom'.

    Returns:
        list or None: Danh sách các sản phẩm bán chạy, hoặc None nếu có lỗi.
    """
    # --- 1. Xác thực đầu vào ---
    if sort_by not in ['quantity', 'revenue']:
        print(f"Lỗi: Tiêu chí sắp xếp '{sort_by}' không hợp lệ.", file=sys.stderr)
        return None
    if top_n not in [3, 5, 10]:
        print(f"Lỗi: Giá trị Top N '{top_n}' không hợp lệ.", file=sys.stderr)
        return None
    try:
        start_date, end_date = _get_date_range(period, start_date_str, end_date_str)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return None

    # --- 2. Xây dựng câu lệnh SQL ---
    # FIX: Đảm bảo tên cột trong ORDER BY khớp với bí danh trong SELECT.
    order_clause = "tong_so_luong_ban DESC" if sort_by == 'quantity' else "tong_doanh_thu DESC"

    sql = f"""
        SELECT 
            sp.id AS id_san_pham,
            sp.ten_san_pham,
            sp.ma_san_pham,
            SUM(ctdhb.so_luong) AS tong_so_luong_ban,
            SUM(ctdhb.tong_gia_ban) AS tong_doanh_thu
        FROM ChiTietDonHangBan ctdhb
        JOIN DonHangBan dhb ON ctdhb.id_don_hang_ban = dhb.id
        JOIN SanPham sp ON ctdhb.id_san_pham = sp.id
        WHERE dhb.trang_thai_don_hang = 'Hoàn tất' 
          AND dhb.ngay_dat_hang::date BETWEEN %s AND %s
        GROUP BY sp.id, sp.ten_san_pham, sp.ma_san_pham
        ORDER BY {order_clause}
        LIMIT %s;
    """

    # --- 3. Thực thi và trả về kết quả ---
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (start_date, end_date, top_n))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo báo cáo sản phẩm bán chạy: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)


def get_inventory_report(status: str, category_id: int = None):
    """
    Tạo báo cáo về các sản phẩm có tồn kho thấp hoặc cao.

    Args:
        status (str): Trạng thái tồn kho cần lọc ('low_stock' hoặc 'high_stock').
        category_id (int, optional): Lọc theo một ID danh mục cụ thể.

    Returns:
        list or None: Danh sách các sản phẩm phù hợp, hoặc None nếu có lỗi.
    """
    # --- 1. Xác thực đầu vào ---
    if status not in ['low_stock', 'high_stock']:
        print(f"Lỗi: Trạng thái tồn kho '{status}' không hợp lệ.", file=sys.stderr)
        return None

    # --- 2. Xây dựng câu lệnh SQL ---
    base_sql = """
        SELECT
            sp.id AS id_san_pham,
            sp.ten_san_pham,
            sp.ma_san_pham,
            sp.so_luong_ton_kho,
            dm.ten_danh_muc
        FROM SanPham sp
        JOIN DanhMuc dm ON sp.id_danh_muc = dm.id
    """
    conditions = []
    params = []

    if status == 'low_stock':
        conditions.append("sp.so_luong_ton_kho < 10")
        order_clause = "ORDER BY sp.so_luong_ton_kho ASC"
    else:  # high_stock
        conditions.append("sp.so_luong_ton_kho > 100")
        order_clause = "ORDER BY sp.so_luong_ton_kho DESC"

    if category_id:
        conditions.append("sp.id_danh_muc = %s")
        params.append(category_id)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)

    final_sql = base_sql + " " + order_clause + ";"

    # --- 3. Thực thi và trả về kết quả ---
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(final_sql, tuple(params))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo báo cáo tồn kho: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)
