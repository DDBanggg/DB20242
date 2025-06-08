CREATE TABLE ChiPhi (
    id SERIAL PRIMARY KEY,
    loai_chi_phi VARCHAR(255) NOT NULL,
    so_tien NUMERIC(15, 0) NOT NULL CHECK (so_tien > 0),
    ngay_chi_phi DATE NOT NULL DEFAULT CURRENT_DATE,
    mo_ta TEXT NULL,
    id_nhan_vien INTEGER NULL,
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_nhan_vien_chiphi
        FOREIGN KEY(id_nhan_vien)
        REFERENCES NhanVien(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);