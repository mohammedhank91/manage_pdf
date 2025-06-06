import sys
import os
import PyPDF2

def extract_page(input_pdf, output_pdf, page_number):
    try:
        # Open the input PDF
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if the page number is valid
            if page_number < 1 or page_number > len(pdf_reader.pages):
                print(f"Error: Page number {page_number} is out of range. The PDF has {len(pdf_reader.pages)} pages.")
                return False
            
            # Create a PDF writer
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add the requested page (convert from 1-based to 0-based indexing)
            pdf_writer.add_page(pdf_reader.pages[page_number - 1])
            
            # Write to the output file
            with open(output_pdf, 'wb') as output:
                pdf_writer.write(output)
                
            print(f"Successfully extracted page {page_number} to {output_pdf}")
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def count_pages(input_pdf):
    try:
        # Open the input PDF
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        print(f"Error counting pages: {str(e)}")
        return 0

def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        import logging
        logging.error("Pytest encountered errors.")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf_splitter.py input.pdf output.pdf [page_number]")
        print("If page_number is not provided, page 1 will be extracted.")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    page_number = 1  # Default to page 1
    
    if len(sys.argv) >= 4:
        try:
            page_number = int(sys.argv[3])
        except ValueError:
            print("Error: Page number must be an integer.")
            sys.exit(1)
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input file '{input_pdf}' does not exist.")
        sys.exit(1)
    
    # Count total pages
    total_pages = count_pages(input_pdf)
    print(f"PDF has {total_pages} pages.")
    
    # Extract the page
    if extract_page(input_pdf, output_pdf, page_number):
        print("Extraction completed successfully.")
    else:
        print("Failed to extract page.")
        sys.exit(1) 

    run_pytest()
