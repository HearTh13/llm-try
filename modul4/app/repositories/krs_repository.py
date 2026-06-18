from sqlalchemy.orm import Session
from app.models.krs import KRS


class KrsRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(KRS).all()

    @staticmethod
    def get_by_id(db: Session, krs_id: int):
        return db.query(KRS).filter(KRS.id == krs_id).first()

    @staticmethod
    def create(db: Session, data: dict):
        krs = KRS(
            mahasiswa_id=data["mahasiswa_id"],
            mata_kuliah_id=data["mata_kuliah_id"],
            semester_diambil=data["semester_diambil"],
            nilai_huruf=data.get("nilai_huruf"),
        )
        db.add(krs)
        db.commit()
        db.refresh(krs)
        return krs

    @staticmethod
    def update(db: Session, krs_id: int, data: dict):
        krs = db.query(KRS).filter(KRS.id == krs_id).first()
        if not krs:
            return None
        krs.mahasiswa_id = data["mahasiswa_id"]
        krs.mata_kuliah_id = data["mata_kuliah_id"]
        krs.semester_diambil = data["semester_diambil"]
        krs.nilai_huruf = data.get("nilai_huruf")
        db.commit()
        db.refresh(krs)
        return krs

    @staticmethod
    def delete(db: Session, krs_id: int):
        krs = db.query(KRS).filter(KRS.id == krs_id).first()
        if not krs:
            return None
        db.delete(krs)
        db.commit()
        return krs
