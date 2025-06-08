CREATE TABLE NhaCungCap (
    id SERIAL PRIMARY KEY,
    ten_nha_cung_cap VARCHAR(255) NOT NULL UNIQUE,
    ma_so_thue VARCHAR(20) NULL UNIQUE,
    so_dien_thoai VARCHAR(20) NULL,
    email VARCHAR(255) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    dia_chi TEXT NOT NULL,
    nguoi_lien_he_chinh VARCHAR(100) NULL,
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);