import asyncio
import json
from datetime import datetime

# Import các thư viện/đối tượng mà PyCharm không hiểu
from pyodide.http import pyfetch
from typing import TYPE_CHECKING, Any

# Khối này chỉ chạy cho PyCharm, không chạy trong trình duyệt
if TYPE_CHECKING:
    # "Giả vờ" định nghĩa các đối tượng để PyCharm không báo lỗi
    pyscript: Any
    Element: Any
    create: Any
    when: Any

# --- Cấu hình chung ---
API_BASE_URL = "http://127.0.0.1:8000/api"

# --- Hàm gọi API chung ---
async def api_call(endpoint, method="GET", body=None):
    headers = {"Content-Type": "application/json"}
    try:
        response = await pyfetch(
            url=f"{API_BASE_URL}{endpoint}",
            method=method,
            headers=headers,
            body=json.dumps(body) if body else None,
        )
        if not response.ok:
            print(f"Lỗi API {method} {endpoint}: {response.status} {await response.string()}")
            return None
        return await response.json()
    except Exception as e:
        print(f"Lỗi mạng hoặc JSON khi gọi {endpoint}: {e}")
        return None

# ==============================================================================
# QUẢN LÝ DANH MỤC
# ==============================================================================
def render_danhmuc_table(danhmuc_list):
    table_html = """
    <figure><table><thead><tr>
        <th>Mã Danh Mục</th><th>Tên Danh Mục</th><th>Mô tả</th><th>Hành động</th>
    </tr></thead><tbody>
    """
    for dm in danhmuc_list:
        table_html += f"""
        <tr>
            <td>{dm['ma_danh_muc']}</td><td>{dm['ten_danh_muc']}</td>
            <td>{dm.get('mo_ta') or ''}</td><td><button class="outline secondary small">Sửa</button></td>
        </tr>"""
    table_html += "</tbody></table></figure>"
    return table_html

async def show_danhmuc_page(*args, **kwargs):
    main_content = Element("main-content")
    main_content.clear()
    form_html = """
    <article>
        <header><strong>Thêm danh mục mới</strong></header>
        <form id="add-danhmuc-form">
            <div class="grid">
                <label>Mã Danh mục<input type="text" id="ma_danh_muc" name="ma_danh_muc" required></label>
                <label>Tên Danh mục<input type="text" id="ten_danh_muc" name="ten_danh_muc" required></label>
            </div>
            <label>Mô tả</label><textarea id="mo_ta" name="mo_ta"></textarea>
            <button type="submit">Thêm mới</button>
        </form>
    </article>"""
    main_content.write(form_html, append=True)
    Element("add-danhmuc-form").onsubmit(add_danhmuc_submit)
    main_content.write("<div id='danhmuc-list-container'>Đang tải...</div>", append=True)
    await refresh_danhmuc_list()

@when("submit", "#add-danhmuc-form")
async def add_danhmuc_submit(event):
    event.preventDefault()
    ma_dm_input, ten_dm_input, mo_ta_input = Element("ma_danh_muc"), Element("ten_danh_muc"), Element("mo_ta")
    new_category = {"ma_danh_muc": ma_dm_input.value, "ten_danh_muc": ten_dm_input.value, "mo_ta": mo_ta_input.value}
    if await api_call("/categories/", method="POST", body=new_category):
        ma_dm_input.clear(); ten_dm_input.clear(); mo_ta_input.clear()
        await refresh_danhmuc_list()

async def refresh_danhmuc_list():
    container = Element("danhmuc-list-container")
    container.innerHtml = "Đang tải danh sách..."
    danhmuc_list = await api_call("/categories/")
    container.innerHtml = render_danhmuc_table(danhmuc_list) if danhmuc_list is not None else "<p>Lỗi tải danh sách.</p>"

# ==============================================================================
# BÁO CÁO THỐNG KÊ
# ==============================================================================
async def show_report_thongke_page(*args, **kwargs):
    main_content = Element("main-content")
    main_content.clear()
    report_ui = """
    <article>
        <header><strong>Báo cáo Thống kê Đơn hàng</strong></header>
        <p>Biểu đồ hiển thị số lượng đơn hàng hoàn tất theo ngày.</p>
        <div id="chart-container" style="height: 400px;"><canvas id="order-chart"></canvas></div>
    </article>"""
    main_content.write(report_ui, append=True)
    await generate_order_count_report()

async def generate_order_count_report():
    chart_container = Element("chart-container")
    chart_container.innerHtml = "Đang tạo báo cáo..."
    report_data = await api_call("/reports/order-count?period=last_month")
    if not report_data:
        chart_container.innerHtml = "<p>Không có dữ liệu.</p>"; return
    labels = [datetime.fromisoformat(item['ky_bao_cao']).strftime('%d/%m') for item in report_data]
    data_values = [item['so_luong_don_hang'] for item in report_data]
    chart_container.innerHtml = '<canvas id="order-chart"></canvas>'
    pyscript.run_js(f'''
        new Chart(document.getElementById('order-chart').getContext('2d'), {{
            type: 'bar', data: {{ labels: {json.dumps(labels)}, datasets: [{{ label: 'Số lượng đơn hàng', data: {json.dumps(data_values)}, backgroundColor: 'rgba(54, 162, 235, 0.6)' }}] }},
            options: {{ responsive: true, maintainAspectRatio: false, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }}
        }});
    ''')

# ==============================================================================
# ROUTING VÀ KHỞI ĐỘNG
# ==============================================================================
page_routes = {"nav-danhmuc": show_danhmuc_page, "nav-report-thongke": show_report_thongke_page}

def setup_nav_events():
    for nav_id, page_function in page_routes.items():
        Element(nav_id).onclick(page_function)

def main():
    print("Frontend App Started!")
    setup_nav_events()
    asyncio.ensure_future(show_danhmuc_page())

main()