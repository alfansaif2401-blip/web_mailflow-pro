"""
MailFlow Pro — Sistem Manajemen Surat Masuk & Keluar.

Arsitektur:
  - Flask sebagai web framework utama.
  - SQLAlchemy + SQLite sebagai ORM & penyimpanan data.
  - Session berbasis server (cookie HTTPONLY) untuk autentikasi.
  - Role-Based Access Control: Admin (CRUD penuh) vs Staff (Create/Read/Update).
  - Jinja2 untuk server-side rendering halaman HTML.

Cara Menjalankan:
  pip install -r requirements.txt
  python app.py

Akun Default (untuk testing):
  Admin  → username: admin  | password: admin123
  Staff  → username: staff  | password: staff123
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, flash, jsonify, redirect,
    render_template, request, session, url_for,
)
from sqlalchemy.exc import IntegrityError

from database import Surat, User, db

# ─────────────────────────────────────────────────────────────────────────────
# Konfigurasi Aplikasi
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "mailflow-pro-ultra-secure-secret-2024!@#$%^&*",
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///mailsystem.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 30  # 30 hari

db.init_app(app)


# ─────────────────────────────────────────────────────────────────────────────
# Decorators Keamanan
# ─────────────────────────────────────────────────────────────────────────────

def login_required(f):
    """
    Decorator: memproteksi endpoint yang membutuhkan sesi aktif.
    Mengarahkan ke /login untuk request HTML, atau mengembalikan 401 untuk API.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized", "message": "Silakan login terlebih dahulu"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """
    Decorator: memproteksi endpoint khusus Admin.
    Mengembalikan 403 jika role bukan Admin.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "Admin":
            if request.path.startswith("/api/"):
                return jsonify({"error": "Forbidden", "message": "Akses ditolak. Fitur ini khusus Admin."}), 403
            flash("Akses ditolak. Hanya Admin yang dapat melakukan operasi ini.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────────────────────────
# Seeder & Helper
# ─────────────────────────────────────────────────────────────────────────────

def seed_database() -> None:
    """
    Mengisi database dengan data awal.
    Membuat dua user default dan beberapa surat contoh jika database masih kosong.
    """
    # ── Default Users ──────────────────────────────────────────────────────────
    if not User.query.first():
        admin = User(username="admin", role="Admin", nama_lengkap="Administrator")
        admin.set_password("admin123")

        staff = User(username="staff", role="Staff", nama_lengkap="Staff Administrasi")
        staff.set_password("staff123")

        db.session.add_all([admin, staff])
        db.session.commit()
        print("✅  Default users dibuat  →  admin/admin123  &  staff/staff123")

    # ── Sample Surat ───────────────────────────────────────────────────────────
    if not Surat.query.first():
        samples = [
            Surat(nomor_surat="SM-2024-0891", judul_surat="Laporan Kuartal Keuangan Q1",
                  jenis_surat="Masuk", pengirim_penerima="Divisi Keuangan Pusat",
                  tanggal_arsip=datetime(2024, 1, 15).date(),
                  keterangan="Laporan keuangan untuk audit tahunan", dibuat_oleh="admin"),
            Surat(nomor_surat="SK-2024-1042", judul_surat="Undangan Rapat Direksi",
                  jenis_surat="Keluar", pengirim_penerima="Seluruh Kepala Divisi",
                  tanggal_arsip=datetime(2024, 1, 20).date(),
                  keterangan="Rapat koordinasi strategi semester I", dibuat_oleh="admin"),
            Surat(nomor_surat="SM-2024-0905", judul_surat="Permintaan Cuti Karyawan",
                  jenis_surat="Masuk", pengirim_penerima="Budi Santoso – Divisi IT",
                  tanggal_arsip=datetime(2024, 2, 1).date(),
                  keterangan="Pengajuan cuti tahunan 5 hari kerja", dibuat_oleh="staff"),
            Surat(nomor_surat="SK-2024-1102", judul_surat="Penawaran Kerjasama Vendor",
                  jenis_surat="Keluar", pengirim_penerima="PT. Digital Solusi Indonesia",
                  tanggal_arsip=datetime(2024, 2, 10).date(),
                  keterangan="Penawaran kerjasama pengembangan sistem ERP", dibuat_oleh="admin"),
            Surat(nomor_surat="SM-2024-0912", judul_surat="Data Kepegawaian 2024",
                  jenis_surat="Masuk", pengirim_penerima="BKN Regional III",
                  tanggal_arsip=datetime(2024, 2, 15).date(),
                  keterangan="Permintaan pemutakhiran data ASN 2024", dibuat_oleh="staff"),
            Surat(nomor_surat="SK-2024-1115", judul_surat="Konfirmasi Kehadiran Rapat",
                  jenis_surat="Keluar", pengirim_penerima="Kementerian Dalam Negeri",
                  tanggal_arsip=datetime(2024, 2, 18).date(),
                  keterangan="Konfirmasi kehadiran rapat koordinasi nasional", dibuat_oleh="admin"),
            Surat(nomor_surat="SM-2024-0930", judul_surat="SPK Pengadaan Perangkat IT",
                  jenis_surat="Masuk", pengirim_penerima="CV. TechSupply Nusantara",
                  tanggal_arsip=datetime(2024, 3, 1).date(),
                  keterangan="Surat perintah kerja pengadaan 20 unit laptop", dibuat_oleh="staff"),
            Surat(nomor_surat="SK-2024-1130", judul_surat="MoU Kerjasama Digitalisasi",
                  jenis_surat="Keluar", pengirim_penerima="Universitas Teknologi Surabaya",
                  tanggal_arsip=datetime(2024, 3, 5).date(),
                  keterangan="Penandatanganan MoU program digitalisasi kampus", dibuat_oleh="admin"),
        ]
        db.session.add_all(samples)
        db.session.commit()
        print("✅  8 data surat contoh berhasil dibuat")


def _get_stats() -> dict:
    """Menghitung dan mengembalikan statistik ringkasan sistem."""
    return {
        "total_masuk": Surat.query.filter_by(jenis_surat="Masuk").count(),
        "total_keluar": Surat.query.filter_by(jenis_surat="Keluar").count(),
        "total_arsip": Surat.query.count(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Redirect otomatis: ke dashboard jika sudah login, atau ke halaman login."""
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login_page"))


@app.route("/login")
def login_page():
    """Render halaman login. Redirect ke dashboard jika sudah memiliki sesi."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Autentikasi pengguna dan pembuatan sesi.

    Payload JSON:
        username (str) : Nama pengguna (wajib).
        password (str) : Kata sandi plaintext (wajib).
        remember (bool): Pertahankan sesi 30 hari (opsional).

    Returns:
        200: Data user + URL redirect.
        400: Input tidak lengkap.
        401: Kredensial salah.
    """
    data = request.get_json() or {}

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username dan password wajib diisi"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Username atau password salah"}), 401

    session.permanent = bool(data.get("remember", False))
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role
    session["nama_lengkap"] = user.nama_lengkap or user.username

    return jsonify({
        "message": f"Selamat datang kembali, {session['nama_lengkap']}!",
        "user": user.to_dict(),
        "redirect": "/dashboard",
    })


@app.route("/api/logout")
def api_logout():
    """Hapus sesi aktif dan arahkan ke halaman login."""
    session.clear()
    return redirect(url_for("login_page"))


# ─────────────────────────────────────────────────────────────────────────────
# Page Routes (Server-Side Rendering)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Render halaman utama dashboard.
    Menampilkan statistik sistem dan 10 aktivitas surat terbaru.
    """
    stats = _get_stats()
    recent_surat = Surat.query.order_by(Surat.dibuat_pada.desc()).limit(10).all()
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        stats=stats,
        recent_surat=recent_surat,
    )


@app.route("/surat")
@login_required
def surat_page():
    """
    Render halaman daftar surat.

    Query Params:
        jenis (str): Filter 'Masuk', 'Keluar', atau kosong (semua surat).
    """
    jenis_filter = request.args.get("jenis", "")
    page_map = {"Masuk": "surat_masuk", "Keluar": "surat_keluar", "": "arsip"}
    active_page = page_map.get(jenis_filter, "arsip")

    query = Surat.query.order_by(Surat.dibuat_pada.desc())
    if jenis_filter:
        query = query.filter_by(jenis_surat=jenis_filter)

    surat_list = query.all()
    stats = _get_stats()

    return render_template(
        "surat.html",
        active_page=active_page,
        jenis_filter=jenis_filter,
        surat_list=surat_list,
        stats=stats,
    )


# ─────────────────────────────────────────────────────────────────────────────
# API CRUD Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/surat", methods=["GET"])
@login_required
def api_get_surat():
    """
    Mengambil daftar surat dengan filter dan pencarian.

    Query Params:
        jenis  (str): Filter jenis surat.
        search (str): Pencarian di nomor, judul, atau pengirim/penerima.

    Returns:
        JSON: { data: [...], total: int, stats: {...} }
    """
    jenis = request.args.get("jenis", "")
    search = request.args.get("search", "").strip()

    query = Surat.query.order_by(Surat.dibuat_pada.desc())

    if jenis:
        query = query.filter_by(jenis_surat=jenis)

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Surat.nomor_surat.ilike(like),
                Surat.judul_surat.ilike(like),
                Surat.pengirim_penerima.ilike(like),
            )
        )

    rows = query.all()
    return jsonify({
        "data": [s.to_dict() for s in rows],
        "total": len(rows),
        "stats": _get_stats(),
    })


