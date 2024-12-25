import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
                             QLineEdit, QPushButton, QStackedWidget)
from PyQt5.QtCore import Qt

class RedactApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RE-DACT")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
                color: white;
                font-family: Arial;
            }
            QLabel {
                font-size: 16px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border: 1px solid #444;
                border-radius: 5px;
                background-color: #2E2E2E;
                color: white;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                background-color: #1E90FF;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1679c4;
            }
        """)

        # Central widget and stacked layout for multiple pages
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        # Initialize pages
        self.login_page = self.create_login_page()
        self.registration_page = self.create_registration_page()

        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.registration_page)

        self.pages.setCurrentWidget(self.login_page)  # Show login page by default

    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Login to RE-DACT")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_input)

        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        layout.addWidget(self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        switch_to_register = QPushButton("Don't have an account? Register here")
        switch_to_register.setStyleSheet("background-color: transparent; color: #1E90FF; border: none;")
        switch_to_register.clicked.connect(lambda: self.pages.setCurrentWidget(self.registration_page))
        layout.addWidget(switch_to_register)

        page.setLayout(layout)
        return page

    def create_registration_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Register for RE-DACT")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(username_label)

        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("Choose a username")
        layout.addWidget(self.reg_username_input)

        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(password_label)

        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setPlaceholderText("Choose a password")
        layout.addWidget(self.reg_password_input)

        confirm_password_label = QLabel("Confirm Password")
        confirm_password_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(confirm_password_label)

        self.reg_confirm_password_input = QLineEdit()
        self.reg_confirm_password_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_password_input.setPlaceholderText("Re-enter your password")
        layout.addWidget(self.reg_confirm_password_input)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.handle_registration)
        layout.addWidget(register_button)

        switch_to_login = QPushButton("Already have an account? Login here")
        switch_to_login.setStyleSheet("background-color: transparent; color: #1E90FF; border: none;")
        switch_to_login.clicked.connect(lambda: self.pages.setCurrentWidget(self.login_page))
        layout.addWidget(switch_to_login)

        page.setLayout(layout)
        return page

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Add actual login logic here (e.g., database query)
        if username == "admin" and password == "password":
            self.show_message("Login Successful!")
        else:
            self.show_message("Invalid username or password.")

    def handle_registration(self):
        username = self.reg_username_input.text()
        password = self.reg_password_input.text()
        confirm_password = self.reg_confirm_password_input.text()

        if password != confirm_password:
            self.show_message("Passwords do not match.")
            return

        # Add actual registration logic here (e.g., save to database)
        self.show_message("Registration Successful! Please login.")
        self.pages.setCurrentWidget(self.login_page)

    def show_message(self, message):
        # Temporary popup-like message display
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 18px; color: #32CD32; margin-top: 20px;")
        self.centralWidget().layout().addWidget(message_label)
        
        # Remove the message after a short delay
        QApplication.processEvents()
        QTimer.singleShot(3000, lambda: message_label.deleteLater())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedactApp()
    window.show()
    sys.exit(app.exec_())