# 📧 MailFlow Pro — Sistem Manajemen Surat

Aplikasi web manajemen surat masuk & keluar berbasis Flask + SQLAlchemy dengan desain profesional glassmorphism.

---

## 🚀 Cara Menjalankan (PyCharm / Terminal)

### Langkah 1 — Buka folder project
```
File → Open → pilih folder mailflow_pro
```

### Langkah 2 — Buat Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Langkah 3 — Install dependensi
```bash
pip install -r requirements.txt
```

### Langkah 4 — Jalankan aplikasi
```bash
python app.py
```

### Langkah 5 — Buka browser
```
http://localhost:5000
```

---

## 👤 Akun Default

| Role  | Username | Password  | Hak Akses              |
|-------|----------|-----------|------------------------|
| Admin | admin    | admin123  | Create, Read, Update, **Delete** |
| Staff | staff    | staff123  | Create, Read, Update (tanpa Delete) |

---

## 📁 Struktur File

```
mailflow_pro/
├── app.py           ← Logic utama Flask + semua endpoint
├── database.py      ← Model SQLAlchemy (User & Surat)
├── requirements.txt ← Daftar dependensi
├── mailsystem.db    ← Database SQLite (dibuat otomatis)
└── templates/
    ├── base.html    ← Layout utama (sidebar + topbar)
    ├── login.html   ← Halaman login
    ├── dashboard.html ← Dashboard statistik
    └── surat.html   ← Manajemen surat (CRUD)
```

---

## 🔗 Endpoint API

| Method | URL                  | Deskripsi                        | Akses        |
|--------|----------------------|----------------------------------|--------------|
| POST   | /api/login           | Login & buat sesi                | Public       |
| GET    | /api/logout          | Hapus sesi & redirect login      | Login        |
| GET    | /api/surat           | Ambil daftar surat (JSON)        | Login        |
| POST   | /api/surat           | Tambah surat baru                | Login        |
| PUT    | /api/surat/\<id\>    | Perbarui surat                   | Login        |
| DELETE | /api/surat/\<id\>    | Hapus surat                      | **Admin only** |
| GET    | /api/stats           | Statistik sistem                 | Login        |
