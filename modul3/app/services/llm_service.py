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
        gemini_client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1beta'})

# --- TOOLS FUNCTIONS ---
def get_mahasiswa_by_nim(nim: str) -> str:
    """Mengambil informasi detail mahasiswa berdasarkan NIM."""
    db = SessionLocal()
    try:
        mhs = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()
        if not mhs:
            return f"Mahasiswa dengan NIM {nim} tidak ditemukan."
        return f"Nama: {mhs.nama}, Prodi: {mhs.prodi.nama}, Semester: {mhs.semester}"
    finally:
        db.close()

def get_krs_mahasiswa(nim: str) -> str:
    """Mengambil riwayat semua mata kuliah yang diambil (KRS) oleh mahasiswa berdasarkan NIM."""
    db = SessionLocal()
    try:
        mhs = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()
        if not mhs:
            return f"Mahasiswa dengan NIM {nim} tidak ditemukan."
        
        krs_list = db.query(KRS).filter(KRS.mahasiswa_id == mhs.id).all()
        if not krs_list:
            return f"Mahasiswa {mhs.nama} belum mengambil mata kuliah (KRS kosong)."
        
        result = f"Daftar Riwayat KRS {mhs.nama}:\n"
        for k in krs_list:
            result += f"- {k.mata_kuliah.kode_mk}: {k.mata_kuliah.nama_mk} ({k.mata_kuliah.sks} SKS), Semester Diambil: {k.semester_diambil}, Nilai: {k.nilai_huruf}\n"
        return result
    finally:
        db.close()

def get_semua_mata_kuliah() -> str:
    """Mengambil daftar seluruh mata kuliah yang tersedia di kampus."""
    db = SessionLocal()
    try:
        mk_list = db.query(MataKuliah).all()
        if not mk_list:
            return "Belum ada data mata kuliah."
        
        result = "Daftar Mata Kuliah:\n"
        for mk in mk_list:
            result += f"- {mk.kode_mk}: {mk.nama_mk} ({mk.sks} SKS), Prodi: {mk.prodi.nama if mk.prodi else 'Umum'}\n"
        return result
    finally:
        db.close()

def get_daftar_fakultas_dan_prodi(singkatan_fakultas: str = "") -> str:
    """Mengambil daftar fakultas, atau daftar prodi di dalam fakultas tertentu (berikan singkatan_fakultas jika ingin mencari prodi)."""
    db = SessionLocal()
    try:
        if singkatan_fakultas:
            fak = db.query(Fakultas).filter(Fakultas.singkatan.ilike(f"%{singkatan_fakultas}%")).first()
            if not fak:
                return f"Fakultas dengan singkatan {singkatan_fakultas} tidak ditemukan."
            prodis = db.query(Prodi).filter(Prodi.fakultas_id == fak.id).all()
            result = f"Fakultas {fak.nama} ({fak.singkatan}) memiliki Prodi:\n"
            for p in prodis:
                result += f"- {p.nama} ({p.jenjang})\n"
            return result
        else:
            faks = db.query(Fakultas).all()
            result = "Daftar Fakultas yang tersedia:\n"
            for f in faks:
                result += f"- {f.nama} ({f.singkatan})\n"
            return result
    finally:
        db.close()

