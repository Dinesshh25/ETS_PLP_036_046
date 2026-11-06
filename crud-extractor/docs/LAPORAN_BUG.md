# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Keyword huruf kecil tidak dikenali (case-sensitive)

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Input query SQL dengan keyword huruf kecil (seperti select id from t) gagal mengenali kata kunci tersebut dan menganggapnya sebagai token IDENT. Akibatnya parser gagal mengenali awal statement. Menurut SPESIFIKASI.md bagian 2.2 (Keyword dan identifier), keyword tidak peka huruf besar/kecil (select, Select, dan SELECT sama-sama keyword) dan nilai tokennya harus diubah ke huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select id from t;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _word(), kata yang dibaca langsung dicek ke KEYWORDS tanpa diubah dulu. Isi KEYWORDS huruf besar semua ("SELECT", "FROM", dst), jadi select huruf kecil tidak dianggap cocok dan malah jadi IDENT. Padahal spesifikasi bilang keyword tidak peka huruf besar/kecil dan nilainya harus selalu huruf besar. Ini nyambung ke Bab 4 (Scanning) bagian 4.7 "Reserved Words and Identifiers", yaitu scanner membaca satu kata utuh dulu, baru dicocokkan ke tabel keyword.

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

## Bug 2: Operator <> terpecah jadi dua token

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Query dengan operator <>, misalnya WHERE status <> 'BATAL', gagal di-parse dengan pesan "Baris 1, kolom 27: diharapkan ekspresi, ditemukan '>'". Menurut SPESIFIKASI.md bagian 2.5 (Operator), lexer harus mengambil operator terpanjang yang cocok, jadi <> seharusnya jadi satu token OP '<>'.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT id FROM t WHERE a <> 1;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _scan_token() pada crud/lexer.py, saat lexer ketemu < dia cuma mengecek apakah karakter berikutnya =. Karakter > tidak pernah dicek, jadi <> terpecah jadi dua token, < lalu >. Parser menerima < sebagai operator perbandingan, lalu menunggu operand di sebelah kanan, tapi yang datang malah >, yang tidak bisa jadi awal ekspresi. Jadi sumber masalahnya ada di lexer, sedangkan error-nya baru kelihatan di parser. Ini nyambung ke Bab 4 (Scanning), bagian 4.5 "Recognizing Lexemes" soal operator dua karakter seperti <=, dan prinsip maximal munch di bagian 4.7 "Reserved Words and Identifiers", kalau dua aturan sama-sama cocok, yang menang yang paling panjang.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
Di _scan_token() pada crud/lexer.py, di bagian karakter `<` di tambahkan pengecekan >. Jadi setelah <, lexer cek dulu, kalau berikutnya = jadi <=, kalau > jadi <>, kalau bukan keduanya baru < sendiri. Dengan begitu <> terbaca sebagai satu token OP.
Alternatif yang ditolak: menggabungkan token < dan > di parser. Ditolak karena memecah dan menggabung token itu tugas lexer, dan spesifikasi mengharuskan lexer selesai dulu sebelum parser jalan.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_2_operator_not_equal di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI mengonfirmasi bahwa ini pelanggaran maximal munch dan menjelaskan struktur cabang untuk < serta menyusun tes.
Diverifikasi dengan menjalankan pytest, lalu dicocokkan lagi dengan spesifikasi.



---

