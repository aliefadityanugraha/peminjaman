class User:
    """
    Represents a user in the system (maps to 'user' table).
    """
    def __init__(self, id, email, username, password, role, no_hp=None):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.role = role
        self.no_hp = no_hp
        self.reservasi = []

    @classmethod
    def from_dict(cls, data):
        """
        Creates a User instance from a database row dictionary.
        """
        if not data:
            return None
        return cls(
            id=data.get('id'),
            email=data.get('email'),
            username=data.get('username'),
            password=data.get('password'),
            role=data.get('role'),
            no_hp=data.get('no_hp')
        )