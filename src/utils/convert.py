import os
import logging
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication
import math

def update_conversion_ui(self):
    """Update the conversion UI based on selected files and settings"""
    if hasattr(self, 'image_summary') and hasattr(self, 'settings_summary'):
        # Update image summary
        if self.selected_files:
            num_files = len(self.selected_files)
            total_size = sum(os.path.getsize(f) for f in self.selected_files) / 1024  # KB
            
            if total_size > 1024:
                size_str = f"{total_size/1024:.1f} MB"
            else:
                size_str = f"{total_size:.1f} KB"
                
            self.image_summary.setText(f"Ready to convert {num_files} image{'s' if num_files > 1 else ''}\nTotal size: {size_str}")
        else:
            self.image_summary.setText("No images selected yet. Please select images in the Main tab first.")
        
        # Update settings summary
        self.settings_summary.setText(
            f"Current settings: {self.paper_size.currentText()}, "
            f"{self.combo_orient.currentText()}, "
            f"{self.num_margin.value()}px margins, "
            f"{self.resolution.currentText()}"
        )

def save_conversion_settings(self):
    """Save the current conversion settings to a preset"""
    # This would normally save to a config file, but for simplicity just show a message
    QMessageBox.information(self, "Settings Saved", "Settings have been saved as a preset.\n(This is just a placeholder - actual saving would be implemented in a real application)")

def load_conversion_settings(self):
    """Load saved conversion settings from a preset"""
    # This would normally load from a config file, but for simplicity just show a message
    QMessageBox.information(self, "Settings Loaded", "Settings have been loaded from a preset.\n(This is just a placeholder - actual loading would be implemented in a real application)")


