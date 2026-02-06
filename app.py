from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Dán cái Internal Database URL của mày vào đây hoặc cấu hình trong Environment Variables trên Render
app.config['SQLALCHEMY_DATABASE_URL'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Định nghĩa bảng dữ liệu ghế
class Seat(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)

@app.route('/')
def index():
    all_seats = Seat.query.all()
    # Chuyển dữ liệu từ database sang dạng dictionary để frontend dễ đọc
    seats_dict = {s.id: {'name': s.customer_name, 'phone': s.customer_phone} if s.customer_name else None for s in all_seats}
    return render_template('index.html', seats=seats_dict)

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    seat_id = data.get('seat_id')
    name = data.get('name')
    phone = data.get('phone')
    
    seat = Seat.query.get(seat_id)
    if seat.customer_name is not None:
        return jsonify({'status': 'error', 'message': 'Ghế này đã có người hốt'}), 400
        
    seat.customer_name = name
    seat.customer_phone = phone
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'Đã chốt ghế {seat_id}'})

# Lệnh khởi tạo database (chỉ chạy một lần hoặc dùng khi cần reset)
@app.cli.command("init-db")
def init_db():
    db.create_all()
    # Tạo sẵn 24 ghế trống nếu chưa có
    if not Seat.query.first():
        for i in range(1, 25):
            db.session.add(Seat(id=str(i)))
        db.session.commit()
    print("Đã khởi tạo database xong!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)