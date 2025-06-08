CREATE TABLE SanPham (
    id SERIAL PRIMARY KEY,
    ma_san_pham VARCHAR(20) NOT NULL UNIQUE,
    ten_san_pham VARCHAR(255) NOT NULL UNIQUE,
    id_danh_muc INTEGER NOT NULL,
    so_luong_ton_kho INTEGER NOT NULL DEFAULT 0 CHECK (so_luong_ton_kho >= 0),
    don_vi_tinh VARCHAR(50) NOT NULL,
    mo_ta_chi_tiet TEXT NULL,
    duong_dan_hinh_anh_chinh VARCHAR(255) NULL,
    trang_thai VARCHAR(50) NOT NULL DEFAULT 'Đang kinh doanh - Còn hàng' CHECK (trang_thai IN ('Đang kinh doanh - Còn hàng', 'Đang kinh doanh - Hết hàng', 'Ngừng kinh doanh')),
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_danh_muc
        FOREIGN KEY(id_danh_muc)
        REFERENCES DanhMuc(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);