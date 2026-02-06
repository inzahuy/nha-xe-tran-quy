from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Cấu hình cơ bản
app.secret_key = 'tranquy_bus_secret' 

# Dữ liệu giả lập (Lưu tạm trong RAM)
# Mày có thể đổi list này theo đúng lộ trình nhà mày
LO_TRINH = [
    "Hà Nội", "Ninh Bình", "Thanh Hóa", "Vinh (Nghệ An)", 
    "Hà Tĩnh", "Đồng Hới (Quảng Bình)", "Huế", "Đà Nẵng", 
    "Quy Nhơn", "Nha Trang", "Phan Thiết", "Sài Gòn"
]

danh_sach_ve = []

@app.route('/')
def index():
    return render_template('index.html', lo_trinh=LO_TRINH)

@app.route('/dat-ve', methods=['POST'])
def dat_ve():
    # Lấy dữ liệu từ form
    ten = request.form.get('ten')
    sdt = request.form.get('sdt')
    diem_di = request.form.get('diem_di')
    diem_den = request.form.get('diem_den')
    ngay_di = request.form.get('ngay_di')
    loai_giuong = request.form.get('loai_giuong')
    ghi_chu = request.form.get('ghi_chu')

    # Tạo mã vé
    ma_ve = f"TQ{len(danh_sach_ve) + 1000}"
    thoi_gian_dat = datetime.now().strftime("%H:%M %d/%m/%Y")

    ve_moi = {
        'ma_ve': ma_ve,
        'ten': ten,
        'sdt': sdt,
        'tuyen': f"{diem_di} đi {diem_den}",
        'ngay_di': ngay_di,
        'loai_giuong': loai_giuong,
        'ghi_chu': ghi_chu,
        'thoi_gian_dat': thoi_gian_dat,
        'trang_thai': 'Chờ thanh toán'
    }

    danh_sach_ve.append(ve_moi)
    
    # Điều hướng sang trang xem lại vé (Giải quyết vấn đề của mày)
    return redirect(url_for('xem_ve', ma_ve=ma_ve))

@app.route('/ve/<ma_ve>')
def xem_ve(ma_ve):
    # Tìm vé vừa đặt để hiển thị
    ve_tim_thay = next((ve for ve in danh_sach_ve if ve['ma_ve'] == ma_ve), None)
    if ve_tim_thay:
        return render_template('success.html', ve=ve_tim_thay)
    return "Không tìm thấy vé", 404

@app.route('/admin')
def admin():
    # Trang quản trị cho Đích tôn
    return render_template('admin.html', ve_xe=danh_sach_ve)

@app.route('/admin/xoa/<ma_ve>')
def xoa_ve(ma_ve):
    global danh_sach_ve
    danh_sach_ve = [ve for ve in danh_sach_ve if ve['ma_ve'] != ma_ve]
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)