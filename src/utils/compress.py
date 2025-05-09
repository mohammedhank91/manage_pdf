import os
import logging
import sys
import subprocess
import pikepdf
import tempfile
import shutil
import io
import gc
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtCore import QCoreApplication
from PIL import Image
from PyQt6.QtCore import QUrl
from src.tabs.preview_tab import HAS_WEBENGINE
from src.utils.cleanup import mark_for_future_cleanup


# Global variable to track temporary files
_temp_files = []

def _register_temp_file(filepath):
    """Register a temporary file for later cleanup"""
    global _temp_files
    if filepath and filepath not in _temp_files:
        _temp_files.append(filepath)

def _cleanup_temp_files():
    """Clean up all registered temporary files"""
    global _temp_files
    for filepath in _temp_files[:]:  # Create a copy to iterate over
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                _temp_files.remove(filepath)
                logging.info(f"Cleaned up temporary file: {filepath}")
        except Exception as e:
            logging.warning(f"Failed to remove temporary file {filepath}: {str(e)}")
            # Mark for future cleanup if we can't delete now
            mark_for_future_cleanup(filepath)
            
    # Search for and clean any stray pdf_compress directories that might be left
    try:
        tmp_dir = tempfile.gettempdir()
        for item in os.listdir(tmp_dir):
            if item.startswith("pdf_compress_"):
                try:
                    item_path = os.path.join(tmp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                        logging.info(f"Cleaned up stray temp directory: {item_path}")
                except Exception as e:
                    logging.error(f"Error cleaning up stray temp directory {item}: {str(e)}")
                    # Mark for future cleanup
                    mark_for_future_cleanup(item_path)
    except Exception as e:
        logging.warning(f"Error searching for stray temp directories: {str(e)}")

def select_pdf(self):
    """Select a PDF file for compression or preview"""
    pdf_file, _ = QFileDialog.getOpenFileName(
        self,
        "Select PDF File",
        "",
        "PDF Files (*.pdf)"
    )

    if pdf_file and os.path.exists(pdf_file):
        self.latest_pdf = pdf_file

        # Enable buttons
        self.btn_compress.setEnabled(True)
        self.btn_preview_pdf.setEnabled(True)
        self.btn_print_pdf.setEnabled(True)

        # Update PDF info display
        file_size = os.path.getsize(pdf_file) / 1024  # KB
        if file_size > 1024:
            file_size = file_size / 1024  # MB
            size_str = f"{file_size:.2f} MB"
        else:
            size_str = f"{file_size:.2f} KB"

        self.pdf_info.setText(f"Current PDF: {os.path.basename(pdf_file)}\nSize: {size_str}\nLocation: {os.path.dirname(pdf_file)}")
        self.status_label.setText(f"PDF file selected: {os.path.basename(pdf_file)}")


def preview_pdf(self):
    """Preview the current PDF file using the PDF Viewer tab"""
    if not self.latest_pdf or not os.path.exists(self.latest_pdf):
        QMessageBox.warning(self, "Warning", "Please select or create a PDF file first.")
        return

    try:
        # First, find the PDF Viewer tab
        pdf_viewer_tab_index = -1
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "PDF Viewer":
                pdf_viewer_tab_index = i
                break

        # If found, switch to it and update the PDF there
        if pdf_viewer_tab_index >= 0:
            # Switch to PDF Viewer tab
            self.tab_widget.setCurrentIndex(pdf_viewer_tab_index)

            # Update UI elements in the PDF Viewer tab
            if hasattr(self, 'preview_pdf_info'):
                file_size = os.path.getsize(self.latest_pdf) / 1024  # KB
                if file_size > 1024:
                    file_size = file_size / 1024  # MB
                    size_str = f"{file_size:.2f} MB"
                else:
                    size_str = f"{file_size:.2f} KB"
                self.preview_pdf_info.setText(f"PDF: {os.path.basename(self.latest_pdf)} ({size_str})")

            if hasattr(self, 'btn_print_preview'):
                self.btn_print_preview.setEnabled(True)

            if hasattr(self, 'btn_open_system'):
                self.btn_open_system.setEnabled(True)

            # Load the PDF directly in the web view
            if hasattr(self, 'pdf_web_view') and HAS_WEBENGINE:
                try:
                    abs_path = os.path.abspath(self.latest_pdf)
                    url = QUrl.fromLocalFile(abs_path)
                    self.pdf_web_view.setUrl(url)

                    self.status_label.setText(f"Previewing {os.path.basename(self.latest_pdf)}")
                    return
                except Exception as e:
                    logging.error(f"Error loading PDF in web view: {str(e)}")

            # If we have a big system button (fallback UI), enable it
            if hasattr(self, 'big_system_btn'):
                self.big_system_btn.setEnabled(True)

            self.status_label.setText(f"Previewing {os.path.basename(self.latest_pdf)}")
            return

        # Fall back to system viewer if tab not found
        if sys.platform == 'win32':
            os.startfile(self.latest_pdf)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', self.latest_pdf])
        else:  # Linux
            subprocess.run(['xdg-open', self.latest_pdf])

        self.status_label.setText(f"Previewing {os.path.basename(self.latest_pdf)} (external viewer)")

    except Exception as e:
        logging.error(f"Error previewing PDF: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error opening PDF: {str(e)}\nSee error.log for details.")


def print_pdf(self):
    """Print the current PDF file using our custom print dialog"""
    if not self.latest_pdf or not os.path.exists(self.latest_pdf):
        QMessageBox.warning(self, "Warning", "Please select or create a PDF file first.")
        return

    try:
        self.status_label.setText(f"Preparing to print {os.path.basename(self.latest_pdf)}")

        # Create a printer object
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)

        # Create a print dialog with available printer options
        dialog = QPrintDialog(printer, self)

        # If the dialog is accepted, print the file
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status_label.setText(f"Printing {os.path.basename(self.latest_pdf)}")

            # Different handling for each OS
            if sys.platform == 'win32':
                printer_name = printer.printerName()
                os.system(f'print /d:"{printer_name}" "{self.latest_pdf}"')
            else:
                # For macOS and Linux, we use the lpr command with the printer name
                printer_name = printer.printerName()
                os.system(f'lpr -P "{printer_name}" "{self.latest_pdf}"')

            self.status_label.setText(f"Sent {os.path.basename(self.latest_pdf)} to printer {printer.printerName()}")

    except Exception as e:
        logging.error(f"Error printing PDF: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error printing PDF: {str(e)}\nSee error.log for details.")

        # Fall back to system print dialog if our method fails
        try:
            if sys.platform == 'win32':
                os.system(f'start /min "" "print" "{self.latest_pdf}"')
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['lpr', self.latest_pdf])
            else:  # Linux
                subprocess.run(['lpr', self.latest_pdf])

            self.status_label.setText(f"Sent {os.path.basename(self.latest_pdf)} to printer (fallback method)")
        except Exception as fallback_error:
            logging.error(f"Error with fallback printing: {str(fallback_error)}")
            QMessageBox.critical(self, "Error", "Could not print PDF using system method either.")


