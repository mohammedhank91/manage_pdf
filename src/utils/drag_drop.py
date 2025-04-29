import os
import logging
from PyQt6.QtWidgets import QMessageBox


def setupDragDrop(self):
    self.setAcceptDrops(True)


def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()


def dropEvent(self, event):
    """Handle dropping files onto the application"""
    if event.mimeData().hasUrls():
        files = [url.toLocalFile() for url in event.mimeData().urls()]

        # Determine which tab is active and process files accordingly
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:  # Main tab
            # Proceed only if image files are dropped
            image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            if image_files:
                for file in image_files:
                    if file not in self.selected_files:
                        self.selected_files.append(file)
                        self.listbox.addItem(os.path.basename(file))

                if len(self.selected_files) > 0:
                    if self.current_index < 0:
                        self.current_index = 0
                    self.update_picture_box()
                    self.status_label.setText(f"Added {len(image_files)} images. Total: {len(self.selected_files)}")
        elif current_tab == 3:  # Merge tab
            # Add PDFs to merge list
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            for pdf in pdf_files:
                self.pdf_listbox.addItem(pdf)

            # Make sure to update the merge summary
            self.update_merge_summary()
            self.status_label.setText(f"Added {len(pdf_files)} PDFs to merge list")
        elif current_tab == 4:  # Split tab
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            if pdf_files and os.path.exists(pdf_files[0]):
                pdf_file = pdf_files[0]
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


def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        logging.error("Pytest encountered errors.")
    return result


if __name__ == "__main__":
    run_pytest()