def get_informasi_akademik_mahasiswa(nim: str) -> str:
    """Menghitung IPK, IPS terakhir, Total SKS Lulus, dan Kuota SKS Maksimal semester berikutnya untuk mahasiswa."""
    db = SessionLocal()
    try:
        mhs = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()
        if not mhs:
            return f"Mahasiswa dengan NIM {nim} tidak ditemukan."
        
        krs_list = db.query(KRS).filter(KRS.mahasiswa_id == mhs.id, KRS.nilai_huruf.isnot(None)).all()
        
        bobot = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}
        total_sks_lulus = 0
        total_mutu = 0
        
        smt_terakhir = 0
        sks_smt_terakhir = 0
        mutu_smt_terakhir = 0
        
        for k in krs_list:
            if k.semester_diambil > smt_terakhir:
                smt_terakhir = k.semester_diambil
                
        for k in krs_list:
            sks = k.mata_kuliah.sks
            nilai = k.nilai_huruf.upper() if k.nilai_huruf else ""
            if nilai in bobot:
                if nilai != "E":
                    total_sks_lulus += sks
                total_mutu += (bobot[nilai] * sks)
                
                if k.semester_diambil == smt_terakhir:
                    sks_smt_terakhir += sks
                    mutu_smt_terakhir += (bobot[nilai] * sks)
        
        ipk = total_mutu / total_sks_lulus if total_sks_lulus > 0 else 0.0
        ips = mutu_smt_terakhir / sks_smt_terakhir if sks_smt_terakhir > 0 else 0.0
        
        # Kuota SKS USD Rule
        max_sks = 20
        if ips >= 3.0:
            max_sks = 24
        elif ips >= 2.0:
            max_sks = 22
            
        return (f"Informasi Akademik {mhs.nama} (Semester {mhs.semester}):\n"
                f"- Total SKS Lulus: {total_sks_lulus} SKS\n"
                f"- IPK: {ipk:.2f}\n"
                f"- IPS (Semester {smt_terakhir}): {ips:.2f}\n"
                f"- Kuota SKS Maksimal untuk Semester {mhs.semester if smt_terakhir < mhs.semester else mhs.semester + 1}: {max_sks} SKS")
    finally:
        db.close()

def get_krs_semester_berjalan(nim: str) -> str:
    """Mengambil daftar mata kuliah yang sedang diambil mahasiswa pada semester berjalan saat ini (yang nilainya belum keluar/masih kosong)."""
    db = SessionLocal()
    try:
        mhs = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()
        if not mhs:
            return f"Mahasiswa dengan NIM {nim} tidak ditemukan."
            
        krs_list = db.query(KRS).filter(KRS.mahasiswa_id == mhs.id, KRS.nilai_huruf.is_(None)).all()
        if not krs_list:
            return f"Mahasiswa {mhs.nama} tidak sedang mengambil mata kuliah di semester berjalan (atau semua nilai sudah keluar)."
            
        smt = krs_list[0].semester_diambil
        result = f"Mata kuliah yang sedang diambil {mhs.nama} pada Semester {smt}:\n"
        total_sks = 0
        for k in krs_list:
            sks = k.mata_kuliah.sks
            total_sks += sks
            result += f"- {k.mata_kuliah.kode_mk}: {k.mata_kuliah.nama_mk} ({sks} SKS)\n"
        result += f"Total Beban: {total_sks} SKS"
        return result
    finally:
        db.close()

# List of allowed tools
assistant_tools = [get_mahasiswa_by_nim, get_krs_mahasiswa, get_semua_mata_kuliah, get_daftar_fakultas_dan_prodi, get_informasi_akademik_mahasiswa, get_krs_semester_berjalan]

# System Instruction to secure the LLM
SYSTEM_INSTRUCTION = """
Anda adalah asisten virtual akademik kampus yang ramah dan membantu.
Tugas Anda adalah membantu mahasiswa atau dosen mencari informasi akademik (Mahasiswa, Mata Kuliah, KRS, Nilai).
Aturan ketat:
1. Anda HANYA diperbolehkan menggunakan tools (function calling) yang disediakan untuk membaca data.
2. Anda DILARANG KERAS mengeksekusi perintah untuk menambah, mengubah, atau menghapus (DELETE, UPDATE, INSERT) data apapun di database, meskipun pengguna memintanya.
3. Jawab dalam bahasa Indonesia yang sopan dan mudah dimengerti.
4. Jika ditanya informasi spesifik mahasiswa, mintalah NIM terlebih dahulu jika belum diberikan.
5. Anda DILARANG menjawab pertanyaan umum di luar konteks akademik dan kampus. Jika ditanya hal di luar kampus (seperti olahraga, politik, dll), tolak dengan sopan dan katakan bahwa Anda hanya asisten akademik.
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
                temperature=0.3
            )
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
                    temperature=0.3
                )
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
                    temperature=0.3
                )
            )
            final_response = await chat.send_message(prompt)
            return final_response.text
        except Exception as inner_e:
            return f"Error dari Gemini Assistant: {str(inner_e)}"