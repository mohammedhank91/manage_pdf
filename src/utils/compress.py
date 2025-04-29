import os
import logging
import sys
import subprocess
import pikepdf
import tempfile
import shutil
import io
import re
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtCore import QCoreApplication
from PIL import Image
from PyQt6.QtCore import QUrl
from src.tabs.preview_tab import HAS_WEBENGINE

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
    with pikepdf.Pdf.open(input_path) as pdf:
        # Process images if it's an image-heavy PDF
        try:
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
                                            # Read image data
                                            img_data = obj.read_raw_bytes()
                                            img = Image.open(io.BytesIO(img_data))
                                            
                                            # Resize large images
                                            if width > 1500 or height > 1500:
                                                ratio = min(1500 / width, 1500 / height)
                                                new_width = int(width * ratio)
                                                new_height = int(height * ratio)
                                                img = img.resize((new_width, new_height), Image.BICUBIC)
                                            
                                            # Recompress
                                            buffer = io.BytesIO()
                                            img.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                                            buffer.seek(0)
                                            new_data = buffer.read()
                                            
                                            # Only replace if smaller
                                            if len(new_data) < len(img_data):
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
                                    
                                    if is_flate:
                                        # For non-JPEGs, try to convert to JPEG
                                        if width >= 100 and height >= 100:
                                            try:
                                                # Get color space
                                                colorspace = obj.get("/ColorSpace")
                                                bits = int(obj.get("/BitsPerComponent", 8))
                                                
                                                # Only process 8-bit images
                                                if bits == 8:
                                                    # Try to load image
                                                    img_data = obj.read_bytes()
                                                    
                                                    # Handle based on colorspace
                                                    if colorspace == "/DeviceRGB":
                                                        img = Image.frombytes("RGB", (width, height), img_data)
                                                    elif colorspace == "/DeviceGray":
                                                        img = Image.frombytes("L", (width, height), img_data)
                                                    else:
                                                        # Skip complex colorspaces
                                                        continue
                                                    
                                                    # Resize large images
                                                    if width > 1500 or height > 1500:
                                                        ratio = min(1500 / width, 1500 / height)
                                                        new_width = int(width * ratio)
                                                        new_height = int(height * ratio)
                                                        img = img.resize((new_width, new_height), Image.BICUBIC)
                                                    
                                                    # Convert to JPEG
                                                    buffer = io.BytesIO()
                                                    img.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                                                    buffer.seek(0)
                                                    new_data = buffer.read()
                                                    
                                                    # Replace with JPEG version
                                                    obj.write(new_data, filter=pikepdf.Name.DCTDecode)
                                                    
                                                    # Update color space
                                                    if img.mode == "L":
                                                        obj["/ColorSpace"] = pikepdf.Name.DeviceGray
                                                    elif img.mode == "RGB":
                                                        obj["/ColorSpace"] = pikepdf.Name.DeviceRGB
                                                        
                                                    # Remove unnecessary entries
                                                    for key in ["/DecodeParms", "/Predictor"]:
                                                        if key in obj:
                                                            del obj[key]
                                                    
                                                    # Set bits per component
                                                    obj["/BitsPerComponent"] = 8
                                                    
                                            except Exception as e:
                                                print(f"Error converting image to JPEG: {e}")
                
                # Clean up any unreferenced objects created during processing
                pdf.remove_unreferenced_resources()
                
        except Exception as e:
            print(f"Error processing images in PDF: {e}")
            
        # Finally apply standard PDF compression
        pdf.save(
            output_path,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate
        )
    
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
            
        # Clean up temporary file
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except Exception as e:
            logging.warning(f"Failed to remove temporary file: {str(e)}")
            
        self.progress_bar.setValue(100)
        self.status_label.setText(f"PDF compressed successfully")
        
    except Exception as e:
        logging.error(f"Error compressing PDF: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error compressing PDF: {str(e)}\nSee error.log for details.")
        self.progress_bar.setValue(0)
        self.status_label.setText("Compression failed")

