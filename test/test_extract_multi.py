import os
import sys
import PyPDF2

def parse_page_range(range_str, max_pages):
    """
    Parse a page range string into a list of page numbers.
    
    Supports formats:
    - Single page: "5"
    - Page range: "1-5"
    - Mixed: "1,3,5-8,10"
    
    Args:
        range_str: String containing page ranges
        max_pages: Maximum number of pages in the PDF
        
    Returns:
        List of page numbers (1-based indexing)
    """
    pages = []
    
    # Handle empty input
    if not range_str.strip():
        return pages
    
    # Split by comma
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        # Skip empty parts
        if not part:
            continue
            
        # Handle range (e.g., "1-5")
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                
                # Validate range
                if start < 1:
                    print(f"Warning: Page number {start} is less than 1, using 1 instead.")
                    start = 1
                    
                if end > max_pages:
                    print(f"Warning: Page number {end} exceeds maximum of {max_pages}, using {max_pages} instead.")
                    end = max_pages
                
                # Add all pages in the range
                for page in range(start, end + 1):
                    if page not in pages:
                        pages.append(page)
            except ValueError:
                print(f"Warning: Invalid page range '{part}', skipping.")
                
        # Handle single page
        else:
            try:
                page = int(part)
                
                # Validate page number
                if page < 1:
                    print(f"Warning: Page number {page} is less than 1, using 1 instead.")
                    page = 1
                    
                if page > max_pages:
                    print(f"Warning: Page number {page} exceeds maximum of {max_pages}, using {max_pages} instead.")
                    page = max_pages
                
                if page not in pages:
                    pages.append(page)
            except ValueError:
                print(f"Warning: Invalid page number '{part}', skipping.")
    
    return sorted(pages)

def extract_pages(input_pdf, output_pdf, page_range):
    """
    Extract specified pages from a PDF file
    
    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to output PDF file
        page_range: String representation of pages to extract (e.g., "1,3,5-8,10")
        
    Returns:
        (success, message) tuple
    """
    try:
        # Open the input PDF
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Parse page range
            pages_to_extract = parse_page_range(page_range, total_pages)
            
            if not pages_to_extract:
                return False, "No valid pages specified for extraction."
            
            print(f"PDF has {total_pages} total pages")
            print(f"Extracting pages: {', '.join(map(str, pages_to_extract))}")
            
            # Create a PDF writer
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add each specified page
            for page_num in pages_to_extract:
                # Convert from 1-based to 0-based indexing
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])
            
            # Write to the output file
            with open(output_pdf, 'wb') as output:
                pdf_writer.write(output)
                
            return True, f"Successfully extracted {len(pages_to_extract)} pages to {output_pdf}"
                
    except Exception as e:
        return False, f"Error: {str(e)}"

def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        import logging
        logging.error("Pytest encountered errors.")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_extract_multi.py input.pdf output.pdf \"page_range\"")
        print("Example page ranges:")
        print("  Single page: \"5\"")
        print("  Page range: \"1-5\"")
        print("  Mixed: \"1,3,5-8,10\"")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    page_range = sys.argv[3]
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input file '{input_pdf}' does not exist.")
        sys.exit(1)
    
    # Extract the pages
    success, message = extract_pages(input_pdf, output_pdf, page_range)
    print(message)
    
    if success:
        print("Extraction completed successfully.")
        sys.exit(0)
    else:
        print("Failed to extract pages.")
        sys.exit(1) 

    run_pytest()
