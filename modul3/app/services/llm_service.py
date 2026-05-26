import os
from google import genai
from google.genai import types
from app.database import SessionLocal
from app.models import Mahasiswa, MataKuliah, KRS, Fakultas, Prodi

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower().strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY"))
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash").strip()

gemini_client = None

if LLM_PROVIDER == "gemini":
    if GEMINI_API_KEY and GEMINI_API_KEY != "GANTI_DENGAN_API_KEY_GEMINI_KAMU_DISINI":
        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"}
        )

import re
from sqlalchemy import text


def is_safe_select_query(sql: str) -> bool:
    """Memastikan query HANYA berupa SELECT dan tidak mengandung keyword berbahaya."""
    if not sql:
        return False

    # Bersihkan query dari pembungkus markdown sql jika ada
    sql_clean = sql.strip()
    if sql_clean.startswith("```"):
        sql_clean = re.sub(r"^```(?:sql)?\s*", "", sql_clean)
        sql_clean = re.sub(r"\s*```$", "", sql_clean)
    sql_clean = sql_clean.strip()

    # Ubah ke lowercase untuk pencarian pola
    query_lower = sql_clean.lower()

    # Wajib dimulai dengan SELECT
    if not query_lower.startswith("select"):
        return False

    # Blacklist kata kunci berbahaya (modifikasi data / DDL / DCL)
    forbidden_patterns = [
        r"\binsert\b",
        r"\bupdate\b",
        r"\bdelete\b",
        r"\bdrop\b",
        r"\balter\b",
        r"\btruncate\b",
        r"\bcreate\b",
        r"\breplace\b",
        r"\bgrant\b",
        r"\brevoke\b",
        r"\bexecute\b",
        r"\bexec\b",
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, query_lower):
            return False

    return True


def execute_academic_query(sql_query: str) -> str:
    """
    Mengeksekusi query SELECT SQL ke database akademik secara aman dan real-time.
    Gunakan tool ini untuk mendapatkan data mahasiswa, prodi, fakultas, KRS, dan mata kuliah.
    Hanya menerima query SELECT yang aman (Read-Only).
    """
    # 1. Bersihkan query dari pembungkus markdown jika ada
    sql_clean = sql_query.strip()
    if sql_clean.startswith("```"):
        sql_clean = re.sub(r"^```(?:sql)?\s*", "", sql_clean)
        sql_clean = re.sub(r"\s*```$", "", sql_clean)
    sql_clean = sql_clean.strip()

    # 2. Jalankan validasi keamanan pra-eksekusi
    print(
        f"\n=========================================\nGEMINI EXECUTING DYNAMIC SQL:\n{sql_clean}\n=========================================\n"
    )
    if not is_safe_select_query(sql_clean):
        return "Error: Query ditolak karena alasan keamanan. Anda hanya diizinkan menjalankan query SELECT pembacaan data (Read-Only)."

    db = SessionLocal()
    try:
        # 3. Paksa transaksi menjadi READ ONLY
        db.execute(text("SET TRANSACTION READ ONLY"))

        # 4. Eksekusi query
        result = db.execute(text(sql_clean))

        # Ambil kolom dan baris
        columns = result.keys()
        rows = result.fetchall()

        # 5. Batasi baris maksimal demi performa
        limited_rows = rows[:50]

        # Konversi hasil ke list of dict
        data = [dict(zip(columns, row)) for row in limited_rows]

        if not data:
            return "Query berhasil dieksekusi, tetapi database tidak mengembalikan data apa pun."

        return str(data)
    except Exception as e:
        # Mengembalikan error database ke LLM agar bisa auto-correct query yang typo/salah
        return f"Database Error: {str(e)}"
    finally:
        db.close()


# List of allowed tools
assistant_tools = [execute_academic_query]

