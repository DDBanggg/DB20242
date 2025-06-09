# test/test_9_lichsugianiemyet.py

import unittest
import sys
import os
from decimal import Decimal
from datetime import date

# --- Thiết lập đường dẫn Project ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports từ ứng dụng của bạn ---
from be.operation.operation_9_lichsugianiemyet import *
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_2_sanpham import add_sanpham
from be.db_connection import get_db_connection, close_db_connection


class TestLichSuGiaOperation(unittest.TestCase):
    """
    Bộ kiểm thử cho nghiệp vụ quản lý Lịch Sử Giá Niêm Yết,
    tập trung vào việc kiểm tra logic của trigger.
    """

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần duy nhất, thiết lập dữ liệu nền (danh mục, sản phẩm).
        """
        print("\n--- Thiết lập môi trường cho Test Lịch Sử Giá ---")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Dọn dẹp các bảng liên quan
                cur.execute("TRUNCATE TABLE DanhMuc, SanPham, LichSuGiaNiemYet RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

        # Tạo dữ liệu mẫu
        cls.danhmuc_id = add_danhmuc("DM_LSG", "Danh mục Test LSG")
        cls.sanpham_id = add_sanpham("SP_TEST_LSG", "Sản phẩm Test Lịch Sử Giá", cls.danhmuc_id, 10, "Cái")

        if not all([cls.danhmuc_id, cls.sanpham_id]):
            raise Exception("Không thể khởi tạo dữ liệu nền, dừng bộ test.")

    def setUp(self):
        """
        Chạy trước mỗi hàm test, đảm bảo bảng LichSuGiaNiemYet luôn sạch.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE LichSuGiaNiemYet RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_price_history_and_verify_trigger(self):
        """
        Kiểm tra việc thêm nhiều mức giá và xác minh trigger
        `trg_cap_nhat_ngay_ket_thuc_gia` hoạt động chính xác.
        """
        print("\n--- Test 1: Thêm lịch sử giá và kiểm tra trigger ---")

        # 1. Thêm mức giá đầu tiên, áp dụng từ 2025-01-01
        price1_date = "2025-01-01"
        price1_id = add_lichsugianiemyet(self.sanpham_id, 100000, price1_date, "Giá ban đầu")
        self.assertIsNotNone(price1_id, "Thêm giá ban đầu thất bại.")

        # Lấy lại và kiểm tra: chỉ có 1 mức giá, ngày kết thúc là NULL
        history1 = get_lichsugianiemyet_for_sanpham(self.sanpham_id)
        self.assertEqual(len(history1), 1)
        self.assertIsNone(history1[0]['ngay_ket_thuc'], "Giá đầu tiên không nên có ngày kết thúc.")

        # 2. Thêm mức giá thứ hai, áp dụng từ 2025-06-01
        price2_date = "2025-06-01"
        price2_id = add_lichsugianiemyet(self.sanpham_id, 120000, price2_date, "Tăng giá hè")
        self.assertIsNotNone(price2_id, "Thêm giá thứ hai thất bại.")

        # 3. Lấy lại toàn bộ lịch sử và kiểm tra
        history2 = get_lichsugianiemyet_for_sanpham(self.sanpham_id)
        self.assertEqual(len(history2), 2, "Số lượng bản ghi lịch sử giá không đúng.")

        # Sắp xếp theo ngày áp dụng tăng dần để dễ kiểm tra
        history2.sort(key=lambda x: x['ngay_ap_dung'])

        old_price_record = history2[0]
        new_price_record = history2[1]

        # Kiểm tra giá mới: ngày kết thúc phải là NULL
        self.assertEqual(new_price_record['id'], price2_id)
        self.assertIsNone(new_price_record['ngay_ket_thuc'], "Giá mới nhất không nên có ngày kết thúc.")

        # Kiểm tra giá cũ: ngày kết thúc phải được trigger cập nhật
        # thành ngày trước ngày áp dụng của giá mới (2025-05-31)
        expected_end_date = date(2025, 5, 31)
        self.assertEqual(old_price_record['id'], price1_id)
        self.assertEqual(old_price_record['ngay_ket_thuc'], expected_end_date,
                         "Trigger đã không cập nhật ngày kết thúc của giá cũ một cách chính xác.")

        print(f"=> PASS: Trigger đã cập nhật ngày kết thúc của giá cũ thành công: {old_price_record['ngay_ket_thuc']}")

    def test_2_invalid_inputs(self):
        """
        Kiểm tra các trường hợp nhập liệu không hợp lệ khi thêm lịch sử giá.
        """
        print("\n--- Test 2: Xử lý nhập liệu không hợp lệ cho lịch sử giá ---")

        # 1. Thêm giá với giá trị âm
        invalid_price_id = add_lichsugianiemyet(self.sanpham_id, -50000, "2025-07-01")
        self.assertIsNone(invalid_price_id, "Lẽ ra không thể thêm giá trị âm.")

        # 2. Thêm giá với định dạng ngày sai
        invalid_date_id = add_lichsugianiemyet(self.sanpham_id, 150000, "01-07-2025")  # DD-MM-YYYY
        self.assertIsNone(invalid_date_id, "Lẽ ra không thể thêm giá với ngày sai định dạng.")

        # 3. Thêm giá cho sản phẩm không tồn tại
        non_existent_product_id = 99999
        foreign_key_error_id = add_lichsugianiemyet(non_existent_product_id, 200000, "2025-08-01")
        self.assertIsNone(foreign_key_error_id, "Lẽ ra không thể thêm giá cho sản phẩm không tồn tại.")

        print("=> PASS: Hệ thống đã xử lý các trường hợp nhập liệu không hợp lệ.")


if __name__ == '__main__':
    unittest.main()
