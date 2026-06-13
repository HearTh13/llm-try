from app.repositories.krs_repository import KrsRepository


class KrsService:

    @staticmethod
    def create_krs(db, data):
        try:
            result = KrsRepository.create(db, data)
            return {"success": True, "message": "KRS berhasil ditambahkan", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal menambahkan KRS: {str(e)}"}

    @staticmethod
    def get_all_krs(db):
        try:
            result = KrsRepository.get_all(db)
            return {"success": True, "message": "Data KRS berhasil diambil", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data KRS: {str(e)}"}

    @staticmethod
    def get_krs_by_id(db, krs_id):
        try:
            result = KrsRepository.get_by_id(db, krs_id)
            if not result:
                return {"success": False, "message": "KRS tidak ditemukan"}
            return {"success": True, "message": "Data KRS ditemukan", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data KRS: {str(e)}"}

    @staticmethod
    def update_krs(db, krs_id, data):
        try:
            result = KrsRepository.update(db, krs_id, data)
            if not result:
                return {"success": False, "message": "KRS tidak ditemukan"}
            return {"success": True, "message": "Data KRS berhasil diupdate", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal update KRS: {str(e)}"}

    @staticmethod
    def delete_krs(db, krs_id):
        try:
            result = KrsRepository.delete(db, krs_id)
            if not result:
                return {"success": False, "message": "KRS tidak ditemukan"}
            return {"success": True, "message": "KRS berhasil dihapus"}
        except Exception as e:
            return {"success": False, "message": f"Gagal menghapus KRS: {str(e)}"}
