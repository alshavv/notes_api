# Notes API (Flask + JWT + Swagger)

Project ini adalah REST API sederhana untuk mengelola catatan (**Notes**) dengan autentikasi JWT, dokumentasi Swagger, dan database MySQL (XAMPP).

---

## 🚀 Fitur
- Register & Login User
- Autentikasi menggunakan **JWT Token**
- CRUD Notes (Create, Read, Update, Delete)
- Dokumentasi interaktif dengan **Swagger UI**
- Database MySQL (XAMPP)

---

## ⚙️ Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/alshavv/notes_api.git
cd notes_api

## Cara Menjalankan
```bash
pip install -r requirements.txt
python app.py
```
Swagger UI: buka http://localhost:5000/apidocs

## Endpoints
- POST /register
- POST /login
- GET /notes (JWT)
- POST /notes (JWT)
- PUT /notes/<id> (JWT)
- DELETE /notes/<id> (JWT)

## Tips pakai Swagger Bearer Token
1. Login untuk mendapatkan `token`.
2. Klik tombol **Authorize** di kanan atas Swagger UI.
3. Masukkan: `Bearer <token>` lalu Authorize.
4. Jalankan endpoint Notes.

## Alur Penggunaan API

1. Register user baru
Endpoint: POST /register
Body (JSON):

{
  "username": "user",
  "password": "tesgencidevpertama"
}


2. Login
Endpoint: POST /login
Body (JSON):

{
  "username": "user",
  "password": "tesgencidevpertama"
}

Response:

{
  "access_token": "<JWT_TOKEN>"
}


## Authorize di Swagger
Klik tombol Authorize → Masukkan:

Bearer <JWT_TOKEN>


## CRUD Notes
Setelah authorize, lakukan :
Tambah note: POST /notes
Lihat semua notes: GET /notes
Update note: PUT /notes/{id}
Hapus note: DELETE /notes/{id}