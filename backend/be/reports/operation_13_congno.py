# be/reports/operation_13_congno.py

import psycopg2
import psycopg2.extras
from datetime import date
import sys
from be.db_connection import get_db_connection, close_db_connection


def get_receivables_report(overdue_only: bool = False):
    """
    Tạo báo cáo về công nợ phải thu của khách hàng.

    Một đơn hàng được tính là công nợ khi:
    - trang_thai_don_hang là 'Đã giao' hoặc 'Hoàn tất'.
    - trang_thai_thanh_toan là 'Chưa thanh toán'.
    - Một khoản nợ được coi là 'quá hạn' nếu ngày hiện tại > ngày giao hàng thực tế + 30 ngày.

    Cấu trúc trả về:
    {
        "summary": { "tong_cong_no_phai_thu": X, "tong_cong_no_qua_han": Y },
        "details": [ { "id_khach_hang": A, "ten_khach_hang": "...", "tong_cong_no": B, "cong_no_qua_han": C }, ... ]
    }

    Args:
        overdue_only (bool, optional): Nếu True, chỉ trả về chi tiết của các khách hàng
                                     có nợ quá hạn. Mặc định là False.

    Returns:
        dict or None: Một dictionary chứa báo cáo, hoặc None nếu có lỗi.
    """
    # --- 1. Định nghĩa các câu lệnh SQL ---

    # SQL để lấy MỘT DÒNG tổng hợp toàn bộ công nợ
    sql_summary = """
        WITH unpaid_orders_value AS (
            -- Tính toán giá trị của từng đơn hàng chưa thanh toán
            SELECT
                -- Dùng SUM ở đây vì một đơn hàng có thể có nhiều chi tiết
                SUM(ctdhb.tong_gia_ban) AS order_value,
                -- Tính giá trị quá hạn, chỉ khi ngày giao hàng thực tế tồn tại
                CASE
                    WHEN dhb.ngay_giao_hang_thuc_te IS NOT NULL AND (CURRENT_DATE - dhb.ngay_giao_hang_thuc_te > 30)
                    THEN SUM(ctdhb.tong_gia_ban)
                    ELSE 0
                END AS overdue_value
            FROM DonHangBan dhb
            JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
            WHERE
                dhb.trang_thai_don_hang IN ('Đã giao', 'Hoàn tất')
                AND dhb.trang_thai_thanh_toan = 'Chưa thanh toán'
            GROUP BY dhb.id, dhb.ngay_giao_hang_thuc_te
        )
        -- Tổng hợp lại tất cả các đơn hàng
        SELECT
            COALESCE(SUM(order_value), 0) AS tong_cong_no_phai_thu,
            COALESCE(SUM(overdue_value), 0) AS tong_cong_no_qua_han
        FROM unpaid_orders_value;
    """

    # SQL để lấy DANH SÁCH chi tiết công nợ theo từng khách hàng
    # Phần này được xây dựng động để có thể thêm bộ lọc overdue_only
    base_sql_details = """
        WITH unpaid_orders_value AS (
            -- Tương tự như trên, tính giá trị từng đơn hàng
            SELECT
                dhb.id_khach_hang,
                SUM(ctdhb.tong_gia_ban) AS order_value,
                CASE
                    WHEN dhb.ngay_giao_hang_thuc_te IS NOT NULL AND (CURRENT_DATE - dhb.ngay_giao_hang_thuc_te > 30)
                    THEN SUM(ctdhb.tong_gia_ban)
                    ELSE 0
                END AS overdue_value
            FROM DonHangBan dhb
            JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
            WHERE
                dhb.trang_thai_don_hang IN ('Đã giao', 'Hoàn tất')
                AND dhb.trang_thai_thanh_toan = 'Chưa thanh toán'
            GROUP BY dhb.id, dhb.id_khach_hang, dhb.ngay_giao_hang_thuc_te
        ),
        customer_debt AS (
            -- Gom nhóm công nợ theo từng khách hàng
            SELECT
                kh.id AS id_khach_hang,
                kh.ten_khach_hang,
                SUM(uov.order_value) AS tong_cong_no,
                SUM(uov.overdue_value) AS cong_no_qua_han
            FROM unpaid_orders_value uov
            JOIN KhachHang kh ON uov.id_khach_hang = kh.id
            GROUP BY kh.id, kh.ten_khach_hang
        )
        SELECT * FROM customer_debt
    """

    # Thêm điều kiện lọc nếu cần
    if overdue_only:
        final_sql_details = base_sql_details + " WHERE cong_no_qua_han > 0 ORDER BY cong_no_qua_han DESC;"
    else:
        final_sql_details = base_sql_details + " ORDER BY tong_cong_no DESC;"

    # --- 2. Thực thi và xây dựng kết quả ---
    conn = get_db_connection()
    if not conn:
        return None

    final_report = {"summary": {}, "details": []}
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Chạy truy vấn tổng hợp
            cur.execute(sql_summary)
            summary_data = cur.fetchone()
            if summary_data:
                final_report['summary'] = dict(summary_data)

            # Chạy truy vấn chi tiết
            cur.execute(final_sql_details)
            final_report['details'] = [dict(row) for row in cur.fetchall()]

    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi tạo báo cáo công nợ phải thu: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)

    return final_report
