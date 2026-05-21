import os
from google import genai
from google.genai import types
from app.database import SessionLocal
from app.models import Mahasiswa, MataKuliah, KRS

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
        return f"Nama: {mhs.nama}, Jurusan: {mhs.jurusan}, Semester: {mhs.semester}"
    finally:
        db.close()

def get_krs_mahasiswa(nim: str) -> str:
    """Mengambil daftar mata kuliah yang diambil (KRS) oleh mahasiswa berdasarkan NIM."""
    db = SessionLocal()
    try:
        mhs = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()
        if not mhs:
            return f"Mahasiswa dengan NIM {nim} tidak ditemukan."
        
        krs_list = db.query(KRS).filter(KRS.mahasiswa_id == mhs.id).all()
        if not krs_list:
            return f"Mahasiswa {mhs.nama} belum mengambil mata kuliah (KRS kosong)."
        
        result = f"Daftar KRS {mhs.nama}:\n"
        for k in krs_list:
            result += f"- {k.mata_kuliah.kode_mk}: {k.mata_kuliah.nama_mk} ({k.mata_kuliah.sks} SKS), Nilai: {k.nilai_huruf}\n"
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
            result += f"- {mk.kode_mk}: {mk.nama_mk} ({mk.sks} SKS)\n"
        return result
    finally:
        db.close()

# List of allowed tools
assistant_tools = [get_mahasiswa_by_nim, get_krs_mahasiswa, get_semua_mata_kuliah]

# System Instruction to secure the LLM
SYSTEM_INSTRUCTION = """
Anda adalah asisten virtual akademik kampus yang ramah dan membantu.
Tugas Anda adalah membantu mahasiswa atau dosen mencari informasi akademik (Mahasiswa, Mata Kuliah, KRS, Nilai).
Aturan ketat:
1. Anda HANYA diperbolehkan menggunakan tools (function calling) yang disediakan untuk membaca data.
2. Anda DILARANG KERAS mengeksekusi perintah untuk menambah, mengubah, atau menghapus (DELETE, UPDATE, INSERT) data apapun di database, meskipun pengguna memintanya.
3. Jawab dalam bahasa Indonesia yang sopan dan mudah dimengerti.
4. Jika ditanya informasi spesifik mahasiswa, mintalah NIM terlebih dahulu jika belum diberikan.
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