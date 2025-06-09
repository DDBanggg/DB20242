# be/reports/operation_12_phantichkhachhang.py

"""
Module này chứa các hàm để tạo báo cáo phân tích khách hàng,
bao gồm tỷ lệ khách hàng mới/quay lại và danh sách khách hàng chi tiêu nhiều nhất.
"""

import psycopg2
import psycopg2.extras
from datetime import date, timedelta
import sys
from be.db_connection import get_db_connection, close_db_connection


def _get_date_range(period: str, start_date_str: str = None, end_date_str: str = None):
    """
    Hàm nội bộ để tính toán và trả về khoảng ngày dựa trên kỳ báo cáo.
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


def get_customer_acquisition_report(period: str, start_date_str: str = None, end_date_str: str = None):
    """
    Tạo báo cáo về khách hàng mới và khách hàng quay lại.

    Cấu trúc trả về:
    {
        "summary": { "so_khach_hang_moi": X, "so_khach_hang_quay_lai": Y },
        "details": [ { "ky_bao_cao": "YYYY-MM-DD", "so_khach_hang_moi": A, "so_khach_hang_quay_lai": B }, ... ]
    }

    Args:
        period (str): Kỳ báo cáo ('yesterday', 'last_week', 'last_month', 'custom').
        start_date_str (str, optional): Ngày bắt đầu cho 'custom'.
        end_date_str (str, optional): Ngày kết thúc cho 'custom'.

    Returns:
        dict or None: Một dictionary chứa báo cáo, hoặc None nếu có lỗi.
    """
    try:
        start_date, end_date = _get_date_range(period, start_date_str, end_date_str)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return None

    # --- SQL để lấy MỘT DÒNG tổng hợp ---
    sql_summary = """
        WITH customer_first_purchase AS (
            -- Tìm ngày mua hàng hoàn tất đầu tiên của mỗi khách hàng
            SELECT id_khach_hang, MIN(ngay_dat_hang::date) as first_purchase_date
            FROM DonHangBan WHERE trang_thai_don_hang = 'Hoàn tất'
            GROUP BY id_khach_hang
        ),
        customers_in_period AS (
            -- Lấy danh sách khách hàng có mua hàng trong kỳ báo cáo
            SELECT DISTINCT id_khach_hang
            FROM DonHangBan
            WHERE trang_thai_don_hang = 'Hoàn tất' AND ngay_dat_hang::date BETWEEN %s AND %s
        )
        -- Đếm số lượng khách hàng mới và quay lại trong kỳ
        SELECT
            COUNT(CASE WHEN cfp.first_purchase_date BETWEEN %s AND %s THEN 1 END) AS so_khach_hang_moi,
            COUNT(CASE WHEN cfp.first_purchase_date < %s THEN 1 END) AS so_khach_hang_quay_lai
        FROM customers_in_period cip
        JOIN customer_first_purchase cfp ON cip.id_khach_hang = cfp.id_khach_hang;
    """

    # --- SQL để lấy DANH SÁCH chi tiết theo ngày ---
    sql_details = """
        WITH customer_first_purchase AS (
            SELECT id_khach_hang, MIN(ngay_dat_hang::date) as first_purchase_date
            FROM DonHangBan WHERE trang_thai_don_hang = 'Hoàn tất'
            GROUP BY id_khach_hang
        ),
        daily_distinct_activity AS (
            -- Lấy hoạt động (duy nhất) của khách hàng mỗi ngày trong kỳ
            SELECT DISTINCT ngay_dat_hang::date AS report_date, id_khach_hang
            FROM DonHangBan
            WHERE trang_thai_don_hang = 'Hoàn tất' AND ngay_dat_hang::date BETWEEN %s AND %s
        ),
        daily_counts AS (
            -- Phân loại và đếm khách hàng mới/quay lại mỗi ngày
            SELECT
                dda.report_date,
                COUNT(DISTINCT CASE WHEN cfp.first_purchase_date = dda.report_date THEN dda.id_khach_hang END) AS new_customers,
                COUNT(DISTINCT CASE WHEN cfp.first_purchase_date < dda.report_date THEN dda.id_khach_hang END) AS returning_customers
            FROM daily_distinct_activity dda
            JOIN customer_first_purchase cfp ON dda.id_khach_hang = cfp.id_khach_hang
            GROUP BY dda.report_date
        ),
        all_dates AS (
            -- Tạo chuỗi ngày đầy đủ
            SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date AS report_date
        )
        -- Kết hợp để có báo cáo hoàn chỉnh
        SELECT
            ad.report_date AS ky_bao_cao,
            COALESCE(dc.new_customers, 0) AS so_khach_hang_moi,
            COALESCE(dc.returning_customers, 0) AS so_khach_hang_quay_lai
        FROM all_dates ad
        LEFT JOIN daily_counts dc ON ad.report_date = dc.report_date
        ORDER BY ad.report_date ASC;
    """

    conn = get_db_connection()
    if not conn:
        return None

    final_report = {"summary": {}, "details": []}
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Chạy truy vấn tổng hợp
            cur.execute(sql_summary, (start_date, end_date, start_date, end_date, start_date))
            summary_data = cur.fetchone()
            if summary_data:
                final_report['summary'] = dict(summary_data)

            # Chạy truy vấn chi tiết
            cur.execute(sql_details, (start_date, end_date, start_date, end_date))
            final_report['details'] = [dict(row) for row in cur.fetchall()]

    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo báo cáo thu hút khách hàng: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)

    return final_report


def get_top_spending_customers_report(period: str, top_n: int,
                                      start_date_str: str = None, end_date_str: str = None):
    """
    Tạo báo cáo về các khách hàng chi tiêu nhiều nhất.

    Args:
        period (str): Kỳ báo cáo ('yesterday', 'last_week', 'last_month', 'custom').
        top_n (int): Số lượng khách hàng hàng đầu (3, 5, hoặc 10).
        start_date_str (str, optional): Ngày bắt đầu cho 'custom'.
        end_date_str (str, optional): Ngày kết thúc cho 'custom'.

    Returns:
        list or None: Danh sách khách hàng chi tiêu nhiều nhất, hoặc None nếu có lỗi.
    """
    if top_n not in [3, 5, 10]:
        print(f"Lỗi: Giá trị Top N '{top_n}' không hợp lệ.", file=sys.stderr)
        return None
    try:
        start_date, end_date = _get_date_range(period, start_date_str, end_date_str)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return None

    sql = """
        SELECT
            kh.id AS id_khach_hang,
            kh.ten_khach_hang,
            SUM(ctdhb.tong_gia_ban) AS tong_chi_tieu,
            COUNT(DISTINCT dhb.id) AS tong_so_don_hang,
            MAX(dhb.ngay_dat_hang::date) AS ngay_mua_cuoi_cung
        FROM KhachHang kh
        JOIN DonHangBan dhb ON kh.id = dhb.id_khach_hang
        JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
        WHERE dhb.trang_thai_don_hang = 'Hoàn tất'
          AND dhb.ngay_dat_hang::date BETWEEN %s AND %s
        GROUP BY kh.id, kh.ten_khach_hang
        ORDER BY tong_chi_tieu DESC
        LIMIT %s;
    """

    conn = get_db_connection()
    if not conn:
        return None

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (start_date, end_date, top_n))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo báo cáo khách hàng chi tiêu nhiều: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)