def direct_compress_pdf(input_path, output_path, compression_level=2):
    """
    Direct PDF compression function with special handling for image-heavy PDFs.
    compression_level: 1=light, 2=medium, 3=maximum
    """
    # Create a temporary working directory for image processing
    temp_image_dir = tempfile.mkdtemp(prefix="pdf_compress_")
    _register_temp_file(temp_image_dir)
    
    pdf = None  # Initialize pdf variable for proper cleanup
    
    try:
        # Open the PDF file
        pdf = pikepdf.Pdf.open(input_path)
        
        # Check if there are images to process
        has_images = False

        # First pass - scan for images
        for page in pdf.pages:
            if "/Resources" in page and "/XObject" in page["/Resources"]:
                for name, obj in list(page["/Resources"].get("/XObject", {}).items()):
                    if isinstance(obj, pikepdf.Stream) and obj.get("/Subtype") == "/Image":
                        has_images = True
                        break
                if has_images:
                    break

        # If images found, process them based on compression level
        if has_images:
            # Determine image compression level
            jpeg_quality = 90  # Default - light compression
            max_resolution = 300  # DPI

            if compression_level == 2:  # Medium
                jpeg_quality = 75
                max_resolution = 200
            elif compression_level == 3:  # Maximum
                jpeg_quality = 60
                max_resolution = 150

            # Process images in each page
            for page in pdf.pages:
                if "/Resources" in page and "/XObject" in page["/Resources"]:
                    resources = page["/Resources"]
                    for name, obj in list(resources.get("/XObject", {}).items()):
                        if isinstance(obj, pikepdf.Stream) and obj.get("/Subtype") == "/Image":
                            # Get image details
                            width = int(obj.get("/Width", 0))
                            height = int(obj.get("/Height", 0))

                            # Skip small images
                            if width < 100 or height < 100:
                                continue

                            # Process based on image type
                            filter_type = obj.get("/Filter")

                            # Images that are already JPEG
                            is_jpeg = False
                            if filter_type == "/DCTDecode" or filter_type == pikepdf.Name.DCTDecode:
                                is_jpeg = True
                            elif isinstance(filter_type, pikepdf.Array):
                                for f in filter_type:
                                    if f == pikepdf.Name.DCTDecode or f == "/DCTDecode":
                                        is_jpeg = True
                                        break

                            if is_jpeg:
                                # For JPEGs, we can try to recompress if they're large
                                if compression_level >= 2 and (width > 1000 or height > 1000):
                                    try:
                                        # Create a unique temp file for this image
                                        temp_img_file = os.path.join(temp_image_dir, f"img_temp_{id(obj)}.jpg")
                                        _register_temp_file(temp_img_file)
                                        
                                        # Read image data
                                        img_data = obj.read_raw_bytes()
                                        img = Image.open(io.BytesIO(img_data))

                                        # Resize large images
                                        if width > 1500 or height > 1500:
                                            ratio = min(1500 / width, 1500 / height)
                                            new_width = int(width * ratio)
                                            new_height = int(height * ratio)
                                            img = img.resize((new_width, new_height), Image.BICUBIC)

                                        # Recompress with adobe-compatible settings
                                        img.save(temp_img_file, format="JPEG", quality=jpeg_quality, optimize=True)
                                        
                                        with open(temp_img_file, 'rb') as f:
                                            new_data = f.read()

                                        # Only replace if smaller
                                        if len(new_data) < len(img_data):
                                            # Make sure new dimensions are updated properly
                                            if width > 1500 or height > 1500:
                                                obj["/Width"] = new_width
                                                obj["/Height"] = new_height
                                            
                                            obj.write(new_data, filter=pikepdf.Name.DCTDecode)
                                    except Exception as e:
                                        print(f"Error processing JPEG image: {e}")

                            # Non-JPEG images (like PNG, bitmap, etc)
                            else:
                                is_flate = False
                                if filter_type == "/FlateDecode" or filter_type == pikepdf.Name.FlateDecode:
                                    is_flate = True
                                elif isinstance(filter_type, pikepdf.Array):
                                    for f in filter_type:
                                        if f == pikepdf.Name.FlateDecode or f == "/FlateDecode":
                                            is_flate = True
                                            break

                                # For Adobe Acrobat compatibility, be more cautious with image conversions
                                # Only convert simple RGB and Grayscale images
                                if is_flate and compression_level >= 2:
                                    try:
                                        # Get color space
                                        colorspace = obj.get("/ColorSpace")
                                        bits = int(obj.get("/BitsPerComponent", 8))
                                        
                                        # Only process standard RGB and Grayscale images
                                        if bits == 8 and colorspace in ["/DeviceRGB", pikepdf.Name.DeviceRGB, 
                                                                      "/DeviceGray", pikepdf.Name.DeviceGray]:
                                            
                                            is_rgb = colorspace in ["/DeviceRGB", pikepdf.Name.DeviceRGB]
                                            
                                            # Create a unique temp file for this image
                                            temp_img_file = os.path.join(temp_image_dir, f"img_temp_{id(obj)}.jpg")
                                            _register_temp_file(temp_img_file)
                                            
                                            # Try to load image
                                            img_data = obj.read_bytes()
                                            
                                            # Handle based on colorspace
                                            if is_rgb:
                                                img = Image.frombytes("RGB", (width, height), img_data)
                                            else:  # DeviceGray
                                                img = Image.frombytes("L", (width, height), img_data)
                                            
                                            # Resize large images
                                            new_width, new_height = width, height
                                            if width > 1500 or height > 1500:
                                                ratio = min(1500 / width, 1500 / height)
                                                new_width = int(width * ratio)
                                                new_height = int(height * ratio)
                                                img = img.resize((new_width, new_height), Image.BICUBIC)

                                            # Convert to JPEG with Adobe compatibility settings
                                            img.save(temp_img_file, format="JPEG", quality=jpeg_quality, optimize=True)
                                            
                                            with open(temp_img_file, 'rb') as f:
                                                new_data = f.read()
                                            
                                            # Calculate if the new version is smaller
                                            original_size = len(img_data)
                                            new_size = len(new_data)
                                            
                                            # Only replace if the new version is smaller
                                            if new_size < original_size:
                                                # Update dimensions if resized
                                                if width > 1500 or height > 1500:
                                                    obj["/Width"] = new_width
                                                    obj["/Height"] = new_height
                                                
                                                # Set proper colorspace
                                                if img.mode == "L":
                                                    obj["/ColorSpace"] = pikepdf.Name.DeviceGray
                                                elif img.mode == "RGB":
                                                    obj["/ColorSpace"] = pikepdf.Name.DeviceRGB
                                                
                                                # Update image data
                                                obj.write(new_data, filter=pikepdf.Name.DCTDecode)
                                                
                                                # Set bits per component
                                                obj["/BitsPerComponent"] = 8
                                                
                                                # Remove unnecessary entries that might cause conflicts
                                                for key in ["/DecodeParms", "/Predictor", "/Interpolate"]:
                                                    if key in obj:
                                                        del obj[key]
                                        
                                    except Exception as e:
                                        print(f"Error converting image to JPEG: {e}")
            
            # Clean up any unreferenced objects created during processing
            pdf.remove_unreferenced_resources()

        # Use a temporary file for the initial save to avoid issues
        temp_output = os.path.join(temp_image_dir, "temp_output.pdf")
        _register_temp_file(temp_output)
        
        # Save with compatibility options for best Adobe support
        pdf.save(
            temp_output,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            preserve_pdfa=True  # Maintain PDF/A compatibility when possible
        )
        
        # Close the PDF before copying to release file handles
        pdf.close()
        pdf = None
        
        # Force garbage collection to release any file handles
        gc.collect()
        
        # Now copy to final destination
        shutil.copy2(temp_output, output_path)
        
    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        if pdf is not None:
            try:
                pdf.close()
            except:
                pass
        raise
    finally:
        # Make sure to close the PDF if it's still open
        if pdf is not None:
            try:
                pdf.close()
            except:
                pass
            
        # Force garbage collection
        gc.collect()
        
        # Clean up the temporary directory and its contents
        try:
            # First try to delete individual files
            for filename in os.listdir(temp_image_dir):
                try:
                    filepath = os.path.join(temp_image_dir, filename)
                    if os.path.isfile(filepath):
                        try:
                            os.unlink(filepath)
                        except Exception as e:
                            logging.warning(f"Could not delete file {filepath}: {str(e)}")
                            mark_for_future_cleanup(filepath)
                except:
                    pass
                
            # Then try to remove the directory
            shutil.rmtree(temp_image_dir, ignore_errors=True)
            _temp_files = [f for f in _temp_files if not f.startswith(temp_image_dir)]
            
            # If directory still exists, mark it for future cleanup
            if os.path.exists(temp_image_dir):
                mark_for_future_cleanup(temp_image_dir)
                
        except Exception as e:
            logging.warning(f"Failed to clean up temp directory {temp_image_dir}: {str(e)}")
            mark_for_future_cleanup(temp_image_dir)

    return True


