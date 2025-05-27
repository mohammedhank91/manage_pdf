import os
import logging
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication
import tempfile

def extract_pages(self):
    """Extract pages from the PDF using PyPDF2 with support for complex page ranges"""
    pdf_file = self.split_pdf_path.text()
    page_range = self.page_range_input.text().strip()
    
    if not pdf_file or pdf_file == "No PDF selected":
        QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
        return
    
    if not page_range:
        QMessageBox.warning(self, "Warning", "Please specify the page range to extract.")
        return
    
    # Choose save path
    output_file, _ = QFileDialog.getSaveFileName(
        self, "Save Extracted Pages As", "", "PDF Files (*.pdf)"
    )
    
    if not output_file:
        return
        
    try:
        import PyPDF2
        
        self.status_label.setText(f"Extracting pages {page_range}...")
        self.progress_bar.setValue(10)
        
        # Parse page range and extract pages
        success, message = self.extract_pages_with_pypdf2(pdf_file, output_file, page_range)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Successfully extracted pages {page_range}")
            QMessageBox.information(self, "Success", f"Successfully extracted pages to {output_file}")
        else:
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Error", message)
            
    except Exception as e:
        logging.error(f"Error in page extraction: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error extracting pages: {str(e)}")
        self.progress_bar.setValue(0)
        
def parse_page_range(self, range_str, max_pages):
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
                    self.status_label.setText(f"Warning: Page number {start} is less than 1, using 1 instead.")
                    start = 1
                    
                if end > max_pages:
                    self.status_label.setText(f"Warning: Page number {end} exceeds maximum of {max_pages}, using {max_pages} instead.")
                    end = max_pages
                
                # Add all pages in the range
                for page in range(start, end + 1):
                    if page not in pages:
                        pages.append(page)
            except ValueError:
                QMessageBox.warning(self, "Invalid Range", f"Invalid page range '{part}', skipping.")
                
        # Handle single page
        else:
            try:
                page = int(part)
                
                # Validate page number
                if page < 1:
                    self.status_label.setText(f"Warning: Page number {page} is less than 1, using 1 instead.")
                    page = 1
                    
                if page > max_pages:
                    self.status_label.setText(f"Warning: Page number {page} exceeds maximum of {max_pages}, using {max_pages} instead.")
                    page = max_pages
                
                if page not in pages:
                    pages.append(page)
            except ValueError:
                QMessageBox.warning(self, "Invalid Page", f"Invalid page number '{part}', skipping.")
    
    return sorted(pages)

def extract_pages_with_pypdf2(self, input_pdf, output_pdf, page_range):
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
        # Import PyPDF2 here to ensure it's available
        import PyPDF2
        
        # Open the input PDF
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Parse page range
            pages_to_extract = self.parse_page_range(page_range, total_pages)
            
            if not pages_to_extract:
                return False, "No valid pages specified for extraction."
            
            self.status_label.setText(f"PDF has {total_pages} total pages. Extracting {len(pages_to_extract)} pages...")
            
            # Update progress bar
            self.progress_bar.setValue(20)
            QApplication.processEvents()  # Keep UI responsive
            
            # Create a PDF writer
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add each specified page
            for i, page_num in enumerate(pages_to_extract):
                # Convert from 1-based to 0-based indexing
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])
                
                # Update progress (from 20% to 80%)
                progress = 20 + int(60 * (i + 1) / len(pages_to_extract))
                self.progress_bar.setValue(progress)
                QApplication.processEvents()  # Keep UI responsive
            
            # Write to the output file
            with open(output_pdf, 'wb') as output:
                pdf_writer.write(output)
            
            # Final progress update
            self.progress_bar.setValue(100)
                
            return True, f"Successfully extracted {len(pages_to_extract)} pages to {output_pdf}"
                
    except Exception as e:
        return False, f"Error: {str(e)}"