@app.route("/api/surat", methods=["POST"])
@login_required
def api_create_surat():
    """
    Membuat entri surat baru.

    Payload JSON (wajib*):
        nomor_surat*       : Nomor surat unik.
        judul_surat*       : Judul/perihal surat.
        jenis_surat*       : 'Masuk' atau 'Keluar'.
        pengirim_penerima  : Nama pengirim/penerima (opsional).
        tanggal_arsip      : Format YYYY-MM-DD (opsional, default: hari ini).
        keterangan         : Catatan (opsional).

    Returns:
        201: Data surat yang berhasil dibuat.
        400: Validasi gagal.
        409: Nomor surat sudah ada.
    """
    data = request.get_json() or {}

    required_fields = ["nomor_surat", "judul_surat", "jenis_surat"]
    errors = [f"'{f}' wajib diisi" for f in required_fields if not data.get(f, "").strip()]
    if errors:
        return jsonify({"error": "Validasi gagal", "details": errors}), 400

    if data["jenis_surat"] not in ("Masuk", "Keluar"):
        return jsonify({"error": "Jenis surat harus 'Masuk' atau 'Keluar'"}), 400

    tanggal = datetime.utcnow().date()
    if data.get("tanggal_arsip"):
        try:
            tanggal = datetime.strptime(data["tanggal_arsip"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Format tanggal tidak valid — gunakan YYYY-MM-DD"}), 400

    surat = Surat(
        nomor_surat=data["nomor_surat"].strip().upper(),
        judul_surat=data["judul_surat"].strip(),
        jenis_surat=data["jenis_surat"],
        pengirim_penerima=data.get("pengirim_penerima", "").strip() or None,
        tanggal_arsip=tanggal,
        keterangan=data.get("keterangan", "").strip() or None,
        dibuat_oleh=session["username"],
    )

    try:
        db.session.add(surat)
        db.session.commit()
        return jsonify({"message": f"Surat {surat.nomor_surat} berhasil ditambahkan", "data": surat.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Nomor surat '{data['nomor_surat']}' sudah terdaftar di sistem"}), 409


@app.route("/api/surat/<int:surat_id>", methods=["PUT"])
@login_required
def api_update_surat(surat_id: int):
    """
    Memperbarui data surat yang ada. Tersedia untuk Admin dan Staff.

    Args:
        surat_id: ID surat yang akan diperbarui.

    Returns:
        200: Data surat setelah diperbarui.
        400: Input tidak valid.
        404: Surat tidak ditemukan.
        409: Konflik nomor surat.
    """
    surat = db.get_or_404(Surat, surat_id)
    data = request.get_json() or {}

    if data.get("nomor_surat", "").strip():
        surat.nomor_surat = data["nomor_surat"].strip().upper()
    if data.get("judul_surat", "").strip():
        surat.judul_surat = data["judul_surat"].strip()
    if data.get("jenis_surat") in ("Masuk", "Keluar"):
        surat.jenis_surat = data["jenis_surat"]
    if "pengirim_penerima" in data:
        surat.pengirim_penerima = data["pengirim_penerima"].strip() or None
    if "keterangan" in data:
        surat.keterangan = data["keterangan"].strip() or None
    if data.get("tanggal_arsip"):
        try:
            surat.tanggal_arsip = datetime.strptime(data["tanggal_arsip"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Format tanggal tidak valid"}), 400

    surat.diperbarui_pada = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({"message": f"Surat {surat.nomor_surat} berhasil diperbarui", "data": surat.to_dict()})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Nomor surat sudah digunakan surat lain"}), 409


@app.route("/api/surat/<int:surat_id>", methods=["DELETE"])
@login_required
@admin_required
def api_delete_surat(surat_id: int):
    """
    Menghapus surat dari sistem. KHUSUS ADMIN.

    Args:
        surat_id: ID surat yang akan dihapus.

    Returns:
        200: Konfirmasi penghapusan.
        403: Bukan Admin.
        404: Surat tidak ditemukan.
    """
    surat = db.get_or_404(Surat, surat_id)
    nomor = surat.nomor_surat
    db.session.delete(surat)
    db.session.commit()
    return jsonify({"message": f"Surat {nomor} berhasil dihapus dari sistem"})


@app.route("/api/stats")
@login_required
def api_stats():
    """Mengembalikan statistik lengkap sistem beserta 5 aktivitas terbaru."""
    stats = _get_stats()
    recent = Surat.query.order_by(Surat.dibuat_pada.desc()).limit(5).all()
    stats["recent"] = [s.to_dict() for s in recent]
    return jsonify(stats)


# ─────────────────────────────────────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(_):
    """Handler 404 — API: JSON, halaman HTML: redirect ke dashboard."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint tidak ditemukan"}), 404
    return redirect(url_for("dashboard"))


@app.errorhandler(500)
def server_error(_):
    """Handler 500 — rollback transaksi dan kirim respons error."""
    db.session.rollback()
    if request.path.startswith("/api/"):
        return jsonify({"error": "Terjadi kesalahan pada server internal"}), 500
    return redirect(url_for("dashboard"))


# ─────────────────────────────────────────────────────────────────────────────
# Inisialisasi & Entry Point
# ─────────────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()       # Buat tabel jika belum ada
    seed_database()       # Isi data awal

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  🚀  MailFlow Pro — http://localhost:5000")
    print("  📧  Admin  :  username=admin   password=admin123")
    print("  👤  Staff  :  username=staff   password=staff123")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
