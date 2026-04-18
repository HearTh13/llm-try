from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool    
from sqlalchemy.orm import Session

from app.models.faculty import Faculty
from app.models.study_program import StudyProgram
from app.models.building import Building
from app.models.news import News


def tanya_ai_dengan_konteks(prompt_user: str, db: Session) -> str:
    llm = ChatOllama(
        model="llama3.2",
        base_url="http://host.docker.internal:11434"
    )

    @tool
    def cari_perpustakaan() -> str:
        """Cari lokasi perpustakaan di kampus."""
        hasil = (
            db.query(Building)
            .filter(Building.category.ilike("%perpustakaan%"))
            .all()
        )

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{b.name} - {b.address}"
            for b in hasil
        )

    @tool
    def cari_tempat_ibadah() -> str:
        """Cari masjid atau tempat ibadah di kampus."""
        hasil = (
            db.query(Building)
            .filter(Building.category.ilike("%ibadah%"))
            .all()
        )

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{b.name} - {b.address}"
            for b in hasil
        )

    @tool
    def cari_parkir() -> str:
        """Cari lokasi parkir di kampus."""
        hasil = (
            db.query(Building)
            .filter(Building.category.ilike("%parkir%"))
            .all()
        )

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{b.name} - {b.address}"
            for b in hasil
        )

    @tool
    def daftar_fakultas() -> str:
        """Menampilkan daftar fakultas kampus."""
        hasil = db.query(Faculty).all()

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{f.name}: {f.description}"
            for f in hasil
        )

    @tool
    def daftar_program_studi() -> str:
        """Menampilkan daftar program studi kampus."""
        hasil = db.query(StudyProgram).all()

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{p.name} ({p.degree}) - Akreditasi {p.accreditation}"
            for p in hasil
        )

    @tool
    def berita_terbaru() -> str:
        """Mengambil berita terbaru kampus."""
        hasil = (
            db.query(News)
            .order_by(News.date.desc())
            .limit(5)
            .all()
        )

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n\n".join(
            f"{n.title}\n{n.content[:200]}"
            for n in hasil
        )

    tools = [
        cari_perpustakaan,
        cari_tempat_ibadah,
        cari_parkir,
        daftar_fakultas,
        daftar_program_studi,
        berita_terbaru,
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": """
Kamu adalah chatbot informasi kampus.

Gunakan tool yang tersedia untuk menjawab pertanyaan.
Jangan mengarang data.
Jika data tidak ditemukan, jawab:
'Informasi tersebut belum tersedia di database kampus.'
"""
        }
    )

    try:
        hasil = agent.invoke({
            "input": prompt_user
        })

        return hasil["output"]

    except Exception as e:
        return f"Kesalahan AI: {e}"