class InfoBarang:
    """
    Represents custom technical information about an equipment (maps to 'info_barang' table).
    """
    def __init__(self, id, tahun_beli, panduan=None):
        self.id = id
        self.tahun_beli = tahun_beli
        self.panduan = panduan

    @classmethod
    def from_dict(cls, data):
        """
        Creates an InfoBarang instance from a database row dictionary.
        """
        if not data:
            return None
        return cls(
            id=data.get('id'),
            tahun_beli=data.get('tahun_beli'),
            panduan=data.get('panduan')
        )

# For backward compatibility with the English alias
InfoEquipment = InfoBarang