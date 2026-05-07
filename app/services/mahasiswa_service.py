from app.repositories.mahasiswa_repository import MahasiswaRepository


class MahasiswaService:

    @staticmethod
    def create_mahasiswa(db, data):

        return MahasiswaRepository.create(
            db,
            data
        )
    
    @staticmethod
    def get_all_mahasiswa(db):

        return MahasiswaRepository.get_all(db)
    
    @staticmethod
    def get_mahasiswa_by_id(db, mahasiswa_id):

        return MahasiswaRepository.get_by_id(
            db,
            mahasiswa_id
        )
    
    @staticmethod
    def update_mahasiswa(db, mahasiswa_id, data):

        return MahasiswaRepository.update(
            db,
            mahasiswa_id,
            data
        )

    @staticmethod
    def delete_mahasiswa(db, mahasiswa_id):

        return MahasiswaRepository.delete(
            db,
            mahasiswa_id
        )