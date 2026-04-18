from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool
from sqlalchemy.orm import Session

from app.models.faculty import Faculty
from app.models.study_program import StudyProgram
from app.models.building import Building
from app.models.news import News


def tanya_ai_dengan_agent(prompt_user: str, db: Session) -> str:
    llm = ChatOllama(
        model="llama3.2",
        base_url="http://host.docker.internal:11434",
        temperature=0
    )

    def _cari_perpustakaan(_: str) -> str:
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

    def _cari_tempat_ibadah(_: str) -> str:
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

    def _cari_parkir(_: str) -> str:
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

    def _daftar_fakultas(_: str) -> str:
        hasil = db.query(Faculty).all()

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{f.name}: {f.description}"
            for f in hasil
        )

    def _daftar_program_studi(_: str) -> str:
        hasil = db.query(StudyProgram).all()

        if not hasil:
            return "Informasi tersebut belum tersedia di database kampus."

        return "\n".join(
            f"{p.name} ({p.degree}) - Akreditasi {p.accreditation}"
            for p in hasil
        )

    def _berita_terbaru(_: str) -> str:
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
        Tool(
            name="cari_perpustakaan",
            func=_cari_perpustakaan,
            description="Gunakan tool ini jika user menanyakan perpustakaan, library, atau lokasi membaca di kampus."
        ),
        Tool(
            name="cari_tempat_ibadah",
            func=_cari_tempat_ibadah,
            description="Gunakan tool ini jika user menanyakan masjid, mushola, atau tempat ibadah."
        ),
        Tool(
            name="cari_parkir",
            func=_cari_parkir,
            description="Gunakan tool ini jika user menanyakan parkiran atau lokasi parkir."
        ),
        Tool(
            name="daftar_fakultas",
            func=_daftar_fakultas,
            description="Gunakan tool ini jika user menanyakan daftar fakultas yang tersedia."
        ),
        Tool(
            name="daftar_program_studi",
            func=_daftar_program_studi,
            description="Gunakan tool ini jika user menanyakan program studi, jurusan, atau prodi."
        ),
        Tool(
            name="berita_terbaru",
            func=_berita_terbaru,
            description="Gunakan tool ini jika user menanyakan berita terbaru kampus."
        ),
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    try:
        hasil = agent.invoke(prompt_user)

        if isinstance(hasil, dict):
            return hasil.get("output", str(hasil))

        return str(hasil)

    except Exception as e:
        return f"Kesalahan AI: {e}"