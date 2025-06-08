CREATE TYPE enum_gioi_tinh AS ENUM ('Nam', 'Nữ', 'Khác');

CREATE TABLE KhachHang (
    id SERIAL PRIMARY KEY,
    ten_khach_hang VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    dia_chi TEXT NULL,
    ngay_sinh DATE NULL,
    gioi_tinh enum_gioi_tinh NULL,
    so_lan_mua_hang INTEGER NOT NULL DEFAULT 0 CHECK (so_lan_mua_hang >= 0),
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);