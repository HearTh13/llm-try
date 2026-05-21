from sqlalchemy.orm import Session
from app.models.mahasiswa import Mahasiswa


class MahasiswaRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Mahasiswa).all()

    @staticmethod
    def get_by_id(db: Session, mahasiswa_id: int):
        return db.query(Mahasiswa).filter(
            Mahasiswa.id == mahasiswa_id
        ).first()

    @staticmethod
    def create(db: Session, data: dict):

        mahasiswa = Mahasiswa(
            nim=data["nim"],
            nama=data["nama"],
            jurusan=data["jurusan"],
            semester=data["semester"]
        )

        db.add(mahasiswa)
        db.commit()
        db.refresh(mahasiswa)

        return mahasiswa

    @staticmethod
    def update(db: Session, mahasiswa_id: int, data: dict):

        mahasiswa = db.query(Mahasiswa).filter(
            Mahasiswa.id == mahasiswa_id
        ).first()

        if not mahasiswa:
            return None

        mahasiswa.nim = data["nim"]
        mahasiswa.nama = data["nama"]
        mahasiswa.jurusan = data["jurusan"]
        mahasiswa.semester = data["semester"]

        db.commit()
        db.refresh(mahasiswa)

        return mahasiswa

    @staticmethod
    def delete(db: Session, mahasiswa_id: int):

        mahasiswa = db.query(Mahasiswa).filter(
            Mahasiswa.id == mahasiswa_id
        ).first()

        if not mahasiswa:
            return None

        db.delete(mahasiswa)
        db.commit()

        return mahasiswa