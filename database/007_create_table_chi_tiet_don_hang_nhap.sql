CREATE TABLE ChiTietDonHangNhap (
    id SERIAL PRIMARY KEY,
    id_don_hang_nhap INTEGER NOT NULL,
    id_san_pham INTEGER NOT NULL,
    so_luong INTEGER NOT NULL CHECK (so_luong > 0),
    so_luong_con_lai INTEGER NOT NULL CHECK (so_luong_con_lai >= 0),
    gia_nhap_don_vi NUMERIC(12, 0) NOT NULL CHECK (gia_nhap_don_vi >= 0),
    tong_gia_nhap NUMERIC(15, 0) NOT NULL CHECK (tong_gia_nhap >= 0),
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ghi_chu TEXT NULL,
    CONSTRAINT fk_don_hang_nhap
        FOREIGN KEY(id_don_hang_nhap)
        REFERENCES DonHangNhap(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_san_pham
        FOREIGN KEY(id_san_pham)
        REFERENCES SanPham(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT unique_sanpham_trong_don_nhap UNIQUE (id_don_hang_nhap, id_san_pham)
);