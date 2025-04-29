import os
import logging
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication

def merge_pdfs(self):
    """Merge PDFs in the list using PyPDF2."""
    if self.pdf_listbox.count() < 2:
        QMessageBox.warning(self, "Warning", "Please add at least two PDF files to merge.")
        return

    output_pdf, _ = QFileDialog.getSaveFileName(
        self,
        "Save Merged PDF As",
        "",
        "PDF Files (*.pdf)"
    )
    if not output_pdf:
        return

    try:
        self.status_label.setText("Merging PDFs...")
        self.progress_bar.setValue(0)

        # Collect files
        pdf_files = [self.pdf_listbox.item(i).text()
                        for i in range(self.pdf_listbox.count())]
        
        # Import PyPDF2 here to ensure it's available
        import PyPDF2
        
        # Create a PDF merger object
        pdf_merger = PyPDF2.PdfMerger()
        
        total_files = len(pdf_files)
        for i, pdf in enumerate(pdf_files):
            # Ensure the file exists
            if not os.path.exists(pdf):
                QMessageBox.warning(self, "File Not Found", f"The file '{pdf}' does not exist.")
                continue
                
            # Add PDF with a bookmark if requested
            if self.chk_add_bookmarks.isChecked():
                bookmark_name = os.path.basename(pdf)  # Use filename as bookmark
                pdf_merger.append(pdf, outline_item=bookmark_name)
            else:
                pdf_merger.append(pdf)
            
            # Update progress
            progress = int(((i + 1) / total_files) * 90)  # Reserve last 10% for writing
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Merging PDF {i+1}/{total_files}")
            QApplication.processEvents()  # Keep UI responsive
        
        # Write the merged PDF to output file
        with open(output_pdf, 'wb') as f:
            pdf_merger.write(f)
        
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Successfully merged {total_files} PDFs")
        
        QMessageBox.information(self, "Success", f"PDFs merged into:\n{output_pdf}")
        self.latest_pdf = output_pdf

        # Re-enable any tool buttons
        if hasattr(self, 'btn_preview_pdf'):
            self.btn_preview_pdf.setEnabled(True)
        if hasattr(self, 'btn_print_pdf'):
            self.btn_print_pdf.setEnabled(True)
        if hasattr(self, 'btn_compress'):
            self.btn_compress.setEnabled(True)
        
        # Update PDF info if it exists
        if hasattr(self, 'pdf_info'):
            file_size = os.path.getsize(output_pdf) / 1024  # KB
            if file_size > 1024:
                file_size = file_size / 1024  # MB
                size_str = f"{file_size:.2f} MB"
            else:
                size_str = f"{file_size:.2f} KB"
            
            self.pdf_info.setText(f"Current PDF: {os.path.basename(output_pdf)}\nSize: {size_str}\nLocation: {os.path.dirname(output_pdf)}")
            
    except Exception as e:
        logging.error(f"Error in PDF merge: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error merging PDFs: {str(e)}\nSee error.log for details.")
        self.progress_bar.setValue(0)

def update_merge_summary(self):
    """Update the merge summary display"""
    count = self.pdf_listbox.count()
    print(f"update_merge_summary called - PDF count: {count}")
    if count == 0:
        self.merge_summary.setText("No PDF files selected yet")
        self.btn_merge_pdfs.setEnabled(False)
        print("Disabled merge button - no PDFs")
    elif count == 1:
        self.merge_summary.setText("1 PDF file selected. Add at least one more file to merge.")
        self.btn_merge_pdfs.setEnabled(False)
        print("Disabled merge button - only 1 PDF")
    else:
        self.merge_summary.setText(f"{count} PDF files ready to merge")
        self.btn_merge_pdfs.setEnabled(True)
        print(f"Enabled merge button - {count} PDFs ready")
    print(f"btn_merge_pdfs.isEnabled(): {self.btn_merge_pdfs.isEnabled()}")
     

def add_pdf(self):
    """Add a PDF to the merge list"""
    print("add_pdf function called")
    files, _ = QFileDialog.getOpenFileNames(
        self,
        "Select PDF Files",
        "",
        "PDF Files (*.pdf)"
    )
    
    if files:
        print(f"Selected {len(files)} PDF files")
        for file in files:
            self.pdf_listbox.addItem(file)
        
        self.update_merge_summary()
        print("Called update_merge_summary from add_pdf")
        
def remove_pdf(self):
    """Remove the selected PDF from the merge list"""
    current_row = self.pdf_listbox.currentRow()
    if current_row >= 0:
        self.pdf_listbox.takeItem(current_row)
        self.update_merge_summary()
        self.status_label.setText(f"Removed PDF from merge list")
        
def move_pdf_up(self):
    """Move the selected PDF up in the list"""
    current_row = self.pdf_listbox.currentRow()
    if current_row > 0:
        item = self.pdf_listbox.takeItem(current_row)
        self.pdf_listbox.insertItem(current_row - 1, item)
        self.pdf_listbox.setCurrentRow(current_row - 1)
        self.status_label.setText("Moved PDF up in the list")
        
def move_pdf_down(self):
    """Move the selected PDF down in the list"""
    current_row = self.pdf_listbox.currentRow()
    if current_row >= 0 and current_row < self.pdf_listbox.count() - 1:
        item = self.pdf_listbox.takeItem(current_row)
        self.pdf_listbox.insertItem(current_row + 1, item)
        self.pdf_listbox.setCurrentRow(current_row + 1)
        self.status_label.setText("Moved PDF down in the list")

def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        logging.error("Pytest encountered errors.")
    return result

if __name__ == "__main__":
    run_pytest()
