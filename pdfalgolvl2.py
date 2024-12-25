import sys
import os
import fitz  # PyMuPDF
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFileDialog, QLineEdit

def get_sensitive_data(lines):
    """
    Function to get all lines containing sensitive data such as emails, phone numbers, and dates.
    """
    EMAIL_REG = r"([\w\.\d]+@[\w\d]+\.[\w\d]+)"
    PHONE_REG = r"(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}"
    DATE_REG = r"(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[\s/]\d{2}[\s/]\d{4}|" \
               r"\d{2}\s[A-Za-z]+\s\d{4})"

    for line in lines:
        if re.search(EMAIL_REG, line, re.IGNORECASE):
            search = re.search(EMAIL_REG, line, re.IGNORECASE)
            if search:
                yield "EMAIL", search.group(1)

        if re.search(PHONE_REG, line):
            search = re.search(PHONE_REG, line)
            if search:
                yield "PHONE", search.group(0)

        if re.search(DATE_REG, line):
            search = re.search(DATE_REG, line)
            if search:
                yield "DATE", search.group(0)


def redact_pdf(path, mode='blackout'):
    """
    Redact sensitive data in the PDF.
    """
    if not os.path.exists(path):
        print(f"Error: The file '{path}' does not exist.")
        return

    doc = fitz.open(path)
    for page_number, page in enumerate(doc):
        text = page.get_text("text")
        sensitive_data = get_sensitive_data(text.split('\n'))
        for label, data in sensitive_data:
            areas = page.search_for(data)
            for area in areas:
                if mode == 'blur':
                    page.add_redact_annot(area, fill=(0, 0, 0), text='*' * len(data))
                else:
                    page.add_redact_annot(area, fill=(0, 0, 0))
        page.apply_redactions()

    output_path = 'redacted.pdf'
    doc.save(output_path)
    print(f"Successfully redacted. The file has been saved as {output_path}")


class RedactionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PDF Redaction Tool')
        self.setGeometry(100, 100, 500, 300)

        self.main_layout = QVBoxLayout()

        # File path input
        self.file_label = QLabel("Select the PDF file to redact:")
        self.file_label.setStyleSheet("font-size: 14px; color: #333;")

        self.file_input = QLineEdit(self)
        self.file_input.setPlaceholderText("No file selected")
        self.file_input.setStyleSheet("font-size: 12px; padding: 5px;")

        self.browse_button = QPushButton('Browse')
        self.browse_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 12px; padding: 5px;")
        self.browse_button.clicked.connect(self.browse_file)

        # Redaction mode selection
        self.mode_label = QLabel("Select the redaction mode:")
        self.mode_label.setStyleSheet("font-size: 14px; color: #333;")

        self.mode_combobox = QComboBox(self)
        self.mode_combobox.addItems(['blackout', 'blur'])
        self.mode_combobox.setStyleSheet("font-size: 12px; padding: 5px;")

        # Redact button
        self.redact_button = QPushButton('Redact')
        self.redact_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;")
        self.redact_button.clicked.connect(self.perform_redaction)

        # Exit button
        self.exit_button = QPushButton('Exit')
        self.exit_button.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; padding: 10px;")
        self.exit_button.clicked.connect(self.close)

        # Layout organization
        self.main_layout.addWidget(self.file_label)
        self.main_layout.addWidget(self.file_input)
        self.main_layout.addWidget(self.browse_button)
        self.main_layout.addWidget(self.mode_label)
        self.main_layout.addWidget(self.mode_combobox)
        self.main_layout.addWidget(self.redact_button)
        self.main_layout.addWidget(self.exit_button)

        self.setLayout(self.main_layout)

    def browse_file(self):
        # Open file dialog to select a PDF file
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select PDF File', '', 'PDF Files (*.pdf)')
        if file_path:
            self.file_input.setText(file_path)

    def perform_redaction(self):
        file_path = self.file_input.text().strip()
        mode = self.mode_combobox.currentText()

        if not os.path.exists(file_path):
            print("Error: The file does not exist.")
            return

        # Perform redaction
        print(f"Redacting the file {file_path} with mode: {mode}")
        redact_pdf(file_path, mode)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RedactionApp()
    window.show()
    sys.exit(app.exec_())
