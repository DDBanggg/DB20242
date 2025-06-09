# test/test_8_chiphi.py

import unittest
import sys
import os
from decimal import Decimal

# --- Thiết lập đường dẫn Project ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports từ ứng dụng của bạn ---
from be.operation.operation_8_chiphi import *
from be.operation.operation_5_nhanvien import add_nhanvien
from be.db_connection import get_db_connection, close_db_connection


class TestChiPhiOperation(unittest.TestCase):
    """
    Bộ kiểm thử cho các nghiệp vụ liên quan đến Chi Phí (CRUD).
    """

    @classmethod
    def setUpClass(cls):
        """
        Chạy một lần duy nhất, thiết lập dữ liệu nền (nhân viên).
        """
        print("\n--- Thiết lập môi trường cho Test Chi Phí ---")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Dọn dẹp các bảng liên quan để đảm bảo môi trường test sạch
                cur.execute("TRUNCATE TABLE NhanVien, ChiPhi RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

        # Tạo một nhân viên mẫu để sử dụng trong các test
        cls.nhanvien_id = add_nhanvien("NV Test Chi Phí", "nv_test_cp", "pass123", "nv.cp@test.com", "0909090909")
        if not cls.nhanvien_id:
            raise Exception("Không thể tạo nhân viên mẫu, dừng bộ test.")

    def setUp(self):
        """
        Chạy trước mỗi hàm test.
        Đảm bảo bảng ChiPhi luôn sạch sẽ cho mỗi test case.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE ChiPhi RESTART IDENTITY CASCADE;")
                conn.commit()
        finally:
            close_db_connection(conn)

    def test_1_add_and_get_chiphi(self):
        """
        Kiểm tra việc thêm mới và lấy danh sách chi phí.
        """
        print("\n--- Test 1: Thêm và lấy chi phí ---")

        # 1. Thêm chi phí có liên kết với nhân viên
        cp1_id = add_chiphi(
            loai_chi_phi="Tiền thuê nhà tháng 5",
            so_tien=15000000,
            ngay_chi_phi_str="2025-05-05",
            mo_ta="Thanh toán tiền nhà",
            id_nhan_vien=self.nhanvien_id
        )
        self.assertIsNotNone(cp1_id, "Thêm chi phí 1 thất bại.")

        # 2. Thêm chi phí không có nhân viên liên kết
        cp2_id = add_chiphi(
            loai_chi_phi="Tiền điện tháng 5",
            so_tien=2500000,
            ngay_chi_phi_str="2025-05-15",
            mo_ta="Thanh toán tiền điện"
        )
        self.assertIsNotNone(cp2_id, "Thêm chi phí 2 thất bại.")

        # 3. Lấy tất cả chi phí và kiểm tra
        all_costs = get_chiphi()
        self.assertIsNotNone(all_costs)
        self.assertEqual(len(all_costs), 2, "Số lượng chi phí trả về không đúng.")

        # 4. Kiểm tra chi tiết một khoản chi
        cost_item = next((c for c in all_costs if c['id'] == cp1_id), None)
        self.assertIsNotNone(cost_item)
        self.assertEqual(cost_item['loai_chi_phi'], "Tiền thuê nhà tháng 5")
        self.assertEqual(cost_item['so_tien'], Decimal('15000000'))
        self.assertEqual(cost_item['id_nhan_vien'], self.nhanvien_id)
        print("=> PASS: Thêm và lấy chi phí thành công.")

    def test_2_filter_chiphi(self):
        """
        Kiểm tra chức năng lọc chi phí theo loại và ngày tháng.
        """
        print("\n--- Test 2: Lọc chi phí ---")

        # Thêm dữ liệu để lọc
        add_chiphi("Tiền nước tháng 5", 500000, "2025-05-20")
        add_chiphi("Mua sắm văn phòng phẩm", 1200000, "2025-05-25")
        add_chiphi("Tiền nước tháng 6", 550000, "2025-06-20")

        # 1. Lọc theo loại
        water_costs = get_chiphi(loai_filter="nước")
        self.assertEqual(len(water_costs), 2, "Lọc theo loại 'nước' thất bại.")

        # 2. Lọc theo ngày bắt đầu
        from_may_25 = get_chiphi(date_from_str="2025-05-25")
        self.assertEqual(len(from_may_25), 2, "Lọc theo ngày bắt đầu thất bại.")

        # 3. Lọc theo ngày kết thúc
        until_may_20 = get_chiphi(date_to_str="2025-05-20")
        self.assertEqual(len(until_may_20), 1, "Lọc theo ngày kết thúc thất bại.")

        # 4. Lọc theo khoảng ngày
        in_june = get_chiphi(date_from_str="2025-06-01", date_to_str="2025-06-30")
        self.assertEqual(len(in_june), 1, "Lọc theo khoảng ngày thất bại.")
        self.assertEqual(in_june[0]['loai_chi_phi'], "Tiền nước tháng 6")

        # 5. Lọc kết hợp
        no_result = get_chiphi(loai_filter="văn phòng", date_to_str="2025-05-24")
        self.assertEqual(len(no_result), 0, "Lọc kết hợp không nên trả về kết quả.")
        print("=> PASS: Lọc chi phí hoạt động chính xác.")

    def test_3_update_chiphi(self):
        """
        Kiểm tra việc cập nhật một khoản chi phí đã tồn tại.
        """
        print("\n--- Test 3: Cập nhật chi phí ---")

        # 1. Thêm một chi phí để cập nhật
        cp_id = add_chiphi("Chi phí quảng cáo", 5000000, "2025-06-01")

        # 2. Cập nhật chi phí
        update_success = update_chiphi(cp_id,
                                       so_tien=6500000,
                                       mo_ta="Tăng cường quảng cáo Facebook")
        self.assertTrue(update_success, "Cập nhật chi phí thất bại.")

        # 3. Lấy lại và kiểm tra
        updated_costs = get_chiphi(loai_filter="quảng cáo")
        self.assertEqual(len(updated_costs), 1)
        self.assertEqual(updated_costs[0]['so_tien'], Decimal('6500000'))
        self.assertEqual(updated_costs[0]['mo_ta'], "Tăng cường quảng cáo Facebook")

        # 4. Cập nhật chi phí không tồn tại
        update_fail = update_chiphi(99999, so_tien=1)
        self.assertFalse(update_fail, "Lẽ ra không thể cập nhật chi phí không tồn tại.")
        print("=> PASS: Cập nhật chi phí thành công.")


    def test_5_invalid_inputs(self):
        """
        Kiểm tra các trường hợp nhập liệu không hợp lệ.
        """
        print("\n--- Test 5: Xử lý nhập liệu không hợp lệ ---")

        # 1. Thêm chi phí với số tiền không hợp lệ
        invalid_amount_id = add_chiphi("Lỗi tiền", -100)
        self.assertIsNone(invalid_amount_id, "Lẽ ra không thể thêm chi phí với số tiền âm.")

        invalid_amount_id_2 = add_chiphi("Lỗi tiền", 0)
        self.assertIsNone(invalid_amount_id_2, "Lẽ ra không thể thêm chi phí với số tiền bằng 0.")

        # 2. Thêm chi phí với ngày sai định dạng
        invalid_date_id = add_chiphi("Lỗi ngày", 100000, "06-06-2025")
        self.assertIsNone(invalid_date_id, "Lẽ ra không thể thêm chi phí với ngày sai định dạng.")

        print("=> PASS: Hệ thống đã xử lý các trường hợp nhập liệu không hợp lệ.")


if __name__ == '__main__':
    unittest.main()
