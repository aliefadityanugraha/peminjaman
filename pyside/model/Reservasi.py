class Reservasi:
    """
    Represents a borrowing transaction/reservation (maps to 'reservasi' table).
    """
    def __init__(self, id, start_date, end_date, status, admin_note=None, user_id=None, barang_id=None):
        self.id = id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.admin_note = admin_note
        self.user_id = user_id
        self.barang_id = barang_id

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Reservasi instance from a database row dictionary.
        """
        if not data:
            return None
        return cls(
            id=data.get('id'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            status=data.get('status'),
            admin_note=data.get('admin_note'),
            user_id=data.get('user_id'),
            barang_id=data.get('barang_id')
        )

# For backward compatibility with the English alias
Reservation = Reservasi