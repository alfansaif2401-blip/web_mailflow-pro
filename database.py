"""
Modul database untuk MailFlow Pro.
Mendefinisikan model-model SQLAlchemy: User dan Surat.
ls
Penggunaan:
    from database import db, User, Surat
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    Model pengguna sistem dengan dukungan hashing password.

    Atribut:
        id          : Kunci utama, auto-increment.
        username    : Nama pengguna yang unik dan terindeks.
        password    : Hash password (Werkzeug PBKDF2-SHA256).
        role        : Peran pengguna — 'Admin' atau 'Staff'.
        nama_lengkap: Nama lengkap untuk tampilan UI.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Staff")
    nama_lengkap = db.Column(db.String(100), nullable=True)

    def set_password(self, raw_password: str) -> None:
        """Hash password menggunakan PBKDF2-SHA256 dan simpan ke kolom password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verifikasi password plaintext terhadap hash yang tersimpan."""
        return check_password_hash(self.password, raw_password)

    def to_dict(self) -> dict:
        """Konversi objek User ke dictionary bersih untuk respons API."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "nama_lengkap": self.nama_lengkap or self.username,
        }

    def __repr__(self) -> str:
        return f"<User {self.username!r} ({self.role})>"


class Surat(db.Model):
    """
    Model surat masuk dan keluar dengan metadata lengkap.

    Atribut:
        id               : Kunci utama, auto-increment.
        nomor_surat      : Nomor surat yang unik dan terindeks (mis. SM-2024-001).
        judul_surat      : Judul atau perihal surat.
        jenis_surat      : Kategori — 'Masuk' atau 'Keluar'.
        pengirim_penerima: Nama pihak pengirim (Masuk) atau penerima (Keluar).
        tanggal_arsip    : Tanggal surat dicatat ke sistem.
        keterangan       : Catatan tambahan (opsional).
        dibuat_oleh      : Username pembuat entri.
        dibuat_pada      : Timestamp pembuatan (UTC).
        diperbarui_pada  : Timestamp perubahan terakhir (UTC).
    """

    __tablename__ = "surat"

    id = db.Column(db.Integer, primary_key=True)
    nomor_surat = db.Column(db.String(100), unique=True, nullable=False, index=True)
    judul_surat = db.Column(db.String(200), nullable=False)
    jenis_surat = db.Column(db.String(10), nullable=False)          # 'Masuk' | 'Keluar'
    pengirim_penerima = db.Column(db.String(150), nullable=True)
    tanggal_arsip = db.Column(db.Date, nullable=True)
    keterangan = db.Column(db.Text, nullable=True)
    dibuat_oleh = db.Column(db.String(80), nullable=True)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)
    diperbarui_pada = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Konversi objek Surat ke dictionary bersih untuk respons API."""
        return {
            "id": self.id,
            "nomor_surat": self.nomor_surat,
            "judul_surat": self.judul_surat,
            "jenis_surat": self.jenis_surat,
            "pengirim_penerima": self.pengirim_penerima or "-",
            "tanggal_arsip": (
                self.tanggal_arsip.strftime("%Y-%m-%d") if self.tanggal_arsip else None
            ),
            "tanggal_arsip_fmt": (
                self.tanggal_arsip.strftime("%d %b %Y") if self.tanggal_arsip else "-"
            ),
            "keterangan": self.keterangan or "",
            "dibuat_oleh": self.dibuat_oleh or "-",
            "dibuat_pada": (
                self.dibuat_pada.strftime("%Y-%m-%d %H:%M") if self.dibuat_pada else None
            ),
        }

    def __repr__(self) -> str:
        return f"<Surat {self.nomor_surat!r} ({self.jenis_surat})>"
