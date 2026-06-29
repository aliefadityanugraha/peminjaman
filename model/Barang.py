class Barang:
    def __init__(self, id, nama_barang, kategori, serial_number, stock, description=None, info_id=None):
        self.id = id
        self.nama_barang = nama_barang
        self.kategori = kategori
        self.serial_number = serial_number
        self.stock = stock
        self.description = description
        self.info_id = info_id
        self.reservasi = []

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            nama_barang=data.get('nama_barang'),
            kategori=data.get('kategori'),
            serial_number=data.get('serial_number'),
            stock=data.get('stock'),
            description=data.get('description'),
            info_id=data.get('info_id')
        )

Equipment = Barang