import os
import logging
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap

def select_images(self):
    files, _ = QFileDialog.getOpenFileNames(
        self,
        "Select Images",
        "",
        "Image Files (*.jpg *.jpeg *.png *.bmp)"
    )
    if files:
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.listbox.addItem(os.path.basename(file))
        
        if self.current_index < 0 or self.current_index >= len(self.selected_files):
            self.current_index = 0
        
        self.update_picture_box()
        self.status_label.setText(f"Added {len(files)} images. Total: {len(self.selected_files)}")
        
        # Update conversion tab UI if it exists
        if hasattr(self, 'update_conversion_ui'):
            self.update_conversion_ui()

def prev_image(self):
    """Navigate to the previous image in the selected files list"""
    if self.selected_files and self.current_index > 0:
        self.current_index -= 1
        self.update_picture_box()

def next_image(self):
    """Navigate to the next image in the selected files list"""
    if self.selected_files and self.current_index < len(self.selected_files) - 1:
        self.current_index += 1
        self.update_picture_box()

def update_picture_box(self):
    """Update the image preview based on the current index"""
    if len(self.selected_files) > 0 and 0 <= self.current_index < len(self.selected_files):
        try:
            # Open the image
            img = Image.open(self.selected_files[self.current_index])
            
            # Apply rotation if stored
            if self.current_index in self.rotations:
                angle = self.rotations[self.current_index]
                if angle == 90:
                    img = img.transpose(Image.Transpose.ROTATE_90)
                elif angle == 180:
                    img = img.transpose(Image.Transpose.ROTATE_180)
                elif angle == 270:
                    img = img.transpose(Image.Transpose.ROTATE_270)
            
            # Apply zoom factor and resize to fit preview
            img_width, img_height = img.size
            new_width = int(img_width * self.zoom_factor)
            new_height = int(img_height * self.zoom_factor)
            
            # Resize the image maintaining aspect ratio
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert PIL Image to QPixmap for display
            img_data = img.tobytes("raw", "RGB")
            qimage = QImage(img_data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            
            self.preview_label.setPixmap(pixmap)
            self.status_label.setText(f"Image {self.current_index + 1} of {len(self.selected_files)}")
            
            # Update listbox selection
            if self.listbox.count() > 0:
                self.listbox.setCurrentRow(self.current_index)
        except Exception as e:
            logging.error(f"Error in update_picture_box: {str(e)}")
            self.status_label.setText("Error loading image.")
    else:
        self.preview_label.clear()
        self.status_label.setText("No images selected!")

def rotate_image(self):
    """Rotate the current image 90 degrees clockwise"""
    if len(self.selected_files) == 0:
        self.status_label.setText("No image to rotate!")
        return
    
    if self.current_index in self.rotations:
        self.rotations[self.current_index] = (self.rotations[self.current_index] + 90) % 360
    else:
        self.rotations[self.current_index] = 90
    
    self.update_picture_box()
    self.status_label.setText(f"Rotated image {self.current_index + 1} to {self.rotations[self.current_index]}°")

def on_listbox_select(self, current_row):
    """Handle the selection of an item in the listbox"""
    if current_row >= 0:
        self.current_index = current_row
        self.update_picture_box()

def move_up(self):
    """Move the selected image up in the list"""
    current_row = self.listbox.currentRow()
    if current_row > 0:
        # Swap items in list widget
        item_text = self.listbox.item(current_row).text()
        self.listbox.takeItem(current_row)
        self.listbox.insertItem(current_row - 1, item_text)
        
        # Swap selected files
        self.selected_files[current_row], self.selected_files[current_row - 1] = \
            self.selected_files[current_row - 1], self.selected_files[current_row]
        
        # Swap rotations if they exist
        if current_row in self.rotations and current_row - 1 in self.rotations:
            self.rotations[current_row], self.rotations[current_row - 1] = \
                self.rotations[current_row - 1], self.rotations[current_row]
        elif current_row in self.rotations:
            self.rotations[current_row - 1] = self.rotations.pop(current_row)
        elif current_row - 1 in self.rotations:
            self.rotations[current_row] = self.rotations.pop(current_row - 1)
        
        self.current_index = current_row - 1
        self.listbox.setCurrentRow(self.current_index)
        self.update_picture_box()
        self.status_label.setText(f"Moved image up. Current position: {self.current_index + 1}")

def move_down(self):
    """Move the selected image down in the list"""
    current_row = self.listbox.currentRow()
    if current_row >= 0 and current_row < self.listbox.count() - 1:
        # Swap items in list widget
        item_text = self.listbox.item(current_row).text()
        self.listbox.takeItem(current_row)
        self.listbox.insertItem(current_row + 1, item_text)
        
        # Swap selected files
        self.selected_files[current_row], self.selected_files[current_row + 1] = \
            self.selected_files[current_row + 1], self.selected_files[current_row]
        
        # Swap rotations if they exist
        if current_row in self.rotations and current_row + 1 in self.rotations:
            self.rotations[current_row], self.rotations[current_row + 1] = \
                self.rotations[current_row + 1], self.rotations[current_row]
        elif current_row in self.rotations:
            self.rotations[current_row + 1] = self.rotations.pop(current_row)
        elif current_row + 1 in self.rotations:
            self.rotations[current_row] = self.rotations.pop(current_row + 1)
        
        self.current_index = current_row + 1
        self.listbox.setCurrentRow(self.current_index)
        self.update_picture_box()
        self.status_label.setText(f"Moved image down. Current position: {self.current_index + 1}")

def delete_image(self):
    """Delete the selected image from the list"""
    current_row = self.listbox.currentRow()
    if current_row >= 0:
        try:
            # Remove from selected files list
            del self.selected_files[current_row]
            
            # Update rotations dictionary
            if current_row in self.rotations:
                del self.rotations[current_row]
            
            # Reindex rotations for items after the deleted one
            new_rotations = {}
            for key, value in self.rotations.items():
                if key > current_row:
                    new_rotations[key - 1] = value
                elif key < current_row:
                    new_rotations[key] = value
            self.rotations = new_rotations
            
            # Remove from listbox
            self.listbox.takeItem(current_row)
            
            # Update current index
            if self.listbox.count() == 0:
                self.current_index = -1
            elif current_row >= self.listbox.count():
                self.current_index = self.listbox.count() - 1
            else:
                self.current_index = current_row
            
            self.update_picture_box()
            self.status_label.setText(f"Deleted image. Remaining: {len(self.selected_files)}")
            
            # Update conversion tab UI if it exists
            if hasattr(self, 'update_conversion_ui'):
                self.update_conversion_ui()
        except Exception as e:
            logging.error(f"Error in delete_image: {str(e)}")
            QMessageBox.critical(self, "Error", "Error deleting image. See error.log for details.")

def reset_inputs(self):
    """Reset all inputs and image selections"""
    self.selected_files = []
    self.rotations = {}
    self.current_index = 0
    self.listbox.clear()
    self.update_picture_box()
    self.progress_bar.setValue(0)
    self.status_label.setText("All images and settings have been reset")
    self.zoom_factor = 1.0
    self.latest_pdf = None
    
    # Reset UI elements if they exist
    if hasattr(self, 'btn_preview_pdf'):
        self.btn_preview_pdf.setEnabled(False)
    if hasattr(self, 'btn_print_pdf'):
        self.btn_print_pdf.setEnabled(False)
    if hasattr(self, 'btn_compress'):
        self.btn_compress.setEnabled(False)
    if hasattr(self, 'pdf_info'):
        self.pdf_info.setText("No PDF has been selected or created yet.")
    
    # Update conversion tab UI if it exists
    if hasattr(self, 'update_conversion_ui'):
        self.update_conversion_ui()

def wheelEvent(self, event):
    """Handle mouse wheel events for zooming"""
    # Mouse wheel for zooming
    delta = event.angleDelta().y()
    if delta > 0:
        self.zoom_factor += 0.1
    else:
        self.zoom_factor = max(0.1, self.zoom_factor - 0.1)
    self.update_picture_box()
