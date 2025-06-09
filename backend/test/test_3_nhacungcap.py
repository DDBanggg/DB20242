# test/test_3_nhacungcap.py

import unittest
import sys
import os

# Thêm thư mục gốc của dự án vào Python Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from be.operation.operation_3_nhacungcap import *
from be.db_connection import get_db_connection, close_db_connection


class TestNhaCungCapOperation(unittest.TestCase):

    def setUp(self):
        """Chạy trước mỗi test case để dọn dẹp bảng."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE NhaCungCap RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_and_get_nhacungcap(self):
        """Kiểm tra việc thêm mới và lấy danh sách nhà cung cấp."""
        print("\n--- Chạy test: Thêm và Lấy nhà cung cấp ---")

        # Thêm nhà cung cấp 1
        ncc1_id = add_nhacungcap(
            ten_nha_cung_cap="Công ty TNHH An Khang",
            email="contact@ankhang.com",
            dia_chi="123 Đường A, Hà Nội",
            so_dien_thoai="0987654321"
        )
        self.assertIsNotNone(ncc1_id)

        # Thêm nhà cung cấp 2
        ncc2_id = add_nhacungcap(
            ten_nha_cung_cap="Công ty Cổ phần Sách và Thiết bị Bình Minh",
            email="sales@binhminhbooks.com",
            dia_chi="456 Đường B, TP. HCM",
            so_dien_thoai="0123456789"
        )
        self.assertIsNotNone(ncc2_id)

        # Lấy tất cả và kiểm tra số lượng
        all_ncc = get_all_nhacungcap()
        self.assertEqual(len(all_ncc), 2)

    def test_2_update_nhacungcap(self):
        """Kiểm tra việc cập nhật thông tin nhà cung cấp."""
        print("\n--- Chạy test: Cập nhật nhà cung cấp ---")

        ncc_id = add_nhacungcap(
            ten_nha_cung_cap="NCC Test Update",
            email="update@test.com",
            dia_chi="Địa chỉ cũ"
        )
        self.assertIsNotNone(ncc_id)

        # Cập nhật
        update_success = update_nhacungcap(
            ncc_id,
            dia_chi="Địa chỉ mới nhất",
            nguoi_lien_he_chinh="Anh Bảy"
        )
        self.assertTrue(update_success)

        # Lấy lại và kiểm tra
        all_ncc = get_all_nhacungcap()
        self.assertEqual(all_ncc[0]['dia_chi'], "Địa chỉ mới nhất")
        self.assertEqual(all_ncc[0]['nguoi_lien_he_chinh'], "Anh Bảy")

    def test_3_search_functions(self):
        """Kiểm tra các chức năng tìm kiếm."""
        print("\n--- Chạy test: Tìm kiếm nhà cung cấp ---")

        add_nhacungcap("Công ty TNHH An Khang", "contact@ankhang.com", "123 Đường A, Hà Nội",
                       so_dien_thoai="0987654321")
        add_nhacungcap("Công ty Sách Bình Minh", "sales@binhminh.com", "456 Đường B, TP. HCM",
                       so_dien_thoai="0123456789")
        add_nhacungcap("Tạp hóa Chú Tám Khang", "tamkhang@store.com", "789 Đường C, Cần Thơ",
                       so_dien_thoai="0912345678")

        # Tìm theo tên
        results_name = search_nhacungcap_by_name("khang")
        self.assertEqual(len(results_name), 2)

        # Tìm theo SĐT
        results_phone = search_nhacungcap_by_phone("0123")
        self.assertEqual(len(results_phone), 1)
        self.assertEqual(results_phone[0]['ten_nha_cung_cap'], "Công ty Sách Bình Minh")

        # Tìm theo email
        results_email = search_nhacungcap_by_email("sales@binhminh.com")
        self.assertEqual(len(results_email), 1)

    def test_4_add_duplicate_nhacungcap(self):
        """Kiểm tra ràng buộc UNIQUE của nhà cung cấp."""
        print("\n--- Chạy test: Thêm nhà cung cấp trùng lặp ---")

        # Thêm lần 1 thành công
        add_nhacungcap("Công ty ABC", "contact@abc.com", "Địa chỉ ABC")

        # Thêm lần 2 với cùng email -> thất bại
        duplicate_id = add_nhacungcap("Công ty XYZ", "contact@abc.com", "Địa chỉ XYZ")
        self.assertIsNone(duplicate_id)

        # Kiểm tra lại DB chỉ có 1 nhà cung cấp
        all_ncc = get_all_nhacungcap()
        self.assertEqual(len(all_ncc), 1)


if __name__ == '__main__':
    unittest.main()