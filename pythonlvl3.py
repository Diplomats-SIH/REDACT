import fitz  # PyMuPDF
import re
import os


def get_sensitive_data(lines):
    """
    Function to dynamically extract sensitive data including specific parts of names (e.g., middle names),
    addresses, emails, phone numbers, and dates.

    Args:
        lines (list): List of text lines from the PDF.
    """
    EMAIL_REG = r"([\w\.\d]+@[\w\d]+\.[\w\d]+)"
    PHONE_REG = r"(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}"
    DATE_REG = r"(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[\s/]\d{2}[\s/]\d{4}|" \
               r"\d{2}\s[A-Za-z]+\s\d{4})"  # Formats: dd-mm-yyyy, yyyy-mm-dd, dd/mm/yyyy, dd Month yyyy
    ADDRESS_REG = r"(Address\s*[:\-]\s*[A-Za-z0-9\s,]+)"  # Pattern for addresses
    NAME_REG = r"Name\s*[:\-]\s*(\w+\s\w+\s\w+)"  # Pattern to detect full names like "Name: Rajesh Bhgvan Khavane"

    for line in lines:
        # Check for email
        if re.search(EMAIL_REG, line, re.IGNORECASE):
            search = re.search(EMAIL_REG, line, re.IGNORECASE)
            if search:
                yield "EMAIL", search.group(1)

        # Check for phone number
        if re.search(PHONE_REG, line):
            search = re.search(PHONE_REG, line)
            if search:
                yield "PHONE", search.group(0)

        # Check for date
        if re.search(DATE_REG, line):
            search = re.search(DATE_REG, line)
            if search:
                yield "DATE", search.group(0)

        # Check for address
        if re.search(ADDRESS_REG, line, re.IGNORECASE):
            search = re.search(ADDRESS_REG, line, re.IGNORECASE)
            if search:
                yield "ADDRESS", search.group(0)

        # Check for names with middle name redaction
        if re.search(NAME_REG, line, re.IGNORECASE):
            search = re.search(NAME_REG, line, re.IGNORECASE)
            if search:
                full_name = search.group(1)
                parts = full_name.split()
                if len(parts) == 3:  # Assuming format "First Middle Last"
                    middle_name = parts[1]
                    yield "MIDDLE_NAME", middle_name


def redact_pdf(path, mode='blackout'):
    """
    Redact sensitive data in the PDF, including specific middle names, addresses, emails, phone numbers, and dates.

    Args:
        path (str): Path to the PDF file.
        mode (str): Redaction mode, either 'blur' or 'blackout'.
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

    output_path = 'redacted1.pdf'
    doc.save(output_path)
    print(f"Successfully redacted. The file has been saved as {output_path}")


# Driver code for testing
if __name__ == "__main__":
    path = input("Enter the path of the PDF file: ").strip()
    mode = input("Do you want to blur or blackout the sensitive data? (Type 'blur' or 'blackout'): ").strip().lower()

    if mode not in ['blur', 'blackout']:
        print("Invalid choice. Please type 'blur' or 'blackout'.")
    else:
        redact_pdf(path, mode)
