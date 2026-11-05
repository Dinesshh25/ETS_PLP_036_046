# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: (Case-sensitivity keyword)

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Input query SQL dengan keyword huruf kecil (seperti select id from t) gagal mengenali kata kunci tersebut dan menganggapnya sebagai token IDENT. Akibatnya parser gagal mengenali awal statement. Menurut SPESIFIKASI.md bagian 2.2, keyword tidak peka huruf besar/kecil (select, Select, dan SELECT sama-sama keyword) dan nilainya harus dinormalisasi ke huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select id from t;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _word(), kata yang dibaca langsung dicek ke KEYWORDS tanpa diubah dulu. Isi KEYWORDS huruf besar semua ("SELECT", "FROM", dst), jadi select huruf kecil tidak dianggap cocok dan malah jadi IDENT. Padahal spesifikasi bilang keyword tidak peka huruf besar/kecil dan nilainya harus selalu huruf besar (bab 4 scanning).

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
Di crud/lexer.py, method _word(), kata diubah dulu ke huruf besar (upper = text.upper()), baru dicek ke KEYWORDS. Kalau ada, token jadi KEYWORD dengan nilai upper. Kalau tidak, token jadi IDENT dengan nilai aslinya (text).
Alternatif yang ditolak: Menambahkan semua variasi huruf kecil dan campuran ke KEYWORDS. Ditolak karena daftarnya jadi sangat panjang sehingga kurang efektif dibandingkan dengan diubah ke uppercase.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_1_keyword_case_insensitive di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI tidak membantu menemukan bug ini karena sebelumnya sudah ada tes yang menguji hal tersebut, membantu verifikasi apakah penyelesaian dengan ubah ke uppercase sudah cocok/sesuai dan menyusun tes.
Diverifikasi dengan menyesuaikan spesifikasi dan menjalankan pytest.
---

---

## Bug 2: (Operator <> terbelah)

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Query dengan operator <>, misalnya WHERE status <> 'BATAL', gagal di-parse dengan pesan "Baris 1, kolom 27: diharapkan ekspresi, ditemukan '>'". Menurut SPESIFIKASI.md bagian 2.5, lexer harus mengambil operator terpanjang yang cocok (maximal munch), jadi <> seharusnya jadi satu token OP '<>'.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT id FROM t WHERE a <> 1;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _scan_token() pada crud/lexer.py, saat lexer ketemu < dia cuma mengecek apakah karakter berikutnya =. Karakter > tidak pernah dicek, jadi <> terpecah jadi dua token: < lalu >. Parser menerima < sebagai operator perbandingan, lalu menunggu operand di sebelah kanan, tapi yang datang malah >, yang tidak bisa jadi awal ekspresi. Jadi sumber masalahnya ada di lexer, sedangkan error-nya baru kelihatan di parser. Ini soal lexeme yang harus dibaca selengkap mungkin, seperti di Bab 4 (Scanning) bagian operator dua karakter.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
Di _scan_token() pada crud/lexer.py, ditambahkan cabang untuk > setelah <, sehingga <> jadi satu token. Alternatif yang ditolak: menggabungkan < dan > di parser. Ditolak karena memecah dan menggabung token itu tugas lexer, dan spesifikasi mengharuskan lexer selesai dulu sebelum parser jalan.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_2_operator_not_equal di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI membantu menemukan bug dan menyusun tes.
Diverifikasi dengan menjalankan pytest sebelum dan sesudah perbaikan, lalu dicocokkan lagi dengan spesifikasi.

---

---

## Bug 3: (Escape quote beruntun '')

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
String yang isinya dua kutip tunggal berturut-turut, misalnya 'O''Brien', malah kepotong jadi dua token STRING: 'O' dan 'Brien'. Akibatnya parser error: "Baris 1, kolom 11: diharapkan FROM, ditemukan 'Brien'". Padahal di SPESIFIKASI.md bagian 2.4, '' di dalam string itu artinya satu karakter kutip, jadi hasilnya harusnya satu token STRING dengan nilai O'Brien.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT 'O''Brien' FROM pelanggan;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _string() lexer, begitu ketemu kutip tunggal langsung berhenti (break), nggak ngecek karakter setelahnya. Jadi kutip pertama dari '' dianggap penutup string. Harusnya dicek dulu pakai peek: kalau karakter berikutnya juga kutip, itu bukan penutup tapi escape. Karena stringnya sudah kepotong di lexer, errornya baru kelihatan di parser. Ini nyambung ke Bab 4, soal lexer yang kadang perlu ngintip satu karakter ke depan buat nentuin lexeme-nya selesai atau belum.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
Di _string(), pas ketemu kutip tunggal aku cek self._peek(). Kalau karakter berikutnya juga kutip tunggal, maju satu karakter (self._advance()) dan masukin satu ' ke isi string. Kalau bukan, baru stop.
Alternatif yang ditolak: Pakai .replace("''", "'") setelah tokenisasi, tapi tidak jadi karena stringnya sudah keburu jadi dua token di lexer, jadi tidak ada yang bisa diganti.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_3_string_escaped_quote di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
Membantu merancang logika lookahead self._peek() == "'" pada _string() dan menulis test regresi dengan beragam variasi kutip tunggal ganda.
Diverifikasi dengan menyesuaikan spesifikasi dan menjalankan pytest.

---

---

## Bug 4: (Panic mode recovery ke EOF)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---

---

## Bug 5: (Presedensi AND/OR setara)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---

---

## Bug 6: (Dukungan LEFT OUTER JOIN)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---

---

## Bug 7: (Shadowing scope terbalik)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---

---

## Bug 8: (Scope leak pada DELETE)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---

---

## Bug 9: (Subquery UPDATE ditandai U)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---