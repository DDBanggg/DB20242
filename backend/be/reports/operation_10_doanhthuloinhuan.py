# be/reports/operation_10_doanhthuloinhuan.py

import psycopg2
import psycopg2.extras
from datetime import date, timedelta
import sys
from be.db_connection import get_db_connection, close_db_connection

def get_financial_report(period: str, start_date_str: str = None, end_date_str: str = None):
    # ... (Phần 1: Xử lý ngày tháng period giữ nguyên như cũ) ...
    # (Copy lại đoạn check period, start_date, end_date từ code cũ của bạn)
    allowed_periods = ['yesterday', 'last_week', 'last_month', 'custom']
    if period not in allowed_periods: return None
    today = date.today()
    start_date, end_date = None, None
    report_period_label = ""
    # ... (Code xử lý ngày tháng giữ nguyên) ...
    if period == 'yesterday':
        start_date = end_date = today - timedelta(days=1)
        report_period_label = f"Ngày {start_date}"
    elif period == 'last_week':
        end_date = today - timedelta(days=today.weekday() + 1)
        start_date = end_date - timedelta(days=6)
        report_period_label = f"Tuần {start_date} -> {end_date}"
    elif period == 'last_month':
        end_date = today.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)
        report_period_label = f"Tháng {start_date.strftime('%m-%Y')}"
    elif period == 'custom':
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
        report_period_label = f"Từ {start_date} đến {end_date}"

    # --- PHẦN QUAN TRỌNG: CẬP NHẬT SQL TÍNH TOÁN ---
    
    # Hệ số thuế: 10% VAT + 1.5% HKD = 11.5% = 0.115
    TAX_RATE = 0.115

    # 1. SQL Tổng hợp
    sql_summary = f"""
        WITH sales_data AS (
            SELECT
                SUM(ctdhb.tong_gia_ban) AS revenue,
                SUM(ctdhb.tong_gia_von) AS cogs -- Cost of Goods Sold
            FROM DonHangBan dhb
            JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
            WHERE dhb.trang_thai_don_hang = 'Hoàn tất'
              AND dhb.ngay_dat_hang::date BETWEEN %s AND %s
        ), expenses AS (
            SELECT SUM(so_tien) AS total_expense
            FROM ChiPhi
            WHERE ngay_chi_phi BETWEEN %s AND %s
        )
        SELECT
            COALESCE((SELECT revenue FROM sales_data), 0) AS tong_doanh_thu,
            
            -- Lợi nhuận = (Doanh thu - Giá vốn) - (Doanh thu * {TAX_RATE}) - Chi phí
            (
                COALESCE((SELECT revenue FROM sales_data), 0) 
                - COALESCE((SELECT cogs FROM sales_data), 0)
                - (COALESCE((SELECT revenue FROM sales_data), 0) * {TAX_RATE})
                - COALESCE((SELECT total_expense FROM expenses), 0)
            ) AS loi_nhuan
    """

    # 2. SQL Chi tiết theo ngày
    sql_details = f"""
        WITH daily_sales AS (
            SELECT
                DATE_TRUNC('day', dhb.ngay_dat_hang)::date AS report_date,
                SUM(ctdhb.tong_gia_ban) AS revenue,
                SUM(ctdhb.tong_gia_von) AS cogs
            FROM DonHangBan dhb
            JOIN ChiTietDonHangBan ctdhb ON dhb.id = ctdhb.id_don_hang_ban
            WHERE dhb.trang_thai_don_hang = 'Hoàn tất' AND dhb.ngay_dat_hang::date BETWEEN %s AND %s
            GROUP BY report_date
        ), daily_expenses AS (
            SELECT ngay_chi_phi AS report_date, SUM(so_tien) AS total_expense
            FROM ChiPhi WHERE ngay_chi_phi BETWEEN %s AND %s GROUP BY report_date
        ), all_dates AS (
            SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date AS report_date
        )
        SELECT
            ad.report_date AS ky_bao_cao,
            COALESCE(ds.revenue, 0) AS tong_doanh_thu,
            
            -- Công thức lợi nhuận lặp lại cho từng dòng
            (
                COALESCE(ds.revenue, 0) 
                - COALESCE(ds.cogs, 0)
                - (COALESCE(ds.revenue, 0) * {TAX_RATE})
                - COALESCE(de.total_expense, 0)
            ) AS loi_nhuan
        FROM all_dates ad
        LEFT JOIN daily_sales ds ON ad.report_date = ds.report_date
        LEFT JOIN daily_expenses de ON ad.report_date = de.report_date
        ORDER BY ad.report_date ASC;
    """

    conn = get_db_connection()
    if not conn: return None
    final_report = {"summary": {}, "details": []}
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql_summary, (start_date, end_date, start_date, end_date))
            summary_data = cur.fetchone()
            if summary_data:
                final_report['summary'] = dict(summary_data)
                final_report['summary']['ky_bao_cao'] = report_period_label

            cur.execute(sql_details, (start_date, end_date, start_date, end_date, start_date, end_date))
            final_report['details'] = [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        close_db_connection(conn)

    return final_report