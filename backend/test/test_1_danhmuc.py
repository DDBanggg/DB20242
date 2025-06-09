# test/test_1_danhmuc.py

import unittest
import sys
import os

# Thêm thư mục gốc của dự án vào Python Path để có thể import các module từ 'be'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from be.operation.operation_1_danhmuc import add_danhmuc, get_all_danhmuc, update_danhmuc
from be.db_connection import get_db_connection, close_db_connection


class TestDanhMucOperation(unittest.TestCase):

    def setUp(self):
        """Chạy trước mỗi test case. Dọn dẹp bảng DanhMuc để đảm bảo test độc lập."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Xóa sạch dữ liệu và reset ID bắt đầu từ 1
                cur.execute("TRUNCATE TABLE DanhMuc RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_and_get_danhmuc(self):
        """Kiểm tra việc thêm mới và lấy danh sách danh mục."""
        print("\n--- Chạy test: Thêm và Lấy danh mục ---")

        # Thêm danh mục đầu tiên
        dm1_id = add_danhmuc(ma_danh_muc="DM001", ten_danh_muc="Điện tử", mo_ta="Các thiết bị điện tử")
        self.assertIsNotNone(dm1_id, "Thêm danh mục 1 thất bại.")

        # Thêm danh mục thứ hai
        dm2_id = add_danhmuc(ma_danh_muc="DM002", ten_danh_muc="Thời trang")
        self.assertIsNotNone(dm2_id, "Thêm danh mục 2 thất bại.")

        # Lấy tất cả danh mục và kiểm tra
        all_dms = get_all_danhmuc()
        self.assertEqual(len(all_dms), 2, "Số lượng danh mục trả về không đúng.")
        self.assertEqual(all_dms[0]['ma_danh_muc'], 'DM001')
        self.assertEqual(all_dms[1]['ten_danh_muc'], 'Thời trang')

    def test_2_update_danhmuc(self):
        """Kiểm tra việc cập nhật một danh mục."""
        print("\n--- Chạy test: Cập nhật danh mục ---")

        # Thêm một danh mục ban đầu
        dm_id = add_danhmuc(ma_danh_muc="DM_UPDATE", ten_danh_muc="Tên Cũ", mo_ta="Mô tả cũ")
        self.assertIsNotNone(dm_id)

        # Cập nhật danh mục đó
        update_success = update_danhmuc(dm_id, ten_danh_muc="Tên Mới", mo_ta="Mô tả đã được cập nhật")
        self.assertTrue(update_success, "Cập nhật danh mục thất bại.")

        # Lấy lại và kiểm tra
        all_dms = get_all_danhmuc()
        self.assertEqual(len(all_dms), 1)
        updated_dm = all_dms[0]
        self.assertEqual(updated_dm['ten_danh_muc'], "Tên Mới")
        self.assertEqual(updated_dm['mo_ta'], "Mô tả đã được cập nhật")

    def test_3_add_duplicate_ma_danhmuc(self):
        """Kiểm tra ràng buộc UNIQUE của ma_danh_muc."""
        print("\n--- Chạy test: Thêm mã danh mục trùng lặp ---")

        # Thêm danh mục đầu tiên
        add_danhmuc(ma_danh_muc="DM_DUP", ten_danh_muc="Danh mục 1")

        # Cố gắng thêm danh mục thứ hai với cùng ma_danh_muc
        duplicate_id = add_danhmuc(ma_danh_muc="DM_DUP", ten_danh_muc="Danh mục 2")

        # Hàm add_danhmuc nên trả về None do lỗi UNIQUE constraint
        self.assertIsNone(duplicate_id, "Lỗi: Đã cho phép thêm mã danh mục trùng lặp.")

        # Kiểm tra để đảm bảo chỉ có 1 danh mục trong DB
        all_dms = get_all_danhmuc()
        self.assertEqual(len(all_dms), 1)


if __name__ == '__main__':
    unittest.main()