# System Instruction to secure the LLM
SYSTEM_INSTRUCTION = """
Anda adalah asisten virtual akademik kampus Universitas Sanata Dharma (USD) yang ramah, sopan, dan sangat membantu.
Anda memiliki akses langsung untuk membaca database akademik kampus menggunakan tool 'execute_academic_query' yang menerima query SQL SELECT saja.

Berikut adalah Skema Database PostgreSQL yang tersedia:
1. Tabel 'fakultas':
   - 'id' (INTEGER, Primary Key)
   - 'singkatan' (VARCHAR, singkatan fakultas, e.g. 'FST', 'FKIP')
   - 'nama' (VARCHAR, nama lengkap fakultas)
   
2. Tabel 'prodi' (Program Studi):
   - 'id' (INTEGER, Primary Key)
   - 'fakultas_id' (INTEGER, Foreign Key merujuk ke fakultas.id)
   - 'nama' (VARCHAR, nama prodi, e.g. 'Informatika', 'Matematika')
   - 'jenjang' (VARCHAR, jenjang studi, e.g. 'S1', 'D3')
   
3. Tabel 'mahasiswa':
   - 'id' (INTEGER, Primary Key)
   - 'nim' (VARCHAR, Nomor Induk Mahasiswa, e.g. '225314001')
   - 'nama' (VARCHAR, nama mahasiswa)
   - 'jurusan' (VARCHAR, jurusan/prodi mahasiswa)
   - 'semester' (INTEGER, semester aktif saat ini)
   
4. Tabel 'mata_kuliah':
   - 'id' (INTEGER, Primary Key)
   - 'kode_mk' (VARCHAR, kode mata kuliah, e.g. 'IF601')
   - 'nama_mk' (VARCHAR, nama mata kuliah)
   - 'sks' (INTEGER, bobot SKS)
   - 'prodi_id' (INTEGER, Foreign Key merujuk ke prodi.id, bisa bernilai NULL untuk mata kuliah umum)
   
5. Tabel 'krs' (Kartu Rencana Studi / Riwayat Pengambilan Mata Kuliah):
   - 'id' (INTEGER, Primary Key)
   - 'mahasiswa_id' (INTEGER, Foreign Key merujuk ke mahasiswa.id)
   - 'mata_kuliah_id' (INTEGER, Foreign Key merujuk ke mata_kuliah.id)
   - 'semester_diambil' (INTEGER, semester saat mata kuliah diambil)
   - 'nilai_huruf' (VARCHAR, bisa bernilai NULL untuk semester berjalan, atau 'A', 'B', 'C', 'D', 'E' untuk mata kuliah yang sudah dinilai)

Aturan Konversi & Kalkulasi Akademik (Penting!):
- Bobot Nilai Huruf: A=4, B=3, C=2, D=1, E=0.
- IPS (Indeks Prestasi Semester): Dihitung dari sum(sks * bobot_nilai) / sum(sks) untuk satu semester_diambil tertentu yang nilainya tidak NULL.
- IPK (Indeks Prestasi Kumulatif): Dihitung dari sum(sks * bobot_nilai) / sum(sks) untuk semua semester yang nilainya tidak NULL.
- SKS Lulus: SKS dari mata kuliah dengan nilai selain 'E' dan tidak NULL.
- Kuota SKS Maksimal Semester Berikutnya (USD Rule):
  - IPS terakhir >= 3.00: Maksimal 24 SKS
  - IPS terakhir >= 2.00: Maksimal 22 SKS
  - IPS terakhir < 2.00: Maksimal 20 SKS

Aturan Keamanan dan Perilaku AI:
1. Anda HANYA diperbolehkan menulis query 'SELECT'. DILARANG KERAS menggunakan kata kunci manipulasi data (seperti INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, dll.) meskipun user memintanya secara terselubung.
2. Anda harus merangkum hasil query mentah dari database menjadi respons bahasa Indonesia yang sopan, ramah, dan informatif bagi pengguna.
3. Selalu tanyakan NIM terlebih dahulu jika pengguna meminta informasi spesifik tentang seorang mahasiswa tanpa menyebutkan NIM-nya.
4. Anda DILARANG menjawab pertanyaan umum di luar konteks akademik dan kampus. Tolak dengan sopan pertanyaan tentang politik, olahraga, hiburan, dll.
5. Jika query database yang Anda jalankan menghasilkan error (misalnya karena typo nama tabel/kolom), baca pesan error tersebut, perbaiki query Anda secara mandiri, dan coba jalankan kembali query yang benar.
"""


async def generate_response_async(prompt: str) -> str:
    if not gemini_client:
        return "Error: GEMINI_API_KEY belum di-setup di environment."

    try:
        # Menggunakan format baru dari google-genai SDK
        response = await gemini_client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=assistant_tools,
                temperature=0.3,
            ),
        )

        # Jika Gemini memutuskan memanggil tools
        if response.function_calls:
            # Di google-genai SDK terbaru, untuk mengeksekusi function calls dan mengirim balasan,
            # lebih baik menggunakan fitur chat session. Tapi karena endpoint cuma nerima 1 prompt,
            # kita buat simple agent:
            chat = gemini_client.aio.chats.create(
                model=LLM_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=assistant_tools,
                    temperature=0.3,
                ),
            )
            final_response = await chat.send_message(prompt)
            return final_response.text
        else:
            return response.text
    except Exception as e:
        # Menghandle error fallback
        try:
            # Retry dengan chat logic jika error direct call
            chat = gemini_client.aio.chats.create(
                model=LLM_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=assistant_tools,
                    temperature=0.3,
                ),
            )
            final_response = await chat.send_message(prompt)
            return final_response.text
        except Exception as inner_e:
            return f"Error dari Gemini Assistant: {str(inner_e)}"
