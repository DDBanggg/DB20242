# test/test_11_sales_statistics.py

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
from be.reports.operation_11_thongkebanhang import *
# Import các hàm phụ trợ để tạo dữ liệu test
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_2_sanpham import add_sanpham
from be.operation.operation_4_khachhang import add_khachhang
from be.operation.operation_5_nhanvien import add_nhanvien
from be.operation.operation_7_donhangban import create_donhangban, add_item_to_donhangban, update_donhangban_status
from be.db_connection import get_db_connection, close_db_connection


class TestSalesStatistics(unittest.TestCase):
    """
    Bộ kiểm thử cho các nghiệp vụ thống kê bán hàng.
    """
    MOCKED_TODAY = date(2025, 6, 10)

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần, thiết lập toàn bộ dữ liệu mẫu cho các báo cáo.
        """
        print("\n--- Thiết lập môi trường cho Test Thống kê Bán hàng ---")

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
        cls.nhanvien_id = add_nhanvien("NV Stats", "nv_stats", "pass", "nv.stats@test.com", "0911111111")
        cls.khachhang_id = add_khachhang("KH Stats", "0922222222", "kh.stats@test.com")

        # Tạo 2 danh mục
        cls.cat_dienthoai_id = add_danhmuc("DT", "Điện thoại")
        cls.cat_phukien_id = add_danhmuc("PK", "Phụ kiện")

        # --- Tạo sản phẩm với các mức tồn kho khác nhau ---
        cls.sp_high_stock_id = add_sanpham("SP_HS", "SP Tồn kho nhiều", cls.cat_dienthoai_id, 150, "Cái")
        cls.sp_low_stock_id = add_sanpham("SP_LS", "SP Tồn kho ít", cls.cat_dienthoai_id, 5, "Cái")
        cls.sp_normal_stock_id = add_sanpham("SP_NS", "SP Tồn kho TB", cls.cat_phukien_id, 50, "Cái")

        # --- Tạo dữ liệu bán hàng có chủ đích để test "bán chạy" ---
        # SP1: Doanh thu cao, số lượng ít
        cls.sp1_id = add_sanpham("SP_SALE_1", "SP Doanh thu cao", cls.cat_dienthoai_id, 100, "Cái")
        # SP2: Số lượng nhiều, doanh thu thấp
        cls.sp2_id = add_sanpham("SP_SALE_2", "SP Số lượng nhiều", cls.cat_phukien_id, 100, "Cái")

        # Tạo 2 đơn hàng vào tuần trước (2025-06-04)
        sale_date_last_week = date(2025, 6, 4)
        # Đơn 1: Bán 2 cái SP1
        cls._create_completed_sale(sale_date_last_week, cls.sp1_id, 2, Decimal('1000'))  # Doanh thu: 2000
        # Đơn 2: Bán 5 cái SP2
        cls._create_completed_sale(sale_date_last_week, cls.sp2_id, 5, Decimal('100'))  # Doanh thu: 500

        # Tạo 1 đơn hàng vào hôm qua (2025-06-09)
        sale_date_yesterday = date(2025, 6, 9)
        # Bán thêm 3 cái SP2
        cls._create_completed_sale(sale_date_yesterday, cls.sp2_id, 3, Decimal('100'))  # Doanh thu: 300

    @classmethod
    def _create_completed_sale(cls, sale_date, product_id, quantity, price):
        """Hàm helper để tạo một đơn hàng bán đã hoàn tất."""
        dhb_id = create_donhangban(cls.nhanvien_id, cls.khachhang_id, "Địa chỉ Test", ngay_dat_hang_str=str(sale_date))
        add_item_to_donhangban(dhb_id, product_id, quantity, price, 0)
        update_donhangban_status(dhb_id, 'Hoàn tất', 'Đã thanh toán', str(sale_date))

    @patch('be.reports.operation_11_sales_statistics.date')
    def test_1_get_order_count_report(self, mock_date):
        """Kiểm tra báo cáo số lượng đơn hàng."""
        print("\n--- Test 1: Báo cáo số lượng đơn hàng ---")
        mock_date.today.return_value = self.MOCKED_TODAY

        report = get_order_count_report('last_week')
        self.assertIsNotNone(report)
        self.assertEqual(len(report), 7, "Báo cáo tuần phải có 7 ngày.")

        # Tìm ngày có 2 đơn hàng
        day_with_2_orders = next((d for d in report if d['ky_bao_cao'] == date(2025, 6, 4)), None)
        self.assertIsNotNone(day_with_2_orders)
        self.assertEqual(day_with_2_orders['so_luong_don_hang'], 2)

        # Tìm ngày không có đơn hàng
        day_with_0_orders = next((d for d in report if d['ky_bao_cao'] == date(2025, 6, 5)), None)
        self.assertIsNotNone(day_with_0_orders)
        self.assertEqual(day_with_0_orders['so_luong_don_hang'], 0)
        print("=> PASS: Báo cáo số lượng đơn hàng chính xác.")

    def test_2_get_best_selling_products_report(self):
        """Kiểm tra báo cáo sản phẩm bán chạy theo các tiêu chí."""
        print("\n--- Test 2: Báo cáo sản phẩm bán chạy ---")
        start_date_str = "2025-06-01"
        end_date_str = "2025-06-30"

        # --- Sắp xếp theo SỐ LƯỢNG ---
        # SP2 bán tổng cộng 8 cái, SP1 bán 2 cái
        report_by_qty = get_best_selling_products_report('custom', 'quantity', 3, start_date_str, end_date_str)
        self.assertIsNotNone(report_by_qty)
        self.assertEqual(len(report_by_qty), 2)
        self.assertEqual(report_by_qty[0]['id_san_pham'], self.sp2_id, "SP2 lẽ ra phải bán chạy nhất theo số lượng.")
        self.assertEqual(report_by_qty[0]['tong_so_luong_ban'], 8)

        # --- Sắp xếp theo DOANH THU ---
        # SP1 có doanh thu 2000, SP2 có doanh thu 800
        report_by_rev = get_best_selling_products_report('custom', 'revenue', 3, start_date_str, end_date_str)
        self.assertIsNotNone(report_by_rev)
        self.assertEqual(len(report_by_rev), 2)
        self.assertEqual(report_by_rev[0]['id_san_pham'], self.sp1_id, "SP1 lẽ ra phải bán chạy nhất theo doanh thu.")
        self.assertEqual(report_by_rev[0]['tong_doanh_thu'], Decimal('2000'))

        # --- Kiểm tra TOP N ---
        report_top_1 = get_best_selling_products_report('custom', 'quantity', 3, start_date_str, end_date_str)
        # Giả định top 3,5,10 đều trả về 2 kết quả vì chỉ có 2 sp được bán
        self.assertEqual(len(report_top_1), 2)
        print("=> PASS: Báo cáo sản phẩm bán chạy chính xác.")

    def test_3_get_inventory_report(self):
        """Kiểm tra báo cáo tồn kho thấp và cao, có lọc theo danh mục."""
        print("\n--- Test 3: Báo cáo tồn kho ---")

        # --- Kiểm tra tồn kho THẤP (<10) ---
        low_stock_report = get_inventory_report('low_stock')
        self.assertIsNotNone(low_stock_report)
        self.assertEqual(len(low_stock_report), 1)
        self.assertEqual(low_stock_report[0]['id_san_pham'], self.sp_low_stock_id)

        # --- Kiểm tra tồn kho CAO (>100) ---
        high_stock_report = get_inventory_report('high_stock')
        self.assertIsNotNone(high_stock_report)
        self.assertEqual(len(high_stock_report), 1)
        self.assertEqual(high_stock_report[0]['id_san_pham'], self.sp_high_stock_id)

        # --- Kiểm tra lọc theo DANH MỤC ---
        # Tìm sản phẩm tồn kho thấp trong danh mục "Phụ kiện" -> phải rỗng
        low_stock_in_accessories = get_inventory_report('low_stock', category_id=self.cat_phukien_id)
        self.assertIsNotNone(low_stock_in_accessories)
        self.assertEqual(len(low_stock_in_accessories), 0)

        # Tìm sản phẩm tồn kho cao trong danh mục "Điện thoại" -> phải có 1
        high_stock_in_phones = get_inventory_report('high_stock', category_id=self.cat_dienthoai_id)
        self.assertIsNotNone(high_stock_in_phones)
        self.assertEqual(len(high_stock_in_phones), 1)
        self.assertEqual(high_stock_in_phones[0]['id_san_pham'], self.sp_high_stock_id)
        print("=> PASS: Báo cáo tồn kho chính xác.")


if __name__ == '__main__':
    unittest.main()
