from sqlalchemy.orm import Session
from app.models.grade import Grade


class GradeRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Grade).all()

    @staticmethod
    def get_by_id(db: Session, grade_id: int):
        return db.query(Grade).filter(
            Grade.id == grade_id
        ).first()

    @staticmethod
    def create(db: Session, data: dict):

        grade = Grade(**data)

        db.add(grade)
        db.commit()
        db.refresh(grade)

        return grade

    @staticmethod
    def delete(db: Session, grade_id: int):

        grade = db.query(Grade).filter(
            Grade.id == grade_id
        ).first()

        if not grade:
            return None

        db.delete(grade)
        db.commit()

        return grade