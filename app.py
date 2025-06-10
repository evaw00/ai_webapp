import os
from flask import Flask, redirect, url_for, render_template, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.github import make_github_blueprint, github
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersekret"  # Für Produktion: Umgebungsvariable nutzen

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max 16MB

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'github.login'

# OAuth2 GitHub Setup
github_blueprint = make_github_blueprint(
    client_id="DEINE_GITHUB_CLIENT_ID",
    client_secret="DEIN_GITHUB_CLIENT_SECRET",
)
app.register_blueprint(github_blueprint, url_prefix="/login")

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300))
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='images')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    image = db.relationship('Image', backref='comments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    images = Image.query.all()
    return render_template("index.html", images=images)

@app.route("/login")
def login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    if resp.ok:
        info = resp.json()
        github_id = str(info["id"])
        username = info["login"]
        user = User.query.filter_by(github_id=github_id).first()
        if not user:
            user = User(github_id=github_id, username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Erfolgreich eingeloggt!", "success")
        return redirect(url_for("index"))
    flash("Login fehlgeschlagen!", "danger")
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ausgeloggt!", "info")
    return redirect(url_for("index"))

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "image" not in request.files:
            flash("Kein Bild ausgewählt", "danger")
            return redirect(request.url)
        file = request.files["image"]
        description = request.form.get("description", "")
        if file.filename == "":
            flash("Kein Bild ausgewählt", "danger")
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = Image(filename=filename, description=description, user_id=current_user.id)
            db.session.add(img)
            db.session.commit()
            flash("Bild erfolgreich hochgeladen", "success")
            return redirect(url_for("index"))
    return render_template("upload.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/image/<int:image_id>", methods=["GET", "POST"])
def image_detail(image_id):
    img = Image.query.get_or_404(image_id)
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Bitte einloggen zum Kommentieren", "warning")
            return redirect(url_for("login"))
        text = request.form.get("comment")
        if text:
            comment = Comment(text=text, image_id=img.id, user_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            flash("Kommentar hinzugefügt", "success")
            return redirect(url_for("image_detail", image_id=image_id))
    return render_template("image_detail.html", image=img)

@app.route("/delete/<int:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    img = Image.query.get_or_404(image_id)
    if img.user_id != current_user.id:
        flash("Du kannst nur deine eigenen Bilder löschen", "danger")
        return redirect(url_for("index"))
    # Bilddatei löschen
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
    except Exception:
        pass
    db.session.delete(img)
    db.session.commit()
    flash("Bild gelöscht", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)