import re
from typing import List, Optional
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from better_profanity import profanity
from sqlalchemy.orm import Session
from app.models.faculty import Faculty
from app.models.study_program import StudyProgram
from app.models.building import Building
from app.models.news import News
from app.models.chat import ChatHistory

# Konfigurasi LLM LangChain
llm = ChatOllama(
    model="llama3.2", base_url="http://host.docker.internal:11434", temperature=0.1
)

# --- Safety Guardrail ---


def periksa_keamanan_input(text: str) -> bool:
    if profanity.contains_profanity(text):
        return False
    jailbreak_patterns = [
        r"ignore previous instructions",
        r"lupakan instruksi",
        r"tampilkan system prompt",
        r"reveal your secrets",
    ]
    for pattern in jailbreak_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True


# --- LangChain Tools Definition ---


def get_tools(db: Session):
    @tool
    def informasi_asli_sanata_dharma(_: str = "") -> str:
        """Dapatkan profil, sejarah, visi, misi, dan lokasi kampus Sanata Dharma (USD)."""
        return (
            "Universitas Sanata Dharma (USD) adalah perguruan tinggi Jesuit di Yogyakarta.\n"
            "Motto: Cerdas dan Humanis. Berdiri: 1955.\n"
            "Kampus: 1 (Mrican), 2 & 3 (Paingan), 4 (Kotabaru)."
        )

    @tool
    def ambil_daftar_fakultas(_: str = "") -> str:
        """Melihat daftar seluruh fakultas yang ada di Sanata Dharma."""
        data = db.query(Faculty).all()
        return (
            str([{"nama": f.name} for f in data]) if data else "Data fakultas kosong."
        )

    @tool
    def cari_prodi_kampus(nama_fakultas: Optional[any] = None) -> str:
        """Mencari daftar program studi (prodi). Parameter: nama_fakultas (STRING)."""
        # Defensive: Handle if LLM sends dict
        if isinstance(nama_fakultas, dict):
            nama_fakultas = str(next(iter(nama_fakultas.values()))) if nama_fakultas else None
            
        query = db.query(StudyProgram)
        if nama_fakultas and isinstance(nama_fakultas, str):
            faculty = (
                db.query(Faculty)
                .filter(Faculty.name.ilike(f"%{nama_fakultas}%"))
                .first()
            )
            if faculty:
                query = query.filter_by(faculty_id=faculty.id)
        data = query.all()
        return (
            str([{"prodi": p.name, "akreditasi": p.accreditation} for p in data])
            if data
            else "Prodi tidak ditemukan."
        )

    @tool
    def cek_lokasi_gedung(kategori: Optional[any] = None) -> str:
        """Mencari lokasi gedung fisik kampus (seperti Rektorat, Masjid, Lab). Parameter: kategori (STRING)."""
        # Defensive: Handle if LLM sends dict
        if isinstance(kategori, dict):
            kategori = str(next(iter(kategori.values()))) if kategori else None
            
        query = db.query(Building)
        if kategori and isinstance(kategori, str):
            query = query.filter(Building.category.ilike(f"%{kategori}%") | Building.name.ilike(f"%{kategori}%"))
        data = query.all()
        return (
            str([{"tempat": b.name, "alamat": b.address} for b in data])
            if data
            else "Lokasi tidak ditemukan."
        )

    @tool
    def web_search(query: str) -> str:
        """Cari info umum di internet jika tidak ada di database Sanata Dharma."""
        return DuckDuckGoSearchRun().run(query)

    return [
        informasi_asli_sanata_dharma,
        ambil_daftar_fakultas,
        cari_prodi_kampus,
        cek_lokasi_gedung,
        web_search,
    ]


# --- Agentic Logic with LangChain ---


def tanya_ai_dengan_konteks(prompt_user: str, db: Session) -> str:
    # 0. Safety Check
    if not periksa_keamanan_input(prompt_user):
        return "Maaf, permintaan Anda tidak dapat diproses demi keamanan."

    # 0.1 Handle Identity Directly - Gunakan regex agar lebih kuat terhadap variasi tanda baca/huruf
    if re.search(
        r"(siapa namamu|namamu siapa|siapa kamu|siapa anda|nama kamu)",
        prompt_user,
        re.IGNORECASE,
    ):
        return "Halo! Nama saya CxR Mas Owok, asisten virtual resmi dari Universitas Sanata Dharma (USD). Senang bertemu denganmu! Ada yang bisa saya bantu terkait informasi kampus kita?"

    tools = get_tools(db)
    llm_with_tools = llm.bind_tools(tools)

    # Membatasi history hanya 3 pasang agar tidak terlalu bias
    history_db = db.query(ChatHistory).order_by(ChatHistory.id.desc()).limit(3).all()
    history_db.reverse()

    messages = [
        SystemMessage(
            content=(
                "KAMU ADALAH 'CxR Mas Owok', Virtual Assistant resmi Universitas Sanata Dharma (USD). Jawablah dengan ramah, cerdas, dan humanis.\n"
                "ATURAN DISIPLIN JAWABAN:\n"
                "1. JANGAN PERNAH MEMINTA MAAF atau mengatakan 'saya tidak bisa menjawab langsung'.\n"
                "2. JANGAN PERNAH menyebutkan bahwa informasi didapat dari database atau tool.\n"
                "3. LANGSUNG BERIKAN JAWABAN: Jika kamu mendapatkan data dari Tool, langsung sampaikan informasinya seolah-olah kamu memang sudah sangat tahu.\n"
                "4. DILARANG BERIMAJINASI: Hanya gunakan data yang benar-benar ada di Tool.\n"
                "5. GAYA BAHASA: Berikan informasi yang padat, jelas, dan profesional dalam Bahasa Indonesia yang alami."
            )
        )
    ]

    for h in history_db:
        messages.append(HumanMessage(content=h.user_prompt))
        messages.append(AIMessage(content=h.llm_response))

    messages.append(HumanMessage(content=prompt_user))

    try:
        print(f"\n[CxR Mas Owok Thinking] {prompt_user}")
        response = llm_with_tools.invoke(messages)

        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                selected_tool = next(
                    (t for t in tools if t.name == tool_call["name"]), None
                )
                if selected_tool:
                    print(f"  -> Action: {tool_call['name']}({tool_call['args']})")
                    tool_output = selected_tool.invoke(tool_call["args"])
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": tool_output,
                        }
                    )

            final_response = llm.invoke(messages)
            return final_response.content

        return response.content

    except Exception as e:
        print(f"[Error] {e}")
        return f"Maaf, CxR Mas Owok sedang mengalami kendala teknis. Mohon coba lagi sebentar lagi."
