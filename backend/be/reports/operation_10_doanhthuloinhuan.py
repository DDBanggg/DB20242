# be/reports/operation_10_doanhthuloinhuan.py

import psycopg2
import psycopg2.extras
from datetime import date, timedelta
import sys
from be.db_connection import get_db_connection, close_db_connection


def get_financial_report(period: str, start_date_str: str = None, end_date_str: str = None):
    """
    Tạo báo cáo tài chính với một dòng tổng hợp và danh sách chi tiết theo ngày.

    Cấu trúc trả về:
    {
        "summary": { "tong_doanh_thu": X, "loi_nhuan": Y, "ky_bao_cao": "..." },
        "details": [ { "ky_bao_cao": "YYYY-MM-DD", "tong_doanh_thu": A, "loi_nhuan": B }, ... ]
    }

    Args:
        period (str): Kỳ báo cáo. Chấp nhận các giá trị:
                      'yesterday': Báo cáo cho ngày hôm qua.
                      'last_week': Báo cáo cho tuần trước (Thứ 2 - Chủ Nhật).
                      'last_month': Báo cáo cho tháng trước.
                      'custom': Báo cáo cho một khoảng thời gian tùy chỉnh.
        start_date_str (str, optional): Ngày bắt đầu cho 'custom' (YYYY-MM-DD).
        end_date_str (str, optional): Ngày kết thúc cho 'custom' (YYYY-MM-DD).

    Returns:
        dict or None: Một dictionary chứa báo cáo, hoặc None nếu có lỗi.
    """
    # --- 1. Xác thực đầu vào và tính toán khoảng ngày ---
    allowed_periods = ['yesterday', 'last_week', 'last_month', 'custom']
    if period not in allowed_periods:
        print(f"Lỗi: Kỳ báo cáo '{period}' không hợp lệ.", file=sys.stderr)
        return None

    today = date.today()
    start_date, end_date = None, None
    report_period_label = ""

    try:
        if period == 'yesterday':
            start_date = end_date = today - timedelta(days=1)
            report_period_label = f"Ngày {start_date.strftime('%d-%m-%Y')}"
        elif period == 'last_week':
            # Đi về Chủ Nhật của tuần trước
            end_date = today - timedelta(days=today.weekday() + 1)
            # Đi về Thứ Hai của tuần đó
            start_date = end_date - timedelta(days=6)
            report_period_label = f"Tuần {start_date.strftime('%d-%m-%Y')} đến {end_date.strftime('%d-%m-%Y')}"
        elif period == 'last_month':
            # Đi về ngày cuối cùng của tháng trước
            end_date = today.replace(day=1) - timedelta(days=1)
            # Đi về ngày đầu tiên của tháng đó
            start_date = end_date.replace(day=1)
            report_period_label = f"Tháng {start_date.strftime('%m-%Y')}"
        elif period == 'custom':
            if not start_date_str or not end_date_str:
                raise ValueError("Với period='custom', cần cung cấp ngày bắt đầu và kết thúc.")
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            if start_date > end_date:
                raise ValueError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")
            report_period_label = f"Tùy chỉnh từ {start_date.strftime('%d-%m-%Y')} đến {end_date.strftime('%d-%m-%Y')}"

    except ValueError as e:
        print(f"Lỗi xử lý ngày tháng: {e}", file=sys.stderr)
        return None

    # --- 2. Định nghĩa các câu lệnh SQL ---

    # SQL để lấy MỘT DÒNG tổng hợp cho toàn bộ kỳ báo cáo
    sql_summary = """
        WITH sales_profit AS (
            -- Tính tổng doanh thu và lợi nhuận gộp từ các đơn hàng đã 'Hoàn tất'
            SELECT
                SUM(ctdhb.tong_gia_ban) AS total_revenue,
                SUM(ctdhb.tong_gia_ban - ctdhb.tong_gia_von) AS gross_profit
            FROM DonHangBan dhb
            JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
            WHERE dhb.trang_thai_don_hang = 'Hoàn tất'
              AND dhb.ngay_dat_hang::date BETWEEN %s AND %s
        ), expenses AS (
            -- Tính tổng chi phí trong kỳ
            SELECT SUM(so_tien) AS total_expense
            FROM ChiPhi
            WHERE ngay_chi_phi BETWEEN %s AND %s
        )
        -- Kết hợp lại để tính lợi nhuận ròng
        SELECT
            COALESCE((SELECT total_revenue FROM sales_profit), 0) AS tong_doanh_thu,
            (COALESCE((SELECT gross_profit FROM sales_profit), 0) - COALESCE((SELECT total_expense FROM expenses), 0)) AS loi_nhuan;
    """

    # SQL để lấy DANH SÁCH chi tiết theo từng ngày trong kỳ
    sql_details = """
        WITH daily_sales AS (
            -- Gom nhóm doanh thu và lợi nhuận gộp theo ngày
            SELECT
                DATE_TRUNC('day', dhb.ngay_dat_hang)::date AS report_date,
                SUM(ctdhb.tong_gia_ban) AS total_revenue,
                SUM(ctdhb.tong_gia_ban - ctdhb.tong_gia_von) AS gross_profit
            FROM DonHangBan dhb
            JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
            WHERE dhb.trang_thai_don_hang = 'Hoàn tất' AND dhb.ngay_dat_hang::date BETWEEN %s AND %s
            GROUP BY report_date
        ), daily_expenses AS (
            -- Gom nhóm chi phí theo ngày
            SELECT
                ngay_chi_phi AS report_date,
                SUM(so_tien) AS total_expense
            FROM ChiPhi
            WHERE ngay_chi_phi BETWEEN %s AND %s
            GROUP BY report_date
        ), all_dates AS (
            -- Tạo một chuỗi đầy đủ các ngày trong kỳ để đảm bảo không ngày nào bị thiếu
            SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date AS report_date
        )
        -- Kết hợp tất cả lại
        SELECT
            ad.report_date AS ky_bao_cao,
            COALESCE(ds.total_revenue, 0) AS tong_doanh_thu,
            (COALESCE(ds.gross_profit, 0) - COALESCE(de.total_expense, 0)) AS loi_nhuan
        FROM all_dates ad
        LEFT JOIN daily_sales ds ON ad.report_date = ds.report_date
        LEFT JOIN daily_expenses de ON ad.report_date = de.report_date
        ORDER BY ad.report_date ASC;
    """

    # --- 3. Thực thi và xây dựng kết quả ---
    conn = get_db_connection()
    if not conn:
        return None

    final_report = {"summary": {}, "details": []}
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Chạy truy vấn tổng hợp
            cur.execute(sql_summary, (start_date, end_date, start_date, end_date))
            summary_data = cur.fetchone()
            if summary_data:
                final_report['summary'] = dict(summary_data)
                final_report['summary']['ky_bao_cao'] = report_period_label

            # Chạy truy vấn chi tiết
            cur.execute(sql_details, (start_date, end_date, start_date, end_date, start_date, end_date))
            final_report['details'] = [dict(row) for row in cur.fetchall()]

    except psycopg2.Error as e:
        print(f"Lỗi CSDL khi thực thi báo cáo tài chính: {e}", file=sys.stderr)
        return None
    finally:
        close_db_connection(conn)

    return final_report