## Bug 3: Escape kutip '' memotong string jadi dua token

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
String yang isinya dua kutip tunggal berturut-turut, misalnya 'O''Brien', malah kepotong jadi dua token STRING: 'O' dan 'Brien'. Akibatnya parser error: "Baris 1, kolom 11: diharapkan FROM, ditemukan 'Brien'". Padahal menurut SPESIFIKASI.md bagian 2.4 (String), dua kutip berturut-turut di dalam string ('') mewakili satu karakter kutip, jadi 'O''Brien' harus jadi satu token STRING bernilai O'Brien.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT 'O''Brien' FROM pelanggan;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _string() lexer, begitu ketemu kutip tunggal langsung berhenti (break), tidak ngecek karakter setelahnya. Jadi kutip pertama dari '' dianggap penutup string. Harusnya dicek dulu pakai peek, kalau karakter berikutnya juga kutip, itu bukan penutup tapi escape. Karena stringnya sudah kepotong di lexer, errornya baru kelihatan di parser. Ini nyambung ke Bab 4 (Scanning), bagian 4.6 "Longer Lexemes" (4.6.1 String literals), soal cara scanner membaca string sampai kutip penutup, dan peek() untuk mengintip satu karakter ke depan sebelum memutuskan lexeme-nya selesai.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
Di _string(), pas ketemu kutip tunggal di cek self._peek(). Kalau karakter berikutnya juga kutip tunggal, maju satu karakter (self._advance()) dan masukin satu ' ke isi string. Kalau bukan, baru stop.
Alternatif yang ditolak: Pakai .replace("''", "'") setelah tokenisasi, tapi tidak jadi karena stringnya sudah keburu jadi dua token di lexer, jadi tidak ada yang bisa diganti.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_3_string_escaped_quote di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
Membantu merancang logika lookahead self._peek() == "'" pada _string() dan menulis test dengan beragam variasi kutip tunggal ganda.
Diverifikasi dengan menyesuaikan spesifikasi dan menjalankan pytest.


---

## Bug 4: Panic mode recovery membuang statement valid berikutnya

**Ditemukan oleh:** Ganesh · **Diperbaiki oleh:** Ganesh

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Saat program mem-parsing beberapa pernyataan (statement) SQL dan menemukan satu pernyataan yang salah sintaks, pernyataan valid yang berada di bawahnya ikut terhapus dan tidak diproses sama sekali. Seharusnya, program hanya mencatat error pada pernyataan yang rusak, lalu melanjutkan proses membaca pada pernyataan berikutnya..

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT department_id FROM departments EXCEPT SELECT department_id FROM employees;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Masalah ini terletak pada fungsi _synchronize() di modul parser. Ketika menemukan error, fungsi tersebut terus membuang token hingga mencapai batas akhir file (EOF). Hal ini melanggar konsep panic-mode recovery yang dijelaskan dalam buku Crafting Interpreters Bab 6 (Parsing). Berdasarkan konsep tersebut, parser seharusnya mencari titik henti atau sinkronisasi (seperti tanda titik koma) agar bisa pulih dari error dan melanjutkan proses tanpa mengorbankan input yang masih benar.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
Fungsi _synchronize() dimodifikasi agar berhenti membuang token ketika menemukan tanda titik koma (;) atau saat melihat kata kunci awal pernyataan baru (seperti SELECT, INSERT, dll).
Alternatif yang ditolak: Mengabaikan seluruh sisa teks sepenuhnya setelah error pertama. Meskipun lebih sederhana, pendekatan ini merugikan karena menyebabkan perintah valid setelahnya gagal diekstrak.

**Test regresi.** `test_next_statement` di `tests/test_tambahan.py`.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI membantu merumuskan token apa saja yang tepat untuk dijadikan titik sinkronisasi dan membantu menyusun kerangka kode tes regresinya.



---

## Bug 5: Presedensi AND dan OR dianggap setara

**Ditemukan oleh:** Ganesh · **Diperbaiki oleh:** Ganesh

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md \
Ketika sebuah kueri menggunakan operator AND dan OR secara bersamaan, parser menganggap keduanya memiliki tingkat prioritas yang sama. Akibatnya, ekspresi a = 1 OR b = 2 AND c = 3 dievaluasi mendatar dari kiri ke kanan menjadi (a = 1 OR b = 2) AND c = 3. Padahal, operasi AND seharusnya dikerjakan lebih dahulu.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Pada kode bawaan, fungsi `_logical()` memproses `AND` dan `OR` di dalam satu tingkatan perulangan yang sama. Akibatnya, Abstract Syntax Tree (AST) yang dibentuk tidak mencerminkan prioritas operasi. Sesuai dengan penjelasan pada buku Crafting Interpreters Bab 5 (Grammar & AST) dan Bab 6 (Parser), aturan tata bahasa harus dipisah menjadi lapisan-lapisan yang berbeda agar tingkat prioritas operator (presedensi) dievaluasi dengan benar.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.\
Fungsi tersebut dipisah menjadi dua. Saat ini `_logical()` hanya bertugas menangani `OR` (tingkat prioritas lebih rendah). Di dalamnya, fungsi tersebut akan memanggil fungsi baru bernama `_logical_and()` yang khusus mengevaluasi `AND`. Dengan tata bahasa yang berlapis ini, `AND` akan diproses lebih dalam dan mengikat lebih kuat.
Alternatif yang ditolak: Mengubah susunan cabang setelah struktur AST selesai dibuat. Pendekatan ini ditolak karena rumit dan rawan kesalahan; prioritas sebaiknya langsung dibentuk sejak tahap parsing.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus sesudahnya.\
`test_and_or` memeriksa bahwa node terluar adalah `OR` dan anak kanannya adalah `AND`.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian memverifikasinya?\
AI memberikan panduan bahwa aturan tata bahasa harus dipisah untuk mendapatkan presedensi yang tepat dan membantu merancang kasus uji untuk memvalidasi struktur pohon AST-nya.


