from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'khoa_bi_mat_khong_tiet_lo'

# Cấu hình Database
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' hoặc 'user'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seat_id = db.Column(db.String(10), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    pickup_point = db.Column(db.String(200), nullable=False)
    dropoff_point = db.Column(db.String(200), nullable=False)
    travel_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='Chờ thanh toán')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/')
def index():
    db.create_all()
    # Tạo Admin mặc định nếu chưa có (User: admin / Pass: admin123)
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
        admin = User(username='admin', password=hashed_pw, role='admin')
        db.session.add(admin)
        db.session.commit()

    booked_seats = [b.seat_id for b in Booking.query.filter(Booking.seat_id != None).all()]
    return render_template('index.html', booked_seats=booked_seats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Tên này có người dùng rồi!')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/book', methods=['POST'])
@login_required
def book():
    data = request.form
    seat_id = data.get('seat_id')
    
    # Kiểm tra ghế đã đặt chưa
    if seat_id:
        existing = Booking.query.filter_by(seat_id=seat_id).first()
        if existing:
            return "Ghế này đã có người đặt rồi!", 400

    new_booking = Booking(
        user_id=current_user.id,
        seat_id=seat_id,
        customer_name=data.get('customer_name'),
        customer_phone=data.get('customer_phone'),
        pickup_point=data.get('pickup_point'),
        dropoff_point=data.get('dropoff_point'),
        travel_date=data.get('travel_date')
    )
    db.session.add(new_booking)
    db.session.commit()
    return redirect(url_for('my_tickets'))

@app.route('/my-tickets')
@login_required
def my_tickets():
    if current_user.role == 'admin':
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('my_tickets.html', bookings=bookings)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)