from PIL import Image

# Open the icon – by default Pillow will pick the first frame in an .ico
ico = Image.open('src/resources/manage_pdf.ico')

# Create the large version
large = ico.resize((164, 314), Image.LANCZOS)
large.save('src/resources/wizard_image.bmp', format='BMP')

# Create the small version
small = ico.resize((55, 58), Image.LANCZOS)
small.save('src/resources/wizard_small.bmp', format='BMP')
