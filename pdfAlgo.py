from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QSlider, QRadioButton, 
    QButtonGroup, QMessageBox, QHBoxLayout, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import sys
import os

from pdf_redacter import PDFRedactor  # Assuming your `PDFRedactor` code is saved in a file named pdf_redacter.py

class RedactApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RE-DACT")
        self.setGeometry(100, 100, 800, 600)
        self.pdf_path = None
        self.redacted_pdf_path = None
        self.redactor = PDFRedactor()

        self.setStyleSheet("""
            QMainWindow { background-color: #2C2F33; }
            QLabel { color: white; font-size: 16px; }
            QPushButton {
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                background-color: #7289DA;
                color: white;
                border: none;
            }
            QPushButton:hover { background-color: #5A73BF; }
            QSlider::groove:horizontal {
                height: 8px; background: #444; border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #7289DA; width: 18px; margin: -4px 0; border-radius: 9px;
            }
            QRadioButton { color: white; font-size: 16px; }
            QFrame {
                border: 1px solid #444;
                border-radius: 10px;
                background-color: #23272A;
                padding: 10px;
            }
        """)

        main_widget = QWidget()
        layout = QVBoxLayout()

        # File Selection Frame
        file_frame = QFrame()
        file_layout = QVBoxLayout()
        self.file_button = QPushButton("Choose PDF File")
        self.file_button.setIcon(QIcon("file-icon.png"))  # Replace with the path to an icon file
        self.file_button.clicked.connect(self.choose_file)
        file_layout.addWidget(self.file_button)

        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        file_frame.setLayout(file_layout)
        layout.addWidget(file_frame)

        # Redaction Level Frame
        level_frame = QFrame()
        level_layout = QVBoxLayout()

        self.level_label = QLabel("Redaction Level")
        level_layout.addWidget(self.level_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        level_layout.addWidget(self.slider)

        level_frame.setLayout(level_layout)
        layout.addWidget(level_frame)

        # Redaction Style Frame
        style_frame = QFrame()
        style_layout = QVBoxLayout()

        self.style_label = QLabel("Redaction Style")
        style_layout.addWidget(self.style_label)

        self.style_group = QButtonGroup(self)
        self.blur_button = QRadioButton("Blur Out")
        self.blackout_button = QRadioButton("Black Out")
        self.synthetic_button = QRadioButton("Synthetic Data Replacement")

        self.style_group.addButton(self.blur_button)
        self.style_group.addButton(self.blackout_button)
        self.style_group.addButton(self.synthetic_button)
        style_layout.addWidget(self.blur_button)
        style_layout.addWidget(self.blackout_button)
        style_layout.addWidget(self.synthetic_button)

        style_frame.setLayout(style_layout)
        layout.addWidget(style_frame)

        # Redact Button
        self.redact_button = QPushButton("Redact")
        self.redact_button.clicked.connect(self.redact_pdf)
        layout.addWidget(self.redact_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Download Button
        self.download_button = QPushButton("Download Redacted File")
        self.download_button.setIcon(QIcon("download-icon.png"))  # Replace with the path to an icon file
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_redacted_file)
        layout.addWidget(self.download_button)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def choose_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose PDF File", "", "PDF Files (*.pdf)", options=options)
        if file_name:
            self.pdf_path = file_name
            self.file_label.setText(file_name)

    def redact_pdf(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "Error", "Please select a PDF file first.")
            return

        redact_level = self.slider.value()
        if self.blur_button.isChecked():
            action = 'b'
        elif self.blackout_button.isChecked():
            action = 'x'
        elif self.synthetic_button.isChecked():
            action = 's'
        else:
            QMessageBox.warning(self, "Error", "Please select a redaction style.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(30)  # Simulating progress

        try:
            self.redacted_pdf_path = self.redactor.process_pdf(self.pdf_path, redact_level, action)
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", "PDF redacted successfully.")
            self.download_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Redaction failed: {e}")
        finally:
            self.progress_bar.setVisible(False)

    def download_redacted_file(self):
        if not self.redacted_pdf_path:
            QMessageBox.warning(self, "Error", "No redacted file to download.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Redacted PDF", "", "PDF Files (*.pdf)")
        if save_path:
            os.rename(self.redacted_pdf_path, save_path)
            QMessageBox.information(self, "Success", "Redacted file downloaded successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedactApp()
    window.show()
    sys.exit(app.exec_())
