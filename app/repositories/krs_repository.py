from sqlalchemy.orm import Session
from app.models.krs import KRS


class KRSRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(KRS).all()

    @staticmethod
    def get_by_id(db: Session, krs_id: int):
        return db.query(KRS).filter(
            KRS.id == krs_id
        ).first()

    @staticmethod
    def create(db: Session, data: dict):

        krs = KRS(**data)

        db.add(krs)
        db.commit()
        db.refresh(krs)

        return krs

    @staticmethod
    def delete(db: Session, krs_id: int):

        krs = db.query(KRS).filter(
            KRS.id == krs_id
        ).first()

        if not krs:
            return None

        db.delete(krs)
        db.commit()

        return krs