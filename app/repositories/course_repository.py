from sqlalchemy.orm import Session
from app.models.course import Course


class CourseRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Course).all()

    @staticmethod
    def get_by_id(db: Session, course_id: int):
        return db.query(Course).filter(
            Course.id == course_id
        ).first()

    @staticmethod
    def create(db: Session, data: dict):

        course = Course(**data)

        db.add(course)
        db.commit()
        db.refresh(course)

        return course

    @staticmethod
    def delete(db: Session, course_id: int):

        course = db.query(Course).filter(
            Course.id == course_id
        ).first()

        if not course:
            return None

        db.delete(course)
        db.commit()

        return course