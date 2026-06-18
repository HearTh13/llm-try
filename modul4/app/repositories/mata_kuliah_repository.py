from sqlalchemy.orm import Session
from app.models.mata_kuliah import MataKuliah


class MataKuliahRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(MataKuliah).all()

    @staticmethod
    def get_by_id(db: Session, mk_id: int):
        return db.query(MataKuliah).filter(MataKuliah.id == mk_id).first()

    @staticmethod
    def create(db: Session, data: dict):
        mk = MataKuliah(
            kode_mk=data["kode_mk"],
            nama_mk=data["nama_mk"],
            sks=data["sks"],
            prodi_id=data.get("prodi_id"),
        )
        db.add(mk)
        db.commit()
        db.refresh(mk)
        return mk

    @staticmethod
    def update(db: Session, mk_id: int, data: dict):
        mk = db.query(MataKuliah).filter(MataKuliah.id == mk_id).first()
        if not mk:
            return None
        mk.kode_mk = data["kode_mk"]
        mk.nama_mk = data["nama_mk"]
        mk.sks = data["sks"]
        mk.prodi_id = data.get("prodi_id")
        db.commit()
        db.refresh(mk)
        return mk

    @staticmethod
    def delete(db: Session, mk_id: int):
        mk = db.query(MataKuliah).filter(MataKuliah.id == mk_id).first()
        if not mk:
            return None
        db.delete(mk)
        db.commit()
        return mk
