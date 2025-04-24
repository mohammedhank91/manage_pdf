import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import math
import logging
from datetime import datetime

class ImageToPdfConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to PDF Converter")
        self.root.geometry("950x700")
        self.root.configure(bg="white")
        
        # Global variables
        self.zoom_factor = 1.0
        self.latest_pdf = None
        self.selected_files = []
        self.rotations = {}  # Key: index, Value: rotation angle (0,90,180,270)
        self.current_index = 0
        
        # Setup logging
        log_dir = os.path.join(os.environ.get('APPDATA', ''), 'PDF Manager')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'error.log')
        logging.basicConfig(filename=log_file, level=logging.ERROR, 
                           format='%(asctime)s : %(message)s', 
                           datefmt='%Y-%m-%d %H:%M:%S')
        
        # Create and place all widgets
        self.create_widgets()
        
        # Setup drag-and-drop
        self.setup_drag_drop()
        
    def create_widgets(self):
        # Main label
        self.label = tk.Label(self.root, text="Convert Images (JPG, PNG) to PDF", 
                            font=("Arial", 14, "bold"), bg="white")
        self.label.place(x=25, y=10, width=900, height=30)
        
        # Select images button
        self.btn_select = tk.Button(self.root, text="Select Images", 
                                  font=("Arial", 10, "bold"), command=self.select_images)
        self.btn_select.place(x=25, y=50, width=180, height=40)
        
        # Checkbox for separate PDFs
        self.separate_var = tk.BooleanVar()
        self.chk_separate = tk.Checkbutton(self.root, text="Save each image as a separate PDF", 
                                         font=("Arial", 10), bg="white", 
                                         variable=self.separate_var)
        self.chk_separate.place(x=25, y=100, width=300, height=25)
        
        # Margin (border) options
        tk.Label(self.root, text="Margin (px):", font=("Arial", 10), bg="white").place(x=350, y=100, width=80, height=25)
        self.margin_var = tk.IntVar(value=10)
        self.num_margin = ttk.Spinbox(self.root, from_=0, to=100, textvariable=self.margin_var, font=("Arial", 10))
        self.num_margin.place(x=430, y=100, width=60, height=25)
        
        # Orientation options
        tk.Label(self.root, text="Orientation:", font=("Arial", 10), bg="white").place(x=510, y=100, width=80, height=25)
        self.orientation_var = tk.StringVar(value="Portrait")
        self.combo_orient = ttk.Combobox(self.root, values=["Portrait", "Landscape"], 
                                        textvariable=self.orientation_var, font=("Arial", 10))
        self.combo_orient.place(x=590, y=100, width=120, height=25)
        
        # Convert button
        self.btn_convert = tk.Button(self.root, text="Convert to PDF", 
                                   font=("Arial", 10, "bold"), command=self.convert_to_pdf)
        self.btn_convert.place(x=25, y=135, width=180, height=40)
        
        # Reset button
        self.btn_reset = tk.Button(self.root, text="Reset", 
                                font=("Arial", 10, "bold"), command=self.reset_inputs)
        self.btn_reset.place(x=215, y=135, width=180, height=40)
        
        # Image preview area
        self.preview_frame = tk.Frame(self.root, width=550, height=350, bg="white", bd=1, relief=tk.SOLID)
        self.preview_frame.place(x=25, y=190)
        self.preview_label = tk.Label(self.preview_frame, bg="white")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Rotate button
        self.btn_rotate = tk.Button(self.root, text="Rotate Image", 
                                  font=("Arial", 10, "bold"), command=self.rotate_image)
        self.btn_rotate.place(x=590, y=190, width=150, height=30)
        
        # Navigation buttons
        self.btn_prev = tk.Button(self.root, text="Previous", 
                                font=("Arial", 10, "bold"), command=self.prev_image)
        self.btn_prev.place(x=25, y=550, width=150, height=30)
        
        self.btn_next = tk.Button(self.root, text="Next", 
                                font=("Arial", 10, "bold"), command=self.next_image)
        self.btn_next.place(x=225, y=550, width=150, height=30)
        
        # Image list
        self.listbox = tk.Listbox(self.root, font=("Arial", 9))
        self.listbox.place(x=590, y=240, width=280, height=200)
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # Delete button
        self.btn_delete = tk.Button(self.root, text="Delete Image", 
                                 font=("Arial", 10, "bold"), command=self.delete_image)
        self.btn_delete.place(x=590, y=450, width=150, height=30)
        
        # Up and Down buttons
        self.btn_up = tk.Button(self.root, text="Up", 
                             font=("Arial", 10, "bold"), command=self.move_up)
        self.btn_up.place(x=750, y=450, width=120, height=30)
        
        self.btn_down = tk.Button(self.root, text="Down", 
                               font=("Arial", 10, "bold"), command=self.move_down)
        self.btn_down.place(x=590, y=490, width=120, height=30)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"), 
                                   bg="white", fg="darkblue")
        self.status_label.place(x=25, y=600, width=900, height=30)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=900, mode='determinate')
        self.progress_bar.place(x=25, y=640, width=900, height=20)
        
        # Preview and Print PDF buttons (hidden by default)
        self.btn_preview_pdf = tk.Button(self.root, text="Preview PDF", 
                                      font=("Arial", 10, "bold"), command=self.preview_pdf)
        self.btn_preview_pdf.place(x=25, y=680, width=150, height=40)
        self.btn_preview_pdf.place_forget()  # Hide initially
        
        self.btn_print_pdf = tk.Button(self.root, text="Print PDF", 
                                    font=("Arial", 10, "bold"), command=self.print_pdf)
        self.btn_print_pdf.place(x=200, y=680, width=150, height=40)
        self.btn_print_pdf.place_forget()  # Hide initially
        
        # Bind mousewheel for zoom
        self.preview_label.bind("<MouseWheel>", self.on_mousewheel)
        
    def setup_drag_drop(self):
        # This is a placeholder as Tkinter doesn't natively support drag and drop
        # For actual implementation, consider using TkDnD or tkinterdnd2 libraries
        self.status_label.config(text="Note: Drag and drop requires additional libraries")
    
    def update_picture_box(self):
        if len(self.selected_files) > 0 and 0 <= self.current_index < len(self.selected_files):
            try:
                # Open the image
                img = Image.open(self.selected_files[self.current_index])
                
                # Apply rotation if stored
                if self.current_index in self.rotations:
                    angle = self.rotations[self.current_index]
                    if angle == 90:
                        img = img.transpose(Image.ROTATE_90)
                    elif angle == 180:
                        img = img.transpose(Image.ROTATE_180)
                    elif angle == 270:
                        img = img.transpose(Image.ROTATE_270)
                
                # Apply zoom factor and resize to fit preview
                img_width, img_height = img.size
                new_width = int(img_width * self.zoom_factor)
                new_height = int(img_height * self.zoom_factor)
                
                # Resize the image maintaining aspect ratio to fit in preview frame
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Create PhotoImage for display
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo  # Keep a reference
                
                self.status_label.config(text=f"Image {self.current_index + 1} of {len(self.selected_files)}")
                
                # Update listbox selection
                if self.listbox.size() > 0:
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(self.current_index)
                    self.listbox.see(self.current_index)
            except Exception as e:
                logging.error(f"Error in update_picture_box: {str(e)}")
                self.status_label.config(text="Error loading image.")
        else:
            self.preview_label.config(image="")
            self.status_label.config(text="No images selected!")
    
    def select_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.listbox.insert(tk.END, os.path.basename(file))
            
            if self.current_index < 0 or self.current_index >= len(self.selected_files):
                self.current_index = 0
            
            self.update_picture_box()
    
    def rotate_image(self):
        if len(self.selected_files) == 0:
            self.status_label.config(text="No image to rotate!")
            return
        
        if self.current_index in self.rotations:
            self.rotations[self.current_index] = (self.rotations[self.current_index] + 90) % 360
        else:
            self.rotations[self.current_index] = 90
        
        self.update_picture_box()
    
    def on_listbox_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.update_picture_box()
    
    def move_up(self):
        idx = self.listbox.curselection()
        if idx and idx[0] > 0:
            idx = idx[0]
            # Swap list items
            self.listbox.delete(idx-1)
            self.listbox.insert(idx, os.path.basename(self.selected_files[idx]))
            self.listbox.delete(idx)
            self.listbox.insert(idx-1, os.path.basename(self.selected_files[idx-1]))
            
            # Swap selected files
            self.selected_files[idx-1], self.selected_files[idx] = self.selected_files[idx], self.selected_files[idx-1]
            
            # Swap rotations if they exist
            if idx in self.rotations and idx-1 in self.rotations:
                self.rotations[idx-1], self.rotations[idx] = self.rotations[idx], self.rotations[idx-1]
            elif idx in self.rotations:
                self.rotations[idx-1] = self.rotations.pop(idx)
            elif idx-1 in self.rotations:
                self.rotations[idx] = self.rotations.pop(idx-1)
            
            self.current_index = idx - 1
            self.listbox.selection_set(self.current_index)
            self.update_picture_box()
    
    def move_down(self):
        idx = self.listbox.curselection()
        if idx and idx[0] < self.listbox.size() - 1:
            idx = idx[0]
            # Swap list items
            self.listbox.delete(idx+1)
            self.listbox.insert(idx, os.path.basename(self.selected_files[idx+1]))
            self.listbox.delete(idx)
            self.listbox.insert(idx+1, os.path.basename(self.selected_files[idx]))
            
            # Swap selected files
            self.selected_files[idx], self.selected_files[idx+1] = self.selected_files[idx+1], self.selected_files[idx]
            
            # Swap rotations if they exist
            if idx in self.rotations and idx+1 in self.rotations:
                self.rotations[idx], self.rotations[idx+1] = self.rotations[idx+1], self.rotations[idx]
            elif idx in self.rotations:
                self.rotations[idx+1] = self.rotations.pop(idx)
            elif idx+1 in self.rotations:
                self.rotations[idx] = self.rotations.pop(idx+1)
            
            self.current_index = idx + 1
            self.listbox.selection_set(self.current_index)
            self.update_picture_box()
    
    def delete_image(self):
        idx = self.listbox.curselection()
        if idx:
            idx = idx[0]
            try:
                # Remove from selected files list
                del self.selected_files[idx]
                
                # Update rotations dictionary
                if idx in self.rotations:
                    del self.rotations[idx]
                
                # Reindex rotations for items after the deleted one
                new_rotations = {}
                for key, value in self.rotations.items():
                    if key > idx:
                        new_rotations[key - 1] = value
                    elif key < idx:
                        new_rotations[key] = value
                self.rotations = new_rotations
                
                # Remove from listbox
                self.listbox.delete(idx)
                
                # Update current index
                if self.listbox.size() == 0:
                    self.current_index = -1
                elif idx >= self.listbox.size():
                    self.current_index = self.listbox.size() - 1
                else:
                    self.current_index = idx
                
                self.update_picture_box()
            except Exception as e:
                logging.error(f"Error in delete_image: {str(e)}")
                messagebox.showerror("Error", "Error deleting image. See error.log for details.")
    
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_picture_box()
    
    def next_image(self):
        if self.current_index < len(self.selected_files) - 1:
            self.current_index += 1
            self.update_picture_box()
    
    def on_mousewheel(self, event):
        # Mouse wheel for zooming
        delta = event.delta if hasattr(event, 'delta') else -1 * event.num if event.num == 5 else 1
        if delta > 0:
            self.zoom_factor += 0.1
        else:
            self.zoom_factor = max(0.1, self.zoom_factor - 0.1)
        self.update_picture_box()
    
    def reset_inputs(self):
        self.selected_files = []
        self.rotations = {}
        self.current_index = 0
        self.listbox.delete(0, tk.END)
        self.update_picture_box()
        self.progress_bar['value'] = 0
        self.status_label.config(text="")
        self.zoom_factor = 1.0
        self.latest_pdf = None
        self.btn_preview_pdf.place_forget()
        self.btn_print_pdf.place_forget()
    
    def convert_to_pdf(self):
        if len(self.selected_files) == 0:
            self.status_label.config(text="No images selected!")
            return
        
        margin = self.margin_var.get()
        orientation = self.orientation_var.get()
        apply_global_orientation = (orientation == "Landscape")
        
        try:
            if self.separate_var.get():
                # Save as separate PDFs
                folder = filedialog.askdirectory(title="Select Output Folder")
                if folder:
                    self.progress_bar['value'] = 0
                    total = len(self.selected_files)
                    count = 0
                    
                    for i, img_file in enumerate(self.selected_files):
                        out_file = os.path.join(folder, os.path.splitext(os.path.basename(img_file))[0] + ".pdf")
                        
                        # Build ImageMagick command
                        rotate_option = f"-rotate {self.rotations[i]}" if i in self.rotations else ""
                        border_option = f"-border {margin} -bordercolor white" if margin > 0 else ""
                        orient_option = "-rotate 90" if apply_global_orientation else ""
                        
                        cmd = f"magick \"{img_file}\" {rotate_option} {border_option} {orient_option} \"{out_file}\""
                        subprocess.run(cmd, shell=True)
                        
                        count += 1
                        self.progress_bar['value'] = math.floor((count / total) * 100)
                        self.root.update_idletasks()
                    
                    self.status_label.config(text="All images saved as separate PDFs.")
                    messagebox.showinfo("Info", "PDF conversion complete.")
            else:
                # Save as single PDF
                output_pdf = filedialog.asksaveasfilename(
                    title="Save PDF As",
                    defaultextension=".pdf",
                    filetypes=[("PDF Files", "*.pdf")]
                )
                if output_pdf:
                    self.progress_bar['value'] = 0
                    border_option = f"-border {margin} -bordercolor white" if margin > 0 else ""
                    orient_option = "-rotate 90" if apply_global_orientation else ""
                    
                    # Build file string for ImageMagick
                    files_string = " ".join([f"\"{file}\" {border_option} {orient_option}" for file in self.selected_files])
                    cmd = f"magick {files_string} \"{output_pdf}\""
                    
                    subprocess.run(cmd, shell=True)
                    
                    self.progress_bar['value'] = 100
                    self.status_label.config(text=f"PDF created: {output_pdf}")
                    messagebox.showinfo("Info", "PDF conversion complete.")
                    
                    # Store the latest PDF file path and show preview/print buttons
                    self.latest_pdf = output_pdf
                    self.btn_preview_pdf.place(x=25, y=680, width=150, height=40)
                    self.btn_print_pdf.place(x=200, y=680, width=150, height=40)
        except Exception as e:
            logging.error(f"Error in conversion: {str(e)}")
            messagebox.showerror("Error", "Error during PDF conversion. See error.log for details.")
    
    def preview_pdf(self):
        if self.latest_pdf and os.path.exists(self.latest_pdf):
            # Open PDF with the default application
            if os.name == 'nt':  # Windows
                os.startfile(self.latest_pdf)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(('xdg-open', self.latest_pdf))
        else:
            messagebox.showwarning("Warning", "No PDF available to preview.")
    
    def print_pdf(self):
        if self.latest_pdf and os.path.exists(self.latest_pdf):
            if os.name == 'nt':  # Windows
                subprocess.call(['start', '', '/print', self.latest_pdf], shell=True)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['lpr', self.latest_pdf])
        else:
            messagebox.showwarning("Warning", "No PDF available to print.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPdfConverter(root)
    root.mainloop() 