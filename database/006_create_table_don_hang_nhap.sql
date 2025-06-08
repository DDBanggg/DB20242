CREATE TABLE DonHangNhap (
    id SERIAL PRIMARY KEY,
    id_nha_cung_cap INTEGER NOT NULL,
    id_nhan_vien INTEGER NOT NULL,
    ngay_dat_hang DATE NOT NULL DEFAULT CURRENT_DATE,
    ngay_du_kien_nhan_hang DATE NULL,
    ngay_nhan_hang_thuc_te DATE NULL,
    tong_gia_tri NUMERIC(15, 0) NOT NULL DEFAULT 0 CHECK (tong_gia_tri >= 0),
    trang_thai VARCHAR(50) NOT NULL DEFAULT 'Chờ xác nhận' CHECK (trang_thai IN ('Chờ xác nhận', 'Đã đặt hàng', 'Đang giao hàng', 'Hoàn tất', 'Đã hủy')),
    ghi_chu TEXT NULL,
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Sẽ cần trigger để tự động cập nhật
    CONSTRAINT fk_nha_cung_cap
        FOREIGN KEY(id_nha_cung_cap)
        REFERENCES NhaCungCap(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_nhan_vien
        FOREIGN KEY(id_nhan_vien)
        REFERENCES NhanVien(id)
        ON DELETE RESTRICT -- Hoặc SET NULL nếu bạn muốn giữ đơn hàng khi nhân viên nghỉ việc và bị xóa (nhưng chúng ta đã thống nhất là chỉ đổi trạng thái nhân viên)
        ON UPDATE CASCADE
);