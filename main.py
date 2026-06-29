import sys

# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import QApplication
from database import DatabaseConnection
from model import User
from views.login import LayarLogin
from views.admin import DashboardAdmin
from views.peminjam import DashboardPeminjam

class AppController:
    def __init__(self):
        self.login_screen = None
        self.main_window = None

    def show_login_screen(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
            
        self.login_screen = LayarLogin()
        # Connect the view's custom signal to the controller's login verification logic
        self.login_screen.permintaan_login.connect(self.handle_login)
        self.login_screen.show()

    def handle_login(self, username, password):
        db = DatabaseConnection()

        conn = db.get_connection()
        if not conn:
            print("Warning: Could not connect to MySQL database.")
            # Graceful offline mode fallback for GUI design testing and verification
            if username == "admin" and password == "admin":
                print("Offline login successful with mock developer credentials.")
                mock_user = User(
                    id=0,
                    email="admin@pfspaces.com",
                    username="admin",
                    password="admin",
                    role="admin",
                    no_hp="0812345678"
                )
                self.show_main_window(mock_user)
            else:
                self.login_screen.show_error(
                    "Database connection failed.\nVerify host settings in database.py,\nor use 'admin' / 'admin' for offline testing."
                )
            return

        # Database is online, query the credentials
        try:
            # Query user matching the typed username
            query = "SELECT * FROM user WHERE username = %s"
            results = db.execute_read(query, (username,))
            
            if not results:
                self.login_screen.show_error("Username does not exist.")
                return
                
            user_data = results[0]
            # Simple password check (plaintext comparison as requested for simplicity)
            if user_data.get("password") == password:
                user = User.from_dict(user_data)
                self.show_main_window(user)
            else:
                self.login_screen.show_error("Incorrect password.")
        except Exception as e:
            self.login_screen.show_error(f"Error during login: {e}")

    def show_main_window(self, user):
        """
        Instantiates and shows the main application window after successful login.
        Routes to Admin or Peminjam dashboard based on role.
        """
        if self.login_screen:
            self.login_screen.close()
            self.login_screen = None

        if user.role == "admin":
            self.main_window = DashboardAdmin(user)
        else:
            self.main_window = DashboardPeminjam(user)

        self.main_window.logout_requested.connect(self.show_login_screen)
        self.main_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Run the App Coordinator
    controller = AppController()
    controller.show_login_screen()
    
    sys.exit(app.exec())