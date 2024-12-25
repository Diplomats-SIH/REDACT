import os
import re
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QSlider, QRadioButton, 
    QButtonGroup, QMessageBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt

def redact_text(text, symbol="█"):
    """Redacts text with a given symbol."""
    return symbol * len(text)

def redact_line(line, redaction_scale, option):
    """Redacts sensitive information in a single line based on redaction scale."""
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}[A-Za-z]+\d{2}\b'
    time_pattern = r'\b\d{2}:\d{2}:\d{2}\b'
    relay_pattern = r'relay=.*?@.*? '

    patterns = [
        (25, ip_pattern),
        (50, date_pattern),
        (75, time_pattern),
        (100, relay_pattern)
    ]

    for threshold, pattern in patterns:
        if redaction_scale >= threshold:
            matches = re.finditer(pattern, line)
            for match in matches:
                redacted = redact_text(match.group()) if option.lower() != 'blur' else redact_text(match.group(), "-")
                line = line.replace(match.group(), redacted)

    return line

def redact_file(input_file, output_file, redaction_scale, option):
    """Handles file redaction for .txt, .csv, .xlsx, and .11 formats."""
    file_extension = input_file.split('.')[-1].lower()

    if file_extension == 'csv':
        df = pd.read_csv(input_file)
        redacted_df = df.apply(lambda row: row.apply(lambda x: redact_line(str(x), redaction_scale, option) if isinstance(x, str) else x), axis=1)
        redacted_df.to_csv(output_file, index=False)
    else:
        print(f"Unsupported file format: {file_extension}")
        return

    print(f"Redacted file saved as {output_file}")

class LogRedactorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Log Redactor - CSV File Redactor")
        self.setGeometry(100, 100, 800, 600)
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
        self.file_button = QPushButton("Choose CSV File")
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

        self.style_group.addButton(self.blur_button)
        self.style_group.addButton(self.blackout_button)
        style_layout.addWidget(self.blur_button)
        style_layout.addWidget(self.blackout_button)

        style_frame.setLayout(style_layout)
        layout.addWidget(style_frame)

        # Redact Button
        self.redact_button = QPushButton("Redact")
        self.redact_button.clicked.connect(self.redact_file)
        layout.addWidget(self.redact_button)

        # Download Button
        self.download_button = QPushButton("Download Redacted File")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_redacted_file)
        layout.addWidget(self.download_button)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def choose_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            self.input_file = file_name
            self.file_label.setText(file_name)

    def redact_file(self):
        if not hasattr(self, 'input_file'):
            QMessageBox.warning(self, "Error", "Please select a CSV file first.")
            return

        redaction_scale = self.slider.value()
        if self.blur_button.isChecked():
            option = 'blur'
        elif self.blackout_button.isChecked():
            option = 'blackout'
        else:
            QMessageBox.warning(self, "Error", "Please select a redaction style.")
            return

        output_file = self.input_file.split('.')[0] + '_redacted.csv'
        try:
            redact_file(self.input_file, output_file, redaction_scale, option)
            self.download_button.setEnabled(True)
            QMessageBox.information(self, "Success", f"Redaction completed! File saved as: {output_file}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def download_redacted_file(self):
        if hasattr(self, 'input_file'):
            output_file = self.input_file.split('.')[0] + '_redacted.csv'
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Redacted File", output_file, "CSV Files (*.csv)", options=options)
            if save_path:
                os.rename(output_file, save_path)
                QMessageBox.information(self, "Success", f"File saved successfully at {save_path}")

if __name__ == "__main__":
    app = QApplication([])
    window = LogRedactorApp()
    window.show()
    app.exec_()
