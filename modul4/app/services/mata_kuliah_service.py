from app.repositories.mata_kuliah_repository import MataKuliahRepository


class MataKuliahService:

    @staticmethod
    def create_mata_kuliah(db, data):
        try:
            result = MataKuliahRepository.create(db, data)
            return {"success": True, "message": "Mata kuliah berhasil ditambahkan", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal menambahkan mata kuliah: {str(e)}"}

    @staticmethod
    def get_all_mata_kuliah(db):
        try:
            result = MataKuliahRepository.get_all(db)
            return {"success": True, "message": "Data mata kuliah berhasil diambil", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data mata kuliah: {str(e)}"}

    @staticmethod
    def get_mata_kuliah_by_id(db, mk_id):
        try:
            result = MataKuliahRepository.get_by_id(db, mk_id)
            if not result:
                return {"success": False, "message": "Mata kuliah tidak ditemukan"}
            return {"success": True, "message": "Data mata kuliah ditemukan", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal mengambil data mata kuliah: {str(e)}"}

    @staticmethod
    def update_mata_kuliah(db, mk_id, data):
        try:
            result = MataKuliahRepository.update(db, mk_id, data)
            if not result:
                return {"success": False, "message": "Mata kuliah tidak ditemukan"}
            return {"success": True, "message": "Data mata kuliah berhasil diupdate", "data": result}
        except Exception as e:
            return {"success": False, "message": f"Gagal update mata kuliah: {str(e)}"}

    @staticmethod
    def delete_mata_kuliah(db, mk_id):
        try:
            result = MataKuliahRepository.delete(db, mk_id)
            if not result:
                return {"success": False, "message": "Mata kuliah tidak ditemukan"}
            return {"success": True, "message": "Mata kuliah berhasil dihapus"}
        except Exception as e:
            return {"success": False, "message": f"Gagal menghapus mata kuliah: {str(e)}"}
