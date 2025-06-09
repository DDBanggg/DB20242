# test/test_7_donhangban.py

import unittest
import sys
import os
from decimal import Decimal

# --- Thiết lập đường dẫn Project ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports từ ứng dụng của bạn ---
from be.operation.operation_7_donhangban import *
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_2_sanpham import add_sanpham
from be.operation.operation_4_khachhang import add_khachhang
from be.operation.operation_5_nhanvien import add_nhanvien
from be.db_connection import get_db_connection, close_db_connection


class TestDonHangBanOperation(unittest.TestCase):
    """
    Bộ kiểm thử cho các nghiệp vụ liên quan đến Đơn Hàng Bán.
    Mỗi hàm test được thiết kế để kiểm tra một khía cạnh cụ thể của quy trình.
    """

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần duy nhất trước tất cả các test.
        Thiết lập dữ liệu nền cần thiết (danh mục, sản phẩm, khách hàng, nhân viên).
        """
        print("\n--- Thiết lập môi trường cho Test Bán Hàng ---")

        # Dọn dẹp CSDL để đảm bảo môi trường test sạch
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "TRUNCATE TABLE DanhMuc, SanPham, NhanVien, KhachHang, DonHangBan, ChiTietDonHangBan RESTART IDENTITY CASCADE;"
                )
                conn.commit()
        finally:
            close_db_connection(conn)

        # Tạo dữ liệu mẫu và kiểm tra ngay lập tức
        cls.danhmuc_id = add_danhmuc("DM_T_BAN", "Danh mục Test Bán Hàng")
        cls.khachhang_id = add_khachhang("KH Test Bán", "0900000001", "kh.test.ban@example.com")
        cls.nhanvien_id = add_nhanvien("NV Test Bán", "nv_test_ban", "pass123", "nv.test.ban@example.com", "0900000002")

        cls.stock_sp1 = 100
        cls.stock_sp2 = 20
        cls.sanpham_id_1 = add_sanpham("SP_TEST_BAN_1", "Sản phẩm Test Bán 1", cls.danhmuc_id, cls.stock_sp1, "Cái")
        cls.sanpham_id_2 = add_sanpham("SP_TEST_BAN_2", "Sản phẩm Test Bán 2", cls.danhmuc_id, cls.stock_sp2, "Hộp")

        # Dừng toàn bộ bộ test nếu dữ liệu nền không được tạo thành công
        if not all([cls.danhmuc_id, cls.khachhang_id, cls.nhanvien_id, cls.sanpham_id_1, cls.sanpham_id_2]):
            raise Exception("Không thể khởi tạo dữ liệu nền, dừng bộ test.")

    def setUp(self):
        """
        Chạy trước mỗi hàm test.
        Đảm bảo các bảng đơn hàng luôn sạch và các giá trị được reset.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Xóa tất cả các đơn hàng cũ
                cur.execute("TRUNCATE TABLE DonHangBan, ChiTietDonHangBan RESTART IDENTITY CASCADE;")
                # Reset số lượng tồn kho
                cur.execute("UPDATE SanPham SET so_luong_ton_kho = %s WHERE id = %s",
                            (self.stock_sp1, self.sanpham_id_1))
                cur.execute("UPDATE SanPham SET so_luong_ton_kho = %s WHERE id = %s",
                            (self.stock_sp2, self.sanpham_id_2))
                # Reset số lần mua hàng của khách
                cur.execute("UPDATE KhachHang SET so_lan_mua_hang = 0 WHERE id = %s", (self.khachhang_id,))
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_create_order_and_add_item(self):
        """
        Kiểm tra việc tạo đơn hàng bán, thêm sản phẩm thành công
        và xác minh các giá trị được trigger tính toán.
        """
        print("\n--- Test 1: Tạo đơn, thêm sản phẩm và kiểm tra trigger tính giá ---")

        # 1. Tạo đơn hàng bán
        dhb_id = create_donhangban(self.nhanvien_id, self.khachhang_id, "123 Đường Test, Quận ABC")
        self.assertIsNotNone(dhb_id, "Tạo đơn hàng bán thất bại.")

        # 2. Thêm một sản phẩm vào đơn hàng
        so_luong_ban = 10
        gia_niem_yet = Decimal('150000')
        giam_gia = Decimal('0.1')  # 10%

        chi_tiet_id = add_item_to_donhangban(dhb_id, self.sanpham_id_1, so_luong_ban, gia_niem_yet, giam_gia)
        self.assertIsNotNone(chi_tiet_id, "Thêm chi tiết đơn hàng thất bại.")

        # 3. Lấy lại chi tiết đơn hàng và kiểm tra các giá trị được trigger tính
        details = get_chitietdonhangban(dhb_id)
        self.assertIsNotNone(details, "Không lấy được chi tiết đơn hàng.")
        self.assertEqual(len(details['chi_tiet_san_pham']), 1, "Số lượng chi tiết trong đơn không đúng.")

        item = details['chi_tiet_san_pham'][0]
        gia_cuoi_cung_ky_vong = gia_niem_yet * (1 - giam_gia)
        tong_gia_ban_ky_vong = gia_cuoi_cung_ky_vong * so_luong_ban

        self.assertEqual(item['gia_ban_cuoi_cung_don_vi'], gia_cuoi_cung_ky_vong,
                         "Giá bán cuối cùng được trigger tính sai.")
        self.assertEqual(item['tong_gia_ban'], tong_gia_ban_ky_vong, "Tổng giá bán được trigger tính sai.")
        print("=> PASS: Tạo đơn, thêm sản phẩm và tính giá thành công.")

    def test_2_add_item_insufficient_stock_fails(self):
        """
        Kiểm tra rằng hệ thống ngăn chặn việc bán hàng khi không đủ tồn kho.
        """
        print("\n--- Test 2: Thêm sản phẩm quá tồn kho thất bại ---")

        # 1. Tạo đơn hàng
        dhb_id = create_donhangban(self.nhanvien_id, self.khachhang_id, "456 Đường Lỗi, Quận XYZ")

        # 2. Cố gắng thêm sản phẩm với số lượng vượt quá tồn kho (tồn 20, yêu cầu 21)
        chi_tiet_id_fail = add_item_to_donhangban(dhb_id, self.sanpham_id_2, 21, Decimal('200000'), 0)

        self.assertIsNone(chi_tiet_id_fail, "Hệ thống đã cho phép bán hàng quá số lượng tồn kho.")

        # 3. Đảm bảo không có chi tiết nào được thêm vào đơn
        details = get_chitietdonhangban(dhb_id)
        self.assertEqual(len(details['chi_tiet_san_pham']), 0, "Đơn hàng không nên có chi tiết nào.")
        print("=> PASS: Hệ thống đã ngăn chặn bán hàng khi tồn kho không đủ.")

    def test_3_update_status_to_completed_and_verify_triggers(self):
        """
        Kiểm tra việc cập nhật trạng thái đơn hàng sang 'Hoàn tất'
        và xác minh các trigger cập nhật tồn kho và số lần mua hàng.
        """
        print("\n--- Test 3: Cập nhật trạng thái 'Hoàn tất' và kiểm tra trigger ---")

        # 1. Tạo đơn và thêm sản phẩm
        dhb_id = create_donhangban(self.nhanvien_id, self.khachhang_id, "789 Đường Hoàn Tất, Quận JQK")
        so_luong_ban = 10
        add_item_to_donhangban(dhb_id, self.sanpham_id_1, so_luong_ban, Decimal('150000'), 0)

        # 2. Lấy thông tin tồn kho và số lần mua trước khi cập nhật
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT so_luong_ton_kho FROM SanPham WHERE id = %s", (self.sanpham_id_1,))
                ton_kho_cu = cur.fetchone()['so_luong_ton_kho']
                cur.execute("SELECT so_lan_mua_hang FROM KhachHang WHERE id = %s", (self.khachhang_id,))
                so_lan_mua_cu = cur.fetchone()['so_lan_mua_hang']
        finally:
            close_db_connection(conn)

        # 3. Cập nhật trạng thái
        update_success = update_donhangban_status(dhb_id, 'Hoàn tất', 'Đã thanh toán', '2025-06-10')
        self.assertTrue(update_success, "Cập nhật trạng thái đơn hàng thất bại.")

        # 4. Kiểm tra lại thông tin sau khi trigger đã chạy
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT so_luong_ton_kho FROM SanPham WHERE id = %s", (self.sanpham_id_1,))
                ton_kho_moi = cur.fetchone()['so_luong_ton_kho']
                cur.execute("SELECT so_lan_mua_hang FROM KhachHang WHERE id = %s", (self.khachhang_id,))
                so_lan_mua_moi = cur.fetchone()['so_lan_mua_hang']
        finally:
            close_db_connection(conn)

        self.assertEqual(ton_kho_moi, ton_kho_cu - so_luong_ban, "Trigger cập nhật tồn kho không chính xác.")
        self.assertEqual(so_lan_mua_moi, so_lan_mua_cu + 1, "Trigger cập nhật số lần mua hàng không chính xác.")
        print(f"=> PASS: Tồn kho ({ton_kho_moi}) và số lần mua hàng ({so_lan_mua_moi}) đã được cập nhật đúng.")


if __name__ == '__main__':
    unittest.main()
