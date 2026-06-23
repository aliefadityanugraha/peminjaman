import mysql.connector
from mysql.connector import Error

# Database connection configurations
# You can customize these variables to match your local MySQL configuration.
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "peminjaman"
DB_PORT = 3306

class DatabaseConnection:
    """
    A simple helper class to manage MySQL database connections.
    Provides methods to execute read (SELECT) and write (INSERT/UPDATE/DELETE) queries
    securely using parameterized statements to prevent SQL injection.
    """
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        self.port = DB_PORT

    def get_connection(self):
        """
        Establishes and returns a new connection to the MySQL database.
        Returns None if the connection fails.
        """
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
        """
        Executes write queries (like INSERT, UPDATE, DELETE).
        Automatically commits the transaction and closes the connection.
        
        Args:
            query (str): The SQL query string.
            params (tuple, optional): Parameters to bind to the query.
            
        Returns:
            bool: True if successful, False otherwise.
        """
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
        """
        Executes read queries (SELECT statements) and returns the records.
        Automatically maps columns to a dictionary key-value structure for ease of use.
        
        Args:
            query (str): The SQL select query.
            params (tuple, optional): Parameters to bind to the query.
            
        Returns:
            list[dict]: A list of rows, where each row is represented as a dictionary.
        """
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
        """
        Fetches all equipment details from the 'barang' table.
        """
        query = "SELECT id, nama_barang, kategori, stock, serial_number, description, info_id FROM barang"
        return self.execute_read(query)

    def add_equipment(self, nama_barang, kategori, serial_number, stock, description=None, info_id=None):
        """
        Inserts a new equipment record into the 'barang' table.
        """
        query = """
            INSERT INTO barang (nama_barang, kategori, serial_number, stock, description, info_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (nama_barang, kategori, serial_number, stock, description, info_id)
        return self.execute_query(query, params)

    def get_pending_reservations(self):
        """
        Fetches all pending reservations from the 'reservasi' table.
        """
        query = """
            SELECT id, user_id, start_date, end_date, status, admin_note, barang_id 
            FROM reservasi 
            WHERE status = 'pending'
        """
        return self.execute_read(query)