def convert_to_pdf(self):
    """Convert selected images to PDF based on current settings"""
    if len(self.selected_files) == 0:
        self.status_label.setText("No images selected!")
        QMessageBox.warning(self, "Warning", "Please select images first before converting.")
        self.tab_widget.setCurrentIndex(0)  # Switch to main tab to select images
        return
    
    margin = self.num_margin.value()
    orientation = self.combo_orient.currentText()
    apply_global_orientation = (orientation == "Landscape")
    
    # Get paper size from dropdown
    paper_size = self.paper_size.currentText()
    
    # Get resolution settings from dropdown if it exists
    dpi = 150  # Default DPI
    quality = 95  # Default quality
    if hasattr(self, 'resolution'):
        resolution_text = self.resolution.currentText()
        if "72" in resolution_text:
            dpi = 72
        elif "300" in resolution_text:
            dpi = 300
        elif "600" in resolution_text:
            dpi = 600
            
    # Get compression settings if they exist
    compression = "JPEG"  # Default compression
    if hasattr(self, 'compression'):
        compression_text = self.compression.currentText()
        if "Maximum Quality" in compression_text:
            compression = "LZW"
            quality = 100
        elif "High Quality" in compression_text:
            compression = "JPEG"
            quality = 95
        elif "Balanced" in compression_text:
            compression = "JPEG"
            quality = 90
        elif "Maximum Compression" in compression_text:
            compression = "JPEG"
            quality = 85
    
    try:
        if self.chk_separate.isChecked():
            # Save as separate PDFs
            folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if folder:
                self.progress_bar.setValue(0)
                total = len(self.selected_files)
                count = 0
                
                for i, img_file in enumerate(self.selected_files):
                    out_file = os.path.join(folder, os.path.splitext(os.path.basename(img_file))[0] + ".pdf")
                    
                    # Build ImageMagick command
                    rotate_option = f"-rotate {self.rotations[i]}" if i in self.rotations else ""
                    border_option = f"-border {margin} -bordercolor white" if margin > 0 else ""
                    orient_option = "-rotate 90" if apply_global_orientation else ""
                    quality_option = f"-quality {quality}" if quality != 95 else ""
                    density_option = f"-density {dpi}" if dpi != 150 else ""
                    compress_option = f"-compress {compression}" if compression != "JPEG" else ""
                    
                    # Add paper size option
                    page_size_option = f"-page {paper_size}"
                    
                    # Combine options
                    options = " ".join(filter(None, [rotate_option, border_option, orient_option, 
                                                        page_size_option, quality_option, density_option, compress_option]))
                    
                    cmd = f'magick "{img_file}" {options} "{out_file}"'
                    try:
                        self.run_imagemagick(cmd)
                        
                        count += 1
                        self.progress_bar.setValue(math.floor((count / total) * 100))
                        QApplication.processEvents()
                    except Exception as e:
                        # Show error but continue with other files
                        error_message = f"Error processing file {img_file}: {str(e)}"
                        logging.error(error_message)
                        QMessageBox.warning(self, "Processing Error", 
                            f"Error converting {os.path.basename(img_file)}\n{str(e)}\n\nContinuing with remaining files.")
                
                self.status_label.setText(f"All {count} images saved as separate PDFs in: {folder}")
                QMessageBox.information(self, "Success", f"Created {count} PDF files in:\n{folder}")
                
                # We don't enable the tools for multiple PDFs
        else:
            # Save as single PDF
            output_pdf, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF As",
                "",
                "PDF Files (*.pdf)"
            )
            if output_pdf:
                self.progress_bar.setValue(0)
                
                # Apply formatting options
                border_option = f"-border {margin} -bordercolor white" if margin > 0 else ""
                orient_option = "-rotate 90" if apply_global_orientation else ""
                
                # Use simpler set of options that are more compatible
                common_options = "-quality 95"  # Simple quality setting
                
                # Process each file individually to create temporary PDFs
                temp_pdfs = []
                for i, img_file in enumerate(self.selected_files):
                    # Create a temporary PDF for each image
                    temp_pdf = os.path.join(os.path.dirname(output_pdf), f"temp_{i}.pdf")
                    temp_pdfs.append(temp_pdf)
                    
                    # Build command with individual file options
                    rotation = f"-rotate {self.rotations[i]}" if i in self.rotations else ""
                    
                    # Simple command for single image conversion
                    file_cmd = f'magick "{img_file}" {rotation} {border_option} {common_options} "{temp_pdf}"'
                    
                    try:
                        print(f"Converting image {i+1}/{len(self.selected_files)}")
                        self.run_imagemagick(file_cmd)
                        
                        # Update progress
                        progress = int((i + 1) / len(self.selected_files) * 90)
                        self.progress_bar.setValue(progress)
                        QApplication.processEvents()
                    except Exception as e:
                        logging.error(f"Error converting image {img_file}: {str(e)}")
                        QMessageBox.warning(self, "Conversion Error", f"Error converting {os.path.basename(img_file)}: {str(e)}")
                        continue
                
                # Now merge all temporary PDFs using PyPDF2
                if temp_pdfs:
                    try:
                        import PyPDF2
                        merger = PyPDF2.PdfMerger()
                        
                        for pdf in temp_pdfs:
                            if os.path.exists(pdf):
                                merger.append(pdf)
                        
                        # Write the final merged PDF
                        with open(output_pdf, 'wb') as f:
                            merger.write(f)
                        
                        # Clean up temporary PDFs
                        for pdf in temp_pdfs:
                            if os.path.exists(pdf):
                                try:
                                    os.remove(pdf)
                                except:
                                    pass
                                
                        self.progress_bar.setValue(100)
                        self.status_label.setText(f"PDF created with {len(self.selected_files)} images: {output_pdf}")
                        QMessageBox.information(self, "Success", "PDF conversion complete!")
                        
                        # Store the latest PDF file path and enable preview/print/compress buttons
                        self.latest_pdf = output_pdf
                    except Exception as merge_error:
                        logging.error(f"Error merging PDFs: {str(merge_error)}")
                        QMessageBox.critical(self, "Error", f"Error creating final PDF: {str(merge_error)}")
                        self.progress_bar.setValue(0)
                        return
                else:
                    QMessageBox.critical(self, "Error", "No images were successfully converted to PDF")
                    self.progress_bar.setValue(0)
                    return
                
                # Enable buttons if they exist
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
                
                # Switch to Tools tab if it exists
                if self.tab_widget.count() > 2:
                    self.tab_widget.setCurrentIndex(2)
    except Exception as e:
        logging.error(f"Error in conversion: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error during PDF conversion: {str(e)}\nSee error.log for details.")
        self.progress_bar.setValue(0)
