import PyPDF2
import os

def create_simple_pdf(filename, text):
    """Create a simple PDF file with the given text content"""
    # Create a new PDF file
    pdf_writer = PyPDF2.PdfWriter()
    
    # Create a new page
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from io import BytesIO
    
    # Create a BytesIO object to hold the PDF content
    packet = BytesIO()
    
    # Create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Helvetica', 14)
    
    # Add text to the PDF
    can.drawString(100, 400, text)
    can.save()
    
    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    
    # Create a new PDF with PyPDF2
    new_pdf = PyPDF2.PdfReader(packet)
    
    # Add page to the PDF
    pdf_writer.add_page(new_pdf.pages[0])
    
    # Save the new PDF to a file
    with open(filename, 'wb') as f:
        pdf_writer.write(f)
    
    print(f"Created PDF: {filename}")

# Create test PDFs
if __name__ == "__main__":
    os.makedirs("test_pdfs", exist_ok=True)
    
    create_simple_pdf("test_pdfs/test1.pdf", "This is test PDF 1")
    create_simple_pdf("test_pdfs/test2.pdf", "This is test PDF 2")
    create_simple_pdf("test_pdfs/test3.pdf", "This is test PDF 3")
    
    print("Test PDFs created successfully in test_pdfs directory.") 