def select_pdf_to_split(self):
    """Select a PDF file to split"""
    pdf_file, _ = QFileDialog.getOpenFileName(
        self,
        "Select PDF to Split",
        "",
        "PDF Files (*.pdf)"
    )
    
    if pdf_file and os.path.exists(pdf_file):
        self.split_pdf_path.setText(pdf_file)
        self.btn_extract_pages.setEnabled(True)
        
        # Get file size information
        file_size = os.path.getsize(pdf_file) / 1024  # KB
        if file_size > 1024:
            file_size = file_size / 1024  # MB
            size_str = f"{file_size:.2f} MB"
        else:
            size_str = f"{file_size:.2f} KB"
        
        # Try to get page count using our improved method
        try:
            page_count = self.count_pages(pdf_file)
            self.split_pdf_info.setText(f"PDF Information: {os.path.basename(pdf_file)}\nPages: {page_count}\nSize: {size_str}")
        except Exception as e:
            logging.error(f"Failed to count pages: {str(e)}")
            self.split_pdf_info.setText(f"PDF Information: {os.path.basename(pdf_file)}\nPages: Unknown\nSize: {size_str}")
            QMessageBox.warning(self, "Warning", f"Could not determine page count: {str(e)}\n\nYou can still extract pages, but you'll need to know the total number of pages in the document.")
        
        # Load the PDF in the split tab preview if available
        if hasattr(self, 'load_pdf_in_split_preview'):
            try:
                self.load_pdf_in_split_preview(pdf_file)
            except Exception as preview_error:
                logging.warning(f"Could not load PDF preview: {str(preview_error)}")
                # Preview loading failure shouldn't prevent the main functionality

def count_pages(self, pdf_file):
    """Count the number of pages in a PDF file using multiple methods with fallbacks"""
    # First try using PyPDF2 as it's the most reliable
    try:
        import PyPDF2
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page_count = len(pdf_reader.pages)
            logging.info(f"Counted {page_count} pages using PyPDF2")
            return page_count
    except Exception as pypdf_error:
        logging.warning(f"Error counting pages with PyPDF2: {str(pypdf_error)}")
        
    # Then try ImageMagick
    try:
        cmd = f'magick identify -format "%n\n" "{pdf_file}"'
        result = self.run_imagemagick(cmd)
        
        # Try to parse the output - should be just a number
        if result.stdout.strip():
            try:
                page_count = int(result.stdout.strip())
                logging.info(f"Counted {page_count} pages using ImageMagick format method")
                return page_count
            except ValueError:
                pass
        
        # If that fails, try counting .pdf[ in the output
        cmd = f'magick identify "{pdf_file}"'
        result = self.run_imagemagick(cmd)
        page_count = result.stdout.count(".pdf[")
        
        # If that also fails, count the number of lines in the output
        if page_count == 0:
            page_count = len(result.stdout.strip().split('\n'))
            
        if page_count > 0:
            logging.info(f"Counted {page_count} pages using ImageMagick")
            return page_count
    except Exception as im_error:
        logging.warning(f"Error counting pages with ImageMagick: {str(im_error)}")
    
    # If all methods fail, raise an exception
    logging.error("All page counting methods failed")
    raise RuntimeError("Could not determine page count in PDF file using any available method")

def set_page_range(self, range_type):
    """Set page range selection based on quick options"""
    pdf_file = self.split_pdf_path.text()
    
    if not pdf_file or pdf_file == "No PDF selected":
        QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
        return
    
    try:
        # Import PyPDF2 here to ensure it's available
        import PyPDF2
        
        # Get total pages
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
        
        # Set range based on type
        if range_type == "all":
            self.page_range_input.setText(f"1-{total_pages}")
        elif range_type == "even":
            even_pages = ",".join(str(i) for i in range(2, total_pages + 1, 2))
            self.page_range_input.setText(even_pages)
        elif range_type == "odd":
            odd_pages = ",".join(str(i) for i in range(1, total_pages + 1, 2))
            self.page_range_input.setText(odd_pages)
        
        self.status_label.setText(f"Set page range to {self.page_range_input.text()}")
        
    except Exception as e:
        logging.error(f"Error setting page range: {str(e)}")
        QMessageBox.warning(self, "Error", f"Could not set page range: {str(e)}")

def extract_single_page_with_pypdf2(self, input_pdf, output_pdf, page_number):
    """Extract a single page from a PDF file using PyPDF2"""
    try:
        # Import PyPDF2
        import PyPDF2
        
        # Open the input PDF
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Make sure the page number is valid
            if page_number < 1 or page_number > len(pdf_reader.pages):
                return False, f"Page number {page_number} is out of range. The PDF has {len(pdf_reader.pages)} pages."
            
            # Create a PDF writer
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add the requested page (convert from 1-based to 0-based indexing)
            pdf_writer.add_page(pdf_reader.pages[page_number - 1])
            
            # Write to the output file
            with open(output_pdf, 'wb') as output:
                pdf_writer.write(output)
                
            return True, f"Successfully extracted page {page_number}"
            
    except ImportError:
        return False, "PyPDF2 module is not installed. Please install it using 'pip install PyPDF2'"
    except Exception as e:
        return False, f"Error extracting page: {str(e)}"

def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        logging.error("Pytest encountered errors.")
    return result

if __name__ == "__main__":
    run_pytest()
