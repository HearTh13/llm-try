from app.repositories.mahasiswa_repository import MahasiswaRepository


class MahasiswaService:

    @staticmethod
    def create_mahasiswa(db, data):
        try:
            result = MahasiswaRepository.create(db, data)

            return {
                "success": True,
                "message": "Mahasiswa berhasil ditambahkan",
                "data": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal menambahkan mahasiswa: {str(e)}"
            }

    @staticmethod
    def get_all_mahasiswa(db):
        try:
            result = MahasiswaRepository.get_all(db)

            return {
                "success": True,
                "message": "Data mahasiswa berhasil diambil",
                "data": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil data mahasiswa: {str(e)}"
            }

    @staticmethod
    def get_mahasiswa_by_id(db, mahasiswa_id):
        try:
            result = MahasiswaRepository.get_by_id(db, mahasiswa_id)

            if not result:
                return {
                    "success": False,
                    "message": "Mahasiswa tidak ditemukan"
                }

            return {
                "success": True,
                "message": "Data mahasiswa berhasil ditemukan",
                "data": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil data mahasiswa: {str(e)}"
            }

    @staticmethod
    def update_mahasiswa(db, mahasiswa_id, data):
        try:
            result = MahasiswaRepository.update(
                db,
                mahasiswa_id,
                data
            )

            return {
                "success": True,
                "message": "Data mahasiswa berhasil diupdate",
                "data": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal update mahasiswa: {str(e)}"
            }

    @staticmethod
    def delete_mahasiswa(db, mahasiswa_id):
        try:
            MahasiswaRepository.delete(db, mahasiswa_id)

            return {
                "success": True,
                "message": "Mahasiswa berhasil dihapus"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal menghapus mahasiswa: {str(e)}"
            }
