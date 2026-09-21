#game name Midnight Torque

from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'verysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------------
# Модель користувача
# ---------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------
# Головна
# ---------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------------
# Реєстрація
# ---------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Такий логін вже існує!")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Такий email вже існує!")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Акаунт створено!")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------------
# Логін
# ---------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("profile"))
        else:
            flash("Неправильні дані!")

    return render_template("login.html")

# ---------------------
# Профіль
# ---------------------
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# ---------------------
# Завантаження гри
# ---------------------
@app.route("/download")
@login_required
def download():
    return send_file("mdtsetup.exe", as_attachment=True)

# ---------------------
# Вихід
# ---------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ---------------------
# Запуск
# ---------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)