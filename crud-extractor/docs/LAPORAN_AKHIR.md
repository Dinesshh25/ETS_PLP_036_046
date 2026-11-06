# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text
Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. Perintah SQL di dalam komentar diekstraksi sebagai operasi CRUD (False Positive)
   - SQL (data/sample/laporan_penjualan.sql baris 2 dan data/sample/pemeliharaan.sql baris 2):
     -- DELETE FROM pelanggan   (baris ini komentar, bukan perintah)
     /* Catatan lama: UPDATE pelanggan_lama sudah tidak dipakai. */
   - Kesalahan regex:
     Regex mencocokkan pola teks DELETE FROM pelanggan dan UPDATE pelanggan_lama secara naif, lalu salah mencatatnya sebagai operasi DELETE pada tabel pelanggan dan UPDATE pada tabel pelanggan_lama.
   - Mengapa parser benar (Konsep Lexing - Bab 4):
     Pada tahap scanning leksikal (Crafting Interpreters Bab 4), lexer menyaring dan mengabaikan komentar baris (--) serta komentar blok (/* ... */ pada TODO 3). Komentar tidak menghasilkan token leksikal ke token stream. Karena token tersebut tidak pernah masuk ke parser, parser tidak pernah membentuk AST untuk komentar, sehingga CRUD matrix tidak terkotori oleh teks komentar.

2. Keyword SQL di dalam string literal dianggap sebagai nama tabel (False Positive)
   - SQL (data/sample/laporan_penjualan.sql baris 6):
     WHERE o.status = 'LUNAS' AND o.catatan <> 'FROM rahasia'
   - Kesalahan regex:
     Regex mencocokkan pola FROM yang diikuti kata rahasia di dalam tanda kutip tunggal, sehingga salah mendeteksi tabel palsu rahasia dengan operasi READ (R).
   - Mengapa parser benar (Konsep Lexing & Parsing - Bab 4 & 6):
     Lexer mengenali konteks string literal di mana 'FROM rahasia' dipindai secara utuh sebagai satu token STRING, bukan token KEYWORD(FROM) dan IDENT(rahasia). Penanganan escape kutip pada Bug 3 dan operator <> pada Bug 2 juga menjamin tokenisasi string berjalan tuntas. Selanjutnya, parser rekursif (Bab 6) menempatkan token string tersebut ke dalam node Literal sebagai operand nilai dari BinaryOp perbandingan, bukan sebagai TableRef pada klausa FROM. Analyzer mengenali rahasia sebagai nilai data, bukan nama tabel.

3. Statement rusak/salah sintaks tetap dihitung operasinya (False Positive)
   - SQL (data/sample/campuran_error.sql baris 4):
     SELECT id nama, FROM pesanan;
   - Kesalahan regex:
     Regex tidak memahami struktur tata bahasa (grammar). Begitu menemukan pola FROM pesanan, regex langsung mengekstrak operasi READ (R) pada tabel pesanan, mengabaikan fakta bahwa query tersebut rusak.
   - Mengapa parser benar (Konsep Grammar & Error Recovery - Bab 5, 6, & Spesifikasi Bagian 5):
     Parser rekursif memverifikasi susunan token terhadap aturan grammar formal. Saat membaca koma sebelum FROM tanpa ekspresi valid, parser mendeteksi pelanggaran sintaks, mencatat ParseError, dan memicu panic mode recovery untuk menyinkronkan token ke titik koma (;) berikutnya (Bug 4). Berdasarkan SPESIFIKASI.md Bagian 5 ("Statement yang gagal di-parse tidak dihitung"), analyzer hanya memproses statement yang valid membentuk pohon AST utuh. Karena statement baris 4 gagal di-parse, tabel pesanan dari statement rusak tersebut tidak dimasukkan ke dalam CRUD matrix.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. 
2. 
3. 

## 4. Pembagian kerja
Proyek ini dikerjakan oleh kelompok beranggotakan dua orang (Alifah dan Ganesh) dengan pembagian modul dan tanggung jawab berbasis file untuk mencegah konflik git
1. **Alifah**:
   - **Modul**: crud/lexer.py dan crud/resolver.py.
   - **Fitur (TODO)**: 
     - TODO 3: Implementasi pemindaian komentar blok multi-baris /* ... */ dan penanganan unclosed comment saat EOF.
   - **Perbaikan Bug**:
     - Bug 1: Normalisasi keyword huruf kecil (case-insensitive) di lexer.
     - Bug 2: Operator <> terbelah dua (maximal munch) di lexer.
     - Bug 3: Escape tanda petik tunggal ganda ('') di string literal.
     - Bug 7: Arah pencarian scope terbalik pada _lookup() di resolver (shadowing subquery).
     - Bug 8: Scope leak pada statement DELETE akibat ketiadaan _pop().
   - **Data, Test, & Dokumen**: 
     - Pelabelan manual ground truth untuk data/sample/pemeliharaan.sql.
     - Test regresi untuk Bug 1, 2, 3, 7, 8 di tests/test_tambahan.py.
     - Penulisan Kartu Desain No. 1, 2, dan 3 di docs/KARTU_DESAIN.md.
2. **Ganesh**:
   - **Modul**: crud/parser.py dan crud/analyzer.py.
   - **Fitur (TODO)**:
     - TODO 1: Implementasi dukungan sintaks INSERT INTO ... SELECT ...
     - TODO 2: Implementasi resolusi kolom tanpa qualifier pada scope terdalam.
   - **Perbaikan Bug**:
     - Bug 4: Panic mode error recovery parser berhenti di semicolon (;) bukannya EOF.
     - Bug 5: Pemisahan hierarki presedensi operator logika AND dan OR ke fungsi terpisah.
     - Bug 6: Dukungan keyword OUTER pada klausa LEFT OUTER JOIN.
     - Bug 9: Koreksi penandaan operasi subquery pada UPDATE dari U menjadi R di analyzer.
   - **Data, Test, & Dokumen**:
     - Pelabelan manual ground truth untuk data/sample/audit.sql.
     - Test regresi untuk Bug 4, 5, 6, 9 di tests/test_tambahan.py.
     - Penulisan Kartu Desain No. 4 dan 5 di docs/KARTU_DESAIN.md.

### Cara Memastikan Keduanya Memahami Seluruh Kode
1. **Bedah Kode dan Spesifikasi Bersama di Awal**: Sebelum membagi file, kami meninjau deskripsi, SPESIFIKASI.md, dan mengidentifikasi anomali kode bersama, sehingga keduanya memahami alur lengkap dari Lexer sampai Analyzer. Kami juga mengerjakan bagian TODO bersama bergantian.
2. **Pemberian Komentar Kode dan Review Silang**: Kami masing-masing menambahkan komentar penjelasan yang memadai langsung di dalam kode pada setiap bagian yang kami selesaikan atau perbaiki. Komentar ini ditujukan agar partner dapat membaca dan memahaminya dengan jauh lebih mudah saat proses review. Setelah itu, kami saling meninjau kode satu sama lain.
