# test/test_10_doanhthuloinhuan.py

import unittest
import sys
import os
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import patch

# --- Thiết lập đường dẫn Project ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports từ ứng dụng của bạn (Sửa lỗi đường dẫn tại đây) ---
from be.reports.operation_10_doanhthuloinhuan import get_financial_report
# Import các hàm phụ trợ để tạo dữ liệu test
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_2_sanpham import add_sanpham
from be.operation.operation_3_nhacungcap import add_nhacungcap
from be.operation.operation_4_khachhang import add_khachhang
from be.operation.operation_5_nhanvien import add_nhanvien
from be.operation.operation_6_donhangnhap import create_donhangnhap, add_item_to_donhangnhap, update_donhangnhap_status
from be.operation.operation_7_donhangban import create_donhangban, add_item_to_donhangban, update_donhangban_status
from be.operation.operation_8_chiphi import add_chiphi
from be.db_connection import get_db_connection, close_db_connection


class TestFinancialReport(unittest.TestCase):
    """
    Bộ kiểm thử cho nghiệp vụ báo cáo tài chính.
    """
    # Đóng băng thời gian để kết quả test luôn nhất quán
    MOCKED_TODAY = date(2025, 6, 10)

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần, thiết lập toàn bộ dữ liệu mẫu cho báo cáo.
        Dữ liệu được tạo một cách có chủ đích để kiểm tra các khoảng thời gian khác nhau.
        """
        print("\n--- Thiết lập môi trường cho Test Báo cáo Tài chính ---")

        # --- Dọn dẹp CSDL ---
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "TRUNCATE TABLE DanhMuc, SanPham, NhanVien, KhachHang, NhaCungCap, DonHangNhap, ChiTietDonHangNhap, DonHangBan, ChiTietDonHangBan, ChiPhi RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

        # --- Tạo các thực thể cơ bản ---
        cls.danhmuc_id = add_danhmuc("DM_REPORT", "Danh mục Report")
        cls.nhanvien_id = add_nhanvien("NV Report", "nv_report", "pass", "nv.report@test.com", "0901231231")
        cls.khachhang_id = add_khachhang("KH Report", "0901231232", "kh.report@test.com")
        cls.nhacungcap_id = add_nhacungcap("NCC Report", "ncc.report@test.com", "123 NCC Street")
        cls.sanpham_id = add_sanpham("SP_REPORT", "Sản phẩm Report", cls.danhmuc_id, 0, "Cái")

        # --- Tạo giá vốn cho sản phẩm (quan trọng cho việc tính lợi nhuận) ---
        cls.gia_von = Decimal('50000')
        dhn_id = create_donhangnhap(cls.nhacungcap_id, cls.nhanvien_id)
        add_item_to_donhangnhap(dhn_id, cls.sanpham_id, 1000, cls.gia_von)
        update_donhangnhap_status(dhn_id, 'Hoàn tất')

        # --- Tạo dữ liệu giao dịch và chi phí trong quá khứ ---
        cls.gia_ban = Decimal('120000')

        # Dữ liệu cho "tháng trước" (Tháng 5, 2025)
        cls.ngay_ban_thang_truoc = date(2025, 5, 15)
        cls.doanh_thu_thang_truoc = cls.gia_ban * 2
        cls.loi_nhuan_gop_thang_truoc = (cls.gia_ban - cls.gia_von) * 2
        cls.chiphi_thang_truoc = Decimal('10000')
        cls._create_completed_sale(cls.ngay_ban_thang_truoc, 2)
        add_chiphi("Chi phí Marketing T5", cls.chiphi_thang_truoc, str(cls.ngay_ban_thang_truoc))

        # Dữ liệu cho "tuần trước" (02/06/2025 - 08/06/2025)
        cls.ngay_ban_tuan_truoc = date(2025, 6, 4)
        cls.doanh_thu_tuan_truoc = cls.gia_ban * 3
        cls.loi_nhuan_gop_tuan_truoc = (cls.gia_ban - cls.gia_von) * 3
        cls.chiphi_tuan_truoc = Decimal('25000')
        cls._create_completed_sale(cls.ngay_ban_tuan_truoc, 3)
        add_chiphi("Chi phí vận chuyển", cls.chiphi_tuan_truoc, str(cls.ngay_ban_tuan_truoc))

        # Dữ liệu cho "hôm qua" (09/06/2025)
        cls.ngay_ban_hom_qua = date(2025, 6, 9)
        cls.doanh_thu_hom_qua = cls.gia_ban * 1
        cls.loi_nhuan_gop_hom_qua = (cls.gia_ban - cls.gia_von) * 1
        cls.chiphi_hom_qua = Decimal('5000')
        cls._create_completed_sale(cls.ngay_ban_hom_qua, 1)
        add_chiphi("Chi phí linh tinh", cls.chiphi_hom_qua, str(cls.ngay_ban_hom_qua))

    @classmethod
    def _create_completed_sale(cls, sale_date, quantity):
        """Hàm helper để tạo một đơn hàng bán đã hoàn tất."""
        dhb_id = create_donhangban(cls.nhanvien_id, cls.khachhang_id, "Địa chỉ Test", ngay_dat_hang_str=str(sale_date))
        add_item_to_donhangban(dhb_id, cls.sanpham_id, quantity, cls.gia_ban, 0)
        update_donhangban_status(dhb_id, 'Hoàn tất', 'Đã thanh toán', str(sale_date))

    # Sửa lỗi đường dẫn Mock tại đây để trỏ đến đúng file của bạn
    @patch('be.reports.operation_10_doanhthuloinhuan.date')
    def test_report_for_yesterday(self, mock_date):
        """Kiểm tra báo cáo cho ngày hôm qua."""
        print("\n--- Test: Báo cáo ngày hôm qua ---")
        mock_date.today.return_value = self.MOCKED_TODAY

        # Đổi tên kỳ báo cáo từ 'day' thành 'yesterday' cho khớp với hàm
        report = get_financial_report(period='yesterday')
        self.assertIsNotNone(report)

        summary = report['summary']
        expected_profit = self.loi_nhuan_gop_hom_qua - self.chiphi_hom_qua
        self.assertEqual(summary['tong_doanh_thu'], self.doanh_thu_hom_qua)
        self.assertEqual(summary['loi_nhuan'], expected_profit)

        details = report['details']
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]['ky_bao_cao'], self.ngay_ban_hom_qua)
        self.assertEqual(details[0]['loi_nhuan'], expected_profit)

    # Sửa lỗi đường dẫn Mock tại đây
    @patch('be.reports.operation_10_doanhthuloinhuan.date')
    def test_report_for_last_week(self, mock_date):
        """Kiểm tra báo cáo cho tuần trước."""
        print("\n--- Test: Báo cáo tuần trước ---")
        mock_date.today.return_value = self.MOCKED_TODAY

        report = get_financial_report(period='last_week')
        self.assertIsNotNone(report)

        summary = report['summary']
        expected_profit = self.loi_nhuan_gop_tuan_truoc - self.chiphi_tuan_truoc
        self.assertEqual(summary['tong_doanh_thu'], self.doanh_thu_tuan_truoc)
        self.assertEqual(summary['loi_nhuan'], expected_profit)

        details = report['details']
        self.assertEqual(len(details), 7)
        transaction_day = next((d for d in details if d['ky_bao_cao'] == self.ngay_ban_tuan_truoc), None)
        self.assertIsNotNone(transaction_day)
        self.assertEqual(transaction_day['loi_nhuan'], expected_profit)

    # Sửa lỗi đường dẫn Mock tại đây
    @patch('be.reports.operation_10_doanhthuloinhuan.date')
    def test_report_for_last_month(self, mock_date):
        """Kiểm tra báo cáo cho tháng trước."""
        print("\n--- Test: Báo cáo tháng trước ---")
        mock_date.today.return_value = self.MOCKED_TODAY

        report = get_financial_report(period='last_month')
        self.assertIsNotNone(report)

        summary = report['summary']
        expected_profit = self.loi_nhuan_gop_thang_truoc - self.chiphi_thang_truoc
        self.assertEqual(summary['tong_doanh_thu'], self.doanh_thu_thang_truoc)
        self.assertEqual(summary['loi_nhuan'], expected_profit)

        details = report['details']
        self.assertEqual(len(details), 31)

    def test_report_for_custom_range(self):
        """Kiểm tra báo cáo cho khoảng thời gian tùy chỉnh."""
        print("\n--- Test: Báo cáo tùy chỉnh ---")

        start_date = "2025-06-01"
        end_date = "2025-06-30"

        report = get_financial_report(period='custom', start_date_str=start_date, end_date_str=end_date)
        self.assertIsNotNone(report)

        expected_revenue = self.doanh_thu_tuan_truoc + self.doanh_thu_hom_qua
        expected_profit = (self.loi_nhuan_gop_tuan_truoc + self.loi_nhuan_gop_hom_qua) - (
                    self.chiphi_tuan_truoc + self.chiphi_hom_qua)

        self.assertEqual(report['summary']['tong_doanh_thu'], expected_revenue)
        self.assertEqual(report['summary']['loi_nhuan'], expected_profit)

        details = report['details']
        self.assertEqual(len(details), 30)

    def test_report_for_no_data_range(self):
        """Kiểm tra báo cáo cho khoảng thời gian không có dữ liệu."""
        print("\n--- Test: Báo cáo không có dữ liệu ---")

        report = get_financial_report(period='custom', start_date_str="2024-01-01", end_date_str="2024-01-31")
        self.assertIsNotNone(report)

        self.assertEqual(report['summary']['tong_doanh_thu'], 0)
        self.assertEqual(report['summary']['loi_nhuan'], 0)
        self.assertEqual(len(report['details']), 31)
        self.assertTrue(all(d['tong_doanh_thu'] == 0 for d in report['details']))


if __name__ == '__main__':
    unittest.main()
