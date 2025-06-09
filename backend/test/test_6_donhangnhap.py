# test/test_6_donhangnhap.py

import unittest
import sys
import os
from decimal import Decimal

# --- Thiết lập đường dẫn Project ---
# Điều này đảm bảo các module trong 'be' có thể được import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports từ ứng dụng của bạn ---
from be.operation.operation_6_donhangnhap import *
from be.operation.operation_1_danhmuc import add_danhmuc
from be.operation.operation_2_sanpham import add_sanpham
from be.operation.operation_3_nhacungcap import add_nhacungcap
from be.operation.operation_5_nhanvien import add_nhanvien
from be.db_connection import get_db_connection, close_db_connection


class TestDonHangNhapOperation(unittest.TestCase):
    """
    Bộ kiểm thử cho các nghiệp vụ liên quan đến Đơn Hàng Nhập.
    Mỗi hàm test được thiết kế để kiểm tra một khía cạnh cụ thể của quy trình.
    """

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần duy nhất trước tất cả các test trong class này.
        Thiết lập dữ liệu nền cần thiết (danh mục, sản phẩm, nhà cung cấp, nhân viên).
        """
        print("\n--- Thiết lập môi trường cho Test Đơn Hàng Nhập ---")

        # Dọn dẹp CSDL để đảm bảo môi trường test sạch
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # TRUNCATE ... RESTART IDENTITY CASCADE sẽ xóa dữ liệu và reset ID tự tăng
                cur.execute(
                    "TRUNCATE TABLE DanhMuc, SanPham, NhanVien, NhaCungCap, DonHangNhap, ChiTietDonHangNhap RESTART IDENTITY CASCADE;"
                )
                conn.commit()
        finally:
            close_db_connection(conn)

        # --- FIX: Sửa mã danh mục thành 10 ký tự hoặc ít hơn ---
        cls.danhmuc_id = add_danhmuc("DM_T_NHAP", "Danh mục Test Nhập Hàng")
        # Kiểm tra xem việc tạo danh mục có thành công không trước khi tiếp tục
        if not cls.danhmuc_id:
            raise Exception("Không thể tạo Danh mục, dừng bộ test.")

        cls.nhacungcap_id = add_nhacungcap("NCC Test Corp", "contact@ncctest.com", "123 NCC Test Street", "0987654321")
        cls.nhanvien_id = add_nhanvien("NV Test Nhập", "nv_test_nhap", "securepass123", "nv.nhap@test.com",
                                       "0901112233")

        # Tạo 2 sản phẩm để kiểm tra việc thêm nhiều mặt hàng
        cls.initial_stock = 10
        cls.sanpham_id_1 = add_sanpham("SP_TEST_NHAP_1", "Sản phẩm Test Nhập 1", cls.danhmuc_id, cls.initial_stock,
                                       "Cái")
        cls.sanpham_id_2 = add_sanpham("SP_TEST_NHAP_2", "Sản phẩm Test Nhập 2", cls.danhmuc_id, cls.initial_stock,
                                       "Hộp")

        # Kiểm tra xem việc tạo sản phẩm có thành công không
        if not all([cls.nhacungcap_id, cls.nhanvien_id, cls.sanpham_id_1, cls.sanpham_id_2]):
            raise Exception("Thiết lập dữ liệu nền (NCC, NV, SP) thất bại, dừng bộ test.")

    def setUp(self):
        """
        Chạy trước mỗi hàm test.
        Đảm bảo bảng DonHangNhap và ChiTietDonHangNhap luôn sạch sẽ cho mỗi test case.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE DonHangNhap, ChiTietDonHangNhap RESTART IDENTITY CASCADE;")
                # Reset lại số lượng tồn kho của sản phẩm về giá trị ban đầu
                cur.execute("UPDATE SanPham SET so_luong_ton_kho = %s WHERE id IN (%s, %s)",
                            (self.initial_stock, self.sanpham_id_1, self.sanpham_id_2))
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_create_and_add_items(self):
        """
        Kiểm tra việc tạo đơn hàng nhập và thêm các sản phẩm vào đơn.
        Xác minh rằng các chi tiết được lưu chính xác.
        """
        print("\n--- Test 1: Tạo đơn và thêm sản phẩm ---")

        # 1. Tạo một đơn hàng nhập mới
        dhn_id = create_donhangnhap(self.nhacungcap_id, self.nhanvien_id)
        self.assertIsNotNone(dhn_id, "Tạo đơn hàng nhập thất bại, không nhận được ID.")

        # 2. Thêm hai sản phẩm khác nhau vào đơn hàng
        sl_1, gia_1 = 50, Decimal('100000')
        item_1_id = add_item_to_donhangnhap(dhn_id, self.sanpham_id_1, sl_1, gia_1)
        self.assertIsNotNone(item_1_id, "Thêm sản phẩm 1 thất bại.")

        sl_2, gia_2 = 25, Decimal('250000')
        item_2_id = add_item_to_donhangnhap(dhn_id, self.sanpham_id_2, sl_2, gia_2)
        self.assertIsNotNone(item_2_id, "Thêm sản phẩm 2 thất bại.")

        # 3. Lấy lại chi tiết đơn hàng để kiểm tra
        details = get_chitietdonhangnhap(dhn_id)
        self.assertIsNotNone(details, "Không thể lấy chi tiết đơn hàng đã tạo.")

        # 4. Xác minh thông tin
        self.assertEqual(details['id'], dhn_id)
        self.assertEqual(len(details['chi_tiet_san_pham']), 2, "Số lượng sản phẩm trong chi tiết không khớp.")

        # 5. Kiểm tra tổng giá trị các chi tiết (dựa vào trigger tính tong_gia_nhap)
        tong_gia_tri_thuc_te = sum(item['tong_gia_nhap'] for item in details['chi_tiet_san_pham'])
        tong_gia_tri_ky_vong = (sl_1 * gia_1) + (sl_2 * gia_2)
        self.assertEqual(tong_gia_tri_thuc_te, tong_gia_tri_ky_vong, "Tổng giá trị tính từ chi tiết không đúng.")
        print("=> PASS: Tạo đơn và thêm sản phẩm thành công.")

    def test_2_update_status_and_stock(self):
        """
        Kiểm tra việc cập nhật trạng thái đơn hàng thành 'Hoàn tất'
        và xác minh trigger `trg_after_update_donhangnhap_hoantat` đã cập nhật tồn kho chính xác.
        """
        print("\n--- Test 2: Cập nhật trạng thái và tồn kho ---")

        # 1. Tạo đơn và thêm sản phẩm
        dhn_id = create_donhangnhap(self.nhacungcap_id, self.nhanvien_id)
        so_luong_nhap = 50
        add_item_to_donhangnhap(dhn_id, self.sanpham_id_1, so_luong_nhap, Decimal('100000'))

        # 2. Cập nhật trạng thái sang "Hoàn tất"
        update_success = update_donhangnhap_status(dhn_id, 'Hoàn tất', '2025-06-10')
        self.assertTrue(update_success, "Cập nhật trạng thái đơn hàng thất bại.")

        # 3. Kiểm tra lại tồn kho sau khi trigger đã chạy
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT so_luong_ton_kho FROM SanPham WHERE id = %s", (self.sanpham_id_1,))
                ton_kho_moi = cur.fetchone()['so_luong_ton_kho']
        finally:
            close_db_connection(conn)

        ton_kho_ky_vong = self.initial_stock + so_luong_nhap
        self.assertEqual(ton_kho_moi, ton_kho_ky_vong,
                         "Số lượng tồn kho đã không được cập nhật chính xác sau khi hoàn tất đơn.")
        print(f"=> PASS: Tồn kho đã được cập nhật từ {self.initial_stock} -> {ton_kho_moi}.")

    def test_3_add_duplicate_product_fails(self):
        """
        Kiểm tra rằng không thể thêm cùng một sản phẩm hai lần vào cùng một đơn hàng
        do ràng buộc UNIQUE `unique_sanpham_trong_don_nhap`.
        """
        print("\n--- Test 3: Thêm sản phẩm trùng lặp thất bại ---")

        # 1. Tạo đơn và thêm sản phẩm lần đầu
        dhn_id = create_donhangnhap(self.nhacungcap_id, self.nhanvien_id)
        add_item_to_donhangnhap(dhn_id, self.sanpham_id_1, 10, Decimal('10000'))

        # 2. Cố gắng thêm lại chính sản phẩm đó
        # Hàm add_item_to_donhangnhap sẽ bắt lỗi psycopg2.Error và trả về None
        result = add_item_to_donhangnhap(dhn_id, self.sanpham_id_1, 5, Decimal('20000'))

        self.assertIsNone(result, "Lẽ ra không thể thêm sản phẩm trùng lặp.")

        # 3. Đảm bảo chỉ có một chi tiết trong đơn hàng
        details = get_chitietdonhangnhap(dhn_id)
        self.assertEqual(len(details['chi_tiet_san_pham']), 1,
                         "Số lượng chi tiết không đúng sau khi cố thêm sản phẩm trùng lặp.")
        print("=> PASS: Hệ thống đã ngăn chặn thêm sản phẩm trùng lặp.")

    def test_4_operations_on_nonexistent_order(self):
        """
        Kiểm tra các hàm xử lý đúng cách khi được gọi với một ID đơn hàng không tồn tại.
        """
        print("\n--- Test 4: Thao tác trên đơn hàng không tồn tại ---")

        non_existent_id = 999999

        # 1. Lấy chi tiết đơn hàng không tồn tại
        details = get_chitietdonhangnhap(non_existent_id)
        self.assertIsNone(details, "Lấy chi tiết đơn hàng không tồn tại phải trả về None.")

        # 2. Cập nhật trạng thái đơn hàng không tồn tại
        updated = update_donhangnhap_status(non_existent_id, 'Hoàn tất')
        self.assertFalse(updated, "Cập nhật đơn hàng không tồn tại phải trả về False.")

        # 3. Thêm sản phẩm vào đơn hàng không tồn tại
        item_id = add_item_to_donhangnhap(non_existent_id, self.sanpham_id_1, 10, 100)
        self.assertIsNone(item_id, "Thêm sản phẩm vào đơn không tồn tại phải trả về None.")

        print("=> PASS: Các hàm xử lý đúng với ID không tồn tại.")


if __name__ == '__main__':
    unittest.main()