---

## Bug 6: Sintaks LEFT OUTER JOIN tidak dikenali

**Ditemukan oleh:** Ganesh · **Diperbaiki oleh:** Ganesh

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Kueri yang menggunakan klausa `LEFT OUTER JOIN` menghasilkan pesan error karena program secara kaku mengharapkan kata kunci `JOIN` muncul tepat setelah kata `LEFT`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT * FROM a LEFT OUTER JOIN b ON a.id = b.id;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Fungsi `_join()` pada `crud/parser.py` tidak memberikan ruang untuk kata opsional. Setelah membaca token `LEFT`, fungsi langsung memaksa pencarian kata `JOIN` tanpa mengecek kehadiran kata `OUTER`. Hal ini merupakan kekurangan dalam penerapan logika di buku Crafting Interpreters Bab 6 (Parser), di mana parser seharusnya dirancang untuk dapat mengakomodasi sintaks opsional sebelum memvalidasi kata kunci utamanya.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.\
Pada fungsi `_join()`, setelah kata `LEFT` cocok, ditambahkan satu baris kode untuk mendeteksi dan mengabaikan token `OUTER` secara opsional sebelum program memeriksa kehadiran token `JOIN`.
Alternatif yang ditolak: Membuat jenis join baru khusus untuk `OUTER`. Keputusan ini ditolak karena secara konsep operasinya tetap berupa `LEFT` join; kata `OUTER` hanya bersifat tambahan sintaks.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
`test_left_outer_join` memastikan tidak ada parse error dan jenis join pada AST bernilai `LEFT`.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian memverifikasinya?\
Tidak ada penggunaan AI untuk menemukan atau memperbaiki bug ini. Pemecahan masalah dan verifikasi dilakukan murni dengan mencocokkan kode terhadap dokumen SPESIFIKASI.md secara mandiri dan menjalankan evaluasi pengujian.

---

## Bug 7: Alias di subquery tidak menutupi alias luar (shadowing terbalik)

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Kalau alias di subquery sama dengan alias di query luar (contohnya sama-sama x), kolom di dalam subquery malah ter-resolve ke tabel luar. x.total di subquery jadi dianggap milik pelanggan, padahal harusnya pesanan. Menurut SPESIFIKASI.md bagian 4.3, qualifier dicari dari scope paling dalam dulu baru ke luar, jadi alias di subquery harus menutupi alias yang sama di luar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT x.id FROM pelanggan x
WHERE x.id IN (SELECT x.total FROM pesanan x);
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _lookup() pada resolver.py, scope dikumpulkan dulu ke list chain (dari scope sekarang naik ke parent-nya), lalu list itu dibaca pakai reversed(chain). Jadinya pencarian mulai dari scope paling luar, bukan paling dalam. Alias di luar ketemu duluan, jadi alias subquery tidak pernah kepakai. Padahal di Bab 11 (Resolving and Binding) resolver harus nyari variabel dari scope terdalam ke luar, supaya yang lokal menutupi yang di luar.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
Di _lookup() pada resolver.py, list chain dan reversed() dihapus. Gantinya langsung jalan dari self.scope naik lewat scope.parent pakai while scope is not None, dan berhenti begitu nama ketemu. 
Alternatif yang ditolak: tetap pakai chain tapi reversed-nya dibuang. Itu sebenarnya juga benar, tetapi yang tanpa list tidak perlu bikin list dulu.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_7_scope_shadowing_subquery di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI membantu nunjukin bagian reversed(chain) yang bikin urutan pencarian kebalik, dan bantu nyusun test nya.
Diverifikasi dengan menyesuaikan spesifikasi dan menjalankan pytest serta lihat hasil resolusi di --ast.


