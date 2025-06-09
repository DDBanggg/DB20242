# test/test_13_receivables_report.py

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
from be.reports.operation_13_congno import get_receivables_report
# Import các hàm phụ trợ để tạo dữ liệu test
from be.operation.operation_2_sanpham import add_sanpham
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_4_khachhang import add_khachhang
from be.operation.operation_5_nhanvien import add_nhanvien
from be.operation.operation_7_donhangban import create_donhangban, add_item_to_donhangban, update_donhangban_status
from be.db_connection import get_db_connection, close_db_connection


class TestReceivablesReport(unittest.TestCase):
    """
    Bộ kiểm thử cho nghiệp vụ báo cáo công nợ phải thu.
    """
    # Đóng băng thời gian để kết quả test luôn nhất quán
    # Giả định hôm nay là 2025-06-10
    MOCKED_TODAY = date(2025, 6, 10)

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần, thiết lập toàn bộ dữ liệu mẫu cho báo cáo công nợ.
        """
        print("\n--- Thiết lập môi trường cho Test Báo cáo Công nợ ---")

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
        cls.nhanvien_id = add_nhanvien("NV Cong No", "nv_congno", "pass", "nv.cn@test.com", "0988888888")
        cls.danhmuc_id = add_danhmuc("DM_CN", "Danh mục CN")
        cls.sanpham_id = add_sanpham("SP_CN", "SP Công Nợ", cls.danhmuc_id, 100, "Cái")

        # --- Tạo kịch bản công nợ ---
        # KH 1: Có nợ, nhưng CHƯA quá hạn (giao hàng 20 ngày trước)
        cls.kh_trong_han_id = add_khachhang("KH Trong Hạn", "0988888881", "kh.tronghan@test.com")
        cls.no_trong_han = Decimal('1000000')
        cls._create_unpaid_sale(date(2025, 5, 21), cls.kh_trong_han_id, cls.no_trong_han)

        # KH 2: Có nợ, và ĐÃ quá hạn (giao hàng 40 ngày trước)
        cls.kh_qua_han_id = add_khachhang("KH Quá Hạn", "0988888882", "kh.quahan@test.com")
        cls.no_qua_han = Decimal('2500000')
        cls._create_unpaid_sale(date(2025, 5, 1), cls.kh_qua_han_id, cls.no_qua_han)

        # KH 3: Không có nợ (đơn hàng đã thanh toán)
        cls.kh_khong_no_id = add_khachhang("KH Không Nợ", "0988888883", "kh.khongno@test.com")
        cls._create_unpaid_sale(date(2025, 5, 5), cls.kh_khong_no_id, Decimal('500000'), paid=True)

    @classmethod
    def _create_unpaid_sale(cls, delivery_date, customer_id, total_value, paid=False):
        """Hàm helper để tạo một đơn hàng đã giao nhưng chưa thanh toán."""
        payment_status = 'Đã thanh toán' if paid else 'Chưa thanh toán'
        dhb_id = create_donhangban(cls.nhanvien_id, customer_id, "Địa chỉ Test", trang_thai_thanh_toan=payment_status)
        add_item_to_donhangban(dhb_id, cls.sanpham_id, 1, total_value, 0)
        # Cập nhật trạng thái là 'Đã giao' và có ngày giao hàng thực tế
        update_donhangban_status(dhb_id, 'Đã giao', ngay_giao_hang_thuc_te_str=str(delivery_date))

    @patch('be.reports.operation_13_receivables_report.date')
    def test_1_get_full_receivables_report(self, mock_date):
        """
        Kiểm tra báo cáo đầy đủ (cả nợ trong hạn và quá hạn).
        """
        print("\n--- Test 1: Báo cáo công nợ đầy đủ ---")
        # Giả lập CURRENT_DATE trong SQL là ngày MOCKED_TODAY của chúng ta
        mock_date.today.return_value = self.MOCKED_TODAY

        # Để mock CURRENT_DATE trong câu lệnh SQL, chúng ta cần một cách tiếp cận khác một chút
        # Cách đơn giản nhất là tạm thời sửa câu lệnh SQL để kiểm thử
        # Tuy nhiên, ở đây chúng ta sẽ tính toán và kiểm tra kết quả dựa trên giả định MOCKED_TODAY

        report = get_receivables_report(overdue_only=False)
        self.assertIsNotNone(report, "Báo cáo trả về None.")

        # --- Kiểm tra Summary ---
        summary = report['summary']
        tong_cong_no_ky_vong = self.no_trong_han + self.no_qua_han
        self.assertEqual(summary['tong_cong_no_phai_thu'], tong_cong_no_ky_vong)
        self.assertEqual(summary['tong_cong_no_qua_han'], self.no_qua_han)

        # --- Kiểm tra Details ---
        details = report['details']
        # Phải có 2 khách hàng có nợ: Trong Hạn và Quá Hạn
        self.assertEqual(len(details), 2, "Số lượng khách hàng có nợ không đúng.")

        # Tìm và kiểm tra khách hàng quá hạn
        kh_quahan_details = next((d for d in details if d['id_khach_hang'] == self.kh_qua_han_id), None)
        self.assertIsNotNone(kh_quahan_details, "Không tìm thấy chi tiết của khách hàng quá hạn.")
        self.assertEqual(kh_quahan_details['tong_cong_no'], self.no_qua_han)
        self.assertEqual(kh_quahan_details['cong_no_qua_han'], self.no_qua_han)

        # Tìm và kiểm tra khách hàng trong hạn
        kh_tronghan_details = next((d for d in details if d['id_khach_hang'] == self.kh_trong_han_id), None)
        self.assertIsNotNone(kh_tronghan_details, "Không tìm thấy chi tiết của khách hàng trong hạn.")
        self.assertEqual(kh_tronghan_details['tong_cong_no'], self.no_trong_han)
        self.assertEqual(kh_tronghan_details['cong_no_qua_han'], 0)

        print("=> PASS: Báo cáo công nợ đầy đủ chính xác.")

    @patch('be.reports.operation_13_receivables_report.date')
    def test_2_get_overdue_only_report(self, mock_date):
        """
        Kiểm tra báo cáo chỉ hiển thị các khoản nợ quá hạn.
        """
        print("\n--- Test 2: Báo cáo chỉ nợ quá hạn ---")
        mock_date.today.return_value = self.MOCKED_TODAY

        report = get_receivables_report(overdue_only=True)
        self.assertIsNotNone(report, "Báo cáo trả về None.")

        # --- Kiểm tra Summary (vẫn phải là tổng tất cả) ---
        summary = report['summary']
        tong_cong_no_ky_vong = self.no_trong_han + self.no_qua_han
        self.assertEqual(summary['tong_cong_no_phai_thu'], tong_cong_no_ky_vong)
        self.assertEqual(summary['tong_cong_no_qua_han'], self.no_qua_han)

        # --- Kiểm tra Details (chỉ có 1 khách hàng quá hạn) ---
        details = report['details']
        self.assertEqual(len(details), 1, "Báo cáo chỉ nợ quá hạn phải có đúng 1 khách hàng.")
        self.assertEqual(details[0]['id_khach_hang'], self.kh_qua_han_id)

        print("=> PASS: Lọc công nợ quá hạn chính xác.")


if __name__ == '__main__':
    unittest.main()
