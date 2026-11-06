# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 | Penanganan komentar blok multi-baris /* ... */ secara manual di loop lexer memakai lookahead 2 karakter (_peek() dan _peek(1)) serta pelacakan baris/kolom via _advance(). | Menghapus komentar di awal memakai Regex (re.sub) atau pre-processing teks sebelum tokenisasi. | Regex merusak penomoran baris dan kolom token asli (line dan col) untuk pelaporan error sintaks. Pendekatan manual lexer menjaga koordinat tetap akurat dan memungkinkan pelaporan LexError jika komentar tidak ditutup sampai EOF (SPESIFIKASI.md Bagian 2.3). |
| 2 | Penelusuran rantai scope pada _lookup() langsung dari scope terdalam ke luar memakai traversal pointer while scope is not None. | Mengumpulkan scope ke list sementara lalu mengiterasi dari luar ke dalam memakai reversed(chain). | Menghindari alokasi list perantara dan mematuhi semantik lexical scoping (Crafting Interpreters Bab 11) agar deklarasi lokal di subquery menutupi (shadow) alias luar. Mencari dari luar ke dalam merusak prioritas resolusi subquery. |
| 3 | Resolusi kolom tanpa qualifier dibatasi hanya memeriksa scope terdalam; jika terdapat lebih dari satu tabel, resolusi dibiarkan None dan memberi warning ambigu. | Melanjutkan pencarian kolom tanpa qualifier ke scope luar jika scope terdalam punya lebih dari satu tabel, atau menebak salah satu tabel. | Sesuai SPESIFIKASI.md Bagian 4.3 dan batasan ketiadaan skema database. Tool tidak bisa memastikan pemilik kolom jika ada multi-tabel di scope lokal (misal FROM pelanggan, pesanan). Merambat ke luar berisiko salah ikat ke alias luar. |
| 4 | Mengintegrasikan INSERT INTO ... SELECT ke kelas AST Insert yang ada dengan mengisi field query dan mengosongkan baris nilai (values=[]). | Membuat kelas AST node baru terpisah (misalnya InsertSelect) atau memasukkan query SELECT ke dalam baris values. | Mematuhi kontrak AST publik (SPESIFIKASI.md Bagian 7) di mana kelas Insert sudah punya field query. Menggunakan values=[] mencegah TypeError saat diiterasi di resolver dan analyzer. |
| 5 | Memisahkan parsing operator logika OR dan AND ke dua fungsi hierarkis terpisah (_or() memanggil _and(), dan _and() memanggil _not()). | Menggabungkan AND dan OR dalam satu loop di _logical() dengan membedakan bobot presedensi secara manual. | Mengikuti pola Recursive Descent Parser (Crafting Interpreters Bab 6). Struktur fungsi pemanggil otomatis menegakkan presedensi operator di mana AND (Tingkat 2) mengikat lebih kuat dari OR (Tingkat 1) pada pohon AST. |
