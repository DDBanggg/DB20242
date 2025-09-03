from graphviz import Digraph

# Khởi tạo biểu đồ, hướng từ TRÁI sang PHẢI (LR) và dùng đường cong
dot = Digraph('ERD_QuanLyBanHang_CaiTien', comment='Sơ đồ Quan hệ Thực thể Cải tiến')
dot.attr(rankdir='LR', splines='curved', overlap='false')

# Định dạng chung
dot.attr('node', shape='plaintext', fontname='Arial', fontsize='10')
dot.attr('edge', fontname='Arial', fontsize='8', len='1.5')

# == Cụm 1: Dữ liệu Gốc (Master Data) ==
with dot.subgraph(name='cluster_master_data') as c:
    c.attr(label='Dữ liệu Gốc (Master Data)', style='filled', color='lightgrey', fontname='Arial', fontsize='12')
    c.node('DanhMuc', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#A8DADC">
      <TR><TD><b>DanhMuc</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">ten_danh_muc</TD></TR>
    </TABLE>>''')
    c.node('SanPham', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#A8DADC">
      <TR><TD><b>SanPham</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD PORT="id_danh_muc" ALIGN="LEFT">id_danh_muc (FK)</TD></TR>
      <TR><TD ALIGN="LEFT">ten_san_pham</TD></TR>
    </TABLE>>''')
    c.node('NhaCungCap', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#A8DADC">
      <TR><TD><b>NhaCungCap</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">ten_nha_cung_cap</TD></TR>
    </TABLE>>''')
    c.node('KhachHang', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#A8DADC">
      <TR><TD><b>KhachHang</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">ten_khach_hang</TD></TR>
    </TABLE>>''')
    c.node('NhanVien', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#A8DADC">
      <TR><TD><b>NhanVien</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD ALIGN="LEFT">ten_nhan_vien</TD></TR>
    </TABLE>>''')

# == Cụm 2: Quy trình Nhập Hàng ==
with dot.subgraph(name='cluster_nhap_hang') as c:
    c.attr(label='Quy trình Nhập Hàng', style='filled', color='lightskyblue', fontname='Arial', fontsize='12')
    c.node('DonHangNhap', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#F1FAEE">
      <TR><TD><b>DonHangNhap</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD PORT="id_nha_cung_cap" ALIGN="LEFT">id_nha_cung_cap (FK)</TD></TR>
      <TR><TD PORT="id_nhan_vien" ALIGN="LEFT">id_nhan_vien (FK)</TD></TR>
    </TABLE>>''')
    c.node('ChiTietDonHangNhap', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#F1FAEE">
      <TR><TD><b>ChiTietDonHangNhap</b></TD></TR>
      <TR><TD PORT="id_don_hang_nhap" ALIGN="LEFT">id_don_hang_nhap (FK)</TD></TR>
      <TR><TD PORT="id_san_pham" ALIGN="LEFT">id_san_pham (FK)</TD></TR>
      <TR><TD ALIGN="LEFT">so_luong</TD></TR>
    </TABLE>>''')

# == Cụm 3: Quy trình Bán Hàng ==
with dot.subgraph(name='cluster_ban_hang') as c:
    c.attr(label='Quy trình Bán Hàng', style='filled', color='palegreen', fontname='Arial', fontsize='12')
    c.node('DonHangBan', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#F1FAEE">
      <TR><TD><b>DonHangBan</b></TD></TR>
      <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
      <TR><TD PORT="id_khach_hang" ALIGN="LEFT">id_khach_hang (FK)</TD></TR>
      <TR><TD PORT="id_nhan_vien" ALIGN="LEFT">id_nhan_vien (FK)</TD></TR>
    </TABLE>>''')
    c.node('ChiTietDonHangBan', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#F1FAEE">
      <TR><TD><b>ChiTietDonHangBan</b></TD></TR>
      <TR><TD PORT="id_don_hang_ban" ALIGN="LEFT">id_don_hang_ban (FK)</TD></TR>
      <TR><TD PORT="id_san_pham" ALIGN="LEFT">id_san_pham (FK)</TD></TR>
      <TR><TD ALIGN="LEFT">so_luong</TD></TR>
    </TABLE>>''')

# == Các thực thể còn lại ==
dot.node('LichSuGiaNiemYet', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFF2CC">
  <TR><TD><b>LichSuGiaNiemYet (Weak)</b></TD></TR>
  <TR><TD PORT="id_san_pham" ALIGN="LEFT">id_san_pham (FK)</TD></TR>
  <TR><TD ALIGN="LEFT">gia_niem_yet</TD></TR>
</TABLE>>''')
dot.node('ChiPhi', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFD9E2">
  <TR><TD><b>ChiPhi</b></TD></TR>
  <TR><TD PORT="id" ALIGN="LEFT">id (PK)</TD></TR>
  <TR><TD PORT="id_nhan_vien" ALIGN="LEFT">id_nhan_vien (FK)</TD></TR>
</TABLE>>''')

# === Định nghĩa các mối quan hệ (Edges) ===
# Mối quan hệ trong Master Data
dot.edge('DanhMuc:id', 'SanPham:id_danh_muc', label='1..N')

# Mối quan hệ từ Master Data đến các quy trình
dot.edge('NhaCungCap:id', 'DonHangNhap:id_nha_cung_cap', label='1..N')
dot.edge('NhanVien:id', 'DonHangNhap:id_nhan_vien', label='1..N')
dot.edge('KhachHang:id', 'DonHangBan:id_khach_hang', label='1..N')
dot.edge('NhanVien:id', 'DonHangBan:id_nhan_vien', label='1..N')
dot.edge('NhanVien:id', 'ChiPhi:id_nhan_vien', label='1..N')
dot.edge('SanPham:id', 'LichSuGiaNiemYet:id_san_pham', label='1..N')

# Mối quan hệ của các bảng chi tiết (Thực thể kết hợp)
dot.edge('DonHangNhap:id', 'ChiTietDonHangNhap:id_don_hang_nhap')
dot.edge('SanPham:id', 'ChiTietDonHangNhap:id_san_pham')
dot.edge('DonHangBan:id', 'ChiTietDonHangBan:id_don_hang_ban')
dot.edge('SanPham:id', 'ChiTietDonHangBan:id_san_pham')

# Xuất file
output_filename = 'sodo_lienket_database_caitien'
dot.render(output_filename, format='png', view=True, cleanup=True)

print(f"✅ Đã tạo sơ đồ cải tiến thành công! File ảnh đã được lưu với tên '{output_filename}.png'")