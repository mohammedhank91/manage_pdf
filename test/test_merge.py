import os
import sys
import PyPDF2

def merge_pdfs(input_pdfs, output_pdf, add_bookmarks=True):
    """
    Merge multiple PDF files into one output PDF using PyPDF2
    
    Args:
        input_pdfs: List of input PDF file paths
        output_pdf: Output PDF file path
        add_bookmarks: Whether to add bookmarks for each merged PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a PDF merger object
        pdf_merger = PyPDF2.PdfMerger()
        
        # Add each PDF to the merger
        for i, pdf in enumerate(input_pdfs):
            # Ensure the file exists
            if not os.path.exists(pdf):
                print(f"Error: Input file '{pdf}' does not exist.")
                return False
                
            # Add PDF with a bookmark/outline if requested
            if add_bookmarks:
                bookmark_name = os.path.basename(pdf)  # Use filename as bookmark
                pdf_merger.append(pdf, outline_item=bookmark_name)
            else:
                pdf_merger.append(pdf)
                
            # Print progress
            print(f"Added {i+1}/{len(input_pdfs)}: {pdf}")
        
        # Write the merged PDF to output file
        with open(output_pdf, 'wb') as f:
            pdf_merger.write(f)
            
        print(f"Successfully merged {len(input_pdfs)} PDFs into {output_pdf}")
        return True
            
    except Exception as e:
        print(f"Error during merge: {str(e)}")
        return False

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
        print("Usage: python test_merge.py output.pdf input1.pdf input2.pdf [input3.pdf ...]")
        sys.exit(1)
    
    output_pdf = sys.argv[1]
    input_pdfs = sys.argv[2:]
    
    if len(input_pdfs) < 2:
        print("Error: At least two input PDFs are required for merging.")
        sys.exit(1)
    
    # Merge the PDFs
    if merge_pdfs(input_pdfs, output_pdf):
        print("Merge completed successfully.")
    else:
        print("Failed to merge PDFs.")
        sys.exit(1) 

    run_pytest()
