# Proyek Portfolio Pribadi - Flask & MySQL

Ini adalah proyek website portfolio pribadi yang dibuat untuk memenuhi tugas Responsi Pemrograman Web Praktik III. Proyek ini dibangun menggunakan Python dengan *framework* Flask dan terhubung ke database MySQL.

Website ini memiliki dua bagian utama:
1.  **Halaman Publik:** Menampilkan profil, daftar skill, dan galeri proyek.
2.  **Panel Admin:** Halaman *dashboard* yang dilindungi login untuk mengelola (CRUD) semua konten di halaman publik.

---

## 🚀 Fitur Utama

* **Halaman Publik:** Menampilkan data profil, skill, dan proyek langsung dari database.
* **Login Admin:** Otentikasi admin manual menggunakan **Flask Session**.
* **Manajemen Profil:** Admin dapat mengubah nama, bio, dan foto profil.
* **CRUD Proyek:** Admin dapat menambah, mengedit, dan menghapus data proyek (termasuk *upload* gambar).
* **CRUD Skill:** Admin dapat menambah, mengedit, dan menghapus data skill (termasuk nama ikon Font Awesome).
* **Upload Gambar:** Fungsionalitas untuk meng-upload foto profil dan gambar proyek ke server.

---

## 🛠️ Teknologi yang Digunakan

* **Back-end:** Python, Flask
* **Database:** MySQL
* **Driver Database:** `flask-mysqldb` (dijalankan dengan `PyMySQL` untuk kompatibilitas Windows)
* **Front-end:** HTML5, Bootstrap 5, Font Awesome
* **Templating:** Jinja2

---

## ⚙️ Cara Menjalankan Proyek

Berikut adalah langkah-langkah untuk menjalankan proyek ini di lingkungan lokal.

### 1. Persiapan Awal

1.  **Clone Repositori**
    ```bash
    git clone [https://github.com/NAMA_KAMU/NAMA_REPO_KAMU.git](https://github.com/NAMA_KAMU/NAMA_REPO_KAMU.git)
    cd NAMA_REPO_KAMU
    ```

2.  **Buat & Aktifkan Virtual Environment**
    ```bash
    # Windows
    python -m venv env
    .\env\Scripts\activate
    ```

3.  **Install Dependencies**
    Pastikan Anda memiliki file `requirements.txt` dan jalankan:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Setup Database (XAMPP & phpMyAdmin)

1.  Jalankan **XAMPP Control Panel**, lalu start **Apache** dan **MySQL**.
2.  Buka `localhost/phpmyadmin`.
3.  Buat database baru dengan nama `portofolio`.
4.  Pilih database `portofolio`, lalu klik *tab* **SQL**.
5.  Salin dan jalankan skema di bawah ini untuk membuat semua tabel:

    ```sql
    CREATE TABLE `users` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `username` varchar(80) NOT NULL,
      `password` varchar(255) NOT NULL,
      `name` varchar(100) NOT NULL,
      `bio` text,
      `photo` varchar(255) DEFAULT 'default.jpg',
      PRIMARY KEY (`id`),
      UNIQUE KEY `username` (`username`)
    );

    CREATE TABLE `projects` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `title` varchar(150) NOT NULL,
      `description` text,
      `image` varchar(255) DEFAULT NULL,
      `link` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`id`)
    );

    CREATE TABLE `skills` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(100) NOT NULL,
      `level` varchar(50) DEFAULT NULL,
      `icon` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`id`)
    );
    ```

6.  **PENTING (Data Admin):** Masukkan satu data admin secara manual.
    * Klik tabel `users`, lalu *tab* **Insert**.
    * Isi `username` (misal: `admin`).
    * Isi `password` (misal: `admin123`). **Peringatan:** Kode ini menggunakan perbandingan teks biasa, jadi *password* ini harus cocok dengan yang Anda ketik saat login.
    * Isi `name` (misal: `Nama Admin`).
    * Klik **Go**.

### 3. Buat Folder Upload

1.  Di dalam folder proyek, buat folder `static`.
2.  Di dalam folder `static`, buat folder `image`.
    Strukturnya akan menjadi: `.../static/image/`
3.  (Opsional) Masukkan file `default.jpg` di dalam `static/image` sebagai foto profil awal.

### 4. Jalankan Aplikasi

1.  Pastikan Anda berada di direktori utama proyek (tempat `myapp.py` berada).
2.  Jalankan aplikasi Flask:
    ```bash
    py myapp.py
    ```
3.  Buka `http://127.0.0.1:5000` di browser Anda.

---

## 🧠 Cara Kerja (Arsitektur Logika)

Proyek ini sengaja dibuat dalam satu file `myapp.py` untuk kesederhanaan, namun menggunakan beberapa logika kunci:

### 1. Aplikasi File Tunggal (`myapp.py`)

Seluruh logika back-end, termasuk konfigurasi, definisi rute, dan fungsi *helper* (upload file) dimuat dalam satu file.

### 2. Driver `PyMySQL`

Proyek ini menggunakan `flask-mysqldb`, yang sering bermasalah di Windows. Solusinya adalah dengan mengimpor `pymysql` dan menjalankannya sebagai *driver* MySQLdb di baris paling atas `myapp.py`:

```python
import pymysql
pymysql.install_as_MySQLdb()
