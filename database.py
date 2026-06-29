import mysql.connector
from mysql.connector import Error

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "peminjaman"
DB_PORT = 3306

class DatabaseConnection:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        self.port = DB_PORT

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if not connection:
            return False

        cursor = None
        success = False
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            success = True
        except Error as e:
            print(f"Write query execution error: {e}")
            connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        return success

    def execute_read(self, query, params=None):

        connection = self.get_connection()
        if not connection:
            return []

        cursor = None
        results = []
        try:
            # dictionary=True ensures each row is returned as a dictionary: {'column_name': value}
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
        except Error as e:
            print(f"Read query execution error: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        return results

    def get_all_equipment(self):
        query = "SELECT id, nama_barang, kategori, stock, serial_number, description, info_id FROM barang"
        return self.execute_read(query)

    def add_equipment(self, nama_barang, kategori, serial_number, stock, description=None, info_id=None):
        query = """
            INSERT INTO barang (nama_barang, kategori, serial_number, stock, description, info_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (nama_barang, kategori, serial_number, stock, description, info_id)
        return self.execute_query(query, params)

    def update_equipment(self, id, nama_barang, kategori, serial_number, stock, description=None):
        query = """UPDATE barang SET nama_barang=%s, kategori=%s, serial_number=%s, stock=%s, description=%s WHERE id=%s"""
        return self.execute_query(query, (nama_barang, kategori, serial_number, stock, description, id))

    def delete_equipment(self, id):
        return self.execute_query("DELETE FROM barang WHERE id=%s", (id,))

    def get_pending_reservations(self):
        query = """
            SELECT id, user_id, barang_id, start_date, end_date, status, admin_note 
            FROM reservasi 
            WHERE status = 'pending'
        """
        return self.execute_read(query)

    def approve_reservation(self, id):
        return self.execute_query("UPDATE reservasi SET status='approved' WHERE id=%s", (id,))

    def reject_reservation(self, id):
        return self.execute_query("UPDATE reservasi SET status='rejected' WHERE id=%s", (id,))

    def get_available_barang(self):
        return self.execute_read("SELECT id, nama_barang, kategori, stock, serial_number, description FROM barang WHERE stock > 0")

    def get_unavailable_barang(self):
        return self.execute_read("SELECT id, nama_barang, kategori, stock, serial_number, description FROM barang WHERE stock = 0")

    def add_reservation(self, user_id, barang_id, start_date, end_date):
        query = "INSERT INTO reservasi (user_id, barang_id, start_date, end_date, status) VALUES (%s, %s, %s, %s, 'pending')"
        return self.execute_query(query, (user_id, barang_id, start_date, end_date))

    def get_reservations_by_user(self, user_id):
        query = """
            SELECT r.id, r.barang_id, b.nama_barang, r.start_date, r.end_date, r.status, r.admin_note
            FROM reservasi r
            LEFT JOIN barang b ON r.barang_id = b.id
            WHERE r.user_id = %s
            ORDER BY r.start_date DESC
        """
        return self.execute_read(query, (user_id,))