def compress_pdf(self):
    """Compress the selected PDF file using direct pikepdf approach"""
    if not self.latest_pdf or not os.path.exists(self.latest_pdf):
        QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
        return

    try:
        self.status_label.setText(f"Analyzing {os.path.basename(self.latest_pdf)}...")
        self.progress_bar.setValue(10)
        QCoreApplication.processEvents()

        # Create a temporary output filename for the compressed file
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, f"compressed_{os.path.basename(self.latest_pdf)}")
        _register_temp_file(temp_filename)

        # Record the original file size
        original_size = os.path.getsize(self.latest_pdf) / 1024  # KB

        # Determine compression level based on selected profile
        profile_index = self.compression_profile.currentIndex()

        # Map profile to compression level:
        # 0=Maximum Quality → 1 (light)
        # 1=High Quality → 1 (light)
        # 2=Balanced → 2 (medium)
        # 3=Maximum Compression → 3 (maximum)
        compression_level = 1
        if profile_index == 2:
            compression_level = 2
        elif profile_index == 3:
            compression_level = 3

        # Directly compress using the enhanced method
        self.status_label.setText(f"Compressing PDF and optimizing images...")
        self.progress_bar.setValue(30)
        QCoreApplication.processEvents()

        # Call the direct compression function with the appropriate level
        direct_compress_pdf(self.latest_pdf, temp_filename, compression_level)

        self.progress_bar.setValue(80)
        QCoreApplication.processEvents()

        # Ask user where to save the compressed file
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Compressed PDF",
            os.path.dirname(self.latest_pdf) + f"/compressed_{os.path.basename(self.latest_pdf)}",
            "PDF Files (*.pdf)"
        )

        if save_path:
            # Copy the compressed file to the chosen location
            shutil.copy2(temp_filename, save_path)

            # Get compressed file size
            compressed_size = os.path.getsize(save_path) / 1024  # KB

            # Update latest PDF to point to the compressed one
            self.latest_pdf = save_path

            # Format size strings
            if original_size > 1024:
                original_size = original_size / 1024  # MB
                original_size_str = f"{original_size:.2f} MB"
            else:
                original_size_str = f"{original_size:.2f} KB"

            if compressed_size > 1024:
                compressed_size = compressed_size / 1024  # MB
                compressed_size_str = f"{compressed_size:.2f} MB"
            else:
                compressed_size_str = f"{compressed_size:.2f} KB"

            # Calculate compression percentage
            if original_size > 0:
                compression_percent = ((original_size - compressed_size) / original_size) * 100
                compression_info = f"Compression: {compression_percent:.1f}% reduction"
            else:
                compression_info = ""

            # Update UI with the compressed file info
            self.pdf_info.setText(
                f"Current PDF: {os.path.basename(save_path)}\n"
                f"Size: {compressed_size_str}\n"
                f"Location: {os.path.dirname(save_path)}\n"
                f"{compression_info}"
            )

            # Enable preview and print buttons
            self.btn_preview_pdf.setEnabled(True)
            self.btn_print_pdf.setEnabled(True)

            QMessageBox.information(
                self,
                "Success",
                f"PDF compressed successfully!\nOriginal size: {original_size_str}\nCompressed size: {compressed_size_str}\n{compression_info}")

        # Clean up all temporary files
        _cleanup_temp_files()
        
        # Force garbage collection to release file handles
        gc.collect()

        self.progress_bar.setValue(100)
        self.status_label.setText(f"PDF compressed successfully")

    except Exception as e:
        logging.error(f"Error compressing PDF: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error compressing PDF: {str(e)}\nSee error.log for details.")
        self.progress_bar.setValue(0)
        self.status_label.setText("Compression failed")
        
        # Even on error, try to clean up temp files
        _cleanup_temp_files()
