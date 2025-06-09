# test/test_2_sanpham.py

import unittest
import sys
import os

# Thêm thư mục gốc của dự án vào Python Path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from be.operation.operation_2_sanpham import *
from be.operation.operation_1_danhmuc import add_danhmuc
from be.db_connection import get_db_connection, close_db_connection


class TestSanPhamOperation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Chạy một lần duy nhất trước tất cả các test trong lớp này.
        Tạo dữ liệu phụ thuộc (danh mục) để các test case sản phẩm sử dụng."""
        print("\n--- Thiết lập môi trường cho Test Sản phẩm ---")
        # Tạo một danh mục để test
        cls.danhmuc_id = add_danhmuc(ma_danh_muc="DM_SP_TEST", ten_danh_muc="Danh mục cho Sản phẩm Test")
        if cls.danhmuc_id is None:
            raise Exception("Không thể tạo danh mục cần thiết cho việc test sản phẩm.")

    @classmethod
    def tearDownClass(cls):
        """Chạy một lần duy nhất sau tất cả các test trong lớp này. Dọn dẹp dữ liệu phụ thuộc."""
        print("\n--- Dọn dẹp môi trường Test Sản phẩm ---")
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Xóa danh mục test
                cur.execute("DELETE FROM DanhMuc WHERE id = %s;", (cls.danhmuc_id,))
                conn.commit()
        finally:
            close_db_connection(conn)

    def tearDown(self):
        """Chạy sau mỗi test case. Dọn dẹp bảng SanPham để đảm bảo test độc lập."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Xóa sạch dữ liệu và reset ID bắt đầu từ 1
                cur.execute("TRUNCATE TABLE SanPham RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_and_get_sanpham(self):
        """Kiểm tra việc thêm mới và lấy danh sách sản phẩm."""
        print("\n--- Chạy test: Thêm và Lấy sản phẩm ---")

        # Thêm sản phẩm 1
        sp1_id = add_sanpham(
            ma_san_pham="SP001", ten_san_pham="Laptop Test", id_danh_muc=self.danhmuc_id,
            so_luong_ton_kho=50, don_vi_tinh="Cái"
        )
        self.assertIsNotNone(sp1_id)

        # Thêm sản phẩm 2 (sản phẩm sắp hết hàng)
        sp2_id = add_sanpham(
            ma_san_pham="SP002", ten_san_pham="Chuột Test", id_danh_muc=self.danhmuc_id,
            so_luong_ton_kho=5, don_vi_tinh="Cái"
        )
        self.assertIsNotNone(sp2_id)

        # Lấy tất cả và kiểm tra
        all_sp = get_all_sanpham_with_danhmuc()
        self.assertEqual(len(all_sp), 2)
        # Kiểm tra thông tin JOIN
        self.assertEqual(all_sp[0]['ten_danh_muc'], 'Danh mục cho Sản phẩm Test')

    def test_2_search_and_filter(self):
        """Kiểm tra các chức năng tìm kiếm và lọc sản phẩm."""
        print("\n--- Chạy test: Tìm kiếm và Lọc sản phẩm ---")

        add_sanpham(ma_san_pham="SP001", ten_san_pham="Laptop Pro", id_danh_muc=self.danhmuc_id, so_luong_ton_kho=50,
                    don_vi_tinh="Cái")
        add_sanpham(ma_san_pham="SP002", ten_san_pham="Laptop Air", id_danh_muc=self.danhmuc_id, so_luong_ton_kho=30,
                    don_vi_tinh="Cái")
        add_sanpham(ma_san_pham="SP003", ten_san_pham="Bàn phím Gaming", id_danh_muc=self.danhmuc_id,
                    so_luong_ton_kho=10, don_vi_tinh="Cái")

        # Tìm kiếm theo tên
        search_results = search_sanpham_by_name("Laptop")
        self.assertEqual(len(search_results), 2)

        # Lọc theo danh mục
        filter_results = filter_sanpham_by_danhmuc(self.danhmuc_id)
        self.assertEqual(len(filter_results), 3)

        # Lọc sản phẩm sắp hết hàng (ngưỡng <= 10)
        low_stock_results = get_low_stock_sanpham(10)
        self.assertEqual(len(low_stock_results), 1)
        self.assertEqual(low_stock_results[0]['ma_san_pham'], 'SP003')

    def test_3_update_sanpham(self):
        """Kiểm tra việc cập nhật thông tin và trạng thái sản phẩm."""
        print("\n--- Chạy test: Cập nhật sản phẩm ---")

        sp_id = add_sanpham(ma_san_pham="SP_UPDATE", ten_san_pham="Tên Cũ", id_danh_muc=self.danhmuc_id,
                            so_luong_ton_kho=20, don_vi_tinh="Cái")
        self.assertIsNotNone(sp_id)

        # Cập nhật thông tin cơ bản
        update_info_success = update_sanpham_info(sp_id, ten_san_pham="Tên Mới", mo_ta_chi_tiet="Mô tả mới nhất")
        self.assertTrue(update_info_success)

        # Cập nhật trạng thái
        update_status_success = update_sanpham_status(sp_id, "Ngừng kinh doanh")
        self.assertTrue(update_status_success)

        # Lấy lại và kiểm tra
        all_sp = get_all_sanpham_with_danhmuc()
        updated_sp = all_sp[0]
        self.assertEqual(updated_sp['ten_san_pham'], "Tên Mới")
        self.assertEqual(updated_sp['mo_ta_chi_tiet'], "Mô tả mới nhất")
        self.assertEqual(updated_sp['trang_thai'], "Ngừng kinh doanh")


if __name__ == '__main__':
    unittest.main()