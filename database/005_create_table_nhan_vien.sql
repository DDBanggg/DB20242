CREATE TYPE enum_vai_tro_nhan_vien AS ENUM ('Nhân viên', 'Quản lý');

CREATE TYPE enum_trang_thai_nhan_vien AS ENUM ('Đang làm việc', 'Đã nghỉ việc');

CREATE TABLE NhanVien (
    id SERIAL PRIMARY KEY,
    ten_nhan_vien VARCHAR(255) NOT NULL,
    ten_dang_nhap VARCHAR(50) NOT NULL UNIQUE,
    mat_khau VARCHAR(255) NOT NULL, -- Sẽ lưu mật khẩu đã băm
    email VARCHAR(255) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    so_dien_thoai VARCHAR(20) NOT NULL UNIQUE,
    vai_tro enum_vai_tro_nhan_vien NOT NULL DEFAULT 'Nhân viên',
    trang_thai enum_trang_thai_nhan_vien NOT NULL DEFAULT 'Đang làm việc',
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);