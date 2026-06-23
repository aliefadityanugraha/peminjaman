# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QStackedWidget, QFrame,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, 
    QFormLayout, QHeaderView
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, Signal
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QFont
from database import DatabaseConnection

class LoginScreen(QWidget):
    """
    Login screen widget that handles user input for credentials
    and notifies the main coordinator when login is requested.
    """
    # Define a custom signal that sends (username, password) when login is clicked
    login_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pf Spaces - Login")
        self.resize(400, 420)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        # Login Card container for styling
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)
        card.setLayout(card_layout)
        
        # Title
        title_label = QLabel("Pf Spaces")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1a73e8; border: none; font-weight: bold;")
        card_layout.addWidget(title_label)

        subtitle_label = QLabel("Equipment Borrowing Management")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #5f6368; border: none; margin-bottom: 10px;")
        card_layout.addWidget(subtitle_label)

        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-size: 14px;
                color: #202124;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: #ffffff;
            }
        """)
        card_layout.addWidget(self.username_input)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-size: 14px;
                color: #202124;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: #ffffff;
            }
        """)
        # Trigger login when Enter is pressed in password field
        self.password_input.returnPressed.connect(self.on_login_clicked)
        card_layout.addWidget(self.password_input)

        # Error message label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #d93025; font-size: 12px; border: none; font-weight: 500;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        card_layout.addWidget(self.error_label)

        # Login Button
        self.login_button = QPushButton("Log In")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #0b3c80;
            }
        """)
        self.login_button.clicked.connect(self.on_login_clicked)
        card_layout.addWidget(self.login_button)

        main_layout.addWidget(card)
        
        # Set overall background color for the screen
        self.setStyleSheet("background-color: #f1f3f4;")

    def on_login_clicked(self):
        """
        Retrieves credentials from input fields and emits the login_requested signal.
        """
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        self.error_label.setText("") # Clear previous errors
        self.login_requested.emit(username, password)

    def show_error(self, message):
        """
        Displays an error message on the screen.
        """
        self.error_label.setText(message)

    def clear_inputs(self):
        """
        Clears the username and password input fields.
        """
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setText("")


class EquipmentListView(QWidget):
    """
    Shows a table of all equipment items, loaded from the database.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Equipment Catalog")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; border: none;")
        header_layout.addWidget(title)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 6px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn, 0, Qt.AlignRight)
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Barang", "Kategori", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dadce0;
                gridline-color: #e0e0e0;
                font-size: 13px;
                background-color: #ffffff;
                color: #202124;
            }
            QTableWidget::item {
                color: #202124;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #202124;
                padding: 8px;
                border: 1px solid #dadce0;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.table)

        # Load initial data
        self.load_data()

    def load_data(self):
        """
        Queries the database for equipment items and updates the QTableWidget.
        Provides a mock data fallback if MySQL is offline.
        """
        db = DatabaseConnection()
        items = db.get_all_equipment()

        # Offline Mock Fallback
        if not items and db.get_connection() is None:
            items = [
                {"id": 1, "nama_barang": "Laptop ASUS ROG", "kategori": "Laptop", "stock": 5},
                {"id": 2, "nama_barang": "Projector Epson", "kategori": "Projector", "stock": 3},
                {"id": 3, "nama_barang": "Logitech Pointer", "kategori": "Accessories", "stock": 10},
            ]

        self.table.setRowCount(0)
        for row_idx, item in enumerate(items):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(item.get("nama_barang", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(item.get("kategori", ""))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(item.get("stock", ""))))


class AddEquipmentView(QWidget):
    """
    Form to add new equipment records to the database.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        title = QLabel("Add New Equipment")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 10px; border: none;")
        layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 8px;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #3c4043;
                border: none;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-size: 13px;
                color: #202124;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1a73e8;
                background-color: #ffffff;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(15)
        form_frame.setLayout(form_layout)

        # Fields
        self.name_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(["Laptop", "Projector", "Camera", "Accessories", "Others"])
        self.sn_input = QLineEdit()
        self.stock_input = QLineEdit()
        self.desc_input = QLineEdit()

        form_layout.addRow("Nama Barang:", self.name_input)
        form_layout.addRow("Kategori:", self.category_input)
        form_layout.addRow("Serial Number:", self.sn_input)
        form_layout.addRow("Stock:", self.stock_input)
        form_layout.addRow("Description:", self.desc_input)

        layout.addWidget(form_frame)

        # Save Button
        save_btn = QPushButton("Save Equipment")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                max-width: 200px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        save_btn.clicked.connect(self.on_save_clicked)
        layout.addWidget(save_btn, 0, Qt.AlignLeft)
        layout.addStretch()

    def on_save_clicked(self):
        """
        Saves the equipment details to the database.
        """
        nama = self.name_input.text().strip()
        kategori = self.category_input.currentText()
        sn = self.sn_input.text().strip()
        stock_text = self.stock_input.text().strip()
        desc = self.desc_input.text().strip()

        if not nama or not sn or not stock_text:
            QMessageBox.warning(self, "Validation Error", "Nama Barang, Serial Number, and Stock are required.")
            return

        try:
            stock = int(stock_text)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Stock must be a valid integer.")
            return

        db = DatabaseConnection()
        success = db.add_equipment(nama, kategori, sn, stock, desc)

        if success:
            QMessageBox.information(self, "Success", "Equipment saved successfully!")
            self.clear_fields()
        else:
            # Fallback for Offline Developer Demo
            if db.get_connection() is None:
                QMessageBox.information(
                    self, 
                    "Offline Mode (Demo)", 
                    f"Offline simulation successful!\nSaved:\nNama: {nama}\nSN: {sn}\nStock: {stock}"
                )
                self.clear_fields()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to add equipment to database.")

    def clear_fields(self):
        self.name_input.clear()
        self.category_input.setCurrentIndex(0)
        self.sn_input.clear()
        self.stock_input.clear()
        self.desc_input.clear()


class ConfirmReservationView(QWidget):
    """
    Shows pending reservation requests for approval.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Pending Reservation Approvals")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; border: none;")
        header_layout.addWidget(title)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 6px 15px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn, 0, Qt.AlignRight)
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Reservation ID", "User ID", "Start Date", "End Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dadce0;
                gridline-color: #e0e0e0;
                font-size: 13px;
                background-color: #ffffff;
                color: #202124;
            }
            QTableWidget::item {
                color: #202124;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #202124;
                padding: 8px;
                border: 1px solid #dadce0;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.table)

        # Load initial data
        self.load_data()

    def load_data(self):
        """
        Queries the database for pending reservations and updates QTableWidget.
        Provides a mock data fallback if MySQL is offline.
        """
        db = DatabaseConnection()
        reservations = db.get_pending_reservations()

        # Offline Mock Fallback
        if not reservations and db.get_connection() is None:
            reservations = [
                {"id": 101, "user_id": 2, "start_date": "2026-06-25", "end_date": "2026-06-28"},
                {"id": 102, "user_id": 3, "start_date": "2026-06-29", "end_date": "2026-06-30"},
            ]

        self.table.setRowCount(0)
        for row_idx, res in enumerate(reservations):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(res.get("id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(res.get("user_id", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(res.get("start_date", ""))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(res.get("end_date", ""))))


class AdminDashboardView(QWidget):
    """
    Main container for Admin features.
    Provides sub-navigation to switch between list, add, and pending views.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Top Nav Bar
        nav_bar = QFrame()
        nav_bar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #dadce0;
            }
            QPushButton {
                background-color: transparent;
                color: #5f6368;
                padding: 12px 20px;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 13px;
                font-weight: 500;
                border-radius: 0px;
            }
            QPushButton:hover {
                color: #1a73e8;
            }
            QPushButton:checked {
                color: #1a73e8;
                border-bottom: 3px solid #1a73e8;
                font-weight: bold;
            }
        """)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(20, 0, 20, 0)
        nav_layout.setSpacing(10)
        nav_bar.setLayout(nav_layout)

        # Nav Buttons
        self.btn_list = QPushButton("Equipment List")
        self.btn_list.setCheckable(True)
        self.btn_list.setChecked(True)
        self.btn_list.clicked.connect(lambda: self.switch_tab(0))
        nav_layout.addWidget(self.btn_list)

        self.btn_add = QPushButton("Add Equipment")
        self.btn_add.setCheckable(True)
        self.btn_add.clicked.connect(lambda: self.switch_tab(1))
        nav_layout.addWidget(self.btn_add)

        self.btn_pending = QPushButton("Pending Approvals")
        self.btn_pending.setCheckable(True)
        self.btn_pending.clicked.connect(lambda: self.switch_tab(2))
        nav_layout.addWidget(self.btn_pending)

        nav_layout.addStretch()
        layout.addWidget(nav_bar)

        # Sub-pages container (QStackedWidget)
        self.sub_stacked = QStackedWidget()
        self.sub_stacked.setStyleSheet("background-color: #ffffff;")
        
        self.view_list = EquipmentListView()
        self.view_add = AddEquipmentView()
        self.view_pending = ConfirmReservationView()

        self.sub_stacked.addWidget(self.view_list)
        self.sub_stacked.addWidget(self.view_add)
        self.sub_stacked.addWidget(self.view_pending)

        layout.addWidget(self.sub_stacked)

    def switch_tab(self, index):
        """
        Switches the visible child view and updates the navigation buttons checked states.
        """
        self.sub_stacked.setCurrentIndex(index)
        self.btn_list.setChecked(index == 0)
        self.btn_add.setChecked(index == 1)
        self.btn_pending.setChecked(index == 2)
        
        # Automatically refresh table data when switching to list or pending view
        if index == 0:
            self.view_list.load_data()
        elif index == 2:
            self.view_pending.load_data()


class MainWindow(QMainWindow):
    """
    Main Application Window acting as the shell of the application.
    Contains a QStackedWidget for future pages and a sidebar for navigation.
    """
    # Define custom logout signal
    logout_requested = Signal()

    def __init__(self, user=None):
        super().__init__()
        self.user = user  # User object containing info of authenticated user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pf Spaces - Equipment Borrowing")
        self.resize(950, 650)
        
        # Main widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # 1. Sidebar Frame
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #202124;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: #e8eaed;
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3c4043;
            }
            QPushButton:checked {
                background-color: #1a73e8;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(8)
        sidebar.setLayout(sidebar_layout)

        # App Logo/Title in Sidebar
        app_title = QLabel("Pf Spaces")
        app_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        app_title.setStyleSheet("color: #ffffff; padding: 10px 10px 15px 10px;")
        sidebar_layout.addWidget(app_title)

        # User profile summary in Sidebar
        user_name = self.user.username if self.user else "User"
        user_role = self.user.role if self.user else "Role"
        profile_label = QLabel(f"Logged in as:\n{user_name} ({user_role.upper()})")
        profile_label.setFont(QFont("Segoe UI", 9))
        profile_label.setWordWrap(True)
        profile_label.setStyleSheet("color: #9aa0a6; padding: 0 10px 20px 10px; line-height: 1.4;")
        sidebar_layout.addWidget(profile_label)

        # Divider line
        divider = QFrame()
        divider.setStyleSheet("background-color: #3c4043; max-height: 1px; margin-bottom: 10px;")
        sidebar_layout.addWidget(divider)

        # Navigation Buttons
        is_admin = (self.user and self.user.role == "admin")
        
        if is_admin:
            self.btn_admin_panel = QPushButton("Admin Panel")
            self.btn_admin_panel.setCheckable(True)
            self.btn_admin_panel.setChecked(True)
            self.btn_admin_panel.clicked.connect(lambda: self.switch_page(3))
            sidebar_layout.addWidget(self.btn_admin_panel)
        else:
            self.btn_dashboard = QPushButton("Dashboard")
            self.btn_dashboard.setCheckable(True)
            self.btn_dashboard.setChecked(True)
            self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
            sidebar_layout.addWidget(self.btn_dashboard)

            self.btn_equipment = QPushButton("Equipment List")
            self.btn_equipment.setCheckable(True)
            self.btn_equipment.clicked.connect(lambda: self.switch_page(1))
            sidebar_layout.addWidget(self.btn_equipment)

            self.btn_history = QPushButton("Borrowing History")
            self.btn_history.setCheckable(True)
            self.btn_history.clicked.connect(lambda: self.switch_page(2))
            sidebar_layout.addWidget(self.btn_history)

        sidebar_layout.addStretch()

        # Logout Button
        self.btn_logout = QPushButton("Log Out")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f28b82;
            }
            QPushButton:hover {
                background-color: #3b2222;
                color: #ffffff;
            }
        """)
        self.btn_logout.clicked.connect(self.on_logout_clicked)
        sidebar_layout.addWidget(self.btn_logout)

        main_layout.addWidget(sidebar)

        # 2. Content area Container
        self.content_container = QStackedWidget()
        self.content_container.setStyleSheet("background-color: #ffffff;")
        
        # Setup pages
        self.create_pages()
        main_layout.addWidget(self.content_container)

    def create_pages(self):
        """
        Creates simple placeholder views inside the QStackedWidget.
        """
        is_admin = (self.user and self.user.role == "admin")

        # Page 0: Dashboard
        self.page_dashboard = QWidget()
        layout_dash = QVBoxLayout()
        layout_dash.setContentsMargins(40, 45, 40, 45)
        
        lbl_dash_title = QLabel("Dashboard")
        lbl_dash_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_dash_title.setStyleSheet("color: #202124; margin-bottom: 10px;")
        
        lbl_dash_desc = QLabel(
            "Welcome to the Pf Spaces Equipment Borrowing Dashboard.\n\n"
            "This application allows users to check available equipment, place reservation requests, "
            "and manage equipment lists. The system is connected to a local MySQL database storing "
            "users, items, custom equipment specs, and active reservations."
        )
        lbl_dash_desc.setFont(QFont("Segoe UI", 11))
        lbl_dash_desc.setStyleSheet("color: #5f6368; line-height: 1.6;")
        lbl_dash_desc.setWordWrap(True)
        
        layout_dash.addWidget(lbl_dash_title)
        layout_dash.addWidget(lbl_dash_desc)
        layout_dash.addStretch()
        self.page_dashboard.setLayout(layout_dash)
        self.content_container.addWidget(self.page_dashboard)

        # Page 1: Equipment List
        self.page_equipment = EquipmentListView()
        self.content_container.addWidget(self.page_equipment)

        # Page 2: Borrowing History
        self.page_history = QWidget()
        layout_hist = QVBoxLayout()
        layout_hist.setContentsMargins(40, 45, 40, 45)
        
        lbl_hist_title = QLabel("Borrowing History")
        lbl_hist_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_hist_title.setStyleSheet("color: #202124; margin-bottom: 10px;")
        
        lbl_hist_desc = QLabel(
            "View historical and current equipment reservations, status updates, and administrative notes.\n\n"
            "(Borrowing transactions will be listed here in the next phase)."
        )
        lbl_hist_desc.setFont(QFont("Segoe UI", 11))
        lbl_hist_desc.setStyleSheet("color: #5f6368; line-height: 1.6;")
        lbl_hist_desc.setWordWrap(True)
        
        layout_hist.addWidget(lbl_hist_title)
        layout_hist.addWidget(lbl_hist_desc)
        layout_hist.addStretch()
        self.page_history.setLayout(layout_hist)
        self.content_container.addWidget(self.page_history)

        # Page 3: Admin Dashboard
        if is_admin:
            self.page_admin = AdminDashboardView()
            self.content_container.addWidget(self.page_admin)
            self.content_container.setCurrentIndex(3)

    def switch_page(self, index):
        """
        Switches the QStackedWidget visible page index and updates sidebar button highlights.
        """
        self.content_container.setCurrentIndex(index)
        
        # Update checked state for sidebar buttons
        if hasattr(self, 'btn_dashboard'):
            self.btn_dashboard.setChecked(index == 0)
        if hasattr(self, 'btn_equipment'):
            self.btn_equipment.setChecked(index == 1)
        if hasattr(self, 'btn_history'):
            self.btn_history.setChecked(index == 2)
        if hasattr(self, 'btn_admin_panel'):
            self.btn_admin_panel.setChecked(index == 3)

    def on_logout_clicked(self):
        """
        Emits the logout request signal to notify the main controller.
        """
        self.logout_requested.emit()
