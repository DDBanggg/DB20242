CREATE TYPE enum_phuong_thuc_thanh_toan AS ENUM (
    'Tiền mặt',
    'Chuyển khoản',
    'Thẻ tín dụng',
    'COD'
);

CREATE TYPE enum_trang_thai_don_hang_ban AS ENUM (
    'Chờ xác nhận',
    'Đã xác nhận',
    'Đang giao hàng',
    'Đã giao',
    'Hoàn tất',
    'Đã hủy',
    'Trả hàng'
);

CREATE TYPE enum_trang_thai_thanh_toan AS ENUM (
    'Chưa thanh toán',
    'Đã thanh toán'
);

CREATE TABLE DonHangBan (
    id SERIAL PRIMARY KEY,
    id_khach_hang INTEGER NOT NULL,
    id_nhan_vien INTEGER NOT NULL,
    ngay_dat_hang TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_giao_hang_du_kien DATE NULL,
    ngay_giao_hang_thuc_te DATE NULL,
    dia_chi_giao_hang TEXT NOT NULL,
    tong_doanh_thu NUMERIC(15, 0) NOT NULL DEFAULT 0 CHECK (tong_doanh_thu >= 0),
    phuong_thuc_thanh_toan enum_phuong_thuc_thanh_toan NOT NULL,
    trang_thai_don_hang enum_trang_thai_don_hang_ban NOT NULL DEFAULT 'Chờ xác nhận',
    trang_thai_thanh_toan enum_trang_thai_thanh_toan NOT NULL DEFAULT 'Chưa thanh toán',
    ghi_chu_don_hang TEXT NULL,
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Sẽ cần trigger để tự động cập nhật
    CONSTRAINT fk_khach_hang_donban
        FOREIGN KEY(id_khach_hang)
        REFERENCES KhachHang(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_nhan_vien_donban
        FOREIGN KEY(id_nhan_vien)
        REFERENCES NhanVien(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);