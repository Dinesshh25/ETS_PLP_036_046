# Ekstraktor CRUD Matrix (ETS PLP)

Ekstraktor CRUD Matrix adalah sebuah *tool* berbasis Python yang berfungsi untuk membaca file skrip SQL dan menghasilkan matriks CRUD (Create, Read, Update, Delete). *Tool* ini menganalisis operasi apa saja yang dilakukan terhadap tabel-tabel di dalam *database* tanpa memerlukan koneksi langsung ke *database* atau skema aktif, melainkan murni melalui analisis teks kueri SQL.

Proyek ini dibangun dari awal menggunakan prinsip *compiler design* yang diadaptasi dari buku **Crafting Interpreters**.

## Arsitektur Pipeline
Pemrosesan kueri SQL dilakukan melalui empat tahapan utama secara berurutan:
1. **Lexer (`crud/lexer.py`)**: Membaca teks SQL mentah dan mengubahnya menjadi deretan token bermakna.
2. **Parser (`crud/parser.py`)**: Menyusun token menjadi *Abstract Syntax Tree* (AST) menggunakan pendekatan *Recursive Descent Parsing*.
3. **Resolver (`crud/resolver.py`)**: Menangani penelusuran lingkup (*scope*), membongkar alias, dan menentukan ke tabel mana sebuah kolom merujuk.
4. **Analyzer (`crud/analyzer.py`)**: Berjalan di atas AST untuk menerapkan aturan ekstraksi operasi C, R, U, D sesuai spesifikasi.

## Persyaratan Sistem
* **Python**: Versi 3.10 atau lebih baru.
* **Dependensi**: `pytest` (untuk menjalankan pengujian).

## Instalasi
1. Kloning repositori ini ke dalam mesin lokal Anda.
2. Buka terminal dan arahkan ke direktori proyek (`crud-extractor`).
3. Instal *package* yang dibutuhkan (hanya `pytest` untuk *testing*):
   ```bash
   python -m pip install pytest
   ```

## Penggunaan (Command Line Interface)

*Tool* ini menyediakan CLI yang fungsional untuk menganalisis skrip SQL. Jalankan perintah berikut dari root direktori proyek.

**1. Mengekstrak Matriks CRUD Dasar:**
```bash
python -m crud.cli data/sample/*.sql
```
*(Menghasilkan file `crud_matrix.csv` yang berisi rangkuman operasi tabel per file SQL).*

**2. Mengekstrak Matriks dengan Detail dan Penggunaan Kolom:**
```bash
python -m crud.cli data/sample/*.sql --detail detail.csv --kolom kolom.csv
```
*(Menyimpan detail baris dan jenis statement ke `detail.csv`, serta melacak penggunaan kolom ke `kolom.csv`).*

**3. Visualisasi Pohon AST & Resolusi Tabel (Untuk Debugging):**
```bash
python -m crud.cli data/sample/audit.sql --ast
```
*(Mencetak hierarki AST dan memperlihatkan hasil resolusi tabel/alias langsung di layar terminal).*

**4. Evaluasi Kinerja (Parser vs Regex Baseline):**
```bash
python evaluate.py
```
*(Menghitung skor Precision, Recall, dan F1 dengan membandingkan hasil parser melawan `regex_extractor.py` dan kunci jawaban di `ground_truth.csv`).*

## Pengujian (Testing)
Proyek ini mengadopsi *Test-Driven Development* (TDD). Untuk menjalankan seluruh pengujian (*unit test*, tes regresi bug, dan *edge cases*):

```bash
python -m pytest
```
*Gunakan opsi `-v` (`python -m pytest -v`) untuk melihat detail pengujian yang lulus atau gagal.*

## Struktur Direktori
* `crud/` - Inti dari program (Lexer, Parser, AST, Resolver, Analyzer, Pipeline, CLI).
* `tests/` - Direktori pengujian (`pytest`).
* `data/` - Dataset file SQL uji coba (`sample/*.sql`) dan kunci jawaban (`ground_truth.csv`).
* `baseline/` - Implementasi ekstraktor berbasis Regex sederhana sebagai pembanding.
* `docs/` - Dokumentasi proyek, Laporan Akhir, Kartu Desain, Log AI, dan Laporan Bug.

## Tim Pengembang
Proyek ini dikerjakan secara *Pair Programming* oleh:
* **Alifah** - (Lexer & Resolver)
* **Ganesh** - (Parser & Analyzer)
