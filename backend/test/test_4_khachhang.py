# test/test_4_khachhang.py

import unittest
import sys
import os
from datetime import date

# Thêm thư mục gốc của dự án vào Python Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from be.operation.operation_4_khachhang import add_khachhang, get_all_khachhang, update_khachhang
from be.db_connection import get_db_connection, close_db_connection


class TestKhachHangOperation(unittest.TestCase):

    def setUp(self):
        """Chạy trước mỗi test case để dọn dẹp bảng."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE KhachHang RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_and_get_khachhang(self):
        """Kiểm tra việc thêm mới và lấy danh sách khách hàng."""
        print("\n--- Chạy test: Thêm và Lấy khách hàng ---")

        kh1_id = add_khachhang(
            ten_khach_hang="Nguyễn Văn A",
            so_dien_thoai="0909111222",
            email="nva@email.com",
            ngay_sinh="1990-01-15",
            gioi_tinh="Nam"
        )
        self.assertIsNotNone(kh1_id)

        kh2_id = add_khachhang(
            ten_khach_hang="Trần Thị B",
            so_dien_thoai="0909333444",
            email="ttb@email.com"
        )
        self.assertIsNotNone(kh2_id)

        all_kh = get_all_khachhang()
        self.assertEqual(len(all_kh), 2)
        # so_lan_mua_hang mặc định là 0 khi thêm mới
        self.assertEqual(all_kh[0]['so_lan_mua_hang'], 0)
        self.assertEqual(all_kh[1]['ten_khach_hang'], 'Trần Thị B')

    def test_2_update_khachhang(self):
        """Kiểm tra việc cập nhật thông tin khách hàng."""
        print("\n--- Chạy test: Cập nhật khách hàng ---")

        kh_id = add_khachhang(
            ten_khach_hang="Tên Cũ",
            so_dien_thoai="0123456789",
            email="old.name@email.com",
            dia_chi="Địa chỉ cũ"
        )
        self.assertIsNotNone(kh_id)

        update_success = update_khachhang(
            kh_id,
            ten_khach_hang="Tên Mới",
            dia_chi="Địa chỉ mới",
            ngay_sinh="2000-10-20"
        )
        self.assertTrue(update_success)

        all_kh = get_all_khachhang()
        updated_kh = all_kh[0]
        self.assertEqual(updated_kh['ten_khach_hang'], "Tên Mới")
        self.assertEqual(updated_kh['dia_chi'], "Địa chỉ mới")
        self.assertEqual(updated_kh['ngay_sinh'], date(2000, 10, 20))

    def test_3_add_duplicate_khachhang(self):
        """Kiểm tra ràng buộc UNIQUE của SĐT và email."""
        print("\n--- Chạy test: Thêm khách hàng trùng lặp ---")

        add_khachhang("Nguyễn Văn A", "0909111222", "nva@email.com")

        # Thử thêm với SĐT trùng
        duplicate_phone_id = add_khachhang("Người Lạ 1", "0909111222", "la1@email.com")
        self.assertIsNone(duplicate_phone_id)

        # Thử thêm với email trùng
        duplicate_email_id = add_khachhang("Người Lạ 2", "0909555666", "nva@email.com")
        self.assertIsNone(duplicate_email_id)

        # Đảm bảo chỉ có 1 khách hàng trong DB
        all_kh = get_all_khachhang()
        self.assertEqual(len(all_kh), 1)


if __name__ == '__main__':
    unittest.main()