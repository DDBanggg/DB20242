# test/test_12_customer_analysis.py

import unittest
import sys
import os
from decimal import Decimal
from datetime import date
from unittest.mock import patch

# --- Thiết lập đường dẫn Project ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports từ ứng dụng của bạn ---
from be.reports.operation_12_phantichkhachhang import *
# Import các hàm phụ trợ để tạo dữ liệu test
from be.operation.operation_2_sanpham import add_sanpham
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_4_khachhang import add_khachhang
from be.operation.operation_5_nhanvien import add_nhanvien
from be.operation.operation_7_donhangban import create_donhangban, add_item_to_donhangban, update_donhangban_status
from be.db_connection import get_db_connection, close_db_connection


class TestCustomerAnalysis(unittest.TestCase):
    """
    Bộ kiểm thử cho các nghiệp vụ phân tích khách hàng.
    """
    MOCKED_TODAY = date(2025, 6, 10)

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần, thiết lập toàn bộ dữ liệu mẫu cho các báo cáo.
        Dữ liệu được tạo có chủ đích để kiểm tra logic khách hàng mới/cũ.
        """
        print("\n--- Thiết lập môi trường cho Test Phân tích Khách hàng ---")

        # Dọn dẹp CSDL
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "TRUNCATE TABLE DanhMuc, SanPham, NhanVien, KhachHang, DonHangBan, ChiTietDonHangBan RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

        # --- Tạo các thực thể cơ bản ---
        cls.nhanvien_id = add_nhanvien("NV Analysis", "nv_analysis", "pass", "nv.analysis@test.com", "0933333333")
        # FIX: Sửa mã danh mục thành 10 ký tự hoặc ít hơn
        cls.danhmuc_id = add_danhmuc("DM_ANLYS", "Danh mục Analysis")
        cls.sanpham_id = add_sanpham("SP_ANALYSIS", "SP Analysis", cls.danhmuc_id, 100, "Cái")

        # --- Tạo kịch bản khách hàng ---
        # KH 1: Khách hàng cũ, đã mua từ lâu
        cls.kh_cu_id = add_khachhang("Khách Hàng Cũ", "0944444444", "kh.cu@test.com")
        cls._create_completed_sale(date(2024, 12, 15), cls.kh_cu_id, 1, Decimal('100'))

        # KH 2: Khách hàng mới, đơn đầu tiên trong kỳ báo cáo
        cls.kh_moi_id = add_khachhang("Khách Hàng Mới", "0955555555", "kh.moi@test.com")

        # KH 3: Khách hàng chi tiêu nhiều
        cls.kh_vip_id = add_khachhang("Khách Hàng VIP", "0966666666", "kh.vip@test.com")

        # --- Tạo dữ liệu bán hàng trong "tháng trước" (Tháng 5, 2025) ---
        # KH Cũ mua lại
        cls._create_completed_sale(date(2025, 5, 10), cls.kh_cu_id, 2, Decimal('150'))  # Chi tiêu: 300
        # KH Mới có đơn đầu tiên
        cls._create_completed_sale(date(2025, 5, 20), cls.kh_moi_id, 3, Decimal('200'))  # Chi tiêu: 600
        # KH VIP có 2 đơn hàng
        cls._create_completed_sale(date(2025, 5, 25), cls.kh_vip_id, 5, Decimal('100'))  # Chi tiêu: 500
        cls._create_completed_sale(date(2025, 5, 28), cls.kh_vip_id, 4, Decimal('120'))  # Chi tiêu: 480
        # => Tổng chi tiêu KH VIP: 980

    @classmethod
    def _create_completed_sale(cls, sale_date, customer_id, quantity, price):
        """Hàm helper để tạo một đơn hàng bán đã hoàn tất."""
        dhb_id = create_donhangban(cls.nhanvien_id, customer_id, "Địa chỉ Test", ngay_dat_hang_str=str(sale_date))
        add_item_to_donhangban(dhb_id, cls.sanpham_id, quantity, price, 0)
        update_donhangban_status(dhb_id, 'Hoàn tất', 'Đã thanh toán', str(sale_date))

    @patch('be.reports.operation_12_customer_analysis.date')
    def test_1_get_customer_acquisition_report(self, mock_date):
        """
        Kiểm tra báo cáo khách hàng mới và khách hàng quay lại.
        """
        print("\n--- Test 1: Báo cáo thu hút khách hàng ---")
        mock_date.today.return_value = self.MOCKED_TODAY

        report = get_customer_acquisition_report('last_month')
        self.assertIsNotNone(report)

        # Kiểm tra summary: 2 khách hàng mới (Mới, VIP), 1 khách hàng quay lại (Cũ)
        summary = report['summary']
        self.assertEqual(summary['so_khach_hang_moi'], 2)
        self.assertEqual(summary['so_khach_hang_quay_lai'], 1)

        # Kiểm tra details
        details = report['details']
        self.assertEqual(len(details), 31)  # Tháng 5 có 31 ngày

        # Tìm ngày có khách quay lại
        day_returning = next((d for d in details if d['ky_bao_cao'] == date(2025, 5, 10)), None)
        self.assertIsNotNone(day_returning)
        self.assertEqual(day_returning['so_khach_hang_moi'], 0)
        self.assertEqual(day_returning['so_khach_hang_quay_lai'], 1)

        # Tìm ngày có khách mới
        day_new = next((d for d in details if d['ky_bao_cao'] == date(2025, 5, 20)), None)
        self.assertIsNotNone(day_new)
        self.assertEqual(day_new['so_khach_hang_moi'], 1)
        self.assertEqual(day_new['so_khach_hang_quay_lai'], 0)
        print("=> PASS: Báo cáo thu hút khách hàng chính xác.")

    def test_2_get_top_spending_customers_report(self):
        """
        Kiểm tra báo cáo các khách hàng chi tiêu nhiều nhất.
        """
        print("\n--- Test 2: Báo cáo top khách hàng chi tiêu ---")

        # Lấy báo cáo cho tháng 5
        start_date_str = "2025-05-01"
        end_date_str = "2025-05-31"

        # --- Kiểm tra Top 3 ---
        report_top_3 = get_top_spending_customers_report('custom', 3, start_date_str, end_date_str)
        self.assertIsNotNone(report_top_3)
        self.assertEqual(len(report_top_3), 3)

        # Kiểm tra người đứng đầu phải là KH VIP
        top_customer = report_top_3[0]
        self.assertEqual(top_customer['id_khach_hang'], self.kh_vip_id)
        self.assertEqual(top_customer['tong_chi_tieu'], Decimal('980'))
        self.assertEqual(top_customer['tong_so_don_hang'], 2)
        self.assertEqual(top_customer['ngay_mua_cuoi_cung'], date(2025, 5, 28))

        # --- Kiểm tra Top 5, 10 ---
        # Vì chỉ có 3 khách hàng, kết quả trả về cũng chỉ có 3
        report_top_5 = get_top_spending_customers_report('custom', 5, start_date_str, end_date_str)
        self.assertEqual(len(report_top_5), 3)

        report_top_10 = get_top_spending_customers_report('custom', 10, start_date_str, end_date_str)
        self.assertEqual(len(report_top_10), 3)

        # --- Kiểm tra trường hợp không có dữ liệu ---
        report_no_data = get_top_spending_customers_report('custom', 3, "2024-01-01", "2024-01-31")
        self.assertIsNotNone(report_no_data)
        self.assertEqual(len(report_no_data), 0)

        print("=> PASS: Báo cáo top khách hàng chi tiêu chính xác.")


if __name__ == '__main__':
    unittest.main()