def compress_images_on_page(page, target_dpi, jpeg_quality, convert_to_grayscale, downsample_images, 
                           downsize_large_images, max_dimension, aggressive=False):
    """Process all images on a page and compress them"""
    try:
        # Check if page has resources
        if "/Resources" not in page:
            return
            
        # Check if page has XObject resources
        if "/XObject" not in page.get("/Resources", {}):
            return
            
        resources = page["/Resources"]
        
        # Process all image XObjects
        for name, obj in list(resources.get("/XObject", {}).items()):
            # Skip if it's not an image
            if not isinstance(obj, pikepdf.Stream) or obj.get("/Subtype") != "/Image":
                continue
            
            # Get image info
            try:
                pim = obj
                
                # Make sure image is compressed
                if "/Filter" not in pim and isinstance(pim, pikepdf.Stream):
                    # Uncompressed image - apply compression
                    pim.write(pim.read_bytes(), filter=pikepdf.Name.FlateDecode)
                
                # Skip very small images (thumbnails, icons, etc.)
                width = int(pim.get("/Width", "0"))
                height = int(pim.get("/Height", "0"))
                if width < 50 or height < 50:
                    continue
                
                # Handle different image formats
                if pim.get("/ColorSpace") == "/DeviceRGB":
                    mode = "RGB"
                elif pim.get("/ColorSpace") == "/DeviceGray":
                    mode = "L"
                elif pim.get("/ColorSpace") == "/DeviceCMYK":
                    mode = "CMYK"
                else:
                    # Try other possible color space formats
                    cs = pim.get("/ColorSpace")
                    if isinstance(cs, pikepdf.Array) and len(cs) > 0 and cs[0] == "/ICCBased":
                        # This is an ICC-based color profile, assume RGB for simplicity
                        mode = "RGB"
                    else:
                        # If we can't determine the color space, skip this image
                        continue
                
                # Handle different compression types
                filter_type = pim.get("/Filter")
                
                # For JPEG images (DCTDecode)
                if filter_type == "/DCTDecode" or (isinstance(filter_type, pikepdf.Array) and pikepdf.Name.DCTDecode in filter_type):
                    # JPEG image
                    img_data = pim.read_raw_bytes()
                    try:
                        img = Image.open(io.BytesIO(img_data))
                    except Exception:
                        # If we can't open the image, skip it
                        continue
                    
                    # Skip smaller images that are already well-compressed
                    if img.width < 200 and img.height < 200 and len(img_data) < 30000 and not aggressive:
                        continue
                    
                    # Force more aggressive processing
                    need_recompression = False
                    
                    # Check if we need to resize large images
                    if downsize_large_images and (img.width > max_dimension or img.height > max_dimension):
                        # Calculate new dimensions while maintaining aspect ratio
                        if img.width > img.height:
                            new_width = max_dimension
                            new_height = int(img.height * (max_dimension / img.width))
                        else:
                            new_height = max_dimension
                            new_width = int(img.width * (max_dimension / img.height))
                        
                        try:
                            # Use BICUBIC instead of LANCZOS
                            img = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
                            need_recompression = True
                        except AttributeError:
                            # Fallback for older Pillow versions
                            try:
                                img = img.resize((new_width, new_height), Image.BICUBIC)
                                need_recompression = True
                            except AttributeError:
                                # Last resort
                                img = img.resize((new_width, new_height))
                                need_recompression = True
                                
                    # Or downsample based on DPI
                    elif downsample_images and not need_recompression:
                        # Be more aggressive with downsampling
                        x_factor = min(target_dpi / 300.0, 0.9)  # More aggressive
                            
                        # For maximum compression, be even more aggressive
                        if aggressive and img.width > 800 and img.height > 800:
                            x_factor = min(x_factor, 0.7)  # More reduction for large images
                            
                        new_width = max(int(img.width * x_factor), 100)  # Don't go below 100px
                        new_height = max(int(img.height * x_factor), 100)
                        
                        # Resize if we need a smaller image
                        if new_width < img.width * 0.95 or new_height < img.height * 0.95:
                            try:
                                img = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
                                need_recompression = True
                            except AttributeError:
                                try:
                                    img = img.resize((new_width, new_height), Image.BICUBIC) 
                                    need_recompression = True
                                except AttributeError:
                                    img = img.resize((new_width, new_height))
                                    need_recompression = True
                    
                    # Convert to grayscale if requested
                    if convert_to_grayscale and mode != "L":
                        img = img.convert("L")
                        mode = "L"
                        need_recompression = True
                    
                    # Always recompress if compression is aggressive
                    if aggressive:
                        need_recompression = True
                    
                    # Only recompress if needed
                    if need_recompression:
                        # Compress and replace the image
                        img_buffer = io.BytesIO()
                        
                        # For really aggressive compression, use lower quality
                        final_quality = jpeg_quality
                        if aggressive and len(img_data) > 100000:
                            # For larger images, use even lower quality
                            final_quality = max(35, jpeg_quality - 15)
                        
                        img.save(img_buffer, format="JPEG", quality=final_quality, optimize=True)
                        img_buffer.seek(0)
                        new_data = img_buffer.read()
                        
                        # Replace the image if compressed version is smaller
                        # (for aggressive mode, always replace)
                        if len(new_data) < len(img_data) * 0.98 or aggressive:
                            pim.write(new_data, filter=pikepdf.Name.DCTDecode)
                            
                            # Update color space if we converted to grayscale
                            if convert_to_grayscale and mode == "L":
                                pim["/ColorSpace"] = pikepdf.Name.DeviceGray
                    
                # For other image types (FlateDecode, etc.)
                elif filter_type == "/FlateDecode" or (isinstance(filter_type, pikepdf.Array) and pikepdf.Name.FlateDecode in filter_type):
                    try:
                        # Skip if wrong bits per component or no dimensions
                        bits = int(pim.get("/BitsPerComponent", "8"))
                        width = int(pim.get("/Width", "0"))
                        height = int(pim.get("/Height", "0"))
                        
                        if bits != 8 or width <= 0 or height <= 0:
                            continue
                        
                        # Skip smaller images unless in aggressive mode
                        if width < 200 and height < 200 and not aggressive:
                            continue
                            
                        # Extract raw image data
                        img_data = pim.read_bytes()
                        
                        try:
                            # Try to create an image from the raw data
                            if mode == "L":
                                img = Image.frombytes("L", (width, height), img_data)
                            elif mode == "RGB":
                                img = Image.frombytes("RGB", (width, height), img_data)
                            else:
                                # Unsupported mode, try RGB anyway
                                img = Image.frombytes("RGB", (width, height), img_data)
                                mode = "RGB"
                        except:
                            # If can't create image, skip this one
                            continue
                        
                        # For maximum compression, always process
                        need_recompression = aggressive
                        
                        # Check if we need to resize large images
                        if downsize_large_images and (width > max_dimension or height > max_dimension):
                            # Calculate new dimensions preserving aspect ratio
                            if width > height:
                                new_width = max_dimension
                                new_height = int(height * (max_dimension / width))
                            else:
                                new_height = max_dimension
                                new_width = int(width * (max_dimension / height))
                            
                            try:
                                img = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
                                need_recompression = True
                            except AttributeError:
                                # Fallback for older Pillow versions
                                try:
                                    img = img.resize((new_width, new_height), Image.BICUBIC)
                                    need_recompression = True
                                except AttributeError:
                                    # Last resort
                                    img = img.resize((new_width, new_height))
                                    need_recompression = True
                        
                        # Convert to grayscale if requested
                        if convert_to_grayscale and mode == "RGB":
                            img = img.convert("L")
                            mode = "L"
                            need_recompression = True
                        
                        # Downsample if requested
                        if downsample_images and not need_recompression:
                            # Be more aggressive with downsampling for bitmaps
                            x_factor = min(target_dpi / 300.0, 0.8)
                            
                            # For maximum compression, be even more aggressive
                            if aggressive:
                                x_factor = min(x_factor, 0.6)
                                
                            new_width = max(int(width * x_factor), 100)
                            new_height = max(int(height * x_factor), 100)
                            
                            if new_width < width * 0.95 or new_height < height * 0.95:
                                try:
                                    img = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
                                    need_recompression = True
                                except AttributeError:
                                    try:
                                        img = img.resize((new_width, new_height), Image.BICUBIC)
                                        need_recompression = True
                                    except AttributeError:
                                        img = img.resize((new_width, new_height))
                                        need_recompression = True
                        
                        # Only recompress if needed or for aggressive mode
                        if need_recompression or aggressive:
                            # Compress as JPEG with high optimization - use lower quality for bitmap sources
                            final_quality = max(jpeg_quality - 10, 35)  # Even lower quality for bitmaps
                            if aggressive:
                                final_quality = max(30, jpeg_quality - 20)  # Much more aggressive
                                
                            img_buffer = io.BytesIO()
                            img.save(img_buffer, format="JPEG", quality=final_quality, optimize=True)
                            img_buffer.seek(0)
                            new_data = img_buffer.read()
                            
                            # Always replace in aggressive mode, otherwise only if smaller
                            if aggressive or len(new_data) < len(img_data):
                                pim.write(new_data, filter=pikepdf.Name.DCTDecode)
                                
                                # Update color space
                                if mode == "L":
                                    pim["/ColorSpace"] = pikepdf.Name.DeviceGray
                                elif mode == "RGB":
                                    pim["/ColorSpace"] = pikepdf.Name.DeviceRGB
                                
                                # Remove unnecessary entries that are not compatible with JPEG
                                for key in ["/DecodeParms", "/Interpolate"]:
                                    if key in pim:
                                        del pim[key]
                                
                                # Update bits per component for JPEG
                                pim["/BitsPerComponent"] = 8
                            
                    except Exception as e:
                        # If there's an error processing this image, skip it
                        logging.warning(f"Error processing image: {str(e)}")
                        continue
                    
            except Exception as e:
                # Skip images that can't be processed
                logging.warning(f"Error processing image: {str(e)}")
                continue
                
    except Exception as e:
        # If anything else goes wrong, just log and continue
        logging.warning(f"Error processing page: {str(e)}")
