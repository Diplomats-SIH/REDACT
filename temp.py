import fitz  # PyMuPDF
import spacy
import os
import re

# Function to extract text from PDF and get block coordinates
def extract_text_and_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    blocks = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
        for block in page.get_text("dict")["blocks"]:
            if block['type'] == 0:  # Only text blocks
                for line in block["lines"]:
                    for span in line["spans"]:
                        blocks.append({
                            "text": span["text"],
                            "bbox": span["bbox"],  # Coordinates (x0, y0, x1, y1)
                            "page_num": page_num,  # Store page number for each block
                        })
    return text, blocks

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract sensitive data (including email and phone numbers)
def extract_sensitive_data(text):
    doc = nlp(text)
    sensitive_data = []

    # Extract named entities (PERSON, GPE, ORG, DATE, MONEY)
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'GPE', 'ORG', 'DATE', 'MONEY']:
            sensitive_data.append((ent.start, ent.end, ent.text, ent.label_))  # Store span of the sensitive data and label

    # Use regex to find email addresses and phone numbers
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    phone_pattern = r'\b(\+?[0-9]{1,3})?[-. ]?(\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4})\b'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    for email in emails:
        sensitive_data.append((0, 0, email, 'EMAIL'))  # Add email
    for phone in phones:
        sensitive_data.append((0, 0, phone[1], 'PHONE'))  # Add phone number

    return sensitive_data

# Function to redact sensitive data interactively
def redact_data_interactively(sensitive_data, pdf_path, blocks, redact_level):
    doc = fitz.open(pdf_path)
    
    # Determine which entities to redact based on the redact_level
    entities_to_redact = set()
    if redact_level >= 25:
        entities_to_redact.update(['EMAIL', 'PHONE'])
    if redact_level >= 50:
        entities_to_redact.update(['DATE'])
    if redact_level >= 75:
        entities_to_redact.update(['MONEY', 'ORG'])
    if redact_level == 100:
        entities_to_redact.update(['PERSON'])

    # Filter sensitive data based on the redact_level
    filtered_data = [data for data in sensitive_data if data[3] in entities_to_redact]
    
    # Ask user for blur or blackout decision
    action = input(f"Redacting {len(filtered_data)} pieces of sensitive data. Do you want to blur (b) or blackout (x) this data? (b/x): ").strip().lower()

    for start, end, sensitive_text, label in filtered_data:
        # Find the matching block for the sensitive text
        matching_block = next((block for block in blocks if sensitive_text in block["text"]), None)
        if matching_block:
            bbox = matching_block["bbox"]  # Bounding box (x0, y0, x1, y1)
            page_num = matching_block["page_num"]  # Get page number for this block
            page = doc.load_page(page_num)

            print(f"Redacting {sensitive_text} at bbox: {bbox}")  # Debugging the bbox

            if action == 'b':
                # Apply blur (you can implement blur using rectangles on the PDF page)
                redact_blur(page, bbox)
            elif action == 'x':
                # Apply blackout (just draw a black rectangle over the text)
                redact_blackout(page, bbox)

    # Handle file saving
    redacted_pdf_path = os.path.join(os.path.dirname(pdf_path), "redacted_" + os.path.basename(pdf_path))

    # Save the redacted PDF
    doc.save(redacted_pdf_path)
    print(f"Redacted PDF saved to {redacted_pdf_path}")
    return redacted_pdf_path

# Function to apply blackout to sensitive data
def redact_blackout(page, bbox):
    x0, y0, x1, y1 = bbox  # Coordinates of the text to blackout

    # Debugging: Print the bounding box
    print(f"Blackout bounding box: {bbox}")

    # Create a rectangle from the coordinates
    rect = fitz.Rect(x0, y0, x1, y1)
    
    # Ensure the rectangle is within the page dimensions
    page_width, page_height = page.rect.width, page.rect.height
    if x1 > page_width or y1 > page_height:
        x1 = min(x1, page_width)
        y1 = min(y1, page_height)

    # Draw the black rectangle (full fill)
    page.draw_rect(rect, color=(0, 0, 0), fill=True)
    print(f"Applied blackout at: {x0}, {y0}, {x1}, {y1}")

# Function to apply blur (using transparency) to sensitive data
def redact_blur(page, bbox):
    x0, y0, x1, y1 = bbox  # Coordinates of the text to blur
    rect = fitz.Rect(x0, y0, x1, y1)

    # Debugging: Print the bounding box
    print(f"Blur bounding box: {bbox}")

    # Apply a semi-transparent gray overlay (to simulate blur)
    blur_color = (169/255, 169/255, 169/255, 0.5)  # Gray with 50% transparency
    page.draw_rect(rect, color=blur_color, fill=True)
    print(f"Applied blur at: {x0}, {y0}, {x1}, {y1}")

# Main function to process the PDF
def main(pdf_path, redact_level):
    pdf_text, blocks = extract_text_and_coordinates(pdf_path)
    sensitive_data = extract_sensitive_data(pdf_text)

    if not sensitive_data:
        print("No sensitive data found.")
        return

    # Redact sensitive data interactively
    redacted_pdf = redact_data_interactively(sensitive_data, pdf_path, blocks, redact_level)
    return redacted_pdf

# Run the script
if __name__ == "__main__":
    pdf_path = "C:/Users/Rajesh/Documents/chetan cv.pdf"  # The PDF file to process
    redact_level = int(input("Enter the redaction level (25, 50, 75, 100): "))  # Ask user for redaction level
    main(pdf_path, redact_level)
