# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | | Ganesh| Memberikan saran untuk menyelesaikan TODO 1 dan bagaimana aku membuat kodenya jika aku sudah tau bahwa alurnya harus  | | |
| 2 | Alifah | Breakdown tugas: isi PDF, spesifikasi, TODO, deliverable, urutan kerja | Diterima | Biar paham tugas sebelum mulai | Dicocokkan dengan PDF tugas, SPESIFIKASI.md, dan template docs/ |
| 3 | Alifah | Penjelasan alur program (lexer sampai CSV) dengan contoh output CLI | Diterima | Biar paham bentuk input dan output | Dicocokkan dengan hasil menjalankan CLI |
| 4 | Alifah | Alur memindai komentar blok /* ... */ (T3): baris/kolom saat \n dan error kalau tidak ditutup | Diubah | Alurnya benar (cek * lalu /, LexError kalau sampai EOF). Tapi nama fungsi di contoh kodenya tidak ada di lexerku (_is_at_end, _peek_next, _add_token), jadi aku pakai yang ada: _at_end, _peek(1), _advance | pytest dan cocokkan SPESIFIKASI 2.3 |
| 5 | Alifah | test_keyword_huruf_kecil gagal (keyword terbaca IDENT), apakah solusi ubah ke uppercase cocok? | Diterima | Ide uppercase sesuai perkiraan, AI mengonfirmasi dan menjelaskan kenapa IDENT tetap pakai teks asli. Nama variabel di contoh aku sesuaikan dengan kode | pytest dan cocokkan SPESIFIKASI 2.2 |
| 6 | Alifah | WHERE status <> 'BATAL' error "diharapkan ekspresi, ditemukan '>'", apakah ini maximal munch dan bagaimana struktur if-elif untuk <? | Diubah | Penjelasan maximal munch dan cabang <> benar. Urutan cabang di tulis sendiri (cek = dulu, baru >), beda dari saran AI yang > dulu, hasilnya sama. Tambahan AI untuk > dan ! tidak aku pakai karena lexer sudah menanganinya | pytest dan cocokkan SPESIFIKASI 2.5 |
| 7 | Alifah | Alias x.total di subquery terikat ke tabel luar, apakah reversed(chain) di _lookup() melanggar lexical scoping (Bab 11)? | Diubah | AI mengonfirmasi dan memberi dua cara. Aku pilih Cara A (while scope is not None) dan sesuaikan nama atributnya (entries). Cara B (hapus reversed) juga benar, tapi tidak aku pakai | pytest, --ast, dan cocokkan SPESIFIKASI 4.3 |
| 8 | Alifah | DELETE FROM sesi s lalu SELECT s.id FROM pengguna u tidak error, _delete() punya _push() tanpa _pop(), kenapa bocor? | Diubah | Penjelasan push-pop dan isolasi antar-statement diterima. Contoh perbaikan dengan try/finally dan nama yang tidak ada di kode tidak di pakai, cukup menambah self._pop() di akhir _delete() | pytest, --ast, dan cocokkan SPESIFIKASI 4.5 |
| 9 | Alifah | Cara melaporkan diagnostik alias ganda di scope yang sama | Ditolak | Resolver sudah melaporkan alias ganda, jadi tidak ada yang perlu ditambah | Jalankan SQL dengan alias ganda dan lihat diagnostiknya |


**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuiya?
AI paling membantu waktu masih bingung memahami tugasnya, karena deskripsi dan instruksinya tersebar di PDF, spesifikasi, dan komentar di kode, jadi breakdown dari AI bikin proses mulai mengerjakan jadi lebih jelas. AI juga membantu menjelaskan kenapa sebuah bug terjadi dan nyambung ke konsep di buku. AI paling sering keliru atau menyesatkan kalau konteksnya kurang seperti pembagian TODO-nya salah, nama fungsi di contoh kodenya tidak ada di kode proyek, dan ada saran untuk hal yang sebenarnya sudah ada. Kesalahan itu ketahuan setelah membaca kodenya langsung, menjalankan pytest, lalu mencocokkan lagi dengan SPESIFIKASI.md dan bukunya, jadi semua jawaban AI dicek dulu sebelum dipakai.
