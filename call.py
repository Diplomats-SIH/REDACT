import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
                             QPushButton, QFileDialog, QHBoxLayout, QFrame, QComboBox, QDialog, QLineEdit)
from PyQt5.QtCore import Qt
import subprocess


class LoginPage(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(300, 200, 400, 200)

        layout = QVBoxLayout()

        # Username input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter Username")
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        # Simple username/password check (you can replace this with real authentication)
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "user" and password == "password":  # Dummy check
            self.accept()  # Close dialog and return success
        else:
            self.reject()  # Reject and stay on login dialog

class RedactApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RE-DACT")
        self.setGeometry(100, 100, 1000, 600)  # Larger main window size
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
            QPushButton#chooseFileButton {
                background-color: #444;
                color: white;
            }
            QPushButton#chooseFileButton:hover {
                background-color: #555;
            }
            QRadioButton {
                font-size: 16px;
                color: white;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                background: #444;
                margin: 0px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #1E90FF;
                border: 1px solid #1E90FF;
                width: 18px;
                margin: -4px 0;
                border-radius: 9px;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Sidebar - Smaller width
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #1E1E1E; border-right: 1px solid #444;")
        sidebar_layout = QVBoxLayout()

        sidebar_label = QLabel("RE-DACT")
        sidebar_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E90FF; margin-bottom: 20px;")
        sidebar_layout.addWidget(sidebar_label)

        sidebar_buttons = ["Home", "Settings", "Help"]
        for button_text in sidebar_buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("""
                font-size: 16px;
                padding: 10px;
                background-color: #1E1E1E;
                color: white;
                border: none;
                text-align: left;
                border-bottom: 1px solid #444;
            """)
            sidebar_layout.addWidget(button)

        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            background-color: #1E90FF;
            color: white;
            border: none;
            border-radius: 5px;
            margin-top: 20px;
        """)
        sidebar_layout.addWidget(login_button)

        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar, 1)

        # Main content - Expanded area
        self.content = QWidget()  # This will change dynamically
        self.content_layout = QVBoxLayout()

        welcome_label = QLabel("Welcome to RE-DACT")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 20px;")
        self.content_layout.addWidget(welcome_label)

        subtitle_label = QLabel("Securely redact sensitive data with ease.")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; margin-bottom: 20px;")
        self.content_layout.addWidget(subtitle_label)

        # File type selection
        file_type_label = QLabel("Select File Type")
        file_type_label.setStyleSheet("font-size: 18px; margin-top: 20px;")
        self.content_layout.addWidget(file_type_label)

        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["PDF", "Word", "PPT","Log File", "PowerPoint", "Image", "Video"])
        self.file_type_combo.setStyleSheet("font-size: 16px;")
        self.content_layout.addWidget(self.file_type_combo)

        # Redaction button
        redaction_button = QPushButton("Redact")
        redaction_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background-color: #1E90FF;
            color: white;
            border: none;
            border-radius: 5px;
            margin-top: 20px;
        """)
        self.content_layout.addWidget(redaction_button)

        self.content.setLayout(self.content_layout)
        main_layout.addWidget(self.content, 4)  # Give more space to the main content area

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect signals
        login_button.clicked.connect(self.show_login_page)  # Connect to the login page
        redaction_button.clicked.connect(self.redact)

    def show_login_page(self):
        login_page = LoginPage()  # Create the login page instance
        if login_page.exec_() == QDialog.Accepted:  # If login is successful
            self.show_main_content()  # Show the main content

    def show_main_content(self):
        # This method will switch to the main content once logged in
        self.content.setVisible(True)
        print("Main content shown")

    def redact(self):
        selected_file_type = self.file_type_combo.currentText()
        if selected_file_type == "PDF":
            self.pdf_redaction()
        elif selected_file_type == "Word":
            self.doc_redaction()
        elif selected_file_type == "PPT":
            self.ppt_redaction()
        elif selected_file_type == "Log File":
            self.log_redaction()

    def pdf_redaction(self):
        # Change the content of the current window to show processing
        
        try:
            result = subprocess.run(["python", "pdfAlgo.py"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            self.change_content_to_result("Error during PDF Redaction.")
    def doc_redaction(self):
        # Change the content of the current window to show processing
        
        try:
            result = subprocess.run(["python", "docalgo.py"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            self.change_content_to_result("Error during PDF Redaction.")
    def ppt_redaction(self):
        # Change the content of the current window to show processing
        
        try:
            result = subprocess.run(["python", "pptalgo.py"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            self.change_content_to_result("Error during PDF Redaction.")
    def log_redaction(self):
        # Change the content of the current window to show processing
        
        try:
            result = subprocess.run(["python", "logalgo.py"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            self.change_content_to_result("Error during PDF Redaction.")

    # Other redaction methods go here...

    def change_content_to_processing(self, message):
        self.clear_content()
        processing_label = QLabel(message)
        processing_label.setAlignment(Qt.AlignCenter)
        processing_label.setStyleSheet("font-size: 20px; color: #FFA500; margin-top: 100px;")
        self.content_layout.addWidget(processing_label)
        self.content.setLayout(self.content_layout)

    def change_content_to_result(self, message):
        self.clear_content()
        result_label = QLabel(message)
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setStyleSheet("font-size: 20px; color: #32CD32; margin-top: 100px;")
        self.content_layout.addWidget(result_label)
        self.content.setLayout(self.content_layout)

    def clear_content(self):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedactApp()
    window.show()
    sys.exit(app.exec_())
