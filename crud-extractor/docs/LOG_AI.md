# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | | Ganesh| Memberikan saran untuk menyelesaikan TODO 1 dan bagaimana aku membuat kodenya jika aku sudah tau bahwa alurnya harus  | | |
| 2 | Alifah | Alur untuk memindai karakter di dalam komentar hingga */ | diterima | sudah sesuai spesifikasi | Melakukan pytest dan menyesuaikan spesifikasi |
| 3 | Alifah | Analisis kegagalan test_keyword_huruf_kecil di mana keyword huruf kecil terbaca sebagai IDENT, serta kecocokan solusi menggunakan ubah ke uppercase. | diterima | Sudah sesuai pemikiran awal dengan ubah ke uppercase | Melakukan pytest dan menyesuaikan spesifikasi. |
| 4 | Alifah | Merancang logika lookahead self._peek() == "'" pada _string() dan menulis test dengan beragam variasi kutip tunggal ganda. | diterima | Sesuai spesifikasi | Melakukan pytest dan menyesuaikan spesifikasi. |
| 5 | Alifah | Diskusi analisis kegagalan scope shadowing pada subquery akibat reversed(chain) di fungsi _lookup() Resolver sesuai Crafting Interpreters Bab 11. | diterima | Mengonfirmasi bahwa reversed(chain) membalik semantik lexical scope sehingga scope luar menutupi scope lokal. Menggantinya dengan loop langsung while scope is not None: menjamin shadowing subquery dan correlated subquery bekerja benar. | Melakukan pytest dan menyesuaikan spesifikasi |
| 6 | Alifah | Menganalisis penyebab kebocoran alias antar-statement (scope leak) akibat ketiadaan self._pop() di method _delete() Resolver sesuai Crafting Interpreters Bab 11. | diterima | Penjelasan menegaskan bahwa ketiadaan _pop() meninggalkan scope DELETE di dalam stack, sehingga statement berikutnya mewarisi alias yang tidak sah sebagai parent scope. Menambahkan self._pop() memulihkan prinsip statement isolation SPESIFIKASI 4.5. | Melakukan pytest dan menyesuaikan spesifikasi |


**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuiya?