---

## Bug 8: Alias DELETE bocor ke statement berikutnya (scope tidak di-pop)

**Ditemukan oleh:** Alifah · **Diperbaiki oleh:** Alifah

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
Alias tabel dari DELETE (misalnya DELETE FROM sesi s) masih kebaca di statement berikutnya dalam file yang sama. Jadi statement setelahnya yang pakai alias s tanpa mendeklarasikannya tidak kena error, malah kolomnya ter-resolve ke tabel sesi. Menurut SPESIFIKASI.md bagian 4.5 (Setiap statement berdiri sendiri), setelah satu statement selesai tidak boleh ada scope tersisa, dan alias statement sebelumnya tidak boleh terlihat oleh statement berikutnya.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
DELETE FROM sesi s WHERE s.id = 1;
SELECT s.id FROM pengguna u;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?
Di _delete() pada resolver.py, scope dibuka pakai self._push() tapi tidak pernah ditutup pakai self._pop(). Jadi scope DELETE tetap nyangkut dan jadi parent buat statement berikutnya, makanya alias s masih ketemu. Padahal di Bab 11 (Resolving and Binding), bagian 11.3.1 "Resolving blocks", scope harus dibuka di awal dan ditutup di akhir, selalu berpasangan.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
Di _delete() pada resolver.py, di tambahkan self._pop() di akhir fungsi, setelah self._expr(dele.where). 
Alternatif yang ditolak: mengosongkan self.scope = None di awal setiap statement. Ditolak karena itu cuma nutupin gejalanya, sedangkan push dan pop-nya tetap tidak berpasangan.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_bug_8_delete_scope_leak di tests/test_tambahan.py

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI membantu nelusuri kenapa push dan pop di _delete() tidak seimbang dan kenapa _push tanpa _pop membuat scope bocor serta menyusun test. 
Diverifikasi dengan menyesuaikan spesifikasi dan menjalankan pytest dan lihat hasil resolusinya di --ast.

---

## Bug 9: Subquery pada WHERE UPDATE salah ditandai sebagai operasi UPDATE

**Ditemukan oleh:** Ganesh · **Diperbaiki oleh:** Ganesh

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md\
Apabila terdapat perintah `UPDATE` yang menggunakan kueri bersarang (`SELECT` atau subquery) di dalam kondisi `WHERE`, tabel yang berada di dalam subquery tersebut ikut dilabeli sebagai target operasi `U` (Update). Seharusnya, tabel di dalam subquery hanya ditandai sebagai operasi `R` (Read).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
UPDATE pelanggan SET level = 1 WHERE id IN (SELECT id FROM pesanan);
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?\
Pada fungsi `analyze_statement()`, ketika program menelusuri klausa `WHERE` pada perintah `UPDATE`, program meneruskan status operasi `"U"` secara turun-temurun ke cabang-cabang di bawahnya. Saat penelusuran (traversal) Abstract Syntax Tree (berdasarkan konsep Crafting Interpreters Bab 5) mencapai subquery, status `"U"` ini diwariskan ke perintah `SELECT`. Program gagal membatasi ruang lingkup pembaruan tabel utama dengan operasi pembacaan pada subquery.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.\
Logika pada fungsi pengumpulan `(_collect())` disesuaikan. Apabila program menemukan operasi yang melibatkan subquery (seperti `IN`, `EXISTS`), program diinstruksikan untuk memaksa pengiriman parameter status `"R"`, alih-alih meneruskan status operasi dari luar. Dengan demikian, subquery di dalamnya dijamin selalu mendapatkan status baca.
Alternatif yang ditolak: Mengubah seluruh penandaan di klausa `WHERE` pada perintah `UPDATE` menjadi `"R"`. Pendekatan ini ditolak karena akan merusak status pencatatan jika ada ekspresi di klausa `WHERE` yang merujuk langsung ke tabel utama.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
`test_bug9_update_subquery_read` memastikan matriks operasi berisi `pelanggan: U` dan `pesanan: R`.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalianmemverifikasinya?\
AI membantu melacak asal parameter operasi yang terwariskan ke cabang di bawahnya dan membantu menyusun strategi agar status operasi tertahan menjadi `"R"` saat memasuki area subquery.

---