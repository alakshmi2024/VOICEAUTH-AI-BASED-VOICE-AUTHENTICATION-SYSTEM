from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
import numpy as np
from pydub import AudioSegment

from utils.voice_features import extract_voice_features
from utils.voice_verify import verify_voice_match

app = Flask(__name__)
app.secret_key = "VOICEAUTH_SECRET_2026"

UPLOAD_FOLDER = "static/uploads"
DB_NAME = "database.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            voice_features TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        voice_file = request.files.get("voice")

        if not voice_file:
            flash("Please record voice!", "danger")
            return redirect(url_for("register"))

        # Save webm first
        webm_path = os.path.join(UPLOAD_FOLDER, f"{email}_register.webm")
        wav_path = os.path.join(UPLOAD_FOLDER, f"{email}_register.wav")

        voice_file.save(webm_path)

        try:
            # Convert webm to wav
            audio = AudioSegment.from_file(webm_path, format="webm")
            audio.export(wav_path, format="wav")

            # Extract Features
            features = extract_voice_features(wav_path)
            features_str = ",".join(map(str, features))

        except Exception as e:
            print("Error in voice processing:", e)
            flash("Voice processing failed. Try again!", "danger")
            return redirect(url_for("register"))

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(name,email,password,voice_features) VALUES(?,?,?,?)",
                (name, email, password, features_str)
            )

            conn.commit()
            conn.close()

            flash("Registration Successful! Now Login.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        voice_file = request.files.get("voice")

        if not voice_file:
            flash("Please record your voice!", "danger")
            return redirect(url_for("login"))

        # Save webm first
        webm_path = os.path.join(UPLOAD_FOLDER, f"{email}_login.webm")
        wav_path = os.path.join(UPLOAD_FOLDER, f"{email}_login.wav")

        voice_file.save(webm_path)

        try:
            # Convert webm to wav
            audio = AudioSegment.from_file(webm_path, format="webm")
            audio.export(wav_path, format="wav")

        except Exception as e:
            print("Error converting audio:", e)
            flash("Voice conversion failed! Install FFmpeg.", "danger")
            return redirect(url_for("login"))

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id,name,password,voice_features FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            flash("User not found!", "danger")
            return redirect(url_for("login"))

        user_id, name, db_password, db_features = user

        if password != db_password:
            flash("Invalid password!", "danger")
            return redirect(url_for("login"))

        db_vec = np.array(list(map(float, db_features.split(","))))

        ok, similarity = verify_voice_match(wav_path, db_vec)

        if ok:
            session["user_id"] = user_id
            session["name"] = name
            session["email"] = email
            flash(f"Voice Verified  Similarity Score: {similarity:.2f}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(f"Voice Authentication Failed  Similarity Score: {similarity:.2f}", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", name=session["name"])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logout successful!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
