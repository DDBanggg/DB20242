# test/test_5_nhanvien.py

import unittest
import sys
import os

# Thêm thư mục gốc của dự án vào Python Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from be.operation.operation_5_nhanvien import *
from be.db_connection import get_db_connection, close_db_connection


class TestNhanVienOperation(unittest.TestCase):

    def setUp(self):
        """Chạy trước mỗi test case để dọn dẹp bảng."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE NhanVien RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_and_get_nhanvien(self):
        """Kiểm tra việc thêm mới và lấy danh sách nhân viên."""
        print("\n--- Chạy test: Thêm và Lấy nhân viên ---")

        # Thêm nhân viên 1: Quản Lý A
        nv1_id = add_nhanvien("Quản Lý A", "admin", "adminpass", "admin@shop.com", "0901112221", vai_tro="Quản lý")
        self.assertIsNotNone(nv1_id)

        # Thêm nhân viên 2: Nhân Viên B
        nv2_id = add_nhanvien("Nhân Viên B", "staff", "staffpass", "staff@shop.com", "0901112222")
        self.assertIsNotNone(nv2_id)

        # Lấy tất cả danh sách (đã được sắp xếp theo ten_nhan_vien)
        all_nv = get_all_nhanvien()
        self.assertEqual(len(all_nv), 2)

        # --- SỬA ĐỔI Ở ĐÂY ---
        # Do "Nhân Viên B" đứng trước "Quản Lý A" theo alphabet,
        # nên all_nv[0] là nhân viên B và all_nv[1] là quản lý A.

        # Kiểm tra nhân viên đầu tiên trong danh sách (Nhân Viên B)
        self.assertEqual(all_nv[0]['ten_dang_nhap'], 'staff')
        self.assertEqual(all_nv[0]['vai_tro'], 'Nhân viên')

        # Kiểm tra nhân viên thứ hai trong danh sách (Quản Lý A)
        self.assertEqual(all_nv[1]['ten_dang_nhap'], 'admin')
        self.assertEqual(all_nv[1]['vai_tro'], 'Quản lý')

    def test_2_update_nhanvien(self):
        """Kiểm tra các chức năng cập nhật khác nhau."""
        print("\n--- Chạy test: Cập nhật nhân viên ---")

        nv_id = add_nhanvien("Tên Cũ", "nv_update", "pass_cu", "cu@email.com", "0123456789")
        self.assertIsNotNone(nv_id)

        # Cập nhật thông tin cơ bản
        update_info_success = update_nhanvien_info(nv_id, ten_nhan_vien="Tên Mới", email="moi@email.com")
        self.assertTrue(update_info_success)

        # Cập nhật vai trò
        update_role_success = update_nhanvien_role(nv_id, "Quản lý")
        self.assertTrue(update_role_success)

        # Cập nhật trạng thái
        update_status_success = update_nhanvien_status(nv_id, "Đã nghỉ việc")
        self.assertTrue(update_status_success)

        # Cập nhật mật khẩu
        update_pass_success = update_nhanvien_password(nv_id, "pass_moi")
        self.assertTrue(update_pass_success)

        # Lấy lại và kiểm tra toàn bộ
        updated_nv = get_nhanvien_by_username("nv_update")
        self.assertEqual(updated_nv['ten_nhan_vien'], "Tên Mới")
        self.assertEqual(updated_nv['email'], "moi@email.com")
        self.assertEqual(updated_nv['vai_tro'], "Quản lý")
        self.assertEqual(updated_nv['trang_thai'], "Đã nghỉ việc")
        self.assertEqual(updated_nv['mat_khau'], "pass_moi")

    def test_3_add_duplicate_nhanvien(self):
        """Kiểm tra các ràng buộc UNIQUE."""
        print("\n--- Chạy test: Thêm nhân viên trùng lặp ---")

        add_nhanvien("Nhân Viên A", "nv_a", "pass", "nva@email.com", "0901234567")

        # Thử thêm với ten_dang_nhap trùng
        id1 = add_nhanvien("Người Lạ 1", "nv_a", "pass", "la1@email.com", "0901111111")
        self.assertIsNone(id1)

        # Thử thêm với email trùng
        id2 = add_nhanvien("Người Lạ 2", "nv_b", "pass", "nva@email.com", "0902222222")
        self.assertIsNone(id2)

        # Thử thêm với SĐT trùng
        id3 = add_nhanvien("Người Lạ 3", "nv_c", "pass", "la3@email.com", "0901234567")
        self.assertIsNone(id3)

        # Đảm bảo chỉ có 1 nhân viên trong DB
        all_nv = get_all_nhanvien()
        self.assertEqual(len(all_nv), 1)


if __name__ == '__main__':
    unittest.main()